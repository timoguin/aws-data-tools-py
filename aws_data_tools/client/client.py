"""
Module containing classes that abstract interactions with boto3 sessions and clients
"""

from dataclasses import InitVar, dataclass, field
import logging
from typing import Any, Union

from boto3.session import Session
from botocore.client import BaseClient
from humps import depascalize, pascalize

logging.getLogger(__name__).addHandler(logging.NullHandler())


_DEFAULT_PAGINATION_CONFIG = {"MaxItems": 500}


@dataclass
class ApiClient:
    """
    Service client for interacting with named AWS API services. When initialized, it
    establishes a boto3 session and client for the specified service. Loads
    """

    service: str
    client: BaseClient = field(default=None)
    session: Session = field(default=None)

    # Allow customizing the session
    client_kwargs: InitVar[dict[str, Any]] = field(default=None)
    session_kwargs: InitVar[dict[str, Any]] = field(default=None)

    def api(self, func: str, **kwargs) -> Union[dict[str, Any], list[dict[str, Any]]]:
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

    def __post_init__(self, client_kwargs, session_kwargs):  # pragma: no cover
        if client_kwargs is None:
            client_kwargs = {}
        if session_kwargs is None:
            session_kwargs = {}
        if self.session is None:
            self.session = Session(**session_kwargs)
        if self.client is None:
            self.client = self.session.client(self.service, **client_kwargs)


# Support old naming
APIClient = ApiClient
