"""
Kaggle task definitions for cognitive benchmarks.
"""

from vigil.tasks.track1_learning import (
    concept_formation_sub,
    associative_sub,
    reinforcement_sub,
    observational_sub,
    procedural_sub,
    language_sub,
    vigil_learning_benchmark,
    _run_episode,
)

__all__ = [
    "concept_formation_sub",
    "associative_sub",
    "reinforcement_sub",
    "observational_sub",
    "procedural_sub",
    "language_sub",
    "vigil_learning_benchmark",
    "_run_episode",
]
