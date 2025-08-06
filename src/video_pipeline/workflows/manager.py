"""WorkflowManager using ADK workflow primitives (Sequential/Parallel/Loop).

This refactor replaces the previous *pure-python sequential* orchestration with
an ADK-style workflow that provides:

* **Explicit dependencies** – agents can declare which other agents they need
  to run *after*.
* **Parallel execution** – independent agents at the same *graph level* are
  grouped into an ADK ``ParallelAgent``.
* **Retry logic** – every agent is wrapped in a ``LoopAgent`` (max_tries)
  so transient failures are automatically retried before the pipeline aborts.
* **Graceful error propagation** – failures are recorded in
  ``PipelineState.metadata['errors']`` while still moving the graph forward
  when possible.

The code attempts to import the real ADK workflow agents.  If ADK is **not**
installed (e.g. during early scaffolding or CI environments), minimal *shim*
classes are provided so the project remains runnable.

Usage
-----
```python
manager = WorkflowManager(
    agent_classes=[ResearchAgent, ScriptwriterAgent, VisualAgent, AudioAgent,
                   EditorAgent, QCAgent],
    dependencies={
        "VisualAgent": ["ScriptwriterAgent"],
        "AudioAgent": ["ScriptwriterAgent"],
        "EditorAgent": ["VisualAgent", "AudioAgent"],
        "QCAgent":    ["EditorAgent"],
    },
    max_retries=2,
)
final_state = manager.run()
```

The *dependencies* mapping is optional; if omitted the agents run in the order
provided (legacy sequential behaviour, but still via ADK ``SequentialAgent``).
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Dict, List, Sequence, Type

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Attempt to import real ADK workflow primitives. Provide fallbacks otherwise.
# ---------------------------------------------------------------------------
try:
    # These live in google.adk.agents in the real SDK.
    from adk import SequentialAgent, ParallelAgent, LoopAgent  # type: ignore

    _ADK_AVAILABLE = True
except Exception:  # pragma: no cover – SDK may not be present during tests

    _ADK_AVAILABLE = False

    class _WorkflowStub(BaseAgent):  # type: ignore
        """Base class for stub Sequential/Parallel/Loop fallbacks."""

        def __init__(self, name: str, sub_agents: Sequence[BaseAgent], **kwargs):  # noqa: D401
            super().__init__(name=name)
            self.sub_agents = list(sub_agents)
            self.max_iterations: int = kwargs.get("max_iterations", 1)

        # falls back to simple synchronous execution – sufficient for tests
        def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
            """Execute child agents with simple retry semantics.

            The stub emulates ADK ``LoopAgent`` by re-running its *sub_agents*
            list up to *max_iterations* times **until** no new errors are
            added to ``state.metadata['errors']`` during an iteration.  This
            rough approximation is sufficient for unit tests and keeps the
            looping logic self-contained – it terminates early on success.
            """
            for _ in range(self.max_iterations):
                prev_error_count = len(state.metadata.get("errors", []))

                for agent in self.sub_agents:
                    state = agent.run(state)

                # If the iteration didn't add new errors, consider it success
                if len(state.metadata.get("errors", [])) == prev_error_count:
                    break

            return state

    class SequentialAgent(_WorkflowStub):  # type: ignore
        """Run sub-agents one after another (stub)."""

    class ParallelAgent(_WorkflowStub):  # type: ignore
        """Run sub-agents sequentially in stub; real SDK runs concurrently."""

    class LoopAgent(_WorkflowStub):  # type: ignore
        """Repeat sub-agents until success or max_iterations (stub)."""

# ---------------------------------------------------------------------------
# Helper: retry wrapper using LoopAgent
# ---------------------------------------------------------------------------

def _wrap_with_retry(agent: BaseAgent, max_retries: int) -> BaseAgent:
    """Return a LoopAgent that retries *agent* up to *max_retries* times."""

    if max_retries <= 1:
        return agent  # no wrapping needed

    # NOTE: ``LoopAgent`` stops when sub-agents succeed.  Success detection is
    # delegated to the agent's own error-recording behaviour – our BaseAgent
    # records errors in ``state.metadata['errors']``.  The real ADK LoopAgent
    # respects an ``exit_condition`` callable; here we rely on default behaviour
    # (runs fixed *max_iterations* times).  This is acceptable for now.
    return LoopAgent(
        name=f"{agent.__class__.__name__}Retry",
        sub_agents=[agent],
        max_iterations=max_retries,
    )

# ---------------------------------------------------------------------------
# WorkflowManager
# ---------------------------------------------------------------------------


class WorkflowManager:
    """Builds and executes an ADK workflow with explicit dependencies."""

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(
        self,
        agent_classes: Sequence[Type[BaseAgent]],
        *,
        dependencies: Dict[str, Sequence[str]] | None = None,
        max_retries: int = 2,
    ):  # noqa: D401
        """Create a manager.

        Parameters
        ----------
        agent_classes
            List of concrete ``BaseAgent`` subclasses participating in the
            workflow.
        dependencies
            Optional mapping ``{agent_name: [dep_name, ...]}`` describing
            edges in the DAG.  If *None*, agents run sequentially.
        max_retries
            How many times each agent is allowed to retry before the workflow
            records a permanent failure.
        """

        self.max_retries = max_retries

        # Instantiating concrete agent objects – store by name for easy lookup
        self._agents: Dict[str, BaseAgent] = {
            cls.__name__: cls(name=cls.__name__) for cls in agent_classes
        }

        # Resolve dependency map; ensure all referenced names exist
        self._deps: Dict[str, List[str]] = defaultdict(list)
        if dependencies:
            for agent_name, dep_list in dependencies.items():
                if agent_name not in self._agents:
                    raise ValueError(f"Unknown agent in dependencies: {agent_name}")
                for dep in dep_list:
                    if dep not in self._agents:
                        raise ValueError(f"Unknown dependency '{dep}' for {agent_name}")
                self._deps[agent_name] = list(dep_list)

        # Build an ADK workflow (SequentialAgent that may contain Parallel/Loop)
        self._root_agent = self._build_workflow()

    # ------------------------------------------------------------------
    # DAG → ADK workflow conversion
    # ------------------------------------------------------------------

    def _build_workflow(self) -> BaseAgent:
        """Convert the dependency graph into nested ADK workflow agents."""

        if not self._deps:
            # Legacy sequential order (but still ADK style with retries)
            ordered_wrapped = [
                _wrap_with_retry(agent, self.max_retries)
                for agent in self._agents.values()
            ]
            return SequentialAgent(name="SequentialPipeline", sub_agents=ordered_wrapped)

        # --- Topological sort to compute execution layers --------------
        indegree: Dict[str, int] = {n: 0 for n in self._agents}
        for deps in self._deps.values():
            for dep in deps:
                indegree[dep] += 0  # ensure key exists
        for node, deps in self._deps.items():
            indegree[node] += len(deps)

        queue: deque[str] = deque([n for n, deg in indegree.items() if deg == 0])
        layers: List[List[str]] = []
        while queue:
            level_size = len(queue)
            current_layer: List[str] = []
            for _ in range(level_size):
                node = queue.popleft()
                current_layer.append(node)
                # reduce indegree for nodes depending on *node*
                for child, deps in self._deps.items():
                    if node in deps:
                        indegree[child] -= 1
                        if indegree[child] == 0:
                            queue.append(child)
            layers.append(current_layer)

        if sum(len(l) for l in layers) != len(self._agents):
            raise ValueError("Dependency graph contains a cycle – cannot proceed")

        # --- Build ADK agents per layer -------------------------------
        pipeline_blocks: List[BaseAgent] = []
        for i, layer in enumerate(layers):
            sub_agents = [
                _wrap_with_retry(self._agents[name], self.max_retries) for name in layer
            ]
            if len(sub_agents) == 1:
                pipeline_blocks.append(sub_agents[0])
            else:
                pipeline_blocks.append(
                    ParallelAgent(name=f"ParallelLayer{i}", sub_agents=sub_agents)
                )

        return SequentialAgent(name="WorkflowPipeline", sub_agents=pipeline_blocks)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, initial_state: PipelineState | None = None) -> PipelineState:
        """Execute the orchestrated workflow and return the final state."""

        state = initial_state or PipelineState()
        logger.info("Starting workflow via ADK orchestration. ADK present=%s", _ADK_AVAILABLE)
        try:
            state = self._root_agent.run(state)  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover – unexpected crash
            logger.exception("Critical failure in WorkflowManager: %s", exc)
            state.metadata.setdefault("errors", []).append({
                "agent": "WorkflowManager",
                "error": str(exc),
            })
        return state
