import json
import os
from typing import List, Dict, Any


def load_notes(path: str) -> List[Dict[str, Any]]:
    """
    Loads notes from a JSON file specified by path.
    Returns an empty list if the file does not exist or is empty.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_notes(path: str, notes: List[Dict[str, Any]]) -> None:
    """
    Saves a list of note dictionaries to a JSON file at path.
    Creates parent directories if necessary.
    """
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
