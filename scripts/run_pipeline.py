#!/usr/bin/env python3
"""Entry point to run the *stub* AI Video Essay Pipeline.

Usage
-----
$ python scripts/run_pipeline.py --topic "Climate Change"

At this scaffold stage each agent simply adds placeholder data, but the full
workflow runs end-to-end so you can verify dependencies and packaging.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List

import yaml

# Ensure local src/ is importable when executing from project root
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from video_pipeline.agents import (  # noqa: E402
    ResearchAgent,
    ScriptwriterAgent,
    VisualAgent,
    AudioAgent,
    EditorAgent,
    QualityControlAgent,
    TopicGenerationAgent,
)
from video_pipeline.core.state import PipelineState  # noqa: E402
from video_pipeline.workflows import WorkflowManager  # noqa: E402


DEFAULT_AGENT_ORDER: List[type] = [
    ResearchAgent,
    ScriptwriterAgent,
    VisualAgent,
    AudioAgent,
    EditorAgent,
    QualityControlAgent,
]


def main() -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="Run AI Video Essay Pipeline (stub)")
    parser.add_argument("--topic", required=False, help="Video essay topic")
    parser.add_argument(
        "--config",
        default="configs/default.yml",
        help="Path to YAML config file (default: configs/default.yml)",
    )
    parser.add_argument(
        "--discover-topics",
        action="store_true",
        help="Run TopicGenerationAgent first to generate topic ideas before the main pipeline.",
    )
    args = parser.parse_args()

    # Load YAML config (unused for now but demonstrates future pattern)
    config_path = Path(args.config)
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text())
    else:
        logging.warning("Config file %s not found; proceeding with defaults", config_path)
        config = {}

    logging.basicConfig(level=config.get("logging", {}).get("level", "INFO"))

    # Build agent list based on CLI flag
    agent_order: List[type] = DEFAULT_AGENT_ORDER.copy()
    if args.discover_topics:
        logging.info("Idea-discovery mode enabled – TopicGenerationAgent will run first.")
        agent_order.insert(0, TopicGenerationAgent)

    state = PipelineState(topic=args.topic)
    manager = WorkflowManager(agent_order)
    final_state = manager.run(state)

    logging.info("Pipeline finished. Final state: %s", final_state.to_dict())


if __name__ == "__main__":  # pragma: no cover
    main()
