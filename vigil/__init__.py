"""
Vigil: Stateful Cognitive Graph Benchmark Framework

A benchmark framework for the Google DeepMind × Kaggle "Measuring AGI" Hackathon.
Vigil creates stateful cognitive graph environments where AI models must explore,
learn, and demonstrate cognitive abilities through their actions.

Tracks supported:
- Learning (Track 1)
- Metacognition (Track 2)
- Attention (Track 3)
- Executive Functions (Track 4)
- Social Cognition (Track 5)
"""

__version__ = "0.1.0"
__author__ = "Vigil Team"

# Import core components for easy access
from vigil.environments.base import CognitiveEnvironment, EnvironmentState
from vigil.graphs.core import CognitiveGraph, GraphNode, GraphEdge
from vigil.scenarios.loader import ScenarioLoader
from vigil.actions.schemas import GraphAction, ActionType
from vigil.scoring.profile import CognitiveProfile

__all__ = [
    "CognitiveEnvironment",
    "EnvironmentState",
    "CognitiveGraph",
    "GraphNode",
    "GraphEdge",
    "ScenarioLoader",
    "GraphAction",
    "ActionType",
    "CognitiveProfile",
]
