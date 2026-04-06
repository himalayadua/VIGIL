"""
Kaggle task definitions for cognitive benchmarks.

Each task is decorated with @kbench.task and implements
a specific cognitive ability test.
"""

# Tasks are defined in separate modules by track
from vigil.tasks.track1_learning import (
    concept_formation_task,
    associative_learning_task,
    reinforcement_learning_task
)

__all__ = [
    "concept_formation_task",
    "associative_learning_task",
    "reinforcement_learning_task"
]
