from dataclasses import asdict
from json import dumps as json_dumps
from typing import Dict, List

from . import APIClient


def tag_list_to_dict(tags: List[Dict[str, str]]) -> Dict[str, str]:
    tag_dict = {}
    for tag in tags:
        # TODO: Look into why some calls to this function are letting through tag
        # objects with no 'Key' field. For now, dropping them by catching KeyError
        try:
            tag_dict.update({tag['Key']: tag['Value']})
        except KeyError:
            continue
    return tag_dict


def query_tags(self, client: APIClient, resource_id: str) -> Dict[str, str]:
    """Get a dict of tags for a resource"""
    tags = client.api('list_tags_for_resource', resource_id=resource_id)
    if len(tags) == 0:n
        return {}
    return tag_list_to_dict(tags)
