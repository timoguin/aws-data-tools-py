"""
Base classes for data models
"""

from dataclasses import asdict, dataclass
import json
import logging
from typing import Any, Union

from dacite import from_dict
from humps import decamelize, depascalize
import yaml

from ..utils.dynamodb import serialize_dynamodb_item, serialize_dynamodb_items

logging.getLogger(__name__).addHandler(logging.NullHandler())


@dataclass
class ModelBase:
    """Base class for all models with helpers for serialization"""

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Initialize the model from a dictionary"""
        return from_dict(data_class=cls, data=decamelize(depascalize(data)))

    def to_dict(
        self, field_name: str = None, flatten: bool = False
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:  # pragma: no cover
        """
        Serialize the dataclass instance to a dict, or serialize a single field. If the
        field is a collection, it is returned as such. If the field is a simple type,
        it is returned as a k/v dict.
        """
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        if field_name is not None:
            if field_name in data.keys():
                if isinstance(data[field_name], (dict, list)):
                    return self.data[field_name]
                return {field_name: data[field_name]}
            raise Exception(f"Field {field_name} does not exist")
        return data

    def to_list(self, **kwargs) -> list[dict[str, Any]]:
        """Serialize the dataclass instance to a list of dicts (alias for to_dict)"""
        data = self.to_dict(**kwargs)
        if not isinstance(data, list):
            raise Exception("Class or field is not a list")
        return data

    def to_dynamodb(
        self, **kwargs
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:  # pragma: no cover
        """Serialize the dataclass or field to a DynamoDB Item or list of Items"""
        data = self.to_dict(**kwargs)
        if isinstance(data, list):
            return serialize_dynamodb_items(items=data)
        return serialize_dynamodb_item(item=data)

    def to_json(self, escape: bool = False, **kwargs) -> str:  # pragma: no cover
        """Serialize the dataclass instance to a JSON string"""
        data = json.dumps(self.to_dict(**kwargs), default=str)
        if escape:
            return data.replace('"', '"').replace("\n", "\\n")
        return data

    @classmethod
    def from_json(cls, s: str, **kwargs) -> Any:  # pragma: no cover
        """Deserialize the JSON string to an instance of the dataclass"""
        # Try to remove any escape characters from the string based on the assumption
        # that it could be an escape characters
        return cls.from_dict(json.loads(s.replace('\\"', '"').replace("\\n", "\n")))

    def to_yaml(self, escape: bool = False, **kwargs) -> str:  # pragma: no cover
        """Serialize the dataclass instance to a YAML string"""
        data = yaml.dump(self.to_dict(**kwargs))
        if escape:
            return data.replace('"', '"').replace("\n", "\\n")
        return data

    @classmethod
    def from_yaml(cls, s: str, **kwargs) -> Any:  # pragma: no cover
        """Deserialize the YAML string to an instance of the dataclass"""
        # Try to remove any escape characters from the string based on the assumption
        # that it could have escape characters
        return cls.from_dict(yaml.safe_load(s.replace('\\"', '"')))
