"""Subpackage aggregating all specialised pipeline agents.

Importing this subpackage registers or exposes each agent class so that other
modules (e.g., workflow manager, tests) can refer to them via
`video_pipeline.agents.ResearchAgent` etc.
"""

from .research_agent import ResearchAgent  # noqa: F401
from .scriptwriter_agent import ScriptwriterAgent  # noqa: F401
from .visual_agent import VisualAgent  # noqa: F401
from .audio_agent import AudioAgent  # noqa: F401
from .editor_agent import EditorAgent  # noqa: F401
from .qc_agent import QualityControlAgent  # noqa: F401
