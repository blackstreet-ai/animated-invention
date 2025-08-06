"""ScriptwriterAgent stub.

Converts research notes (or directly the topic) into a full narrative script.
In production, this would likely call an LLM via ADK tools.  For now it just
inserts a placeholder string.
"""

from __future__ import annotations

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState


class ScriptwriterAgent(BaseAgent):
    """Generates the video essay script from researched content."""

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        state.script = (
            "[STUB] ScriptwriterAgent executed – replace with LLM-based script generation."
        )
        return state
