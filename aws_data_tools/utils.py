from dataclasses import asdict
from json import dumps as json_dumps
from typing import Dict, List

from . import APIClient


def tag_list_to_dict(tags: List[Dict[str, str]]) -> Dict[str, str]:
    return {tag['key']: tag['value'] for tag in tags}


def query_tags(client: APIClient, resource_id: str) -> Dict[str, str]:
    """Get a dict of tags for a resource"""
    tags = client.api('list_tags_for_resource', resource_id=resource_id)
    if len(tags) == 0:
        return {}
    return tag_list_to_dict(tags)
