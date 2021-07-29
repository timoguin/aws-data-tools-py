"""Utilities for working with DynamoDB"""

import json
import logging
from typing import Any

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

logging.getLogger(__name__).addHandler(logging.NullHandler())


def deserialize_dynamodb_item(item: dict[str, Any]) -> dict[str, Any]:
    """Convert a DynamoDB Item to a dict"""
    deserializer = TypeDeserializer()
    return {key: deserializer.deserialize(value) for key, value in item.items()}


def deserialize_dynamodb_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a list of DynamoDB Items to a list of dicts"""
    return [deserialize_dynamodb_item(item) for item in items]


def serialize_dynamodb_item(item: dict[str, Any]) -> dict[str, Any]:
    """Convert a dict to a DynamoDB Item"""
    serializer = TypeSerializer()
    return {key: serializer.serialize(value) for key, value in item.items()}


def serialize_dynamodb_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a list of dicts to a list of DynamoDB Items"""
    return [serialize_dynamodb_item(item) for item in items]


def prepare_dynamodb_batch_put_request(
    table: str,
    items: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Prepare PutRequest input for a DynamoDB BatchWriteItem request"""
    return {
        table: [{"PutRequest": {"Item": item}} for item in items if item is not None]
    }


def is_valid_json(s: str) -> bool:
    """Check if a string is valid JSON"""
    try:
        json.loads(s)
    except ValueError:
        return False
    return True
