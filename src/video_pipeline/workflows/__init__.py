"""Workflow orchestration subpackage.

Contains classes that coordinate the sequence and parallelism of agents.
Currently only a minimal sequential WorkflowManager is provided.
"""

from .manager import WorkflowManager  # noqa: F401
