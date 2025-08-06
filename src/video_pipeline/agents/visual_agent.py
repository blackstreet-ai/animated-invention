"""VisualAgent stub.

Generates or fetches visual assets (images, clips) that accompany the script.
Real implementations might interface with image generation APIs or stock
footage databases.
"""

from __future__ import annotations

from pathlib import Path

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState


class VisualAgent(BaseAgent):
    """Produces visual aids for the video essay."""

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        # Add placeholder image path
        dummy_image = Path("assets/placeholder_image.png")
        state.visual_assets.append(dummy_image)
        return state
