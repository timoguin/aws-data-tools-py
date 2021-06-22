"""
Base classes for data models
"""

from collections.abc import MutableMapping
from dataclasses import asdict, dataclass
import json
from typing import Any, Dict, List, Union

import yaml

from ..utils import serialize_dynamodb_item, serialize_dynamodb_items


@dataclass
class ModelBase:
    """Base class for all models with helpers for serialization"""

    def _flatten_dict(self, d: Dict[str, str], parent_key: str = "", sep: str = "_"):
        """Convert nested dict into a flattened one with key separators"""
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _flatten_dicts(self, data: List[Dict[str, str]]):
        """Flatten an iterable of dicts"""
        items = []
        for item in data:
            if not isinstance(item, dict):
                items.append(item)
            items.append(self._flatten_dict(item))
        return items

    def _conditional_flatten(
        self, data: Union[Dict[str, str], List[Dict[str, str]]], flatten: bool = False
    ) -> Union[Dict[str, str], List[Dict[str, str]]]:
        """Flatten a dict or a list of dicts if flatten is True"""
        if not flatten:
            return data
        if isinstance(data, dict):
            return self._flatten_dict(data)
        elif isinstance(data, list):
            return self._flatten_dicts(data)

    def to_dict(
        self, field_name: str = None, flatten: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:  # pragma: no cover
        """
        Serialize the dataclass instance to a dict, or serialize a single field. If the
        field is a collection, it is returned as such. If the field is a simple type,
        it is returned as a k/v dict.
        """
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        if field_name is not None:
            if field_name in data.keys():
                if isinstance(data[field_name], (dict, list)):
                    return self._conditional_flatten(data[field_name], flatten=flatten)
                return {field_name: data[field_name]}
            raise Exception(f"Field {field_name} does not exist")
        return self._conditional_flatten(data, flatten=flatten)

    def to_dynamodb(
        self, **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:  # pragma: no cover
        """Serialize the dataclass or field to a DynamoDB Item or list of Items"""
        data = self.to_dict(**kwargs)
        if isinstance(data, list):
            return serialize_dynamodb_items(items=data)
        return serialize_dynamodb_item(item=data)

    def to_json(self, **kwargs) -> str:  # pragma: no cover
        """Serialize the dataclass instance to JSON"""
        return json.dumps(self.to_dict(**kwargs), default=str)

    def to_yaml(self, **kwargs) -> str:  # pragma: no cover
        """Serialize the dataclass instance to YAML"""
        return yaml.dump(self.to_dict(**kwargs))
