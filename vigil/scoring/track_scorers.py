"""
TrackScorer — per-track scoring classes.

Each scorer takes an EnvironmentState, final_answer, justification, and
RuntimeScenarioSpec, and returns a ScoreCard dict. The ScoreCard contains
track-specific dimension scores but does NOT contain a "vis" key — that is
computed by VISScorer.score_episode() in the task loop.

Scorer classes are named after the cognitive faculty, not a track number.
This matches the cognitive_track string dispatch key.

Requirements: 9
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set


class TrackScorer(ABC):
    """
    Abstract base class for per-track scorers.

    Subclasses implement score() for their specific cognitive track.
    The returned ScoreCard must NOT contain a "vis" key.
    """

    def __init__(self, spec: Any) -> None:
        self.spec = spec

    @abstractmethod
    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        """
        Compute track-specific dimension scores.

        Returns:
            ScoreCard dict with at minimum:
              - outcome_score (float 0.0–1.0)
              - process_score (float 0.0–1.0)
              - track_id (str)
              - behavioral_signatures (dict)
              - contamination_warning (bool)
            Must NOT contain a "vis" key.
        """
        pass

    @staticmethod
    def for_track(cognitive_track: str, spec: Any) -> "TrackScorer":
        """
        Return the appropriate TrackScorer for the given cognitive_track string.

        Dispatches by cognitive_track string — never by track number.
        """
        dispatch = {
            "learning": LearningScorer,
            "metacognition": MetacognitionScorer,
            "attention": AttentionScorer,
            "executive_functions": ExecutiveScorer,
            "social_cognition": SocialScorer,
        }
        scorer_cls = dispatch.get(cognitive_track, _StubScorer)
        return scorer_cls(spec)


class _StubScorer(TrackScorer):
    """
    Stub scorer for tracks whose full scorer is not yet implemented.

    Returns a minimal ScoreCard with neutral scores. Used for tracks 2–5
    until their scorers are built in tasks 12–14.
    """

    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        return {
            "outcome_score": 0.0,
            "process_score": 0.0,
            "track_id": getattr(spec, "cognitive_track", "unknown"),
            "behavioral_signatures": {},
            "contamination_warning": False,
            "_stub": True,
        }


# ---------------------------------------------------------------------------
# LearningScorer — Track 1 (learning) full implementation
# ---------------------------------------------------------------------------

class LearningScorer(TrackScorer):
    """
    Track 1 (learning) scorer.

    Scores against the authored scoring_config fields in spec.track_metadata.
    Returns a ScoreCard with no "vis" key — VISScorer wraps it.

    Dimensions:
      correctness         — graded via correctness_tiers (not binary)
      path_efficiency     — len(optimal_path) / max(len(visited_nodes), 1)
      evidence_coverage   — inspected evidence targets / total evidence targets
      justification_quality — cited node IDs in justification / total cited
      behavioral_signatures — from authored metadata + trace analysis
      contamination_warning — from anti_shortcutting_audit + path directness

    process_score = weighted combination using spec.scoring_weights.
    """

    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        """
        Compute the LearningScorer ScoreCard.

        Args:
            state:         Final EnvironmentState after episode ends.
            final_answer:  Model's submitted answer string.
            justification: Model's submitted justification string.
            spec:          RuntimeScenarioSpec for this scenario.

        Returns:
            ScoreCard dict — no "vis" key.
        """
        # Resolve inspected_nodes: use state.inspected_nodes if available
        # (added in task 9), otherwise fall back to state.visited_nodes
        inspected: List[str] = (
            list(getattr(state, "inspected_nodes", None) or state.visited_nodes)
        )

        # --- Dimension 1: correctness (graded via correctness_tiers) ---
        correctness = self._compute_correctness(final_answer, spec)

        # --- Dimension 2: path_efficiency ---
        path_efficiency = self._compute_path_efficiency(state, spec)

        # --- Dimension 3: evidence_coverage ---
        evidence_coverage = self._compute_evidence_coverage(inspected, spec)

        # --- Dimension 4: justification_quality ---
        justification_quality = self._compute_justification_quality(
            justification, inspected
        )

        # --- Dimension 5: behavioral_signatures ---
        behavioral_signatures = self._compute_behavioral_signatures(state, spec)

        # --- Dimension 6: contamination_warning ---
        contamination_warning = self._compute_contamination_warning(state, spec)

        # --- process_score: weighted combination ---
        process_score = self._compute_process_score(
            correctness=correctness,
            path_efficiency=path_efficiency,
            evidence_coverage=evidence_coverage,
            justification_quality=justification_quality,
            behavioral_signatures=behavioral_signatures,
            spec=spec,
        )

        return {
            "outcome_score": round(correctness, 4),
            "process_score": round(process_score, 4),
            "track_id": "learning",
            "correctness": round(correctness, 4),
            "path_efficiency": round(path_efficiency, 4),
            "evidence_coverage": round(evidence_coverage, 4),
            "justification_quality": round(justification_quality, 4),
            "behavioral_signatures": behavioral_signatures,
            "contamination_warning": contamination_warning,
        }

    # ------------------------------------------------------------------
    # Dimension implementations
    # ------------------------------------------------------------------

    def _compute_correctness(self, final_answer: str, spec: Any) -> float:
        """
        Graded correctness via scoring_config.correctness_tiers.

        correctness_tiers maps tier labels to description strings:
          "full_1.0"    → 1.0
          "partial_0.5" → 0.5
          "partial_0.3" → 0.3
          "zero"        → 0.0

        Matching is case-insensitive substring: if the answer contains
        any key phrase from a tier's description, that tier's score applies.
        The highest matching tier wins.
        """
        sc = spec.track_metadata.get("scoring_config", {})
        tiers = sc.get("correctness_tiers", {})

        if not tiers:
            # Fallback: exact match against answer_targets
            correct = spec.answer_targets.get("correct_root_cause", "")
            if correct and final_answer.strip().upper() == correct.strip().upper():
                return 1.0
            return 0.0

        answer_lower = final_answer.lower()
        best_score = 0.0

        for tier_key, tier_desc in tiers.items():
            # Parse score from tier key: "full_1.0" → 1.0, "partial_0.5" → 0.5
            tier_score = self._parse_tier_score(tier_key)
            if tier_score <= best_score:
                continue

            # Check if answer matches this tier's description
            if self._answer_matches_tier(answer_lower, tier_desc, spec):
                best_score = tier_score

        return best_score

    @staticmethod
    def _parse_tier_score(tier_key: str) -> float:
        """Extract numeric score from tier key like 'full_1.0' or 'partial_0.5'."""
        m = re.search(r"(\d+\.?\d*)", tier_key)
        if m:
            return float(m.group(1))
        if tier_key.lower() == "zero":
            return 0.0
        return 0.0

    @staticmethod
    def _answer_matches_tier(answer_lower: str, tier_desc: str, spec: Any) -> bool:
        """
        Check if the answer matches a correctness tier.

        For the "full" tier: check against answer_targets.correct_root_cause.
        For other tiers: check if any key phrase from the tier description
        appears in the answer.
        """
        # Full credit: check against the canonical correct answer
        correct_root = spec.answer_targets.get("correct_root_cause", "")
        correct_mechanism = spec.answer_targets.get("correct_mechanism", "")

        desc_lower = tier_desc.lower()

        # If tier description mentions the correct root cause entity, check for it
        if correct_root and correct_root.lower() in answer_lower:
            return True
        if correct_mechanism and correct_mechanism.lower() in answer_lower:
            return True

        # Keyword matching: extract significant words from tier description
        # and check if any appear in the answer
        words = [w for w in re.findall(r"\b[a-z]{4,}\b", desc_lower)
                 if w not in {"that", "this", "with", "from", "into", "does",
                               "have", "been", "also", "only", "both", "more",
                               "than", "when", "then", "they", "their", "which"}]
        if not words:
            return False

        # Require at least 2 matching keywords for partial tiers
        matches = sum(1 for w in words if w in answer_lower)
        return matches >= 2

    @staticmethod
    def _compute_path_efficiency(state: Any, spec: Any) -> float:
        """
        path_efficiency = len(optimal_path) / max(len(visited_nodes), 1)

        High efficiency: model visited approximately the optimal number of nodes.
        Capped at 1.0 (can't be more efficient than optimal).
        """
        optimal_len = len(spec.optimal_path)
        actual_len = max(len(state.visited_nodes), 1)
        if optimal_len == 0:
            return 0.5  # neutral when no optimal path defined
        return min(1.0, optimal_len / actual_len)

    @staticmethod
    def _compute_evidence_coverage(inspected: List[str], spec: Any) -> float:
        """
        evidence_coverage = |inspected ∩ evidence_targets| / max(|evidence_targets|, 1)

        Uses inspected_nodes (task 9) if available, else visited_nodes.
        """
        targets = set(spec.evidence_targets)
        if not targets:
            return 1.0  # no targets defined → full coverage by default
        covered = len(set(inspected) & targets)
        return covered / len(targets)

    @staticmethod
    def _compute_justification_quality(
        justification: str, inspected: List[str]
    ) -> float:
        """
        justification_quality = |cited_ids ∩ inspected| / max(|cited_ids|, 1)

        Citation grounding: fraction of node IDs mentioned in the justification
        that actually appear in the inspected (or visited) node list.
        """
        if not justification:
            return 0.0

        # Extract node IDs from justification (patterns: N01, n1, node_5, etc.)
        cited = set(re.findall(r"\b(?:[Nn]ode_?\d+|[Nn]\d+|[A-Z]\d{2,})\b", justification))
        if not cited:
            return 0.0

        inspected_set = set(inspected)
        matched = cited & inspected_set
        return len(matched) / len(cited)

    @staticmethod
    def _compute_behavioral_signatures(state: Any, spec: Any) -> Dict[str, Any]:
        """
        Compute behavioral signatures from authored metadata + trace analysis.

        Authored signatures come from spec.track_metadata["behavioral_signatures"].
        Trace-derived signatures are computed from state.action_history.
        """
        from vigil.environments.base import EventType

        authored = spec.track_metadata.get("behavioral_signatures", {})
        # authored may be a list or dict depending on the scenario
        if isinstance(authored, list):
            authored = {}

        history = getattr(state, "action_history", [])
        if not history:
            return dict(authored)

        # Trace-derived: perseveration (repeated explore of same node)
        visited_counts: Dict[str, int] = {}
        for event in history:
            if hasattr(event, "event_type") and event.event_type == EventType.EXPLORE:
                nid = event.node_id or ""
                visited_counts[nid] = visited_counts.get(nid, 0) + 1
        revisit_count = sum(1 for c in visited_counts.values() if c > 1)
        total_explores = sum(1 for e in history
                             if hasattr(e, "event_type") and e.event_type == EventType.EXPLORE)

        trace_sigs: Dict[str, Any] = {}
        if total_explores > 0:
            trace_sigs["perseveration_rate"] = round(revisit_count / total_explores, 4)

        # Premature stopping: submitted before visiting any evidence target
        evidence_targets = set(spec.evidence_targets)
        visited = set(getattr(state, "visited_nodes", []))
        if evidence_targets and not (visited & evidence_targets):
            trace_sigs["premature_stopping"] = True

        return {**authored, **trace_sigs}

    @staticmethod
    def _compute_contamination_warning(state: Any, spec: Any) -> bool:
        """
        Contamination warning from anti_shortcutting_audit + path directness.

        Returns True if the episode looks suspiciously direct (possible memorisation).
        """
        from vigil.environments.base import EventType

        history = getattr(state, "action_history", [])
        if not history:
            return False

        # Signal 1: path directness — unique explores / total explores
        explore_events = [
            e for e in history
            if hasattr(e, "event_type") and e.event_type == EventType.EXPLORE
        ]
        if explore_events:
            unique = len({e.node_id for e in explore_events if e.node_id})
            directness = unique / len(explore_events)
        else:
            directness = 0.0

        # Signal 2: submitted very early (< 20% of budget used)
        budget_used = sum(
            abs(e.state_delta.get("budget_delta", 0))
            for e in history
            if hasattr(e, "state_delta")
        )
        budget_total = getattr(spec, "runtime_config", None)
        budget_total = budget_total.action_budget if budget_total else 16
        early_submit = (budget_used / max(budget_total, 1)) < 0.2

        return directness > 0.9 and early_submit

    def _compute_process_score(
        self,
        correctness: float,
        path_efficiency: float,
        evidence_coverage: float,
        justification_quality: float,
        behavioral_signatures: Dict[str, Any],
        spec: Any,
    ) -> float:
        """
        Weighted combination of dimensions using spec.scoring_weights.

        scoring_weights keys: "correctness", "path_efficiency",
        "evidence_coverage", "justification_quality", "behavioral_signatures".
        """
        weights = spec.scoring_weights

        # behavioral_signatures score: 1.0 - perseveration_rate (if present)
        perseveration = behavioral_signatures.get("perseveration_rate", 0.0)
        sig_score = max(0.0, 1.0 - perseveration)

        dim_values = {
            "correctness": correctness,
            "path_efficiency": path_efficiency,
            "evidence_coverage": evidence_coverage,
            "justification_quality": justification_quality,
            "behavioral_signatures": sig_score,
        }

        total_weight = sum(weights.get(k, 0.0) for k in dim_values)
        if total_weight <= 0:
            # Equal weighting fallback
            return sum(dim_values.values()) / len(dim_values)

        weighted_sum = sum(
            dim_values[k] * weights.get(k, 0.0)
            for k in dim_values
        )
        return weighted_sum / total_weight


# ---------------------------------------------------------------------------
# MetacognitionScorer — Track 2 (metacognition) full implementation
# ---------------------------------------------------------------------------

class MetacognitionScorer(TrackScorer):
    """
    Track 2 (metacognition) scorer — Kaggle Track 2.

    Separately measures object-level correctness and meta-level self-monitoring.
    Returns ScoreCard with outcome_score = object_score, process_score = meta_score.

    Dimensions:
      object_score              — answer vs. object_level_goal
      calibration_score         — 1 - |confidence_at_submission - correctness|
      revision_quality          — 1.0 if contradiction event followed by new-node within 3 steps
      verification_efficiency   — evidence_nodes / max(verification_actions, 1)
      help_seeking_appropriateness — fraction of help requests above budget threshold
      behavioral_signatures     — overconfidence, underconfidence, premature_stopping, etc.
    """

    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        """Compute MetacognitionScorer ScoreCard."""
        # --- object_score: answer vs. object_level_goal ---
        object_score = self._compute_object_score(final_answer, spec)

        # --- calibration_score ---
        calibration_score = self._compute_calibration_score(state, object_score)

        # --- revision_quality ---
        revision_quality = self._compute_revision_quality(state)

        # --- verification_efficiency ---
        verification_efficiency = self._compute_verification_efficiency(state)

        # --- help_seeking_appropriateness ---
        help_seeking = self._compute_help_seeking(state, spec)

        # --- behavioral_signatures ---
        behavioral_signatures = self._compute_behavioral_signatures(
            state, object_score, calibration_score
        )

        # --- meta_score: weighted combination ---
        meta_score = self._compute_meta_score(
            calibration_score=calibration_score,
            revision_quality=revision_quality,
            verification_efficiency=verification_efficiency,
            help_seeking_appropriateness=help_seeking,
        )

        return {
            "outcome_score": round(object_score, 4),
            "process_score": round(meta_score, 4),
            "track_id": "metacognition",
            "object_score": round(object_score, 4),
            "meta_score": round(meta_score, 4),
            "calibration_score": round(calibration_score, 4),
            "revision_quality": round(revision_quality, 4),
            "verification_efficiency": round(verification_efficiency, 4),
            "help_seeking_appropriateness": round(help_seeking, 4),
            "behavioral_signatures": behavioral_signatures,
            "contamination_warning": False,
        }

    @staticmethod
    def _compute_object_score(final_answer: str, spec: Any) -> float:
        """
        object_score: answer vs. object_level_goal.

        Checks if the answer contains key phrases from the object_level_goal.
        Independent of metacognitive behavior.
        """
        goal = spec.answer_targets.get("object_level_goal", "")
        if not goal or not final_answer:
            return 0.0

        answer_lower = final_answer.lower()
        goal_lower = goal.lower()

        # Extract significant words from goal
        import re
        words = [w for w in re.findall(r"\b[a-z]{4,}\b", goal_lower)
                 if w not in {"that", "this", "with", "from", "into", "does",
                               "have", "been", "also", "only", "both", "more",
                               "than", "when", "then", "they", "their", "which",
                               "most", "next", "what", "should", "recommend"}]
        if not words:
            return 0.0

        matches = sum(1 for w in words if w in answer_lower)
        return min(1.0, matches / max(len(words) * 0.3, 1))

    @staticmethod
    def _compute_calibration_score(state: Any, object_score: float) -> float:
        """
        calibration_score = 1 - |confidence_at_submission - correctness|

        Uses the last confidence value from state.confidence_history.
        Returns 0.5 (neutral) when no confidence recorded.
        """
        if not state.confidence_history:
            return 0.5
        confidence = state.confidence_history[-1]
        return max(0.0, 1.0 - abs(confidence - object_score))

    @staticmethod
    def _compute_revision_quality(state: Any) -> float:
        """
        revision_quality = 1.0 if a contradiction event was followed by
        new-node exploration within 3 steps, else 0.0.
        """
        from vigil.environments.base import EventType

        history = state.action_history
        if not history:
            return 0.0

        # Find contradiction events
        contradiction_indices = [
            i for i, e in enumerate(history)
            if hasattr(e, "event_type") and e.event_type == EventType.CONTRADICTION
        ]
        if not contradiction_indices:
            return 0.0

        # Check if any contradiction was followed by new-node exploration within 3 steps
        visited_before = set()
        for i, event in enumerate(history):
            if hasattr(event, "event_type") and event.event_type == EventType.EXPLORE:
                if event.node_id:
                    visited_before.add(event.node_id)

            if i in contradiction_indices:
                # Look at next 3 steps for new-node exploration
                for j in range(i + 1, min(i + 4, len(history))):
                    ev = history[j]
                    if (hasattr(ev, "event_type")
                            and ev.event_type == EventType.EXPLORE
                            and ev.node_id
                            and ev.node_id not in visited_before):
                        return 1.0

        return 0.0

    @staticmethod
    def _compute_verification_efficiency(state: Any) -> float:
        """
        verification_efficiency = len(evidence_nodes) / max(verification_actions, 1)

        Verification actions = inspect actions (proxy for deliberate checking).
        """
        from vigil.environments.base import EventType

        history = state.action_history
        verification_actions = sum(
            1 for e in history
            if hasattr(e, "event_type") and e.event_type == EventType.INSPECT
        )
        evidence_count = len(state.evidence_nodes)
        return min(1.0, evidence_count / max(verification_actions, 1))

    @staticmethod
    def _compute_help_seeking(state: Any, spec: Any) -> float:
        """
        help_seeking_appropriateness: fraction of help requests made when
        budget_remaining was above a threshold (appropriate timing).

        Returns 0.5 (neutral) when no help requests made.
        """
        help_requests = getattr(state, "help_requests", [])
        if not help_requests:
            return 0.5

        budget_total = getattr(spec, "runtime_config", None)
        budget_total = budget_total.action_budget if budget_total else 20
        threshold = budget_total * 0.3  # appropriate if > 30% budget remaining

        appropriate = sum(
            1 for r in help_requests
            if r.get("budget_remaining", budget_total) > threshold
        )
        return appropriate / len(help_requests)

    @staticmethod
    def _compute_behavioral_signatures(
        state: Any,
        object_score: float,
        calibration_score: float,
    ) -> Dict[str, Any]:
        """Compute metacognitive behavioral signatures from trace."""
        from vigil.environments.base import EventType

        sigs: Dict[str, Any] = {}

        # Overconfidence: high confidence + wrong answer
        if state.confidence_history:
            conf = state.confidence_history[-1]
            if conf > 0.8 and object_score < 0.3:
                sigs["overconfidence"] = True
            elif conf < 0.3 and object_score > 0.7:
                sigs["underconfidence"] = True

        # Premature stopping: submitted before any inspect action
        history = state.action_history
        inspect_before_submit = any(
            e.event_type == EventType.INSPECT
            for e in history
            if hasattr(e, "event_type") and e.event_type != EventType.SUBMIT_ANSWER
        )
        if not inspect_before_submit and any(
            hasattr(e, "event_type") and e.event_type == EventType.SUBMIT_ANSWER
            for e in history
        ):
            sigs["premature_stopping"] = True

        # Endless checking: same node inspected > 3 times
        inspect_counts: Dict[str, int] = {}
        for e in history:
            if hasattr(e, "event_type") and e.event_type == EventType.INSPECT and e.node_id:
                inspect_counts[e.node_id] = inspect_counts.get(e.node_id, 0) + 1
        if any(c > 3 for c in inspect_counts.values()):
            sigs["endless_checking"] = True

        # Contradiction blindness: contradiction event with no new action within 5 steps
        contradiction_indices = [
            i for i, e in enumerate(history)
            if hasattr(e, "event_type") and e.event_type == EventType.CONTRADICTION
        ]
        if contradiction_indices:
            last_contradiction = contradiction_indices[-1]
            remaining = history[last_contradiction + 1:]
            new_actions = [
                e for e in remaining[:5]
                if hasattr(e, "event_type") and e.event_type not in (
                    EventType.GET_CONTEXT, EventType.CONTRADICTION
                )
            ]
            if not new_actions:
                sigs["contradiction_blindness"] = True

        return sigs

    @staticmethod
    def _compute_meta_score(
        calibration_score: float,
        revision_quality: float,
        verification_efficiency: float,
        help_seeking_appropriateness: float,
    ) -> float:
        """Weighted combination of metacognitive dimensions."""
        weights = {
            "calibration_score": 0.35,
            "revision_quality": 0.30,
            "verification_efficiency": 0.20,
            "help_seeking_appropriateness": 0.15,
        }
        return (
            calibration_score * weights["calibration_score"]
            + revision_quality * weights["revision_quality"]
            + verification_efficiency * weights["verification_efficiency"]
            + help_seeking_appropriateness * weights["help_seeking_appropriateness"]
        )


# ---------------------------------------------------------------------------
# AttentionScorer — Track 3 (attention) full implementation
# ---------------------------------------------------------------------------

class AttentionScorer(TrackScorer):
    """
    Track 3 (attention) scorer — Kaggle Track 3.

    Measures attentional behavior from the episode trace using authored
    attention_design metadata and edge attention_role fields.

    Dimensions:
      target_hit_rate       — fraction of critical_evidence_node_ids inspected
      distractor_chase_rate — fraction of actions on salient_trap/distractor nodes
      false_alarm_rate      — fraction of actions on false_alarm nodes
      reorientation_latency — mean steps from RELEVANCE_SHIFT to new-relevant action
      correctness           — answer vs. target_conclusion (string similarity)
      cue_coverage          — fraction of target nodes visited at least once
    """

    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        """Compute AttentionScorer ScoreCard."""
        inspected = list(getattr(state, "inspected_nodes", None) or state.visited_nodes)

        # Build attention_role map from spec edges
        attention_role_map = self._build_attention_role_map(spec)

        correctness = self._compute_correctness(final_answer, spec)
        target_hit_rate = self._compute_target_hit_rate(inspected, spec)
        distractor_chase_rate = self._compute_distractor_chase_rate(state, attention_role_map)
        false_alarm_rate = self._compute_false_alarm_rate(state, attention_role_map)
        reorientation_latency = self._compute_reorientation_latency(state, spec)
        cue_coverage = self._compute_cue_coverage(state, spec)
        behavioral_signatures = self._compute_behavioral_signatures(
            state, spec, attention_role_map, target_hit_rate, reorientation_latency
        )

        # process_score: weighted combination
        weights = spec.scoring_weights
        process_score = self._compute_process_score(
            correctness=correctness,
            target_hit_rate=target_hit_rate,
            distractor_chase_rate=distractor_chase_rate,
            reorientation_latency=reorientation_latency,
            cue_coverage=cue_coverage,
            weights=weights,
        )

        return {
            "outcome_score": round(correctness, 4),
            "process_score": round(process_score, 4),
            "track_id": "attention",
            "correctness": round(correctness, 4),
            "target_hit_rate": round(target_hit_rate, 4),
            "distractor_chase_rate": round(distractor_chase_rate, 4),
            "false_alarm_rate": round(false_alarm_rate, 4),
            "reorientation_latency": round(reorientation_latency, 4),
            "cue_coverage": round(cue_coverage, 4),
            "behavioral_signatures": behavioral_signatures,
            "contamination_warning": False,
        }

    @staticmethod
    def _build_attention_role_map(spec: Any) -> Dict[str, str]:
        """Build {node_id: attention_role} from edge metadata."""
        role_map: Dict[str, str] = {}
        for edge in spec.edges:
            role = edge.metadata.get("attention_role", "")
            if role:
                # The attention_role applies to the target node of the edge
                role_map[edge.to_id] = role
        return role_map

    @staticmethod
    def _compute_correctness(final_answer: str, spec: Any) -> float:
        """Correctness: answer vs. target_conclusion (string similarity)."""
        target = spec.answer_targets.get("target_conclusion", "")
        if not target or not final_answer:
            return 0.0

        import re
        answer_lower = final_answer.lower()
        target_lower = target.lower()

        # Extract significant words from target
        words = [w for w in re.findall(r"\b[a-z]{4,}\b", target_lower)
                 if w not in {"that", "this", "with", "from", "into", "does",
                               "have", "been", "also", "only", "both", "more",
                               "than", "when", "then", "they", "their", "which",
                               "most", "next", "what", "should", "prioritize",
                               "proximate", "driver"}]
        if not words:
            return 0.0

        matches = sum(1 for w in words if w in answer_lower)
        return min(1.0, matches / max(len(words) * 0.3, 1))

    @staticmethod
    def _compute_target_hit_rate(inspected: list, spec: Any) -> float:
        """target_hit_rate = |inspected ∩ evidence_targets| / |evidence_targets|"""
        targets = set(spec.evidence_targets)
        if not targets:
            return 1.0
        return len(set(inspected) & targets) / len(targets)

    @staticmethod
    def _compute_distractor_chase_rate(state: Any, attention_role_map: Dict[str, str]) -> float:
        """Fraction of inspect/explore actions on salient_trap or distractor nodes."""
        from vigil.environments.base import EventType
        history = state.action_history
        action_events = [
            e for e in history
            if hasattr(e, "event_type") and e.event_type in (EventType.EXPLORE, EventType.INSPECT)
        ]
        if not action_events:
            return 0.0
        distractor_roles = {"salient_trap", "distractor"}
        distractor_hits = sum(
            1 for e in action_events
            if e.node_id and attention_role_map.get(e.node_id, "") in distractor_roles
        )
        return distractor_hits / len(action_events)

    @staticmethod
    def _compute_false_alarm_rate(state: Any, attention_role_map: Dict[str, str]) -> float:
        """Fraction of inspect/explore actions on false_alarm nodes."""
        from vigil.environments.base import EventType
        history = state.action_history
        action_events = [
            e for e in history
            if hasattr(e, "event_type") and e.event_type in (EventType.EXPLORE, EventType.INSPECT)
        ]
        if not action_events:
            return 0.0
        false_alarm_hits = sum(
            1 for e in action_events
            if e.node_id and attention_role_map.get(e.node_id, "") == "false_alarm"
        )
        return false_alarm_hits / len(action_events)

    @staticmethod
    def _compute_reorientation_latency(state: Any, spec: Any) -> float:
        """
        Mean steps from RELEVANCE_SHIFT to first action on a newly-relevant node.
        Returns 0.0 when no relevance shifts occurred.
        """
        from vigil.environments.base import EventType
        history = state.action_history
        shift_indices = [
            i for i, e in enumerate(history)
            if hasattr(e, "event_type") and e.event_type == EventType.RELEVANCE_SHIFT
        ]
        if not shift_indices:
            return 0.0

        evidence_targets = set(spec.evidence_targets)
        latencies = []
        for shift_idx in shift_indices:
            for j in range(shift_idx + 1, len(history)):
                ev = history[j]
                if (hasattr(ev, "event_type")
                        and ev.event_type in (EventType.EXPLORE, EventType.INSPECT)
                        and ev.node_id in evidence_targets):
                    latencies.append(j - shift_idx)
                    break

        return sum(latencies) / len(latencies) if latencies else 0.0

    @staticmethod
    def _compute_cue_coverage(state: Any, spec: Any) -> float:
        """Fraction of evidence_targets visited at least once."""
        targets = set(spec.evidence_targets)
        if not targets:
            return 1.0
        visited = set(state.visited_nodes)
        return len(visited & targets) / len(targets)

    @staticmethod
    def _compute_behavioral_signatures(
        state: Any,
        spec: Any,
        attention_role_map: Dict[str, str],
        target_hit_rate: float,
        reorientation_latency: float,
    ) -> Dict[str, Any]:
        """Compute attention behavioral signatures from trace."""
        from vigil.environments.base import EventType
        sigs: Dict[str, Any] = {}

        history = state.action_history
        action_events = [
            e for e in history
            if hasattr(e, "event_type") and e.event_type in (EventType.EXPLORE, EventType.INSPECT)
        ]

        # Distractor chasing: consecutive pairs both on distractor nodes
        distractor_roles = {"salient_trap", "distractor"}
        if len(action_events) >= 2:
            consecutive_distractor = sum(
                1 for i in range(len(action_events) - 1)
                if (action_events[i].node_id
                    and action_events[i + 1].node_id
                    and attention_role_map.get(action_events[i].node_id, "") in distractor_roles
                    and attention_role_map.get(action_events[i + 1].node_id, "") in distractor_roles)
            )
            if consecutive_distractor > 0:
                sigs["distractor_chasing"] = True

        # Missed rare alert: rare_critical node never inspected before submit
        rare_critical_nodes = {
            n.node_id for n in spec.nodes
            if n.node_type in ("rare_critical",)
        }
        if rare_critical_nodes:
            inspected = set(getattr(state, "inspected_nodes", state.visited_nodes))
            if not (inspected & rare_critical_nodes):
                sigs["missed_rare_alert"] = True

        # Delayed reorientation
        if reorientation_latency > 5:
            sigs["delayed_reorientation"] = True

        # Tunnel vision: >60% of actions on a single node cluster
        if action_events:
            node_counts: Dict[str, int] = {}
            for e in action_events:
                if e.node_id:
                    node_counts[e.node_id] = node_counts.get(e.node_id, 0) + 1
            max_count = max(node_counts.values()) if node_counts else 0
            if max_count / len(action_events) > 0.6:
                sigs["tunnel_vision"] = True

        return sigs

    @staticmethod
    def _compute_process_score(
        correctness: float,
        target_hit_rate: float,
        distractor_chase_rate: float,
        reorientation_latency: float,
        cue_coverage: float,
        weights: Dict[str, float],
    ) -> float:
        """Weighted combination of attention dimensions."""
        # distractor_chase_rate is a penalty (lower is better)
        distractor_score = max(0.0, 1.0 - distractor_chase_rate)
        # reorientation_latency: 0 = perfect, higher = worse; normalise to [0,1]
        reorientation_score = max(0.0, 1.0 - min(reorientation_latency / 10.0, 1.0))

        dim_values = {
            "correctness": correctness,
            "target_hit_rate": target_hit_rate,
            "distractor_chase_rate": distractor_score,
            "reorientation_latency": reorientation_score,
            "cue_coverage": cue_coverage,
        }
        total_w = sum(weights.get(k, 0.0) for k in dim_values)
        if total_w <= 0:
            return sum(dim_values.values()) / len(dim_values)
        return sum(dim_values[k] * weights.get(k, 0.0) for k in dim_values) / total_w


# ---------------------------------------------------------------------------
# ExecutiveScorer — Track 4 (executive_functions) full implementation
# ---------------------------------------------------------------------------

class ExecutiveScorer(TrackScorer):
    """
    Track 4 (executive_functions) scorer — Kaggle Track 4.

    Measures executive control quality from the episode trace using authored
    executive_design_notes metadata.

    Dimensions:
      inhibition_failures          — actions targeting tempting_wrong_path nodes
      pivot_quality                — 1.0 if required_pivot sequence in trace
      process_scoring_focus_alignment — trace matches authored process_scoring_focus
      correctness                  — answer vs. required_pivot
    """

    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        """Compute ExecutiveScorer ScoreCard."""
        ed = spec.track_metadata.get("executive_design_notes", {})

        correctness = self._compute_correctness(final_answer, spec)
        inhibition_failures = self._compute_inhibition_failures(state, ed)
        pivot_quality = self._compute_pivot_quality(state, ed)
        process_alignment = self._compute_process_alignment(state, ed)
        behavioral_signatures = self._compute_behavioral_signatures(
            state, ed, inhibition_failures, pivot_quality
        )

        # process_score: weighted combination
        weights = spec.scoring_weights
        process_score = self._compute_process_score(
            correctness=correctness,
            inhibition_failures=inhibition_failures,
            pivot_quality=pivot_quality,
            process_alignment=process_alignment,
            weights=weights,
        )

        return {
            "outcome_score": round(correctness, 4),
            "process_score": round(process_score, 4),
            "track_id": "executive_functions",
            "correctness": round(correctness, 4),
            "inhibition_failures": inhibition_failures,
            "pivot_quality": round(pivot_quality, 4),
            "process_scoring_focus_alignment": round(process_alignment, 4),
            "behavioral_signatures": behavioral_signatures,
            "contamination_warning": False,
        }

    @staticmethod
    def _compute_correctness(final_answer: str, spec: Any) -> float:
        """Correctness: answer vs. required_pivot."""
        pivot = spec.answer_targets.get("required_pivot", "")
        if not pivot or not final_answer:
            return 0.0

        import re
        answer_lower = final_answer.lower()
        pivot_lower = pivot.lower()

        words = [w for w in re.findall(r"\b[a-z]{4,}\b", pivot_lower)
                 if w not in {"that", "this", "with", "from", "into", "does",
                               "have", "been", "also", "only", "both", "more",
                               "than", "when", "then", "they", "their", "which",
                               "after", "switch", "timing", "succession"}]
        if not words:
            return 0.0

        matches = sum(1 for w in words if w in answer_lower)
        return min(1.0, matches / max(len(words) * 0.3, 1))

    @staticmethod
    def _compute_inhibition_failures(state: Any, ed: Dict[str, Any]) -> int:
        """
        Count of actions targeting nodes described in tempting_wrong_path.

        Uses keyword matching against node labels/summaries in the trace.
        """
        tempting = str(ed.get("tempting_wrong_path", "")).lower()
        if not tempting:
            return 0

        from vigil.environments.base import EventType
        history = state.action_history
        failures = 0
        for event in history:
            if (hasattr(event, "event_type")
                    and event.event_type in (EventType.EXPLORE, EventType.INSPECT)
                    and event.observation):
                obs_lower = event.observation.lower()
                # Check if the observation content matches tempting path keywords
                tempting_words = [w for w in tempting.split() if len(w) > 4]
                if any(w in obs_lower for w in tempting_words[:3]):
                    failures += 1
        return failures

    @staticmethod
    def _compute_pivot_quality(state: Any, ed: Dict[str, Any]) -> float:
        """
        pivot_quality = 1.0 if the model's trace includes the required_pivot.

        Checks if any observation in the trace contains key phrases from
        the required_pivot description.
        """
        pivot = str(ed.get("required_pivot", "")).lower()
        if not pivot:
            return 0.0

        import re
        pivot_words = [w for w in re.findall(r"\b[a-z]{5,}\b", pivot)
                       if w not in {"after", "switch", "timing", "succession",
                                    "oxygen", "instabi", "transition"}]
        if not pivot_words:
            return 0.0

        history = state.action_history
        for event in history:
            if hasattr(event, "observation") and event.observation:
                obs_lower = event.observation.lower()
                matches = sum(1 for w in pivot_words if w in obs_lower)
                if matches >= 2:
                    return 1.0

        # Also check if the answer itself mentions the pivot
        return 0.0

    @staticmethod
    def _compute_process_alignment(state: Any, ed: Dict[str, Any]) -> float:
        """
        process_scoring_focus_alignment: fraction of authored focus criteria
        that appear to be satisfied by the trace.

        Returns 0.5 (neutral) when no focus criteria defined.
        """
        focus = ed.get("process_scoring_focus", [])
        if not focus:
            return 0.5

        # Simple heuristic: check if any action history observation mentions
        # keywords from the focus criteria
        history = state.action_history
        all_obs = " ".join(
            e.observation.lower() for e in history
            if hasattr(e, "observation") and e.observation
        )

        satisfied = 0
        for criterion in focus:
            criterion_lower = str(criterion).lower()
            # Extract key words from criterion
            import re
            words = re.findall(r"\b[a-z]{5,}\b", criterion_lower)
            if any(w in all_obs for w in words[:2]):
                satisfied += 1

        return satisfied / len(focus) if focus else 0.5

    @staticmethod
    def _compute_behavioral_signatures(
        state: Any,
        ed: Dict[str, Any],
        inhibition_failures: int,
        pivot_quality: float,
    ) -> Dict[str, Any]:
        """Compute executive behavioral signatures from trace."""
        from vigil.environments.base import EventType
        sigs: Dict[str, Any] = {}

        history = state.action_history

        # Impulsive execution: tempting path taken before any goal-relevant action
        if inhibition_failures > 0:
            # Check if first non-error action was on tempting path
            first_actions = [
                e for e in history[:3]
                if hasattr(e, "event_type") and e.event_type in (EventType.EXPLORE, EventType.INSPECT)
            ]
            if first_actions and inhibition_failures >= len(first_actions):
                sigs["impulsive_execution"] = True

        # Goal neglect: pivot_quality = 0 after many actions
        if len(history) > 8 and pivot_quality == 0.0:
            sigs["goal_neglect"] = True

        # Perseveration: same node visited > 3 times
        node_counts: Dict[str, int] = {}
        for e in history:
            if (hasattr(e, "event_type")
                    and e.event_type == EventType.EXPLORE
                    and e.node_id):
                node_counts[e.node_id] = node_counts.get(e.node_id, 0) + 1
        if any(c > 3 for c in node_counts.values()):
            sigs["perseveration"] = True

        # Delayed switching: REPLAN_TRIGGERED event with > 5 steps before new action
        replan_indices = [
            i for i, e in enumerate(history)
            if hasattr(e, "event_type") and e.event_type == EventType.REPLAN_TRIGGERED
        ]
        if replan_indices:
            last_replan = replan_indices[-1]
            post_replan = history[last_replan + 1:]
            new_actions = [
                e for e in post_replan[:6]
                if hasattr(e, "event_type") and e.event_type in (EventType.EXPLORE, EventType.INSPECT)
            ]
            if len(new_actions) < 1:
                sigs["delayed_switching"] = True

        return sigs

    @staticmethod
    def _compute_process_score(
        correctness: float,
        inhibition_failures: int,
        pivot_quality: float,
        process_alignment: float,
        weights: Dict[str, float],
    ) -> float:
        """Weighted combination of executive dimensions."""
        # inhibition_failures is a count — convert to score (0 failures = 1.0)
        inhibition_score = max(0.0, 1.0 - inhibition_failures * 0.2)

        dim_values = {
            "correctness": correctness,
            "inhibition_failures": inhibition_score,
            "pivot_quality": pivot_quality,
            "process_scoring_focus_alignment": process_alignment,
        }
        total_w = sum(weights.get(k, 0.0) for k in dim_values)
        if total_w <= 0:
            return sum(dim_values.values()) / len(dim_values)
        return sum(dim_values[k] * weights.get(k, 0.0) for k in dim_values) / total_w



# ---------------------------------------------------------------------------
# SocialScorer — Track 5 (social_cognition) full implementation
# ---------------------------------------------------------------------------

class SocialScorer(TrackScorer):
    """
    Track 5 (social_cognition) scorer — Kaggle Track 5.

    Works with the real authored schema from
    vigil_track5_social_scenarios_from_skeletons_v1.json.

    The real scenarios express social cognition through causal graph structure:
    agent_groups, evidence nodes, outcome nodes, and causal edges. The scorer
    measures how well the model navigates this social causal graph.

    Dimensions:
      correctness                     — answer vs. hidden_mechanism (causal explanation)
      evidence_coverage               — fraction of evidence nodes inspected
      causal_chain_coverage           — fraction of causal chain steps touched
      red_herring_avoidance           — fraction of actions NOT on red-herring nodes
      disconfirmation_use             — whether disconfirmation_moment was reached

    Behavioral signatures:
      premature_conclusion, red_herring_fixation, disconfirmation_blindness,
      shallow_exploration, social_collapse_after_contradiction

    Requirements: 13
    """

    def score(
        self,
        state: Any,
        final_answer: str,
        justification: str,
        spec: Any,
    ) -> Dict[str, Any]:
        """Compute SocialScorer ScoreCard."""
        correctness = self._compute_correctness(final_answer, spec)
        evidence_coverage = self._compute_evidence_coverage(state, spec)
        causal_chain_coverage = self._compute_causal_chain_coverage(state, spec)
        red_herring_avoidance = self._compute_red_herring_avoidance(state, spec)
        disconfirmation_use = self._compute_disconfirmation_use(state, spec)
        behavioral_signatures = self._compute_behavioral_signatures(
            state, spec, correctness, red_herring_avoidance
        )

        weights = spec.scoring_weights
        process_score = self._compute_process_score(
            correctness=correctness,
            evidence_coverage=evidence_coverage,
            causal_chain_coverage=causal_chain_coverage,
            red_herring_avoidance=red_herring_avoidance,
            disconfirmation_use=disconfirmation_use,
            weights=weights,
        )

        return {
            "outcome_score": round(correctness, 4),
            "process_score": round(process_score, 4),
            "track_id": "social_cognition",
            "correctness": round(correctness, 4),
            "evidence_coverage": round(evidence_coverage, 4),
            "causal_chain_coverage": round(causal_chain_coverage, 4),
            "red_herring_avoidance": round(red_herring_avoidance, 4),
            "disconfirmation_use": round(disconfirmation_use, 4),
            "behavioral_signatures": behavioral_signatures,
            "contamination_warning": False,
        }

    @staticmethod
    def _compute_correctness(final_answer: str, spec: Any) -> float:
        """
        Correctness: answer vs. hidden_mechanism (string similarity).

        Checks if the answer contains key phrases from the authored
        hidden_mechanism explanation.
        """
        import re
        mechanism = spec.answer_targets.get("hidden_mechanism", "")
        if not mechanism or not final_answer:
            return 0.0

        answer_lower = final_answer.lower()
        mechanism_lower = mechanism.lower()

        # Extract significant words from the mechanism
        words = [w for w in re.findall(r"\b[a-z]{5,}\b", mechanism_lower)
                 if w not in {"which", "their", "these", "those", "about",
                               "after", "before", "while", "where", "there",
                               "being", "having", "would", "could", "should",
                               "rather", "because", "through", "between"}]
        if not words:
            return 0.0

        matches = sum(1 for w in words if w in answer_lower)
        return min(1.0, matches / max(len(words) * 0.25, 1))

    @staticmethod
    def _compute_evidence_coverage(state: Any, spec: Any) -> float:
        """
        evidence_coverage: fraction of evidence-kind nodes inspected.

        Evidence nodes are those with node_type == "evidence" in the spec.
        """
        evidence_nodes = [n.node_id for n in spec.nodes if n.node_type == "evidence"]
        if not evidence_nodes:
            return 1.0
        inspected = set(getattr(state, "inspected_nodes", state.visited_nodes))
        return len(set(evidence_nodes) & inspected) / len(evidence_nodes)

    @staticmethod
    def _compute_causal_chain_coverage(state: Any, spec: Any) -> float:
        """
        causal_chain_coverage: fraction of causal chain steps whose
        corresponding nodes were visited.

        The causal_chain is a list of text descriptions. We check if any
        visited node's label appears in each chain step.
        """
        causal_chain = spec.track_metadata.get("causal_chain", [])
        if not causal_chain:
            return 0.5

        visited_labels = {
            n.label.lower() for n in spec.nodes
            if n.node_id in set(state.visited_nodes)
        }

        covered = 0
        for step in causal_chain:
            step_lower = step.lower()
            # Check if any visited node label appears in this causal step
            if any(label in step_lower or step_lower in label
                   for label in visited_labels if len(label) > 4):
                covered += 1

        return covered / len(causal_chain)

    @staticmethod
    def _compute_red_herring_avoidance(state: Any, spec: Any) -> float:
        """
        red_herring_avoidance: fraction of actions NOT on red-herring nodes.

        Red herrings are identified by matching node labels against the
        authored red_herrings list using word-level overlap.
        """
        from vigil.environments.base import EventType
        import re

        red_herrings = spec.track_metadata.get("red_herrings", [])
        if not red_herrings:
            return 1.0

        # Build set of node_ids that match red herring descriptions via word overlap
        rh_words: set = set()
        for rh in red_herrings:
            rh_words |= set(re.findall(r"\b[a-z]{4,}\b", rh.lower()))

        rh_node_ids: set = set()
        for node in spec.nodes:
            node_words = set(re.findall(r"\b[a-z]{4,}\b", node.label.lower()))
            if node_words & rh_words:
                rh_node_ids.add(node.node_id)

        history = state.action_history
        action_events = [
            e for e in history
            if hasattr(e, "event_type") and e.event_type in (
                EventType.EXPLORE, EventType.INSPECT
            )
        ]
        if not action_events:
            return 1.0

        rh_hits = sum(
            1 for e in action_events
            if e.node_id and e.node_id in rh_node_ids
        )
        return 1.0 - (rh_hits / len(action_events))

    @staticmethod
    def _compute_disconfirmation_use(state: Any, spec: Any) -> float:
        """
        disconfirmation_use: 1.0 if the model visited a node whose label
        shares words with the disconfirmation_moment text, else 0.0.

        Returns 0.5 (neutral) when no disconfirmation moment is authored
        or no matching node exists.
        """
        import re
        disconf = spec.track_metadata.get("disconfirmation_moment", "")
        if not disconf:
            return 0.5

        disconf_words = set(re.findall(r"\b[a-z]{4,}\b", disconf.lower()))
        if not disconf_words:
            return 0.5

        # Find nodes whose labels share words with the disconfirmation moment
        disconf_nodes = set()
        for n in spec.nodes:
            node_words = set(re.findall(r"\b[a-z]{4,}\b", n.label.lower()))
            if node_words & disconf_words:
                disconf_nodes.add(n.node_id)

        if not disconf_nodes:
            return 0.5

        visited = set(state.visited_nodes)
        return 1.0 if disconf_nodes & visited else 0.0

    @staticmethod
    def _compute_behavioral_signatures(
        state: Any,
        spec: Any,
        correctness: float,
        red_herring_avoidance: float,
    ) -> Dict[str, Any]:
        """Compute social behavioral signatures from trace."""
        from vigil.environments.base import EventType

        sigs: Dict[str, Any] = {}
        history = state.action_history

        # Premature conclusion: submitted with < 30% of nodes visited
        total_nodes = max(len(spec.nodes), 1)
        visited_count = len(set(state.visited_nodes))
        if visited_count / total_nodes < 0.3 and any(
            hasattr(e, "event_type") and e.event_type == EventType.SUBMIT_ANSWER
            for e in history
        ):
            sigs["premature_conclusion"] = True

        # Red herring fixation: > 40% of actions on red-herring nodes
        if red_herring_avoidance < 0.6:
            sigs["red_herring_fixation"] = True
        # Disconfirmation blindness: never visited disconfirmation node
        import re as _re
        disconf = spec.track_metadata.get("disconfirmation_moment", "")
        if disconf:
            disconf_words = set(_re.findall(r"\b[a-z]{4,}\b", disconf.lower()))
            disconf_nodes = {
                n.node_id for n in spec.nodes
                if set(_re.findall(r"\b[a-z]{4,}\b", n.label.lower())) & disconf_words
            }
            if disconf_nodes and not (disconf_nodes & set(state.visited_nodes)):
                sigs["disconfirmation_blindness"] = True

        # Shallow exploration: submitted after < 3 explore actions
        explore_count = sum(
            1 for e in history
            if hasattr(e, "event_type") and e.event_type == EventType.EXPLORE
        )
        if explore_count < 3 and any(
            hasattr(e, "event_type") and e.event_type == EventType.SUBMIT_ANSWER
            for e in history
        ):
            sigs["shallow_exploration"] = True

        # Social collapse after contradiction
        contradiction_indices = [
            i for i, e in enumerate(history)
            if hasattr(e, "event_type") and e.event_type == EventType.CONTRADICTION
        ]
        if contradiction_indices:
            last_contradiction = contradiction_indices[-1]
            post_contradiction = history[last_contradiction + 1:]
            social_actions = [
                e for e in post_contradiction
                if hasattr(e, "event_type") and e.event_type in (
                    EventType.MESSAGE_SENT, EventType.COMMITMENT_MADE,
                    EventType.EXPLORE, EventType.INSPECT,
                )
            ]
            if not social_actions and len(post_contradiction) > 3:
                sigs["social_collapse_after_contradiction"] = True

        return sigs

    @staticmethod
    def _compute_process_score(
        correctness: float,
        evidence_coverage: float,
        causal_chain_coverage: float,
        red_herring_avoidance: float,
        disconfirmation_use: float,
        weights: Dict[str, float],
    ) -> float:
        """Weighted combination of social dimensions."""
        dim_values = {
            "correctness": correctness,
            "partner_model_accuracy": evidence_coverage,       # maps to evidence_coverage
            "social_repair_quality": causal_chain_coverage,    # maps to causal_chain_coverage
            "trust_calibration": red_herring_avoidance,        # maps to red_herring_avoidance
            "communication_appropriateness": disconfirmation_use,
            "information_asymmetry_exploitation": evidence_coverage,
        }
        total_w = sum(weights.get(k, 0.0) for k in dim_values)
        if total_w <= 0:
            return sum(dim_values.values()) / len(dim_values)
        return sum(dim_values[k] * weights.get(k, 0.0) for k in dim_values) / total_w
