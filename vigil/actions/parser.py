"""
Action parser for the Vigil benchmark.

Converts raw LLM output (string or dict) into a typed VigilAction.
On failure, returns an ActionParseError sentinel — never raises.

The Kaggle SDK passes structured output directly when schema=VigilAction is
used with llm.prompt(). This parser handles the fallback case where the LLM
returns a plain string or malformed JSON.
"""

import json
from typing import Any, Union

from pydantic import TypeAdapter, ValidationError

from vigil.actions.schemas import (
    ActionParseError,
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
    VigilAction,
)

# TypeAdapter lets us validate the discriminated union directly
_adapter: TypeAdapter[VigilAction] = TypeAdapter(
    Union[ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction]
)


def parse_action(raw: Any) -> Union[VigilAction, ActionParseError]:
    """
    Parse raw LLM output into a VigilAction.

    Accepts:
    - A Pydantic model instance (already parsed by SDK schema= parameter)
    - A dict (e.g. from llm.prompt returning structured output as dict)
    - A JSON string
    - A plain string with keyword hints (fallback heuristic)

    Returns:
        A VigilAction subclass on success, ActionParseError on failure.
        Never raises.
    """
    if raw is None:
        return ActionParseError(raw, "Input is None")

    # Already a valid action model — pass through
    if isinstance(raw, (ExploreAction, InspectAction, GetContextAction, SubmitAnswerAction)):
        return raw

    # Dict — validate directly
    if isinstance(raw, dict):
        return _validate_dict(raw)

    # String — try JSON first, then heuristic
    if isinstance(raw, str):
        stripped = raw.strip()
        if stripped.startswith("{"):
            try:
                data = json.loads(stripped)
                return _validate_dict(data)
            except json.JSONDecodeError:
                pass
        # Heuristic fallback for plain-text responses
        return _heuristic_parse(stripped)

    return ActionParseError(raw, f"Unsupported input type: {type(raw).__name__}")


def _validate_dict(data: dict) -> Union[VigilAction, ActionParseError]:
    """Validate a dict against the VigilAction discriminated union."""
    try:
        return _adapter.validate_python(data)
    except ValidationError as e:
        return ActionParseError(data, str(e))


def _heuristic_parse(text: str) -> Union[VigilAction, ActionParseError]:
    """
    Last-resort heuristic parser for plain-text LLM responses.

    Handles patterns like:
      "explore node_5"
      "explore: node_5"
      "inspect n3"
      "get_context"
      "submit_answer: The rule is X | justification: ... | confidence: 0.8"
    """
    lower = text.lower()

    # get_context — no arguments needed
    if lower.startswith("get_context") or lower == "context":
        return GetContextAction(action_type="get_context")

    # explore <node_id>
    if lower.startswith("explore"):
        node_id = _extract_first_token_after(text, "explore")
        if node_id:
            return ExploreAction(action_type="explore", node_id=node_id)
        return ActionParseError(text, "explore requires a node_id")

    # inspect <node_id>
    if lower.startswith("inspect"):
        node_id = _extract_first_token_after(text, "inspect")
        if node_id:
            return InspectAction(action_type="inspect", node_id=node_id)
        return ActionParseError(text, "inspect requires a node_id")

    # submit_answer — try to extract answer, justification, confidence
    if lower.startswith("submit"):
        answer, justification, confidence = _extract_submit_fields(text)
        if answer:
            return SubmitAnswerAction(
                action_type="submit_answer",
                answer=answer,
                justification=justification or "",
                confidence=confidence,
            )
        return ActionParseError(text, "submit_answer requires an answer")

    return ActionParseError(text, f"Could not identify action type in: {text[:80]!r}")


def _extract_first_token_after(text: str, keyword: str) -> str:
    """Extract the first whitespace/colon-separated token after a keyword."""
    import re
    pattern = rf"{re.escape(keyword)}[\s:]+([a-zA-Z0-9_\-]+)"
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m else ""


def _extract_submit_fields(text: str) -> tuple[str, str, float]:
    """
    Extract answer, justification, and confidence from a submit string.

    Tries pipe-separated format first:
      "submit_answer: <answer> | justification: <j> | confidence: 0.8"
    Falls back to treating the whole text (minus keyword) as the answer.
    """
    import re

    # Remove the leading keyword
    body = re.sub(r"^submit[_\s]?answer[\s:]*", "", text, flags=re.IGNORECASE).strip()

    answer = body
    justification = ""
    confidence = 0.5

    # Try to extract confidence
    conf_m = re.search(r"confidence[\s:=]+([0-1]?\.[0-9]+|[01])", body, re.IGNORECASE)
    if conf_m:
        try:
            confidence = float(conf_m.group(1))
        except ValueError:
            pass
        body = body[: conf_m.start()].strip(" |")

    # Try to extract justification
    just_m = re.search(r"justification[\s:]+(.+?)(?:\|confidence|$)", body, re.IGNORECASE | re.DOTALL)
    if just_m:
        justification = just_m.group(1).strip(" |")
        body = body[: just_m.start()].strip(" |")

    # Whatever remains is the answer
    ans_m = re.search(r"(?:answer[\s:]+)?(.+)", body, re.IGNORECASE | re.DOTALL)
    if ans_m:
        answer = ans_m.group(1).strip()

    return answer, justification, confidence
