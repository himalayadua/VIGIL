"""
Procedural graph generator for Vigil cognitive environments.

Generates novel CognitiveGraph instances from a seed + graph family,
ensuring contamination resistance: same seed → identical graph,
different seed → structurally distinct graph.

Pipeline per generate() call:
  1. Build topology via NetworkX (family-specific algorithm)
  2. Assign node features from a seeded feature pool
  3. Embed hidden rule into graph structure (not in Action_API-accessible fields)
  4. Randomise node ID assignment order (seed-controlled)
  5. Randomise edge ordering (seed-controlled)
  6. Wrap in CognitiveGraph and call init_visibility(start_node)

Requirements: 9.1–9.8
"""

import random
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


class GraphFamily(Enum):
    """
    Four graph topology families, each producing structurally distinct graphs.

    ERDOS_RENYI:      Random edges with uniform probability — sparse, unpredictable.
    BARABASI_ALBERT:  Preferential attachment — hubs form naturally, mimics real networks.
    WATTS_STROGATZ:   Small-world — high clustering with short average path lengths.
    STOCHASTIC_BLOCK: Community structure — nodes cluster into groups (ideal for concept formation).
    """
    ERDOS_RENYI = "erdos_renyi"
    BARABASI_ALBERT = "barabasi_albert"
    WATTS_STROGATZ = "watts_strogatz"
    STOCHASTIC_BLOCK = "stochastic_block_model"


# Feature vocabulary — abstract symbols that cannot be derived from training data
_FEATURE_VOCAB = [
    f"attr_{chr(65 + i // 26)}{chr(65 + i % 26)}" for i in range(52)
]  # AA, AB, ..., BZ

# Category labels — abstract, not semantically meaningful
_CATEGORY_LABELS = [f"class_{i}" for i in range(10)]


