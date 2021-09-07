import json
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def is_valid_json(s: str) -> bool:
    """Check if a string is valid JSON"""
    try:
        json.loads(s)
    except ValueError:
        return False
    return True
