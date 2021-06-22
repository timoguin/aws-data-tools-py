"""Utilities for working with DynamoDB"""
from typing import Any, Dict, List

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


def deserialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a DynamoDB Item to a dict"""
    deserializer = TypeDeserializer()
    return {key: deserializer.deserialize(value) for key, value in item.items()}


def deserialize_dynamodb_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert a list of DynamoDB Items to a list of dicts"""
    return [deserialize_dynamodb_item(item) for item in items]


def serialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a dict to a DynamoDB Item"""
    serializer = TypeSerializer()
    return {key: serializer.serialize(value) for key, value in item.items()}


def serialize_dynamodb_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert a list of dicts to a list of DynamoDB Items"""
    return [serialize_dynamodb_item(item) for item in items]


def prepare_dynamodb_batch_put_request(
    table: str,
    items: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Prepare PutRequest input for a DynamoDB BatchWriteItem request"""
    return {
        table: [{"PutRequest": {"Item": item}} for item in items if item is not None]
    }