class ProceduralGenerator:
    """
    Generates CognitiveGraph instances procedurally from a seed and graph family.

    All randomness is seeded — the same (family, seed, difficulty_config) triple
    always produces the identical graph. Different seeds produce structurally
    distinct graphs with high probability.

    Usage:
        gen = ProceduralGenerator()
        graph = gen.generate(
            family=GraphFamily.STOCHASTIC_BLOCK,
            seed=42,
            size_factor=1.0,
            difficulty_config={"num_nodes": 15, "num_categories": 3, ...},
            rule_config={"type": "category_by_core_features", "num_core": 3},
        )
    """

    def generate(
        self,
        family: GraphFamily,
        seed: int,
        size_factor: float,
        difficulty_config: Dict[str, Any],
        rule_config: Optional[Dict[str, Any]] = None,
    ) -> CognitiveGraph:
        """
        Generate a novel CognitiveGraph instance.

        Args:
            family: Which topology algorithm to use
            seed: Random seed — controls all randomness deterministically
            size_factor: Multiplier on num_nodes (1.0 = base size)
            difficulty_config: Dict with at minimum 'num_nodes'; may include
                'num_categories', 'features_per_node', 'core_features_per_category'
            rule_config: Optional dict describing the hidden rule to embed.
                If None, no hidden rule is embedded.

        Returns:
            A fully initialised CognitiveGraph with fog-of-war visibility set.
        """
        rng = random.Random(seed)

        # 1. Determine node count
        base_n = difficulty_config.get("num_nodes", 12)
        n = max(3, int(base_n * size_factor))

        # 2. Build raw NetworkX topology
        nx_graph = self._build_topology(family, n, seed)

        # 3. Assign features and categories to nodes
        num_categories = difficulty_config.get("num_categories", 2)
        features_per_node = difficulty_config.get("features_per_node", 4)
        core_per_cat = difficulty_config.get("core_features_per_category", 2)

        node_features, node_categories, category_core_features = self._assign_features(
            nx_graph, num_categories, features_per_node, core_per_cat, rng
        )

        # 4. Embed hidden rule (stored in graph metadata, not in node.category directly
        #    — category IS the hidden rule signal, but it's never exposed via get_agent_view)
        hidden_rule_str = None
        if rule_config:
            hidden_rule_str = self._embed_hidden_rule(
                rule_config, category_core_features, rng
            )

        # 5. Randomise node ID ordering (prevents positional shortcuts)
        node_id_map = self._randomise_node_ids(list(nx_graph.nodes()), rng)

        # 6. Build CognitiveGraph with randomised edge ordering
        graph = self._build_cognitive_graph(
            nx_graph,
            node_id_map,
            node_features,
            node_categories,
            hidden_rule_str,
            category_core_features,
            rng,
        )

        # 7. Initialise fog-of-war visibility from a random start node
        start_node = rng.choice(list(graph.nodes.keys()))
        graph.init_visibility(start_node)
        graph.metadata["start_node"] = start_node
        graph.metadata["seed"] = seed
        graph.metadata["family"] = family.value

        return graph

    # ------------------------------------------------------------------
    # Step 1: Build NetworkX topology
    # ------------------------------------------------------------------

    def _build_topology(self, family: GraphFamily, n: int, seed: int) -> nx.Graph:
        """Build an undirected NetworkX graph using the specified family algorithm."""
        if family == GraphFamily.ERDOS_RENYI:
            # p chosen so expected edges ≈ 2n (sparse but connected-ish)
            p = min(0.4, 4.0 / max(n - 1, 1))
            G = nx.erdos_renyi_graph(n, p, seed=seed)

        elif family == GraphFamily.BARABASI_ALBERT:
            # m = number of edges to attach per new node; m=2 gives moderate density
            m = max(1, min(3, n // 5))
            G = nx.barabasi_albert_graph(n, m, seed=seed)

        elif family == GraphFamily.WATTS_STROGATZ:
            # k = each node connected to k nearest neighbours; p = rewiring probability
            k = max(2, min(4, n // 3))
            k = k if k % 2 == 0 else k + 1  # must be even
            G = nx.watts_strogatz_graph(n, k, 0.3, seed=seed)

        elif family == GraphFamily.STOCHASTIC_BLOCK:
            # Create 2-4 communities of roughly equal size
            num_blocks = max(2, min(4, n // 4))
            sizes = self._split_evenly(n, num_blocks)
            # High intra-community, low inter-community connection probability
            p_matrix = [
                [0.6 if i == j else 0.05 for j in range(num_blocks)]
                for i in range(num_blocks)
            ]
            G = nx.stochastic_block_model(sizes, p_matrix, seed=seed)

        else:
            raise ValueError(f"Unknown graph family: {family}")

        # Ensure the graph has at least one edge (degenerate case guard)
        if G.number_of_edges() == 0 and n >= 2:
            rng = random.Random(seed)
            nodes = list(G.nodes())
            for i in range(len(nodes) - 1):
                G.add_edge(nodes[i], nodes[i + 1])

        return G

    # ------------------------------------------------------------------
    # Step 2: Assign features and categories
    # ------------------------------------------------------------------

    def _assign_features(
        self,
        G: nx.Graph,
        num_categories: int,
        features_per_node: int,
        core_per_cat: int,
        rng: random.Random,
    ) -> Tuple[Dict[int, List[str]], Dict[int, str], Dict[str, List[str]]]:
        """
        Assign features and hidden categories to each NetworkX node.

        Returns:
            node_features: {nx_node_id: [feature, ...]}
            node_categories: {nx_node_id: category_label}
            category_core_features: {category_label: [core_feature, ...]}
        """
        num_categories = max(2, min(num_categories, len(_CATEGORY_LABELS)))
        categories = _CATEGORY_LABELS[:num_categories]

        # Assign each category a set of unique core features
        shuffled_vocab = _FEATURE_VOCAB.copy()
        rng.shuffle(shuffled_vocab)
        category_core_features: Dict[str, List[str]] = {}
        used = 0
        for cat in categories:
            core = shuffled_vocab[used: used + core_per_cat]
            category_core_features[cat] = core
            used += core_per_cat

        # Remaining features are noise
        noise_pool = shuffled_vocab[used:]

        # Assign categories to nodes (round-robin then shuffle for balance)
        nodes = list(G.nodes())
        node_categories: Dict[int, str] = {}
        for i, node in enumerate(nodes):
            node_categories[node] = categories[i % num_categories]

        # Build feature sets: core features + noise
        node_features: Dict[int, List[str]] = {}
        for node in nodes:
            cat = node_categories[node]
            core = category_core_features[cat].copy()
            noise_count = max(0, features_per_node - len(core))
            noise = rng.sample(noise_pool, min(noise_count, len(noise_pool)))
            all_features = core + noise
            rng.shuffle(all_features)
            node_features[node] = all_features

        return node_features, node_categories, category_core_features

    # ------------------------------------------------------------------
    # Step 3: Embed hidden rule
    # ------------------------------------------------------------------

    def _embed_hidden_rule(
        self,
        rule_config: Dict[str, Any],
        category_core_features: Dict[str, List[str]],
        rng: random.Random,
    ) -> str:
        """
        Produce a hidden rule description string stored in graph.hidden_rule.

        The rule is embedded structurally (via category assignments and core
        features) — it is NOT stored in any field accessible via get_agent_view().
        """
        rule_type = rule_config.get("type", "category_by_core_features")

        if rule_type == "category_by_core_features":
            # Rule: nodes in the same category share core features
            rule_parts = [
                f"{cat}: {', '.join(feats)}"
                for cat, feats in category_core_features.items()
            ]
            return f"category_by_core_features | " + " | ".join(rule_parts)

        elif rule_type == "reward_regions":
            # Rule: certain categories are reward regions
            cats = list(category_core_features.keys())
            rng.shuffle(cats)
            reward_cats = cats[: len(cats) // 2]
            return f"reward_regions | advantageous: {', '.join(reward_cats)}"

        else:
            return f"custom_rule | type={rule_type}"

    # ------------------------------------------------------------------
    # Step 4: Randomise node ID ordering
    # ------------------------------------------------------------------

    def _randomise_node_ids(
        self, nx_nodes: List[int], rng: random.Random
    ) -> Dict[int, str]:
        """
        Map NetworkX integer node IDs to randomised string IDs.

        The same logical graph structure produces different node orderings
        across seeds, preventing positional shortcuts.
        """
        indices = list(range(len(nx_nodes)))
        rng.shuffle(indices)
        return {nx_node: f"n{indices[i]}" for i, nx_node in enumerate(nx_nodes)}

    # ------------------------------------------------------------------
    # Step 5: Build CognitiveGraph with randomised edge ordering
    # ------------------------------------------------------------------

    def _build_cognitive_graph(
        self,
        nx_graph: nx.Graph,
        node_id_map: Dict[int, str],
        node_features: Dict[int, List[str]],
        node_categories: Dict[int, str],
        hidden_rule: Optional[str],
        category_core_features: Dict[str, List[str]],
        rng: random.Random,
    ) -> CognitiveGraph:
        """Assemble the final CognitiveGraph from all computed components."""
        graph = CognitiveGraph(
            hidden_rule=hidden_rule,
            metadata={"category_core_features": category_core_features},
        )

        # Add nodes
        for nx_node, vigil_id in node_id_map.items():
            graph.add_node(GraphNode(
                node_id=vigil_id,
                features=set(node_features.get(nx_node, [])),
                category=node_categories.get(nx_node),
            ))

        # Add edges with randomised ordering and relation type
        relation_types = ["connected_to", "leads_to", "links", "relates_to"]
        edges = list(nx_graph.edges())
        rng.shuffle(edges)  # Req 9.5: randomise edge ordering

        for u, v in edges:
            uid = node_id_map[u]
            vid = node_id_map[v]
            rel = rng.choice(relation_types)
            # Add both directions (undirected → directed)
            graph.add_edge(uid, GraphEdge(source=uid, target=vid, relation_type=rel))
            graph.add_edge(vid, GraphEdge(source=vid, target=uid, relation_type=rel))

        return graph

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _split_evenly(n: int, k: int) -> List[int]:
        """Split n into k roughly equal integer parts."""
        base, remainder = divmod(n, k)
        return [base + (1 if i < remainder else 0) for i in range(k)]
