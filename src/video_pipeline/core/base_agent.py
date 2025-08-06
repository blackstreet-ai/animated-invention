"""Common foundation for all ADK agents in the pipeline.

Every specialised agent (ResearchAgent, ScriptwriterAgent, etc.) inherits from :class:`BaseAgent`.
This layer encapsulates boilerplate such as:
* ADK agent registration / configuration
* Logging helpers (standardised prefix with agent name)
* Error handling wrapper around the `run` method

The class purposefully stays *lightweight*—business logic belongs in child classes.
If you need reusable utilities shared across agents (e.g. retry logic, API helpers), add them here with proper documentation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    from adk import Agent  # type: ignore
except ImportError:  # pragma: no cover
    # Allow import when ADK is not yet installed so that tests still run.
    class Agent:  # type: ignore
        """Fallback shim if ADK unavailable.

        Remove once ADK is installed.  Only implements the minimal API we use
        during scaffolding (i.e., `__init__` accepting `name`).
        """

        def __init__(self, name: str, **kwargs: Any) -> None:  # noqa: D401
            self.name = name


class BaseAgent(Agent):
    """Abstract base class wrapping :class:`adk.Agent` with extras.

    *All* concrete agents must implement :meth:`_execute` which performs the
    agent's actual task and returns (optionally mutated) pipeline state.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:  # noqa: D401
        # Pass through to ADK base class (or shim)
        super().__init__(name=name, **kwargs)
        # Standard logger per agent
        self.logger = logging.getLogger(name)

    # ---------------------------------------------------------------------
    # Public API expected by the WorkflowManager
    # ---------------------------------------------------------------------
    def run(self, state: "video_pipeline.core.state.PipelineState") -> "video_pipeline.core.state.PipelineState":
        """Execute the agent while handling errors uniformly.

        Parameters
        ----------
        state
            Current :class:`PipelineState` instance.
        """
        try:
            self.logger.info("Starting %s", self.__class__.__name__)
            new_state = self._execute(state)
            self.logger.info("Finished %s successfully", self.__class__.__name__)
            return new_state
        except Exception as exc:  # pragma: no cover
            self.logger.exception("%s encountered an error: %s", self.__class__.__name__, exc)
            # Record the failure in metadata so downstream agents can react.
            state.metadata.setdefault("errors", []).append({
                "agent": self.__class__.__name__,
                "error": str(exc),
            })
            return state

    # ------------------------------------------------------------------
    # Mandatory override in subclasses
    # ------------------------------------------------------------------
    def _execute(self, state: "video_pipeline.core.state.PipelineState") -> "video_pipeline.core.state.PipelineState":  # noqa: D401, E501
        """Subclass hook containing domain logic (must be overridden)."""
        raise NotImplementedError(
            "_execute must be implemented by concrete agent subclasses"
        )
