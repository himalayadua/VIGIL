"""
Vigil Intelligence Score (VIS) — 7-dimensional behavioral scoring.

VIS = 0.3 × Outcome_Score + 0.7 × Process_Score

Process dimensions:
  EE  — Exploration Efficiency
  LR  — Learning Rate
  AD  — Adaptivity (inverse perseveration)
  RE  — Recovery (dead-end recovery speed)
  SQ  — Stopping Quality
  MC  — Metacognition (two-stage: citation check + optional judge)
  CR  — Contamination Risk (flag, not a weight)

The full score dict is stored in run artifacts.
The @kbench.task function returns only vis (float) to the leaderboard.

Requirements: 10.1–10.11
"""

import re
from math import sqrt
from typing import Any, Dict, List, Optional

from vigil.environments.base import EnvironmentState, EventType


class VISScorer:
    """
    Computes the 7-dimensional Vigil Intelligence Score for one episode.

    All dimension functions are pure — they take state and return a float.
    No side effects, no external calls except compute_metacognition (optional judge).
    """

    def score_episode(
        self,
        state: EnvironmentState,
        final_answer: str,
        justification: str,
        scenario_config: Dict[str, Any],
        outcome_score: Optional[float] = None,
        judge_llm: Any = None,
        human_baseline: Optional[Dict[str, Any]] = None,
        scorecard: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Compute the full VIS score dict for one episode.

        Two paths:
          1. scorecard=None (backward compat): compute all 7 base dimensions
             from state, using outcome_score as the correctness signal.
          2. scorecard provided: use scorecard["outcome_score"] and
             scorecard["process_score"] directly; merge scorecard dimension
             scores into result. Still always runs compute_contamination_risk().

        Args:
            state: Final EnvironmentState after episode ends
            final_answer: Model's submitted answer string
            justification: Model's submitted justification string
            scenario_config: Scenario JSON config (for optimal_steps, weights)
            outcome_score: Pre-computed correctness score (0.0–1.0).
                           If None and no scorecard, defaults to 0.0.
                           Ignored when scorecard is provided.
            judge_llm: Optional judge LLM for MC stage 2. If None, MC uses
                       citation ratio only (deterministic).
            human_baseline: Optional dict with 'mean' and 'std' for percentile.
            scorecard: Optional pre-computed ScoreCard from a TrackScorer.
                       When provided, outcome_score and process_score are taken
                       from the scorecard. All scorecard dimension scores are
                       merged into the returned result.

        Returns:
            Dict with keys: vis, outcome_score, process_score, track_id,
            contamination_risk, contamination_warning, and either the 7 base
            VIS dimensions (no scorecard) or the scorecard dimensions (with
            scorecard), plus optionally human_percentile.
        """
        # --- Contamination risk: always computed from state trace ---
        cr = self.compute_contamination_risk(state)

        if scorecard is not None:
            return self._score_with_scorecard(
                state=state,
                justification=justification,
                scenario_config=scenario_config,
                scorecard=scorecard,
                judge_llm=judge_llm,
                human_baseline=human_baseline,
                cr=cr,
            )

        # --- Backward-compat path: compute all 7 base dimensions ---
        return self._score_base_dimensions(
            state=state,
            final_answer=final_answer,
            justification=justification,
            scenario_config=scenario_config,
            outcome_score=outcome_score,
            judge_llm=judge_llm,
            human_baseline=human_baseline,
            cr=cr,
        )

    def _score_with_scorecard(
        self,
        state: EnvironmentState,
        justification: str,
        scenario_config: Dict[str, Any],
        scorecard: Dict[str, Any],
        judge_llm: Any,
        human_baseline: Optional[Dict[str, Any]],
        cr: float,
    ) -> Dict[str, Any]:
        """
        Build VISResult from a pre-computed TrackScorer ScoreCard.

        Uses scorecard["outcome_score"] and scorecard["process_score"] directly.
        Merges all scorecard dimension scores into the result.
        Always applies contamination_risk override if cr > 0.8.
        Runs two-stage MC scoring if judge_llm is provided.
        """
        outcome_score = float(scorecard.get("outcome_score", 0.0))
        process_score = float(scorecard.get("process_score", 0.0))

        # VIS = 0.3 × outcome + 0.7 × process (invariant across all tracks)
        vis = 0.3 * outcome_score + 0.7 * process_score
        vis = max(0.0, min(1.0, vis))

        # Contamination warning: scorecard value OR cr > 0.7 override
        contamination_warning = scorecard.get("contamination_warning", False)
        if cr > 0.7:
            contamination_warning = True

        # Contamination gate: cap VIS at 0.45 when contamination is detected.
        # This ensures a legitimate partial-score model always beats a model
        # that skipped exploration and submitted a memorised answer.
        if contamination_warning:
            vis = min(vis, 0.45)

        # track_id from scorecard, fallback to scenario_config
        track_id = scorecard.get(
            "track_id",
            scenario_config.get("cognitive_track", "unknown"),
        )

        # Two-stage MC scoring when judge_llm provided
        mc_score: Optional[float] = None
        if judge_llm is not None:
            citation_ratio = self._compute_citation_ratio(state, justification)
            judge_score = self._compute_judge_score(state, justification, judge_llm)
            mc_score = (citation_ratio + judge_score) / 2.0

        # Build result: start with all scorecard dimensions, then add VIS fields
        result: Dict[str, Any] = {
            k: v for k, v in scorecard.items()
            if k not in ("vis",)  # never let scorecard inject a vis key
        }
        result.update({
            "vis": round(vis, 4),
            "outcome_score": round(outcome_score, 4),
            "process_score": round(process_score, 4),
            "contamination_risk": round(cr, 4),
            "contamination_warning": contamination_warning,
            "track_id": track_id,
        })
        if mc_score is not None:
            result["metacognition"] = round(mc_score, 4)

        # Human percentile if baseline provided
        if human_baseline and "mean" in human_baseline and "std" in human_baseline:
            result["human_percentile"] = self._compute_percentile(
                vis, human_baseline["mean"], human_baseline["std"]
            )

        return result

    def _score_base_dimensions(
        self,
        state: EnvironmentState,
        final_answer: str,
        justification: str,
        scenario_config: Dict[str, Any],
        outcome_score: Optional[float],
        judge_llm: Any,
        human_baseline: Optional[Dict[str, Any]],
        cr: float,
    ) -> Dict[str, Any]:
        """
        Original 7-dimension scoring path (backward compat, no scorecard).
        Identical to the pre-refactor implementation.
        """
        if outcome_score is None:
            outcome_score = 0.0

        optimal_steps = scenario_config.get("optimal_steps", 6)
        process_weights = scenario_config.get("process_weights", {
            "exploration_efficiency": 0.20,
            "learning_rate":          0.15,
            "adaptivity":             0.20,
            "recovery":               0.15,
            "stopping_quality":       0.15,
            "metacognition":          0.15,
        })

        # Compute all 7 dimensions
        ee  = self.compute_exploration_efficiency(state)
        lr  = self.compute_learning_rate(state, scenario_config)
        ad  = self.compute_adaptivity(state)
        re_ = self.compute_recovery(state)
        sq  = self.compute_stopping_quality(state, optimal_steps)
        mc  = self.compute_metacognition(state, justification, judge_llm)
        # cr already computed by caller

        # Process score — weighted combination of EE, LR, AD, RE, SQ, MC
        process_dims = {
            "exploration_efficiency": ee,
            "learning_rate":          lr,
            "adaptivity":             ad,
            "recovery":               re_,
            "stopping_quality":       sq,
            "metacognition":          mc,
        }
        total_w = sum(process_weights.get(k, 0.0) for k in process_dims)
        if total_w > 0:
            process_score = sum(
                process_dims[k] * process_weights.get(k, 0.0)
                for k in process_dims
            ) / total_w
        else:
            process_score = sum(process_dims.values()) / len(process_dims)

        # VIS = 0.3 × outcome + 0.7 × process
        vis = 0.3 * outcome_score + 0.7 * process_score
        vis = max(0.0, min(1.0, vis))

        contamination_warning = cr > 0.7

        # Contamination gate: cap VIS at 0.45 when contamination is detected.
        if contamination_warning:
            vis = min(vis, 0.45)

        result: Dict[str, Any] = {
            "vis": round(vis, 4),
            "outcome_score": round(outcome_score, 4),
            "process_score": round(process_score, 4),
            "exploration_efficiency": round(ee, 4),
            "learning_rate": round(lr, 4),
            "adaptivity": round(ad, 4),
            "recovery": round(re_, 4),
            "stopping_quality": round(sq, 4),
            "metacognition": round(mc, 4),
            "contamination_risk": round(cr, 4),
            "contamination_warning": contamination_warning,
            "track_id": scenario_config.get("cognitive_track", "unknown"),
        }

        # Human percentile if baseline provided
        if human_baseline and "mean" in human_baseline and "std" in human_baseline:
            result["human_percentile"] = self._compute_percentile(
                vis, human_baseline["mean"], human_baseline["std"]
            )

        return result

    # ------------------------------------------------------------------
    # Dimension 1: Exploration Efficiency (EE)
    # ------------------------------------------------------------------

    def compute_exploration_efficiency(self, state: EnvironmentState) -> float:
        """
        EE = len(evidence_nodes) / len(visited_nodes)

        High EE: model targeted information-bearing nodes.
        Low EE: model wandered without collecting evidence.

        Returns 0.0 when no nodes visited.
        """
        if not state.visited_nodes:
            return 0.0
        return min(1.0, len(state.evidence_nodes) / len(state.visited_nodes))

    # ------------------------------------------------------------------
    # Dimension 2: Learning Rate (LR)
    # ------------------------------------------------------------------

    def compute_learning_rate(
        self, state: EnvironmentState, scenario_config: Dict[str, Any]
    ) -> float:
        """
        LR = improvement slope across trials within the session.

        Approximated from the ratio of evidence collected in the first half
        vs second half of the episode. A genuine learner collects more
        evidence per action in the second half (improving efficiency).

        Returns 0.5 (neutral) when insufficient data.
        """
        history = state.action_history
        if len(history) < 4:
            return 0.5

        mid = len(history) // 2
        first_half = history[:mid]
        second_half = history[mid:]

        # Count evidence-adding events in each half
        def evidence_rate(events: list) -> float:
            if not events:
                return 0.0
            evidence_count = sum(
                len(e.state_delta.get("evidence_added", []))
                for e in events
            )
            return evidence_count / len(events)

        first_rate = evidence_rate(first_half)
        second_rate = evidence_rate(second_half)

        # Improvement: second half better than first
        if first_rate == 0 and second_rate == 0:
            return 0.5
        if first_rate == 0:
            return 0.8  # Any improvement from zero is good
        improvement = (second_rate - first_rate) / max(first_rate, 0.001)
        # Map improvement to [0, 1]: 0 = no change, 1 = doubled efficiency
        lr = 0.5 + min(0.5, max(-0.5, improvement * 0.5))
        return round(lr, 4)

    # ------------------------------------------------------------------
    # Dimension 3: Adaptivity (AD)
    # ------------------------------------------------------------------

    def compute_adaptivity(self, state: EnvironmentState) -> float:
        """
        AD = 1 - perseveration_rate

        Perseveration: fraction of actions that repeat a strategy already
        contradicted by evidence (i.e., exploring the same node again after
        it yielded no evidence, or repeated ERROR events).

        Returns 0.5 when no actions taken.
        """
        history = state.action_history
        if not history:
            return 0.5

        # Count repeated ERROR events (model keeps trying invalid actions)
        error_events = [e for e in history if e.event_type == EventType.ERROR]
        # Count repeated explore of already-visited nodes
        visited_set: set = set()
        revisit_count = 0
        for event in history:
            if event.event_type == EventType.EXPLORE and event.node_id:
                if event.node_id in visited_set:
                    revisit_count += 1
                visited_set.add(event.node_id)

        perseverative = len(error_events) + revisit_count
        perseveration_rate = perseverative / len(history)
        return max(0.0, 1.0 - perseveration_rate)

    # ------------------------------------------------------------------
    # Dimension 4: Recovery (RE)
    # ------------------------------------------------------------------

    def compute_recovery(self, state: EnvironmentState) -> float:
        """
        RE = 1 / mean_steps_to_productive_node_after_dead_end

        Dead end: an EXPLORE event that added no evidence and no new neighbors.
        Productive: the next INSPECT event that adds to evidence_nodes.

        Returns 0.5 when no dead ends encountered.
        """
        history = state.action_history
        if not history:
            return 0.5

        # Find dead-end events: EXPLORE that added nothing to evidence
        dead_end_indices = []
        for i, event in enumerate(history):
            if event.event_type == EventType.EXPLORE:
                evidence_added = event.state_delta.get("evidence_added", [])
                if not evidence_added:
                    dead_end_indices.append(i)

        if not dead_end_indices:
            return 0.5  # No dead ends — neutral

        # For each dead end, count steps until next productive event
        steps_to_recovery = []
        for dead_idx in dead_end_indices:
            for j in range(dead_idx + 1, len(history)):
                ev = history[j]
                if ev.state_delta.get("evidence_added"):
                    steps_to_recovery.append(j - dead_idx)
                    break

        if not steps_to_recovery:
            return 0.2  # Dead ends with no recovery at all

        mean_steps = sum(steps_to_recovery) / len(steps_to_recovery)
        # RE = 1 / mean_steps, capped at 1.0
        return min(1.0, 1.0 / max(mean_steps, 1.0))

    # ------------------------------------------------------------------
    # Dimension 5: Stopping Quality (SQ)
    # ------------------------------------------------------------------

    def compute_stopping_quality(
        self, state: EnvironmentState, optimal_steps: int
    ) -> float:
        """
        SQ = 1 - |actual_steps - optimal_steps| / optimal_steps

        Measures whether the model stopped at the right time.
        Stopping too early or too late both reduce SQ.

        Returns 0.0 when optimal_steps is 0.
        """
        if optimal_steps <= 0:
            return 0.0
        actual = len(state.action_history)
        sq = 1.0 - abs(actual - optimal_steps) / optimal_steps
        return max(0.0, min(1.0, sq))

    # ------------------------------------------------------------------
    # Dimension 6: Metacognition (MC) — two-stage
    # ------------------------------------------------------------------

    def compute_metacognition(
        self,
        state: EnvironmentState,
        justification: str,
        judge_llm: Any = None,
    ) -> float:
        """
        MC — two-stage scoring:

        Stage 1 (deterministic): citation coverage ratio.
          Fraction of node IDs mentioned in justification that actually
          appear in state.action_history. Rewards grounded explanations.

        Stage 2 (optional, non-deterministic): judge LLM qualitative score.
          Uses assess_response_with_judge from Kaggle SDK.
          Only runs when judge_llm is provided.

        Returns citation ratio when judge_llm is None.
        Returns average of citation ratio and judge score otherwise.
        """
        citation_ratio = self._compute_citation_ratio(state, justification)

        if judge_llm is None:
            return citation_ratio

        # Stage 2: judge LLM (non-deterministic — documented in benchmark writeup)
        judge_score = self._compute_judge_score(state, justification, judge_llm)
        return (citation_ratio + judge_score) / 2.0

    def _compute_citation_ratio(
        self, state: EnvironmentState, justification: str
    ) -> float:
        """
        Deterministic: fraction of cited node IDs that appear in action_history.
        """
        if not justification:
            return 0.0

        # Extract node IDs from justification (pattern: n\d+ or node_\d+)
        cited = set(re.findall(r'\b(?:node_\d+|n\d+)\b', justification))
        if not cited:
            return 0.0

        # Node IDs that actually appeared in the traversal
        visited_in_history = {
            e.node_id for e in state.action_history if e.node_id
        }

        if not visited_in_history:
            return 0.0

        matched = cited & visited_in_history
        return len(matched) / len(cited)

    def _compute_judge_score(
        self, state: EnvironmentState, justification: str, judge_llm: Any
    ) -> float:
        """
        Non-deterministic: LLM-as-judge qualitative coherence score.
        Uses Kaggle SDK's assess_response_with_judge.
        Returns 0.0 on any failure.
        """
        try:
            import kaggle_benchmarks as kbench

            visited_nodes = [e.node_id for e in state.action_history if e.node_id]
            rubric = [
                f"The justification references specific nodes from the traversal (visited: {visited_nodes[:5]}).",
                "The justification explains why the cited nodes support the conclusion.",
                "The justification is coherent and not self-contradictory.",
            ]

            with kbench.chats.new("vigil_mc_judge"):
                report = kbench.assertions.assess_response_with_judge(
                    criteria=rubric,
                    response_text=justification,
                    judge_llm=judge_llm,
                )

            if report and hasattr(report, "results"):
                passed = sum(1 for r in report.results if r.passed)
                return passed / len(report.results) if report.results else 0.0
        except Exception:
            pass
        return 0.0

    # ------------------------------------------------------------------
    # Dimension 7: Contamination Risk (CR)
    # ------------------------------------------------------------------

    def compute_contamination_risk(self, state: EnvironmentState) -> float:
        """
        CR — composite contamination risk score (0.0 = clean, 1.0 = suspicious).

        Three signals:
          1. Path directness: ratio of direct path length to actual path length.
             Suspiciously direct first-exposure paths suggest memorisation.
          2. Exploration-before-execution ratio: fraction of budget spent
             before first submit attempt. Genuine learners explore first.
          3. Learning curve shape: flat-from-start performance suggests
             memorisation rather than in-context learning.

        If CR > 0.8, contamination_warning is set True in score_episode().
        """
        history = state.action_history
        if not history:
            return 0.0

        # Signal 1: path directness
        # Ratio of unique nodes visited to total explore actions
        # Low ratio (many revisits) = genuine exploration; high ratio = suspiciously direct
        explore_events = [e for e in history if e.event_type == EventType.EXPLORE]
        if explore_events:
            unique_explored = len({e.node_id for e in explore_events if e.node_id})
            directness = unique_explored / len(explore_events)
        else:
            directness = 0.0

        # Signal 2: exploration-before-execution ratio
        # Find index of first SUBMIT_ANSWER event
        submit_idx = next(
            (i for i, e in enumerate(history) if e.event_type == EventType.SUBMIT_ANSWER),
            len(history),
        )
        exploration_ratio = submit_idx / len(history) if history else 0.0
        # Low exploration ratio (submitted very early) is suspicious
        early_submit_risk = max(0.0, 1.0 - exploration_ratio * 2)

        # Signal 3: evidence collection variance
        # Flat evidence collection (all at once at start) is suspicious
        if len(history) >= 4:
            mid = len(history) // 2
            first_evidence = sum(
                len(e.state_delta.get("evidence_added", []))
                for e in history[:mid]
            )
            second_evidence = sum(
                len(e.state_delta.get("evidence_added", []))
                for e in history[mid:]
            )
            total_evidence = first_evidence + second_evidence
            if total_evidence > 0:
                # Perfectly front-loaded evidence collection is suspicious
                front_load = first_evidence / total_evidence
                curve_risk = max(0.0, front_load - 0.7)  # risk only if >70% in first half
            else:
                curve_risk = 0.0
        else:
            curve_risk = 0.0

        # Composite: weighted average of three signals
        cr = 0.4 * directness + 0.4 * early_submit_risk + 0.2 * curve_risk
        return min(1.0, cr)

    # ------------------------------------------------------------------
    # Human percentile
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_percentile(score: float, mean: float, std: float) -> float:
        """Compute percentile rank using normal distribution approximation."""
        if std <= 0:
            return 50.0
        from math import erf
        z = (score - mean) / std
        return round(0.5 * (1 + erf(z / sqrt(2))) * 100, 1)
