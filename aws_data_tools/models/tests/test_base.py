# TODO: Implement these tests using a model that inherits from ModelBase. As-is the
# coverage report doesn't think any of the ModelBase code is executed.
#
# from dataclasses import dataclass, field, InitVar
# import json
# from typing import List
#
# import pytest
# import yaml
#
# from aws_data_tools.models.base import ModelBase
#
#
# @dataclass
# class Model(ModelBase):
#     """A dataclass model for testing ModelBase"""
#     is_test: bool = field(default=True)
#     test_string: str = field(default="This is a test")
#     test_listfield: List[str] = field(default_factory=list)
#     test_initvar: InitVar[str] = field(default="hello")
#
#     @property
#     def expected_dict(self):
#         return {
#             "is_test": True,
#             "test_string": "This is a test",
#             "test_listfield": ["foo", "bar", "baz"],
#         }
#
#     @property
#     def expected_listfield(self):
#         return self.expected_dict["test_listfield"]
#
#     @property
#     def expected_dynamodb(self):
#         return {
#             "is_test": {"BOOL": True},
#             "test_string": {"S": "This is a test"},
#             "test_listfield": {"L": [{"S": "foo"}, {"S": "bar"}, {"S": "baz"}]},
#         }
#
#     @property
#     def expected_json(self):
#         return json.dumps(self.expected_dict)
#
#     @property
#     def expected_yaml(self):
#         return yaml.dump(self.expected_dict)
#
#     def __post_init__(self, test_listfield):
#         self.test_listfield = ["foo", "bar", "baz"]
#
#
# class TestModelBase:
#     """Test the ModelBase class"""
#
#     @pytest.fixture()
#     def model(self):
#         return Model()
#
#     @pytest.mark.parametrize("field_name", [None, "test_listfield", "badfield"])
#     def test_to_dict(self, model, field_name):
#         """Test serializing the model to a dict"""
#         if field_name is not None:
#             if field_name == "test_listfield":
#                 assert model.to_dict(
#                   field_name=field_name
#                 ) == model.expected_listfield
#             elif field_name == "badfield":
#                 with pytest.raises(Exception):
#                     model.to_dict(field_name=field_name)
#         else:
#             assert model.to_dict() == model.expected_dict
#
#     def test_to_dynamodb(self, model):
#         """Test serializing the model to a DynamoDB Item dict"""
#         assert True is True
#         assert model.to_dynamodb() == model.expected_dynamodb
#
#     def test_to_json(self, model):
#         """Test serializing the model to JSON"""
#         assert model.to_json() == model.expected_json
#
#     def test_to_yaml(self, model):
#         """Test serializing the model to YAML"""
#         assert model.to_yaml() == model.expected_yaml
