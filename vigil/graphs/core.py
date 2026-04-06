"""
Core graph data structures.

Provides the basic building blocks for cognitive graph environments:
- GraphNode: A node with features and optional hidden category
- GraphEdge: A directed edge with relation type
- CognitiveGraph: The full graph structure
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
import random


@dataclass
class GraphNode:
    """
    A node in the cognitive graph.

    Attributes:
        node_id: Unique identifier for the node
        features: Set of features/properties associated with this node
        category: Hidden category label (for concept formation tasks)
        metadata: Additional node-specific data
    """
    node_id: str
    features: Set[str] = field(default_factory=set)
    category: Optional[str] = None  # Hidden from model
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "features": list(self.features),
            "category": self.category,
            "metadata": self.metadata
        }

    def get_visible_features(self) -> Set[str]:
        """
        Get features visible to the model.

        Category is hidden - only return non-category features.
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
            "metadata": self.metadata
        }


class CognitiveGraph:
    """
    Main graph structure for cognitive environments.

    A CognitiveGraph is a directed, labeled graph where:
    - Nodes represent entities with features
    - Edges represent relationships between entities
    - Hidden categories/rules exist for learning tasks

    The graph can be procedurally generated or loaded from a scenario config.
    """

    def __init__(
        self,
        nodes: Optional[Dict[str, GraphNode]] = None,
        edges: Optional[Dict[str, List[GraphEdge]]] = None,
        hidden_rule: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the cognitive graph.

        Args:
            nodes: Dictionary mapping node_id to GraphNode
            edges: Adjacency list (node_id -> list of outgoing edges)
            hidden_rule: Description of the hidden rule to discover
            metadata: Additional graph-level metadata
        """
        self.nodes: Dict[str, GraphNode] = nodes or {}
        self.edges: Dict[str, List[GraphEdge]] = edges or {}
        self.hidden_rule = hidden_rule
        self.metadata = metadata or {}

        # Track which nodes have been revealed to the model
        self._revealed_nodes: Set[str] = set()

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []

    def add_edge(self, source: str, edge: GraphEdge) -> None:
        """Add an edge from a source node."""
        if source not in self.edges:
            self.edges[source] = []
        self.edges[source].append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get IDs of neighboring nodes."""
        if node_id not in self.edges:
            return []
        return [edge.target for edge in self.edges[node_id]]

    def get_edges_from(self, node_id: str) -> List[GraphEdge]:
        """Get all outgoing edges from a node."""
        return self.edges.get(node_id, [])

    def get_edge_types(self, node_id: str) -> Set[str]:
        """Get unique relation types from a node."""
        edges = self.edges.get(node_id, [])
        return {edge.relation_type for edge in edges}

    def expand_node(
        self,
        node_id: str,
        relation_type: Optional[str] = None
    ) -> List[GraphEdge]:
        """
        Expand a node to reveal its outgoing edges.

        Args:
            node_id: Node to expand
            relation_type: Optional filter by relation type

        Returns:
            List of edges revealed by this expansion
        """
        self._revealed_nodes.add(node_id)
        edges = self.get_edges_from(node_id)

        if relation_type:
            edges = [e for e in edges if e.relation_type == relation_type]

        return edges

    def is_node_revealed(self, node_id: str) -> bool:
        """Check if a node has been revealed."""
        return node_id in self._revealed_nodes

    def get_all_node_ids(self) -> List[str]:
        """Get all node IDs."""
        return list(self.nodes.keys())

    def get_nodes_by_category(self, category: str) -> List[GraphNode]:
        """
        Get nodes matching a hidden category.

        Note: This is for scoring/verification, not for revealing to model.
        """
        return [n for n in self.nodes.values() if n.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization."""
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": {
                k: [e.to_dict() for e in v]
                for k, v in self.edges.items()
            },
            "hidden_rule": self.hidden_rule,
            "metadata": self.metadata,
            "revealed_nodes": list(self._revealed_nodes)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveGraph":
        """Create CognitiveGraph from dictionary."""
        nodes = {
            k: GraphNode(
                node_id=v["node_id"],
                features=set(v.get("features", [])),
                category=v.get("category"),
                metadata=v.get("metadata", {})
            )
            for k, v in data.get("nodes", {}).items()
        }

        edges = {}
        for source, edge_list in data.get("edges", {}).items():
            edges[source] = [
                GraphEdge(
                    source=e["source"],
                    target=e["target"],
                    relation_type=e.get("relation_type", "default"),
                    weight=e.get("weight", 1.0),
                    metadata=e.get("metadata", {})
                )
                for e in edge_list
            ]

        return cls(
            nodes=nodes,
            edges=edges,
            hidden_rule=data.get("hidden_rule"),
            metadata=data.get("metadata", {})
        )
