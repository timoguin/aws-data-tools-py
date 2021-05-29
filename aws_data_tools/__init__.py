from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from boto3.session import Session
from botocore.client import BaseClient
from botocore.paginate import PageIterator, Paginator
from humps import depascalize, pascalize
from python_jsonschema_objects import ObjectBuilder
from python_jsonschema_objects.util import Namespace
from yaml import safe_load as yaml_load


__VERSION__ = '0.1.0-alpha2'


DEFAULT_SCHEMAS_DIR = Path(__file__).parent / '_schemas'
DEFAULT_PAGINATION_CONFIG = {'MaxItems': 500}


@dataclass
class ModelFactory:
    """Generates service models from a schema file"""
    schema_path: Path
    models: Namespace = field(default=None)
    schema: Dict[str, Any] = field(default=None)

    def __load_schema(self):
        with open(self.schema_path) as f:
            self.schema = yaml_load(f)

    def __build_models(self):
        builder = ObjectBuilder(self.schema)
        self.models = builder.build_classes(named_only=True)

    def __post_init__(self):
        self.__load_schema()
        self.__build_models()


@dataclass
class APIClient:
    """
    Service client for interacting with named AWS API services. When initialized, it
    establishes a boto3 session and client for the specified service. Loads
    """
    service: str
    client: BaseClient = field(default=None)
    models: Namespace = field(default=None)
    schema: Dict[str, Any] = field(default=None)
    session: Session = field(default_factory=Session)

    def api(self, func: str, **kwargs):
        """
        Call a named API action by string. All arguments to the action should be passed
        as kwargs. The returned data has keys normalized to snake_case. Similarly, all
        kwargs can be passed in snake_case as well.

        If the API action is one that supports pagination, it is handled automaticaly.
        All paginated responses are fully aggregated and then returned.
        """
        kwargs = pascalize(kwargs)
        paginate = self.client.can_paginate(func)
        if paginate:
            paginator = self.client.get_paginator(func)
            if kwargs.get('PaginationConfig') is None:
                kwargs.update(PaginationConfig=DEFAULT_PAGINATION_CONFIG)
            page_iterator = paginator.paginate(**kwargs)
            responses = []
            for page in page_iterator:
                page = depascalize(page)
                metakeys = ['next_token', 'response_metadata']
                key = [k for k in page.keys() if k not in metakeys][0]
                responses.extend(page.get(key))
            return responses
        else:
            response = getattr(self.client, func)(**kwargs)
            return depascalize(response)

    def __post_init__(self):
        schema_path = DEFAULT_SCHEMAS_DIR / f'{self.service}.yaml'
        model_factory = ModelFactory(schema_path=schema_path)
        self.models = model_factory.models
        self.schema = model_factory.schema
        self.client = self.session.client(self.service)
