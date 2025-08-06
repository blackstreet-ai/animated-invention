"""WorkflowManager orchestrates sequential execution of agents.

In later iterations you may replace this simple sequential model with more
complex graphs, dynamic branching, or ADK's built-in workflow primitives.
"""

from __future__ import annotations

import logging
from typing import List, Sequence, Type

from video_pipeline.core.state import PipelineState
from video_pipeline.core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WorkflowManager:
    """Runs agents in a specified order and returns the final state."""

    def __init__(self, agent_classes: Sequence[Type[BaseAgent]]):  # noqa: D401
        self.agents: List[BaseAgent] = [cls(name=cls.__name__) for cls in agent_classes]

    def run(self, initial_state: PipelineState | None = None) -> PipelineState:
        """Execute all agents sequentially.

        Parameters
        ----------
        initial_state
            Optional pre-filled :class:`PipelineState`. If *None*, a fresh one
            is created.
        """
        state = initial_state or PipelineState()
        for agent in self.agents:
            logger.debug("Passing state to %s", agent.__class__.__name__)
            state = agent.run(state)
        return state
