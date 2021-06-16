"""
Module containing classes that abstract interactions with boto3 sessions and clients
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from boto3.session import Session
from botocore.client import BaseClient
from humps import depascalize, pascalize


_DEFAULT_PAGINATION_CONFIG = {"MaxItems": 500}


@dataclass
class APIClient:
    """
    Service client for interacting with named AWS API services. When initialized, it
    establishes a boto3 session and client for the specified service. Loads
    """

    service: str
    client: BaseClient = field(default=None)
    session: Session = field(default_factory=Session)

    def api(self, func: str, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Call a named API action by string. All arguments to the action should be passed
        as kwargs. The returned data has keys normalized to snake_case. Similarly, all
        kwargs can be passed in snake_case as well.

        If the API action is one that supports pagination, it is handled automaticaly.
        All paginated responses are fully aggregated and then returned.
        """
        kwargs = {pascalize(key): value for key, value in kwargs.items()}
        paginate = self.client.can_paginate(func)
        if paginate:
            paginator = self.client.get_paginator(func)
            if kwargs.get("PaginationConfig") is None:
                kwargs.update(PaginationConfig=_DEFAULT_PAGINATION_CONFIG)
            page_iterator = paginator.paginate(**kwargs)
            responses = []
            for page in page_iterator:
                page = depascalize(page)
                metakeys = ["next_token", "response_metadata"]
                key = [k for k in page.keys() if k not in metakeys][0]
                responses.extend(page.get(key))
            return responses
        # TODO: Fix logging to use structlog globally
        response = getattr(self.client, func)(**kwargs)
        return depascalize(response)

    def __post_init__(self):
        if self.client is None:
            self.client = self.session.client(self.service)
