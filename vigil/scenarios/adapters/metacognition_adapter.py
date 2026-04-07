"""
MetacognitionAdapter — Track 2 (metacognition) authored schema validator and compiler.

Kaggle Track 2 = Metacognition.

Field mapping (authored → canonical):
  blind_task_prompt                          → opening_prompt
  object_level_goal + meta_level_goal        → answer_targets
  nodes[].node_id                            → node.node_id
  nodes[].content                            → node.summary_text + inspection_detail
  nodes[].node_type                          → node.node_type
  nodes[].visibility                         → node.initial_visibility
  nodes[].meta_relevance                     → node.metadata["meta_relevance"]
  edges[].from                               → edge.from_id
  edges[].to                                 → edge.to_id
  edges[].edge_type                          → edge.relation
  edges[].description                        → edge.reveal_text
  metacognitive_layers, scoring_focus,
  hidden_mechanism, disconfirmation_moment,
  recommended_meta_actions                   → track_metadata

Requirements: 2, 3, 12
"""

from typing import Any, Dict

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


class MetacognitionAdapter:
    """
    Validates and compiles Track 2 (metacognition) authored scenarios.

    Usage (via ScenarioCatalog — not called directly):
        adapter = MetacognitionAdapter()
        adapter.validate(raw, scenario_id)
        spec = adapter.compile(raw)
    """

    TRACK_ID = "metacognition"

    _REQUIRED_FIELDS = [
        "scenario_id",
        "cognitive_track",
        "blind_task_prompt",
        "object_level_goal",
        "meta_level_goal",
        "metacognitive_layers",
        "scoring_focus",
        "nodes",
        "edges",
    ]

    def validate(self, raw: Dict[str, Any], scenario_id: str) -> None:
        """
        Validate a raw authored dict against the Track 2 schema.

        Raises:
            ValueError: With the name of the first missing or invalid field.
        """
        for field in self._REQUIRED_FIELDS:
            if field not in raw:
                raise ValueError(
                    f"Scenario '{scenario_id}' (metacognition) missing required field '{field}'"
                )

    def compile(self, raw: Dict[str, Any]) -> RuntimeScenarioSpec:
        """
        Compile a validated Track 2 authored dict into a RuntimeScenarioSpec.
        """
        nodes = self._compile_nodes(raw["nodes"])
        edges = self._compile_edges(raw["edges"])

        # Entry nodes: nodes with visibility "initial" or "visible"
        entry_node_ids = [
            n.node_id for n in nodes
            if n.initial_visibility in ("visible", "initial")
        ]
        if not entry_node_ids and nodes:
            entry_node_ids = [nodes[0].node_id]

        return RuntimeScenarioSpec(
            scenario_id=raw["scenario_id"],
            cognitive_track="metacognition",
            opening_prompt=raw["blind_task_prompt"],
            nodes=nodes,
            edges=edges,
            entry_node_ids=entry_node_ids,
            answer_targets={
                "object_level_goal": raw["object_level_goal"],
                "meta_level_goal": raw["meta_level_goal"],
            },
            evidence_targets=[],   # metacognition uses node meta_relevance, not a fixed list
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={
                "object_score": 0.3,
                "meta_score": 0.7,
            },
            evaluation_conditions=EvaluationConditions(),
            track_metadata={
                "metacognitive_layers": raw.get("metacognitive_layers", []),
                "scoring_focus": raw.get("scoring_focus", []),
                "hidden_mechanism": raw.get("hidden_mechanism", ""),
                "disconfirmation_moment": raw.get("disconfirmation_moment", ""),
                "recommended_meta_actions": raw.get("recommended_meta_actions", []),
            },
        )

    @staticmethod
    def _map_visibility(raw_vis: str) -> str:
        """Map authored visibility strings to canonical RuntimeNode values."""
        mapping = {
            "visible": "visible",
            "initial": "initial",
            "hidden": "hidden",
            "expanded": "visible",
            "discovered": "hidden",
            "unexplored": "hidden",
        }
        return mapping.get(str(raw_vis).lower(), "hidden")

    @staticmethod
    def _compile_nodes(raw_nodes: list) -> list:
        """Map authored metacognition node dicts to RuntimeNode objects."""
        nodes = []
        for n in raw_nodes:
            content = n.get("content", "")
            nodes.append(RuntimeNode(
                node_id=n["node_id"],
                label=n.get("label", n["node_id"]),
                summary_text=content,
                inspection_detail=content,
                node_type=n.get("node_type", "standard"),
                initial_visibility=MetacognitionAdapter._map_visibility(
                    n.get("visibility", "hidden")
                ),
                metadata={
                    "meta_relevance": n.get("meta_relevance", ""),
                },
            ))
        return nodes

    @staticmethod
    def _compile_edges(raw_edges: list) -> list:
        """Map authored metacognition edge dicts to RuntimeEdge objects."""
        edges = []
        for e in raw_edges:
            edges.append(RuntimeEdge(
                from_id=e["from"],
                to_id=e["to"],
                relation=e.get("edge_type", e.get("relation", "")),
                reveal_text=e.get("description", ""),
            ))
        return edges
