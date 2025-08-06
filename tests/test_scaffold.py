"""Smoke tests ensuring scaffold imports and stub pipeline run.

Run with:
    pytest -q
"""

from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "module_path",
    [
        "video_pipeline.core.state",
        "video_pipeline.core.base_agent",
        "video_pipeline.agents.research_agent",
        "video_pipeline.workflows.manager",
    ],
)
def test_imports(module_path):  # noqa: D401
    """Verify core modules import without error."""
    __import__(module_path)


def test_run_script_smoke(tmp_path: Path):  # noqa: D401
    """Run the pipeline script and assert non-zero exit."""

    script = Path(__file__).resolve().parents[1] / "scripts" / "run_pipeline.py"
    result = subprocess.run(
        [sys.executable, str(script), "--topic", "Test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Pipeline finished" in result.stdout
