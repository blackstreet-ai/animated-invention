"""ResearchAgent stub.

Responsible for gathering factual information, citations, and links about the
chosen topic.  At this scaffold stage it merely logs a message and sets a
placeholder in :attr:`PipelineState.research_notes`.

Once real logic is added, consider integrating web search APIs, Wikipedia,
or other knowledge bases.  Follow ADK best practices for tool usage and
external calls.
"""

from __future__ import annotations

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState


class ResearchAgent(BaseAgent):
    """Collects research notes for the video essay."""

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        # For now, just insert a stub note.
        state.research_notes = (
            "[STUB] ResearchAgent executed – replace with real research logic."
        )
        return state
