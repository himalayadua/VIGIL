"""
Serialization utilities for Vigil.

Provides JSON serialization for environment states, profiles, and results.
"""

import json
from typing import Any, Dict, Optional
from pathlib import Path


def to_json(obj: Any, indent: int = 2) -> str:
    """
    Convert object to JSON string.

    Handles dataclasses, dicts, and common types.

    Args:
        obj: Object to serialize
        indent: JSON indentation level

    Returns:
        JSON string
    """
    if hasattr(obj, 'to_dict'):
        data = obj.to_dict()
    elif isinstance(obj, dict):
        data = obj
    else:
        data = vars(obj) if hasattr(obj, '__dict__') else str(obj)

    return json.dumps(data, indent=indent, default=str)


def from_json(json_str: str) -> Dict[str, Any]:
    """
    Parse JSON string to dictionary.

    Args:
        json_str: JSON string

    Returns:
        Parsed dictionary
    """
    return json.loads(json_str)


def save_results(
    results: Dict[str, Any],
    output_path: str,
    indent: int = 2
) -> None:
    """
    Save results to JSON file.

    Args:
        results: Results dictionary
        output_path: Path to output file
        indent: JSON indentation
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(results, f, indent=indent, default=str)


def load_results(input_path: str) -> Dict[str, Any]:
    """
    Load results from JSON file.

    Args:
        input_path: Path to input file

    Returns:
        Results dictionary
    """
    with open(input_path, 'r') as f:
        return json.load(f)
