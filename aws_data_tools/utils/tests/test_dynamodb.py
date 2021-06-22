import json
from pathlib import Path

import pytest

from aws_data_tools.utils.dynamodb import (
    deserialize_dynamodb_item,
    deserialize_dynamodb_items,
    prepare_dynamodb_batch_put_request,
    serialize_dynamodb_item,
    serialize_dynamodb_items,
)


FIXTURES_PATH = Path(__file__).parent.parent.parent.absolute() / "fixtures"


@pytest.fixture
def dynamodb_item():
    data = {}
    with open(FIXTURES_PATH / "dynamodb_item.json", "rb") as f:
        data = json.load(f)
    return data


@pytest.fixture
def dynamodb_item_serialized():
    data = {}
    with open(FIXTURES_PATH / "dynamodb_item_serialized.json", "rb") as f:
        data = json.load(f)
    return data


def test_deserialize_dynamodb_item(dynamodb_item, dynamodb_item_serialized):
    data = deserialize_dynamodb_item(dynamodb_item_serialized)
    assert data == dynamodb_item


def test_deserialize_dynamodb_items(dynamodb_item, dynamodb_item_serialized):
    serialized_items = [dynamodb_item_serialized, dynamodb_item_serialized]
    deserialized_items = [dynamodb_item, dynamodb_item]
    data = deserialize_dynamodb_items(serialized_items)
    assert data == deserialized_items


def test_serialize_dynamodb_item(dynamodb_item, dynamodb_item_serialized):
    data = serialize_dynamodb_item(dynamodb_item)
    assert data == dynamodb_item_serialized


def test_serialize_dynamodb_items(dynamodb_item, dynamodb_item_serialized):
    deserialized_items = [dynamodb_item, dynamodb_item]
    serialized_items = [dynamodb_item_serialized, dynamodb_item_serialized]
    data = serialize_dynamodb_items(deserialized_items)
    assert data == serialized_items


def test_prepare_dynamodb_batch_put_request(dynamodb_item_serialized):
    table = "TestTable"
    items = [dynamodb_item_serialized, dynamodb_item_serialized]
    expected = {
        table: [
            {"PutRequest": {"Item": dynamodb_item_serialized}},
            {"PutRequest": {"Item": dynamodb_item_serialized}},
        ]
    }
    data = prepare_dynamodb_batch_put_request(table, items)
    assert data == expected
