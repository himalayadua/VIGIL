"""
Normalized internal representation for authored scenarios.

All authored scenario JSON packs (Track 1–5) are compiled into these
dataclasses before being passed to GraphScenarioEnvironment. This means
the runtime never reads raw per-track field names.

Three strictly separate config sections in RuntimeScenarioSpec:
  - runtime_config:       episode mechanics (budget, costs, turn cap)
  - scoring_weights:      dimension weights for scoring math only
  - evaluation_conditions: matched AI/human evaluation contract

Requirements: 3, 5, 20, 21
"""

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# RuntimeConfig — episode mechanics, NOT scoring
# ---------------------------------------------------------------------------

@dataclass
class RuntimeConfig:
    """
    Controls how an episode runs. Kept strictly separate from scoring_weights.

    Attributes:
        action_budget: Starting budget_remaining for the episode.
        action_costs:  Per-action-type budget deductions. Keys: "inspect",
                       "ask_for_help", "communication". Explore cost is
                       edge-driven (RuntimeEdge.traversal_cost), not here.
        turn_cap:      Hard maximum turns per episode, always ≤ 20.
    """
    action_budget: int
    action_costs: Dict[str, int] = field(default_factory=lambda: {
        "inspect": 1,
        "ask_for_help": 1,
        "communication": 1,
    })
    turn_cap: int = 20

    def __post_init__(self) -> None:
        if self.turn_cap > 20:
            raise ValueError(f"turn_cap must be ≤ 20, got {self.turn_cap}")
        if self.action_budget <= 0:
            raise ValueError(f"action_budget must be > 0, got {self.action_budget}")


# ---------------------------------------------------------------------------
# EvaluationConditions — matched AI/human contract
# ---------------------------------------------------------------------------

@dataclass
class EvaluationConditions:
    """
    Defines the evaluation contract that must be identical for AI and human
    participants on the same scenario. Required for valid human-baseline
    comparison per the DeepMind 3-stage protocol.

    Attributes:
        allowed_tools:             List of permitted external tools. Empty = none.
        response_format:           Expected response format from the model.
        interface_mode:            Interaction mode for this scenario.
        tool_policy:               One of "none", "calculator_only", "search_allowed".
        external_knowledge_policy: One of "none", "domain_knowledge_allowed".
    """
    allowed_tools: List[str] = field(default_factory=list)
    response_format: str = "structured_json"
    interface_mode: str = "graph_traversal"
    tool_policy: str = "none"
    external_knowledge_policy: str = "none"

    _VALID_TOOL_POLICIES = {"none", "calculator_only", "search_allowed"}
    _VALID_KNOWLEDGE_POLICIES = {"none", "domain_knowledge_allowed"}

    def __post_init__(self) -> None:
        if self.tool_policy not in self._VALID_TOOL_POLICIES:
            raise ValueError(
                f"tool_policy must be one of {self._VALID_TOOL_POLICIES}, "
                f"got '{self.tool_policy}'"
            )
        if self.external_knowledge_policy not in self._VALID_KNOWLEDGE_POLICIES:
            raise ValueError(
                f"external_knowledge_policy must be one of "
                f"{self._VALID_KNOWLEDGE_POLICIES}, "
                f"got '{self.external_knowledge_policy}'"
            )


# ---------------------------------------------------------------------------
# RuntimeNode and RuntimeEdge — canonical graph elements
# ---------------------------------------------------------------------------

@dataclass
class RuntimeNode:
    """
    Normalized node with canonical fields used by GraphScenarioEnvironment.

    Track-specific field names (e.g. "surface_text" for learning, "content"
    for metacognition) are resolved to these canonical names at compile time.

    Attributes:
        node_id:           Canonical node identifier.
        label:             Human-readable label.
        summary_text:      Brief text shown when the node is explored.
        inspection_detail: Full text shown when the node is inspected.
        node_type:         Role tag (e.g. "standard", "distractor", "agent").
                           Never exposed to the model via get_agent_view().
        initial_visibility: Starting visibility state: "visible", "initial",
                            or "hidden". "visible"/"initial" → EXPANDED at reset.
        metadata:          Track-specific fields (attention_role, meta_relevance,
                           agent_profile, etc.) not covered by canonical fields.
    """
    node_id: str
    label: str
    summary_text: str
    inspection_detail: str
    node_type: str = "standard"
    initial_visibility: str = "hidden"
    metadata: Dict[str, Any] = field(default_factory=dict)

    _VALID_VISIBILITY = {"visible", "initial", "hidden"}

    def __post_init__(self) -> None:
        if self.initial_visibility not in self._VALID_VISIBILITY:
            raise ValueError(
                f"initial_visibility must be one of {self._VALID_VISIBILITY}, "
                f"got '{self.initial_visibility}'"
            )


@dataclass
class RuntimeEdge:
    """
    Normalized edge with canonical fields used by GraphScenarioEnvironment.

    Attributes:
        from_id:        Source node ID.
        to_id:          Target node ID.
        relation:       Edge relation label.
        reveal_text:    Text surfaced to the model when this edge is traversed.
        traversal_cost: Budget deducted from budget_remaining on ExploreAction.
                        Default 1. NOT stored in scoring_weights.
        metadata:       Track-specific fields (is_red_herring, attention_role, etc.)
    """
    from_id: str
    to_id: str
    relation: str
    reveal_text: str = ""
    traversal_cost: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.traversal_cost < 0:
            raise ValueError(
                f"traversal_cost must be ≥ 0, got {self.traversal_cost}"
            )


