"""
Action parsing utilities.

Parses model natural language responses into structured GraphAction objects.
"""

import re
from typing import Optional, Tuple
from vigil.actions.schemas import GraphAction, ActionType


def parse_action(response: str) -> Optional[GraphAction]:
    """
    Parse a model response into a GraphAction.

    Supports multiple formats:
    - "expand:node_id"
    - "expand node_id"
    - "inspect:node_id"
    - "submit"
    - "backtrack"
    - Natural language with keywords

    Args:
        response: Model's natural language response

    Returns:
        GraphAction if parsing succeeds, None otherwise
    """
    if not response:
        return None

    response_lower = response.lower().strip()

    # Check for submit action
    if "submit" in response_lower or "answer" in response_lower:
        # Try to extract confidence if present
        confidence = extract_confidence(response)
        return GraphAction(
            action_type=ActionType.SUBMIT,
            confidence=confidence
        )

    # Check for backtrack
    if "backtrack" in response_lower or "back" in response_lower:
        return GraphAction(action_type=ActionType.BACKTRACK)

    # Check for expand action with colon format
    expand_match = re.search(r'expand[:\s]*([a-zA-Z0-9_]+)', response_lower)
    if expand_match:
        target = expand_match.group(1)
        # Try to extract relation type if present
        relation_match = re.search(r'(?:via|through|by)\s+([a-zA-Z_]+)', response_lower)
        relation = relation_match.group(1) if relation_match else None
        confidence = extract_confidence(response)

        return GraphAction(
            action_type=ActionType.EXPAND,
            target_node=target,
            relation_type=relation,
            confidence=confidence
        )

    # Check for inspect action
    inspect_match = re.search(r'inspect[:\s]*([a-zA-Z0-9_]+)?', response_lower)
    if inspect_match:
        target = inspect_match.group(1)
        confidence = extract_confidence(response)
        return GraphAction(
            action_type=ActionType.INSPECT,
            target_node=target,
            confidence=confidence
        )

    # Try to extract as structured action (JSON-like)
    structured = parse_structured_action(response)
    if structured:
        return structured

    return None


def parse_action_from_response(
    response: str,
    default_action: str = "submit"
) -> Optional[GraphAction]:
    """
    Parse action with fallback to default.

    More robust version that always returns a valid action or None.

    Args:
        response: Model response
        default_action: Default action type if parsing fails

    Returns:
        GraphAction or None
    """
    action = parse_action(response)
    if action and action.is_valid():
        return action
    return None


def extract_confidence(text: str) -> float:
    """
    Extract confidence value from text.

    Looks for patterns like:
    - "confidence: 0.8"
    - "confidence=0.8"
    - "80% confidence"
    - "0.8"

    Args:
        text: Text to search

    Returns:
        Confidence value between 0.0 and 1.0, or 0.5 if not found
    """
    # Pattern: confidence[:=]\s*([0-1].[0-9]*)
    match = re.search(r'confidence[:=\s]*([0-1]?\.[0-9]+|[01])', text)
    if match:
        return float(match.group(1))

    # Pattern: XX%
    match = re.search(r'(\d+)%', text)
    if match:
        return int(match.group(1)) / 100.0

    return 0.5  # Default confidence


def parse_structured_action(text: str) -> Optional[GraphAction]:
    """
    Try to parse action from structured text (JSON-like).

    Looks for patterns like:
    - action_type: expand
    - target: node_5
    - confidence: 0.8

    Args:
        text: Text to parse

    Returns:
        GraphAction if structured data found, None otherwise
    """
    action_type = None
    target = None
    relation = None
    confidence = None

    # Extract action_type
    type_match = re.search(r'action[_\s]?type[:\s]*([a-zA-Z]+)', text)
    if type_match:
        action_type = ActionType.from_string(type_match.group(1))

    # Extract target
    target_match = re.search(r'target[_\s]?node?[:\s]*([a-zA-Z0-9_]+)', text)
    if target_match:
        target = target_match.group(1)

    # Extract relation
    relation_match = re.search(r'relation[_\s]?type?[:\s]*([a-zA-Z_]+)', text)
    if relation_match:
        relation = relation_match.group(1)

    # Extract confidence
    conf_match = re.search(r'confidence[:\s]*([0-1]?\.?[0-9]*)', text)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
        except ValueError:
            confidence = 0.5

    # Only return if we found action_type
    if action_type:
        return GraphAction(
            action_type=action_type,
            target_node=target,
            relation_type=relation,
            confidence=confidence or 0.5
        )

    return None


def format_action_options(
    available_actions: list,
    current_node: str,
    budget: int
) -> str:
    """
    Format available actions as a prompt for the model.

    Args:
        available_actions: List of (action_type, target, relation) tuples
        current_node: Current node ID
        budget: Remaining budget

    Returns:
        Formatted action menu string
    """
    lines = [
        f"Current node: {current_node}",
        f"Budget remaining: {budget} actions",
        "",
        "Available actions:",
        "  - expand:<node_id> [via:<relation>] - Move to a connected node",
        "  - inspect:<node_id> - Examine a node's features",
        "  - backtrack - Return to previous node",
        "  - submit - Submit your final answer",
        "",
        "Your action:"
    ]

    return "\n".join(lines)
