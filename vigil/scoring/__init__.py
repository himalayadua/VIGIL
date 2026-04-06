"""
Scoring engine for cognitive benchmarks.

Provides multi-metric scoring for cognitive profile generation.
"""

from vigil.scoring.profile import CognitiveProfile
from vigil.scoring.metrics import (
    compute_correctness,
    compute_efficiency,
    compute_evidence_quality,
    compute_calibration,
    compute_recovery,
    compute_weighted_score
)

__all__ = [
    "CognitiveProfile",
    "compute_correctness",
    "compute_efficiency",
    "compute_evidence_quality",
    "compute_calibration",
    "compute_recovery",
    "compute_weighted_score"
]