# ---------------------------------------------------------------------------
# RuntimeScenarioSpec — the canonical compiled scenario
# ---------------------------------------------------------------------------

@dataclass
class RuntimeScenarioSpec:
    """
    Normalized internal representation compiled from an authored scenario.

    GraphScenarioEnvironment only reads this object — never the raw JSON.
    Three strictly separate config sections:
      - runtime_config:       episode mechanics
      - scoring_weights:      dimension weights (no action costs here)
      - evaluation_conditions: matched AI/human contract

    Attributes:
        scenario_id:           Unique scenario identifier.
        cognitive_track:       Canonical track string, e.g. "learning".
        opening_prompt:        Blind framing shown to the model at episode start.
        nodes:                 Compiled RuntimeNode list.
        edges:                 Compiled RuntimeEdge list.
        entry_node_ids:        Starting node(s); reset() uses entry_node_ids[0].
        answer_targets:        Ground-truth answer fields for scoring.
        evidence_targets:      Node IDs that count as evidence when inspected.
        optimal_path:          Sequence of node IDs on the optimal traversal.
        optimal_steps:         len(optimal_path) — used ONLY by stopping quality
                               scoring, NOT as a budget ceiling.
        runtime_config:        Episode mechanics (budget, costs, turn cap).
        scoring_weights:       Dimension weights for scoring math only.
        evaluation_conditions: Matched AI/human evaluation contract.
        track_metadata:        Track-specific fields not covered above.
    """
    scenario_id: str
    cognitive_track: str
    opening_prompt: str
    nodes: List[RuntimeNode]
    edges: List[RuntimeEdge]
    entry_node_ids: List[str]
    answer_targets: Dict[str, Any]
    evidence_targets: List[str]
    optimal_path: List[str]
    optimal_steps: int
    runtime_config: RuntimeConfig
    scoring_weights: Dict[str, float]
    evaluation_conditions: EvaluationConditions = field(
        default_factory=EvaluationConditions
    )
    track_metadata: Dict[str, Any] = field(default_factory=dict)

    def apply_seed_perturbation(self, seed: int) -> "RuntimeScenarioSpec":
        """
        Return a new spec with node ID assignment order and edge ordering
        re-randomised using the given seed.

        seed=0 returns self unchanged (no perturbation).
        Other seeds produce deterministic reorderings that preserve:
          - graph structure (adjacency)
          - answer_targets
          - evidence_targets
          - optimal_path (node IDs within it are remapped)
          - evaluation_conditions

        This is equivalent to perturbation_type="reorder_nodes" and gives
        FacultyProfiler.aggregate_seeds() real cross-seed variance to compute.
        """
        if seed == 0:
            return self

        rng = random.Random(seed)

        # Build a shuffled node ID mapping: old_id → new_id
        old_ids = [n.node_id for n in self.nodes]
        new_ids = old_ids[:]
        rng.shuffle(new_ids)
        id_map: Dict[str, str] = dict(zip(old_ids, new_ids))

        # Remap nodes
        new_nodes = [
            RuntimeNode(
                node_id=id_map[n.node_id],
                label=n.label,
                summary_text=n.summary_text,
                inspection_detail=n.inspection_detail,
                node_type=n.node_type,
                initial_visibility=n.initial_visibility,
                metadata=dict(n.metadata),
            )
            for n in self.nodes
        ]

        # Shuffle node list order
        rng.shuffle(new_nodes)

        # Remap edges (from_id, to_id) and shuffle edge list
        new_edges = [
            RuntimeEdge(
                from_id=id_map.get(e.from_id, e.from_id),
                to_id=id_map.get(e.to_id, e.to_id),
                relation=e.relation,
                reveal_text=e.reveal_text,
                traversal_cost=e.traversal_cost,
                metadata=dict(e.metadata),
            )
            for e in self.edges
        ]
        rng.shuffle(new_edges)

        # Remap entry_node_ids, evidence_targets, optimal_path
        new_entry = [id_map.get(nid, nid) for nid in self.entry_node_ids]
        new_evidence = [id_map.get(nid, nid) for nid in self.evidence_targets]
        new_optimal = [id_map.get(nid, nid) for nid in self.optimal_path]

        return RuntimeScenarioSpec(
            scenario_id=self.scenario_id,
            cognitive_track=self.cognitive_track,
            opening_prompt=self.opening_prompt,
            nodes=new_nodes,
            edges=new_edges,
            entry_node_ids=new_entry,
            answer_targets=dict(self.answer_targets),
            evidence_targets=new_evidence,
            optimal_path=new_optimal,
            optimal_steps=self.optimal_steps,
            runtime_config=self.runtime_config,
            scoring_weights=dict(self.scoring_weights),
            evaluation_conditions=self.evaluation_conditions,
            track_metadata=dict(self.track_metadata),
        )

    def to_scenario_config_dict(self) -> Dict[str, Any]:
        """
        Return a dict compatible with VISScorer.score_episode(scenario_config=...).

        Preserves backward compatibility with the existing VISScorer interface
        which expects keys like "optimal_steps" and "process_weights".
        """
        return {
            "scenario_id": self.scenario_id,
            "cognitive_track": self.cognitive_track,
            "optimal_steps": self.optimal_steps,
            "process_weights": self.scoring_weights,
            "scoring_weights": self.scoring_weights,
        }
