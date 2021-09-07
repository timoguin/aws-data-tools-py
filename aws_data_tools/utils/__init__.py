"""
Utilities for common operations that happen across different services
"""
# flake8: noqa: F401

from .dynamodb import (
    deserialize_dynamodb_item,
    deserialize_dynamodb_items,
    prepare_dynamodb_batch_put_request,
    serialize_dynamodb_item,
    serialize_dynamodb_items,
)

from .tags import tag_list_to_dict, query_tags
