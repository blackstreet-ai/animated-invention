"""EditorAgent stub.

Assembles visual and audio assets into a single video file. In future, hook
into ffmpeg or moviepy for programmatic editing.
"""

from __future__ import annotations

from pathlib import Path

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState


class EditorAgent(BaseAgent):
    """Renders the final video from visuals and audio."""

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        # Placeholder output path (no real rendering yet)
        state.final_video = Path("output/placeholder_video.mp4")
        return state
