"""
Core graph data structures.

Provides the basic building blocks for cognitive graph environments:
- NodeVisibility: Three-layer fog-of-war visibility state
- GraphNode: A node with features and optional hidden category
- GraphEdge: A directed edge with relation type
- CognitiveGraph: The full graph structure with POMDP visibility
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeVisibility(Enum):
    """
    Three-layer fog-of-war visibility state for graph nodes.

    UNEXPLORED: Node existence unknown to model — zero information.
    DISCOVERED: Node existence known (revealed as neighbor) but content hidden.
    EXPANDED:   Node fully inspected — features visible, category still hidden.
    """
    UNEXPLORED = "unexplored"
    DISCOVERED = "discovered"
    EXPANDED = "expanded"


@dataclass
class GraphNode:
    """
    A node in the cognitive graph.

    Attributes:
        node_id: Unique identifier for the node
        features: Set of features/properties associated with this node
        category: Hidden category label (never exposed to model)
        metadata: Additional node-specific data
    """
    node_id: str
    features: Set[str] = field(default_factory=set)
    category: Optional[str] = None  # Hidden from model — never expose
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization (includes hidden fields for storage)."""
        return {
            "node_id": self.node_id,
            "features": list(self.features),
            "category": self.category,
            "metadata": self.metadata,
        }

    def get_visible_features(self) -> Set[str]:
        """
        Get features visible to the model.

        Returns features only — never category.
        """
        return self.features.copy()


@dataclass
class GraphEdge:
    """
    A directed edge between two nodes.

    Attributes:
        source: Source node ID
        target: Target node ID
        relation_type: Type of relationship (e.g., "causes", "similar_to")
        weight: Edge weight (default 1.0)
        metadata: Additional edge-specific data
    """
    source: str
    target: str
    relation_type: str = "default"
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "metadata": self.metadata,
        }


