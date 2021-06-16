"""
Utilities for common operations that happen across different services
"""
from typing import Any, Dict, List

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

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


def serialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a dict to a DynamoDB Item"""
    serializer = TypeSerializer()
    return {key: serializer.serialize(value) for key, value in item.items()}


def serialize_dynamodb_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert a list of dicts to a list of DynamoDB Items"""
    return [serialize_dynamodb_item(item) for item in items]


def deserialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a DynamoDB Item to a dict"""
    deserializer = TypeDeserializer()
    return {key: deserializer.deserialize(value) for key, value in item.items()}


def deserialize_dynamodb_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert a list of DynamoDB Items to a list of dicts"""
    return [deserialize_dynamodb_item(item) for item in items]
