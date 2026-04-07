"""
Cognitive profile data structures.

Provides structured representation of multi-metric cognitive assessments,
including human baseline comparison (Req 18.2, 18.3, 18.5).
"""

from dataclasses import dataclass, field
from math import erf, sqrt
from typing import Any, Dict, List, Optional


@dataclass
class HumanBaseline:
    """
    Human performance distribution for one scenario.

    Stores per-participant VIS dimension scores collected under identical
    environment conditions. Used to compute AI percentile rankings.

    Attributes:
        scenario_id:          Which scenario this baseline covers
        participants:         List of per-participant score dicts (one per person)
        n:                    Number of participants
        track_dimensions:     TrackScorer output for the human session
                              (e.g. {"correctness": 0.7, "evidence_coverage": 0.8})
        evaluation_conditions: Conditions under which the session was run.
                              Must match the AI evaluation conditions for valid comparison.
    """
    scenario_id: str
    participants: List[Dict[str, float]] = field(default_factory=list)
    n: int = 0
    track_dimensions: Dict[str, float] = field(default_factory=dict)
    evaluation_conditions: Dict[str, Any] = field(default_factory=dict)

    def add_participant(self, scores: Dict[str, float]) -> None:
        """Add one participant's scores."""
        self.participants.append(scores)
        self.n = len(self.participants)

    def compute_percentile(self, vis_score: float, dimension: str = "vis") -> float:
        """
        Return the percentile rank of vis_score within the human distribution
        for the given dimension.

        Args:
            vis_score: The AI score to rank
            dimension: Which VIS dimension to compare against (default "vis")

        Returns:
            Percentile (0.0–100.0). Returns 50.0 if insufficient data.
        """
        values = [p.get(dimension, 0.0) for p in self.participants if dimension in p]
        if len(values) < 2:
            return 50.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = sqrt(variance)
        if std <= 0:
            return 50.0
        z = (vis_score - mean) / std
        return round(0.5 * (1 + erf(z / sqrt(2))) * 100, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "n": self.n,
            "participants": self.participants,
            "track_dimensions": self.track_dimensions,
            "evaluation_conditions": self.evaluation_conditions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HumanBaseline":
        obj = cls(scenario_id=data["scenario_id"])
        obj.participants = data.get("participants", [])
        obj.n = len(obj.participants)
        obj.track_dimensions = data.get("track_dimensions", {})
        obj.evaluation_conditions = data.get("evaluation_conditions", {})
        return obj


@dataclass
class CognitiveProfile:
    """
    Multi-dimensional cognitive assessment.

    Represents a model's performance across multiple cognitive metrics,
    suitable for comparison against human baselines.

    Attributes:
        correctness: Binary task success (0.0-1.0)
        efficiency: Path optimization score (0.0-1.0)
        evidence_quality: Evidence collection score (0.0-1.0)
        calibration: Confidence-accuracy match (0.0-1.0)
        recovery: Adaptation after errors (0.0-1.0)
        overall_score: Weighted combination of metrics
        human_percentile: Percentile vs human baseline (0-100)
        metadata: Additional profile data
    """
    correctness: float = 0.0
    efficiency: float = 0.0
    evidence_quality: float = 0.0
    calibration: float = 0.0
    recovery: float = 0.0
    overall_score: float = 0.0
    human_percentile: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "correctness": self.correctness,
            "efficiency": self.efficiency,
            "evidence_quality": self.evidence_quality,
            "calibration": self.calibration,
            "recovery": self.recovery,
            "overall_score": self.overall_score
        }

        if self.human_percentile is not None:
            result["human_percentile"] = self.human_percentile

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveProfile":
        """Create from dictionary."""
        return cls(
            correctness=data.get("correctness", 0.0),
            efficiency=data.get("efficiency", 0.0),
            evidence_quality=data.get("evidence_quality", 0.0),
            calibration=data.get("calibration", 0.0),
            recovery=data.get("recovery", 0.0),
            overall_score=data.get("overall_score", 0.0),
            human_percentile=data.get("human_percentile"),
            metadata=data.get("metadata", {})
        )

    def to_summary_string(self) -> str:
        """
        Generate human-readable summary.

        Returns:
            Formatted string summary of cognitive profile
        """
        lines = [
            "Cognitive Profile Summary",
            "=" * 40,
            f"  Correctness:       {self.correctness:.2f}",
            f"  Efficiency:        {self.efficiency:.2f}",
            f"  Evidence Quality:  {self.evidence_quality:.2f}",
            f"  Calibration:       {self.calibration:.2f}",
            f"  Recovery:          {self.recovery:.2f}",
            "-" * 40,
            f"  Overall Score:     {self.overall_score:.2f}"
        ]

        if self.human_percentile is not None:
            lines.append(f"  Human Percentile:  {self.human_percentile:.1f}%")

        return "\n".join(lines)

    def compute_human_percentile(
        self,
        human_mean: float,
        human_std: float
    ) -> float:
        """
        Compute percentile relative to human baseline.

        Uses normal distribution approximation.

        Args:
            human_mean: Mean human score
            human_std: Standard deviation of human scores

        Returns:
            Percentile (0-100)
        """
        if human_std <= 0:
            return 50.0

        # Z-score
        z = (self.overall_score - human_mean) / human_std

        # Convert to percentile (using approximation)
        # erf(x) ≈ tanh(0.797885 * x + 0.035677 * x^3)
        from math import erf
        percentile = 0.5 * (1 + erf(z / sqrt(2))) * 100

        self.human_percentile = percentile
        return percentile


@dataclass
class TrackProfile:
    """
    Aggregated profile for a cognitive track.

    Combines multiple scenario results into a track-level assessment.

    Attributes:
        track_name: Name of the cognitive track
        profiles: List of individual scenario profiles
        aggregate_scores: Aggregated metric scores
    """
    track_name: str
    profiles: List[CognitiveProfile] = field(default_factory=list)
    aggregate_scores: Dict[str, float] = field(default_factory=dict)

    def add_profile(self, profile: CognitiveProfile) -> None:
        """Add a scenario profile to the track."""
        self.profiles.append(profile)
        self._update_aggregates()

    def _update_aggregates(self) -> None:
        """Update aggregate scores from all profiles."""
        if not self.profiles:
            return

        metrics = [
            "correctness", "efficiency", "evidence_quality",
            "calibration", "recovery", "overall_score"
        ]

        for metric in metrics:
            values = [getattr(p, metric) for p in self.profiles]
            self.aggregate_scores[metric] = sum(values) / len(values)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "track_name": self.track_name,
            "profiles": [p.to_dict() for p in self.profiles],
            "aggregate_scores": self.aggregate_scores
        }
