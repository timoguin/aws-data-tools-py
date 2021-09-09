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

from ..client import APIClient
from ..utils.dynamodb import serialize_dynamodb_item, serialize_dynamodb_items

logging.getLogger(__name__).addHandler(logging.NullHandler())


@dataclass
class ModelBase:
    """Base class for all models with helpers for serialization"""

    @property
    def client(self) -> APIClient:
        return self._client

    @client.setter
    def client(self, client: APIClient):
        if not isinstance(client, APIClient):
            raise TypeError(f"Invalid client type: {type(client)}. Must be APIClient")
        self._client = client

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


# @dataclass
# class Edge():
#     """Class that represents edges (node relationships) in a digraph"""
#     _head_id: str
#     _head_type: str
#     _tail_id: str
#     _tail_type: str
#
#
# @dataclass
# class Edges(ModelBase):
#     """Class that represents a collection of edges for a node"""
#     edges: list[Edge]
#     _index: dict[str, int] = field(default_factory=dict)
#
#     @property
#     def index(self) -> dict[str, Edge]:
#         """A map of object IDs to their index in the edges list"""
#         return {edge.id: index for index, edge in enumerate(self.edges)}
#
#     @property
#     def mapping(self) -> dict[str, Edge]:
#         """Output edges as a dict/map of ID -> Edge objects"""
#         return {edge.id: edge for edge in self.edges}
#
#     def add_edge(self, edge: Union[Dict[str, str], Edge]) -> None:
#         """Add an edge by passing either an Edge object or a dict"""
#         if isinstance(edge, Edge):
#             self.edges.append(edge)
#         elif isinstance(edge, dict):
#             self.edges.append(Edge.from_dict(edge))
#         else:
#             raise TypeError(f"Unsupported edge type: {type(edge)}")
#
#     def add_edges(self, edges: List[Union[Dict[str, str], Edge]]) -> None:
#         """Add a list of Edge objects or dicts"""
#         for edge in edges:
#             self.add_edge(edge)
#
# @dataclass
# class Node(ModelBase):
#     """Base class for any node type in an graph"""
#     _node_id: str
#     _node_type: str
#
#     def node_id(self):
#         return self._node_id
#     node_type: str
#
#     _edges: Edges
#
#     @property
#     def edges(self):
#         return self._edges.edges
#
#     def add_edge(self, edge: Union[dict[str, str], Edge]) -> None:
#         """Add an edge to the node via a dict or Edge object"""
#         self._edges.add_edge(edge)
#
#     def delete_edge(self, edge_id: str) -> None:
#         """Delete an edge by ID"""
#         self._edges.delete_edge(edge_id)
