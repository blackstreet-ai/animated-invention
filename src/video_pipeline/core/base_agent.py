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
import asyncio
from typing import Any, Dict, Optional, Callable, Awaitable, Iterable

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

# ---------------------------------------------------------------------------
# Optional A2A protocol client import with graceful fallback
# ---------------------------------------------------------------------------

try:
    # The real Google A2A Python SDK exposes `Client` (per upstream examples).
    from a2a import Client as _A2AClient  # type: ignore

    _A2A_AVAILABLE = True
except Exception:  # pragma: no cover – A2A SDK might not be installed yet
    _A2A_AVAILABLE = False

    class _A2AClient:  # type: ignore
        """Minimal no-op stub so the codebase can run without A2A installed."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
            pass

        async def send_event(self, event: Dict[str, Any]) -> None:  # noqa: D401
            return None

        async def send_request(self, to_agent: str, message: Dict[str, Any]) -> Any:  # noqa: D401,E501
            return None

        def register_handler(
            self, message_type: str, handler: Callable[[Any], Awaitable[None]]
        ) -> None:  # noqa: D401
            return None


class BaseAgent(Agent):
    """Abstract base class wrapping :class:`adk.Agent` with extras.

    *All* concrete agents must implement :meth:`_execute` which performs the
    agent's actual task and returns (optionally mutated) pipeline state.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:  # noqa: D401
        """Create a new agent.

        Parameters
        ----------
        name
            Human-readable identifier.
        a2a_client
            Optional pre-configured A2A client instance.  If *None*, the
            constructor attempts to create a default ``_A2AClient`` so that
            messaging APIs always exist (even if they are no-op stubs while the
            real SDK is missing).
        **kwargs
            Passed straight through to the underlying ADK ``Agent``.
        """

        # Extract optional A2A client so we don't forward an unexpected kwarg to
        # the ADK Agent base class.
        a2a_client: Optional[_A2AClient] = kwargs.pop("a2a_client", None)  # type: ignore[arg-type]

        # Initialise ADK parent (or shim) *before* we access logging so ADK can
        # override attrs if necessary.
        super().__init__(name=name, **kwargs)

        # Standard logger per agent (namespaced by agent name)
        self.logger = logging.getLogger(name)

        # ------------------------------------------------------------------
        # A2A wiring
        # ------------------------------------------------------------------
        self._a2a: _A2AClient = a2a_client or _A2AClient()
        # Local registry for convenience – mirrors remote registration too.
        self._handlers: Dict[str, Callable[[Any], Awaitable[None]]] = {}

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

    # ------------------------------------------------------------------
    # 🔌 A2A Messaging Helpers
    # ------------------------------------------------------------------

    async def broadcast_event(self, event_data: Dict[str, Any]) -> None:  # noqa: D401,E501
        """Publish an *event* to **all** interested agents via A2A.

        The underlying A2A client is awaited, so callers inside synchronous
        code paths should schedule this with :pyfunc:`asyncio.create_task` or
        wrap the coroutine with :pyfunc:`asyncio.run` where appropriate.
        """

        await self._a2a.send_event(event_data)

    async def send_request(self, to_agent: str, message: Dict[str, Any]) -> Any:  # noqa: D401,E501
        """Send a direct *request* to another agent.

        Returns
        -------
        Any
            Whatever the remote agent responds with (depends on protocol).
        """

        return await self._a2a.send_request(to_agent, message)

    def register_handler(
        self,
        message_type: str,
        handler_func: Callable[[Any], Awaitable[None]],
    ) -> None:  # noqa: D401,E501
        """Register a coroutine callback for a specific *message_type*."""

        self._handlers[message_type] = handler_func
        # Propagate to underlying client (no-op if stub).
        self._a2a.register_handler(message_type, handler_func)

    async def stream_updates(self, generator: Iterable[Any]) -> None:  # noqa: D401,E501
        """Utility that relays progress *updates* emitted by *generator*.

        Parameters
        ----------
        generator
            Any synchronous or asynchronous iterable yielding update payloads.
        """

        # Support both sync and async iterables.
        if hasattr(generator, "__aiter__"):
            async for update in generator:  # type: ignore[misc]
                await self.broadcast_event(update)
        else:
            for update in generator:  # type: ignore[not-an-iterable]
                # Fire-and-forget to avoid blocking sync caller.
                asyncio.create_task(self.broadcast_event(update))
