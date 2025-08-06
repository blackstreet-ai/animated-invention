"""Pipeline state definition.

This module defines :class:`PipelineState`, a single dataclass instance that
flows through the entire multi-agent pipeline.  Each ADK agent receives the
state, mutates its dedicated fields, and returns it to the orchestrator.

Why a *single* object?  It simplifies passing intermediate artifacts
between agents while allowing type checking and easy serialization.

Feel free to extend this schema as new data points become necessary (e.g.
transcription text, generated clip paths, etc.).  Downstream agents should
**never** rely on unknown attributes—add them explicitly here with
documented purpose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PipelineState:
    """Centralized container for pipeline-wide data.

    Attributes
    ----------
    topic: str | None
        The user-supplied or AI-generated video essay topic.
    research_notes: str | None
        Structured notes/facts gathered by the ResearchAgent.
    script: str | None
        Full video script produced by the ScriptwriterAgent.
    visual_assets: List[Path]
        Filepaths to images/video clips generated or selected by the VisualAgent.
    audio_assets: List[Path]
        Filepaths to voice-over tracks, SFX, or music produced by the AudioAgent.
    final_video: Optional[Path]
        Path to the rendered video created by the EditorAgent.
    metadata: Dict[str, Any]
        Free-form dictionary for miscellaneous info (e.g., timing, agent logs).
    """

    topic: Optional[str] = None
    research_notes: Optional[str] = None
    script: Optional[str] = None
    visual_assets: List[Path] = field(default_factory=list)
    audio_assets: List[Path] = field(default_factory=list)
    final_video: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the state to a JSON-serializable dict.
        Useful for checkpointing or inspection.
        """
        return {
            "topic": self.topic,
            "research_notes": self.research_notes,
            "script": self.script,
            "visual_assets": [str(p) for p in self.visual_assets],
            "audio_assets": [str(p) for p in self.audio_assets],
            "final_video": str(self.final_video) if self.final_video else None,
            "metadata": self.metadata,
        }
