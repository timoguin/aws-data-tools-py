"""
Utilities for common operations that happen across different services
"""
from typing import Dict, List

from boto3.dynamodb.types import TypeSerializer

from .client import APIClient


def tag_list_to_dict(tags: List[Dict[str, str]]) -> Dict[str, str]:
    """Convert a list of tag objects to a dict"""
    return {tag["key"]: tag["value"] for tag in tags}


def query_tags(client: APIClient, resource_id: str) -> Dict[str, str]:
    """Get a dict of tags for a resource"""
    tags = client.api("list_tags_for_resource", resource_id=resource_id)
    if len(tags) == 0:
        return {}
    return tag_list_to_dict(tags)


def dict_to_dynamodb_item(raw):
    """Convert a dict to a DynamoDB Item"""
    serializer = TypeSerializer()
    return {key: serializer.serialize(value) for key, value in raw.items()}
    # if isinstance(raw, dict):
    #     return {
    #         "M": {
    #             key: dict_to_dynamodb_item(value)
    #             for key, value in raw.items()
    #         }
    #     }
    # elif isinstance(raw, list):
    #     return {
    #         "L": [dict_to_dynamodb_item(value) for value in raw]
    #     }
    # elif isinstance(raw, str):
    #     return {
    #         "S": raw
    #     }
    # elif isinstance(raw, bool):
    #     return {
    #         "BOOL": raw
    #     }
    # elif isinstance(raw, (int, float)):
    #     return {
    #         "N": str(raw)
    #     }
    # elif isinstance(raw, bytes):
    #     return {
    #         "B": raw
    #     }
    # elif raw is None:
    #     return {
    #         "NULL": True
    #     }
