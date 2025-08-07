# WorkflowManager (ADK Orchestrator)

The **WorkflowManager** converts a list of agent classes plus an optional
*dependency graph* into native Agent Development Kit (ADK) workflow primitives
so you get robust orchestration with **zero boilerplate** in user code.

## Key Features

| Capability | ADK Primitive | How it works |
|------------|--------------|--------------|
| Sequential execution | `SequentialAgent` | Layers (computed via topological sort) are chained in order. |
| Parallel fan-out | `ParallelAgent` | Agents that share the same dependency layer run concurrently. |
| Automatic retries | `LoopAgent` | Each agent is wrapped in a `LoopAgent` (up to `max_retries`). |
| Error propagation | `BaseAgent.run()` | Failures are logged and stored in `state.metadata["errors"]`. |
| ADK-less fallback | Stub classes | If ADK isn’t installed, stub workflows run synchronously so tests still pass. |

## Quick Start

```python
from video_pipeline.workflows.manager import WorkflowManager
from video_pipeline.agents import (
    ResearchAgent, ScriptwriterAgent, VisualAgent,
    AudioAgent, EditorAgent, QCAgent,
)

manager = WorkflowManager(
    agent_classes=[ResearchAgent, ScriptwriterAgent,
                   VisualAgent, AudioAgent, EditorAgent, QCAgent],
    dependencies={
        "VisualAgent": ["ScriptwriterAgent"],
        "AudioAgent":  ["ScriptwriterAgent"],
        "EditorAgent": ["VisualAgent", "AudioAgent"],
        "QCAgent":     ["EditorAgent"],
    },
    max_retries=2,
)

final_state = manager.run()
print(final_state.to_dict())
```

## Design Notes

1. **Dependency Handling**  
   A simple *dict* (`{agent_name: [dependency_name, …]}`) is topologically
   sorted into layers. Cycles raise `ValueError`.
2. **Retry Policy**  
   `max_retries=1` disables retry wrapping. Otherwise, each concrete agent is
   placed inside an ADK `LoopAgent` repeating until success or the retry limit.
3. **ADK Optional**  
   The first import attempt loads `SequentialAgent`, `ParallelAgent`, and
   `LoopAgent` from `adk`. If that fails (e.g., in CI without ADK), minimal
   stubs inherit from `BaseAgent` so the code remains runnable.

## Running Tests

```bash
source .venv/bin/activate     # if not already
pytest -q tests/test_workflow_manager.py
```

The test suite validates ordering and retry semantics both with and without the
real ADK present.
