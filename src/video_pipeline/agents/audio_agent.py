"""AudioAgent stub.

Handles text-to-speech voiceover generation and background music selection.
In future iterations integrate TTS APIs (e.g., ElevenLabs, Google TTS) and
royalty-free music libraries.
"""

from __future__ import annotations

from pathlib import Path

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState


class AudioAgent(BaseAgent):
    """Generates audio tracks for the video essay."""

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        dummy_audio = Path("assets/placeholder_voiceover.mp3")
        state.audio_assets.append(dummy_audio)
        return state
