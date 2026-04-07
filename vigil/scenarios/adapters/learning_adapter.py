"""
LearningAdapter — Track 1 (learning) authored schema validator and compiler.

Validates a raw authored JSON dict against the Track 1 schema and compiles
it into a RuntimeScenarioSpec. The ScenarioCatalog dispatches here when
cognitive_track == "learning".

Field mapping (authored → canonical):
  blind_framing                          → opening_prompt
  graph_metadata.entry_nodes             → entry_node_ids
  hidden_objective                       → answer_targets
  hidden_objective.minimum_evidence_nodes → evidence_targets
  optimal_path.sequence                  → optimal_path
  optimal_path.length                    → optimal_steps
  scoring_config.max_steps               → runtime_config.action_budget
  scoring_config.weights                 → scoring_weights
  node.id                                → node.node_id
  node.surface_text                      → node.summary_text
  node.inspection_detail                 → node.inspection_detail
  edge.from                              → edge.from_id
  edge.to                                → edge.to_id
  edge.reveal                            → edge.reveal_text
  edge.traversal_cost                    → edge.traversal_cost
  edge.is_red_herring                    → edge.metadata["is_red_herring"]
  anti_shortcutting_audit, behavioral_signatures, graph_metadata → track_metadata

Requirements: 2, 3
"""

import warnings
from typing import Any, Dict

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


class LearningAdapter:
    """
    Validates and compiles Track 1 (learning) authored scenarios.

    Usage (via ScenarioCatalog — not called directly):
        adapter = LearningAdapter()
        adapter.validate(raw, scenario_id)   # raises ValueError on failure
        spec = adapter.compile(raw)
    """

    TRACK_ID = "learning"

    # Required top-level fields
    _REQUIRED_FIELDS = [
        "scenario_id",
        "cognitive_track",
        "blind_framing",
        "hidden_objective",
        "nodes",
        "edges",
        "optimal_path",
        "scoring_config",
        "graph_metadata",
    ]

    # Required sub-fields inside hidden_objective
    _REQUIRED_HIDDEN_OBJECTIVE = [
        "correct_root_cause",
        "correct_mechanism",
        "minimum_evidence_nodes",
    ]

    def validate(self, raw: Dict[str, Any], scenario_id: str) -> None:
        """
        Validate a raw authored dict against the Track 1 schema.

        Raises:
            ValueError: With the name of the first missing or invalid field.
        """
        for field in self._REQUIRED_FIELDS:
            if field not in raw:
                raise ValueError(
                    f"Scenario '{scenario_id}' (learning) missing required field '{field}'"
                )

        ho = raw["hidden_objective"]
        for sub in self._REQUIRED_HIDDEN_OBJECTIVE:
            if sub not in ho:
                raise ValueError(
                    f"Scenario '{scenario_id}' hidden_objective missing '{sub}'"
                )

    def compile(self, raw: Dict[str, Any]) -> RuntimeScenarioSpec:
        """
        Compile a validated Track 1 authored dict into a RuntimeScenarioSpec.

        All raw field names are resolved to canonical RuntimeNode/RuntimeEdge
        fields here. GraphScenarioEnvironment never reads raw authored keys.
        """
        sc = raw["scoring_config"]
        ho = raw["hidden_objective"]
        gm = raw["graph_metadata"]
        op = raw["optimal_path"]

        nodes = self._compile_nodes(raw["nodes"])
        edges = self._compile_edges(raw["edges"])

        # entry_node_ids from graph_metadata.entry_nodes
        entry_node_ids = gm.get("entry_nodes", [])
        if not entry_node_ids and nodes:
            entry_node_ids = [nodes[0].node_id]

        # scoring_weights from scoring_config.weights — normalise if needed
        weights = dict(sc.get("weights", {}))
        if weights:
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                warnings.warn(
                    f"Scenario '{raw['scenario_id']}' scoring_config.weights sum to "
                    f"{total:.4f}, not 1.0. Normalising.",
                    stacklevel=3,
                )
                weights = {k: v / total for k, v in weights.items()}

        return RuntimeScenarioSpec(
            scenario_id=raw["scenario_id"],
            cognitive_track="learning",
            opening_prompt=self._extract_prompt(raw["blind_framing"]),
            nodes=nodes,
            edges=edges,
            entry_node_ids=entry_node_ids,
            answer_targets=dict(ho),
            evidence_targets=list(ho.get("minimum_evidence_nodes", [])),
            optimal_path=list(op.get("sequence", [])),
            optimal_steps=int(op.get("length", len(op.get("sequence", [])))),
            runtime_config=RuntimeConfig(
                action_budget=int(sc.get("max_steps", 16))
            ),
            scoring_weights=weights,
            evaluation_conditions=EvaluationConditions(),
            track_metadata={
                "anti_shortcutting_audit": raw.get("anti_shortcutting_audit", {}),
                "behavioral_signatures": raw.get("behavioral_signatures", {}),
                "graph_metadata": gm,
                "scoring_config": sc,
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_prompt(blind_framing: Any) -> str:
        """
        Extract the opening prompt string from blind_framing.

        The authored pack may store blind_framing as:
          - a plain string
          - a dict with key "task_presented_to_model"
        """
        if isinstance(blind_framing, str):
            return blind_framing
        if isinstance(blind_framing, dict):
            return (
                blind_framing.get("task_presented_to_model")
                or blind_framing.get("prompt")
                or str(blind_framing)
            )
        return str(blind_framing)

    @staticmethod
    def _compile_nodes(raw_nodes: list) -> list:
        """Map authored node dicts to RuntimeNode objects."""
        nodes = []
        for n in raw_nodes:
            nodes.append(RuntimeNode(
                node_id=n["id"],
                label=n.get("label", n["id"]),
                summary_text=n.get("surface_text", ""),
                inspection_detail=n.get("inspection_detail", ""),
                node_type="entry" if n.get("is_entry_point") else "standard",
                initial_visibility="hidden",
                metadata={
                    k: v for k, v in n.items()
                    if k not in (
                        "id", "label", "surface_text", "inspection_detail",
                        "is_entry_point", "available_relations",
                    )
                },
            ))
        return nodes

    @staticmethod
    def _compile_edges(raw_edges: list) -> list:
        """Map authored edge dicts to RuntimeEdge objects."""
        edges = []
        for e in raw_edges:
            edges.append(RuntimeEdge(
                from_id=e["from"],
                to_id=e["to"],
                relation=e.get("relation", ""),
                reveal_text=e.get("reveal", ""),
                traversal_cost=int(e.get("traversal_cost", 1)),
                metadata={"is_red_herring": e.get("is_red_herring", False)},
            ))
        return edges
