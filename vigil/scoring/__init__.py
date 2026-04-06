"""
Scoring engine for cognitive benchmarks.
"""

from vigil.scoring.profile import CognitiveProfile, HumanBaseline, TrackProfile
from vigil.scoring.vis import VISScorer
from vigil.scoring.metrics import (
    compute_correctness,
    compute_efficiency,
    compute_evidence_quality,
    compute_calibration,
    compute_recovery,
    compute_weighted_score,
)

__all__ = [
    "CognitiveProfile",
    "HumanBaseline",
    "TrackProfile",
    "VISScorer",
    "compute_correctness",
    "compute_efficiency",
    "compute_evidence_quality",
    "compute_calibration",
    "compute_recovery",
    "compute_weighted_score",
]