class CognitiveGraph:
    """
    Directed labeled graph with fog-of-war POMDP visibility.

    The graph maintains a three-layer visibility state per node:
    - UNEXPLORED: model has no knowledge of this node
    - DISCOVERED: model knows the node exists (seen as a neighbor) but not its content
    - EXPANDED: model has inspected the node and can see its features (not category)

    The full ground-truth graph is stored server-side. The model only receives
    information through get_agent_view(), which filters by visibility state.
    """

    def __init__(
        self,
        nodes: Optional[Dict[str, GraphNode]] = None,
        edges: Optional[Dict[str, List[GraphEdge]]] = None,
        hidden_rule: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.nodes: Dict[str, GraphNode] = nodes or {}
        self.edges: Dict[str, List[GraphEdge]] = edges or {}
        self.hidden_rule = hidden_rule
        self.metadata = metadata or {}
        self._visibility: Dict[str, NodeVisibility] = {}

    # ------------------------------------------------------------------
    # Visibility management
    # ------------------------------------------------------------------

    def init_visibility(self, start_node: str) -> None:
        """
        Initialise visibility: all nodes UNEXPLORED except start_node (EXPANDED).

        Must be called after all nodes are added to the graph.
        """
        for node_id in self.nodes:
            self._visibility[node_id] = NodeVisibility.UNEXPLORED
        if start_node in self.nodes:
            self._visibility[start_node] = NodeVisibility.EXPANDED

    def set_visibility(self, node_id: str, v: NodeVisibility) -> None:
        """
        Set visibility for a node, only allowing upgrades (UNEXPLORED → DISCOVERED → EXPANDED).
        """
        current = self._visibility.get(node_id, NodeVisibility.UNEXPLORED)
        # Only upgrade, never downgrade
        order = [NodeVisibility.UNEXPLORED, NodeVisibility.DISCOVERED, NodeVisibility.EXPANDED]
        if order.index(v) > order.index(current):
            self._visibility[node_id] = v

    def get_visibility(self, node_id: str) -> NodeVisibility:
        """Return current visibility state for a node."""
        return self._visibility.get(node_id, NodeVisibility.UNEXPLORED)

    def get_agent_view(self) -> Dict[str, Any]:
        """
        Return only the information the model is allowed to see.

        - EXPANDED nodes: id, features (no category), edge_types
        - DISCOVERED nodes: id, edge_types only (no features, no category)
        - UNEXPLORED nodes: omitted entirely

        Returns:
            Dict with keys 'expanded' and 'discovered', each mapping
            node_id to its visible information.
        """
        expanded = {}
        discovered = {}

        for node_id, visibility in self._visibility.items():
            if visibility == NodeVisibility.EXPANDED:
                node = self.nodes[node_id]
                expanded[node_id] = {
                    "id": node_id,
                    "features": sorted(node.get_visible_features()),
                    "edge_types": sorted(self.get_edge_types(node_id)),
                    "neighbors": self.get_neighbors(node_id),
                }
            elif visibility == NodeVisibility.DISCOVERED:
                discovered[node_id] = {
                    "id": node_id,
                    "edge_types": sorted(self.get_edge_types(node_id)),
                }
            # UNEXPLORED: omit entirely

        return {"expanded": expanded, "discovered": discovered}

    # ------------------------------------------------------------------
    # Graph mutation
    # ------------------------------------------------------------------

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []
        # New nodes start UNEXPLORED unless init_visibility has been called
        if node.node_id not in self._visibility:
            self._visibility[node.node_id] = NodeVisibility.UNEXPLORED

    def add_edge(self, source: str, edge: GraphEdge) -> None:
        """Add an edge from a source node."""
        if source not in self.edges:
            self.edges[source] = []
        self.edges[source].append(edge)

    # ------------------------------------------------------------------
    # Graph queries
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get IDs of all direct neighbors."""
        return [edge.target for edge in self.edges.get(node_id, [])]

    def get_edges_from(self, node_id: str) -> List[GraphEdge]:
        """Get all outgoing edges from a node."""
        return self.edges.get(node_id, [])

    def get_edge_types(self, node_id: str) -> Set[str]:
        """Get unique relation types from a node."""
        return {edge.relation_type for edge in self.edges.get(node_id, [])}

    def get_all_node_ids(self) -> List[str]:
        """Get all node IDs."""
        return list(self.nodes.keys())

    def get_nodes_by_category(self, category: str) -> List[GraphNode]:
        """
        Get nodes matching a hidden category.

        For scoring/verification only — never expose to model.
        """
        return [n for n in self.nodes.values() if n.category == category]

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization (full ground truth)."""
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": {
                k: [e.to_dict() for e in v] for k, v in self.edges.items()
            },
            "hidden_rule": self.hidden_rule,
            "metadata": self.metadata,
            "visibility": {k: v.value for k, v in self._visibility.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveGraph":
        """Create CognitiveGraph from dictionary."""
        nodes = {
            k: GraphNode(
                node_id=v["node_id"],
                features=set(v.get("features", [])),
                category=v.get("category"),
                metadata=v.get("metadata", {}),
            )
            for k, v in data.get("nodes", {}).items()
        }
        edges: Dict[str, List[GraphEdge]] = {}
        for source, edge_list in data.get("edges", {}).items():
            edges[source] = [
                GraphEdge(
                    source=e["source"],
                    target=e["target"],
                    relation_type=e.get("relation_type", "default"),
                    weight=e.get("weight", 1.0),
                    metadata=e.get("metadata", {}),
                )
                for e in edge_list
            ]
        graph = cls(
            nodes=nodes,
            edges=edges,
            hidden_rule=data.get("hidden_rule"),
            metadata=data.get("metadata", {}),
        )
        # Restore visibility state if present
        for node_id, vis_str in data.get("visibility", {}).items():
            graph._visibility[node_id] = NodeVisibility(vis_str)
        return graph

    @classmethod
    def from_spec(cls, spec: Any) -> "CognitiveGraph":
        """
        Build a CognitiveGraph from a RuntimeScenarioSpec.

        Uses RuntimeNode/RuntimeEdge canonical fields — never raw authored keys.
        Visibility is NOT initialised here; call init_visibility_from_spec()
        after construction (done by GraphScenarioEnvironment.reset()).

        Args:
            spec: A RuntimeScenarioSpec instance.

        Returns:
            CognitiveGraph with all nodes and edges loaded, visibility uninitialised.
        """
        graph = cls()

        for rn in spec.nodes:
            node = GraphNode(
                node_id=rn.node_id,
                features={rn.summary_text} if rn.summary_text else set(),
                category=None,  # never expose category to model
                metadata={
                    "label": rn.label,
                    "summary_text": rn.summary_text,
                    "inspection_detail": rn.inspection_detail,
                    "node_type": rn.node_type,
                    "initial_visibility": rn.initial_visibility,
                    **rn.metadata,
                },
            )
            graph.add_node(node)

        for re in spec.edges:
            edge = GraphEdge(
                source=re.from_id,
                target=re.to_id,
                relation_type=re.relation,
                weight=float(re.traversal_cost),
                metadata={
                    "reveal_text": re.reveal_text,
                    "traversal_cost": re.traversal_cost,
                    **re.metadata,
                },
            )
            graph.add_edge(re.from_id, edge)

        return graph

    def init_visibility_from_spec(self, spec: Any) -> None:
        """
        Initialise visibility from RuntimeScenarioSpec.initial_visibility fields.

        Nodes with initial_visibility in ("visible", "initial") start as EXPANDED.
        All other nodes start as UNEXPLORED.

        Args:
            spec: A RuntimeScenarioSpec instance.
        """
        # First set all to UNEXPLORED
        for node_id in self.nodes:
            self._visibility[node_id] = NodeVisibility.UNEXPLORED

        # Then upgrade nodes that start visible/initial
        for rn in spec.nodes:
            if rn.initial_visibility in ("visible", "initial"):
                self._visibility[rn.node_id] = NodeVisibility.EXPANDED
                # Also reveal their neighbors as DISCOVERED
                for neighbor_id in self.get_neighbors(rn.node_id):
                    if self._visibility.get(neighbor_id) == NodeVisibility.UNEXPLORED:
                        self._visibility[neighbor_id] = NodeVisibility.DISCOVERED
