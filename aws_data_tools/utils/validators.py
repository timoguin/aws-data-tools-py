import json


def is_valid_json(s: str) -> bool:
    """Check if a string is valid JSON"""
    try:
        json.loads(s)
    except ValueError:
        return False
    return True
