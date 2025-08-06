"""QualityControlAgent stub.

Performs a final review of the produced video, checking for obvious issues
(e.g., missing assets, duration mismatches).  At scaffold time it only logs a
success message.
"""

from __future__ import annotations

from video_pipeline.core.base_agent import BaseAgent
from video_pipeline.core.state import PipelineState


class QualityControlAgent(BaseAgent):
    """Reviews final output and produces feedback."""

    def _execute(self, state: PipelineState) -> PipelineState:  # noqa: D401
        # Record QC status in metadata
        state.metadata["qc_passed"] = True
        state.metadata["qc_notes"] = "[STUB] QC passed – replace with real checks."
        return state
