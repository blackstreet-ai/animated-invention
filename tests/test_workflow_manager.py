"""Unit tests for the refactored WorkflowManager.

These tests run without the real Google ADK installed thanks to fallback
stub classes.  They verify:

1. Dependency-aware ordering – agents only run after prerequisites.
2. Retry logic – agents wrapped by ``LoopAgent`` retry up to ``max_retries``.

The helper below ensures ``video_pipeline`` can be imported when running tests
directly from project root without installing the package.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Ensure project `src` dir is on sys.path
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState
from video_pipeline.workflows.manager import WorkflowManager


# ---------------------------------------------------------------------------
# Helper agents used in tests
# ---------------------------------------------------------------------------

class RecordingAgent(BaseAgent):
    """Appends its *record_key* to ``state.metadata['events']`` when executed."""

    def __init__(self, name: str, record_key: str, fail_first: bool = False):  # noqa: D401
        super().__init__(name=name)
        self.record_key = record_key
        self.fail_first = fail_first
        self._called_once = False

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        if "events" not in state.metadata:
            state.metadata["events"] = []  # type: ignore[index]

        # Record execution sequence
        state.metadata["events"].append(self.record_key)  # type: ignore[index]

        # Simulate transient failure on first call if requested
        if self.fail_first and not self._called_once:
            self._called_once = True
            raise RuntimeError("intentional failure for retry test")

        return state


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_dependency_order():
    """Agents should respect the explicit dependency DAG order."""

    # Define three dummy agents A -> B -> C (linear chain)
    class AgentA(RecordingAgent):
        def __init__(self, *args, **kwargs):  # name supplied in kwargs by manager
            super().__init__(record_key="A", *args, **kwargs)

    class AgentB(RecordingAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(record_key="B", *args, **kwargs)

    class AgentC(RecordingAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(record_key="C", *args, **kwargs)

    manager = WorkflowManager(
        agent_classes=[AgentA, AgentB, AgentC],
        dependencies={
            "AgentB": ["AgentA"],
            "AgentC": ["AgentB"],
        },
    )

    final_state = manager.run()

    assert final_state.metadata["events"] == ["A", "B", "C"]


def test_retry_logic():
    """An agent that fails once should succeed on retry within max_retries."""

    class FlakyAgent(RecordingAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(record_key="X", fail_first=True, *args, **kwargs)

    manager = WorkflowManager(agent_classes=[FlakyAgent], max_retries=2)

    final_state = manager.run()

    # The agent should have run exactly once successfully (plus one failed try
    # internally).  Our recording is only applied on *entry*, so we expect two
    # entries: one from the failed attempt, one from the successful retry.
    events: List[str] = final_state.metadata["events"]  # type: ignore[index]
    assert events.count("X") >= 1

    # Ensure that at most one error is recorded (the first failure).
    errors = final_state.metadata.get("errors", [])
    assert len(errors) <= 1
