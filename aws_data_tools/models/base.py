"""
Base classes for data models
"""

from dataclasses import asdict, dataclass
from json import dumps as json_dumps
from typing import Any, Dict, List, Union

from yaml import dump as yaml_dump

from ..utils import serialize_dynamodb_item, serialize_dynamodb_items


@dataclass
class ModelBase:
    """Base class for all models with helpers for serialization"""

    def to_dict(
        self, field_name: str = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Serialize the dataclass instance to a dict, or serialize a single field. If the
        field is a collection, it is returned as such. If the field is a simple type,
        it is returned as a k/v dict.
        """
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        if field_name is not None:
            if field_name in data.keys():
                if type(data[field_name]) in [dict, list]:
                    return data[field_name]
                return {field_name: data[field_name]}
            raise Exception(f"Field {field_name} does not exist")
        return data

    def to_dynamodb(self, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Serialize the dataclass or field to a DynamoDB Item or list of Items"""
        data = self.to_dict(**kwargs)
        if isinstance(data, list):
            return serialize_dynamodb_items(items=data)
        return serialize_dynamodb_item(item=data)

    def to_json(self, **kwargs) -> str:
        """Serialize the dataclass instance to JSON"""
        return json_dumps(self.to_dict(**kwargs), default=str)

    def to_yaml(self, **kwargs) -> str:
        """Serialize the dataclass instance to YAML"""
        return yaml_dump(self.to_dict(**kwargs))
