from boto3 import client as boto3_client
from humps import depascalize, pascalize


DEFAULT_PAGINATION_LIMIT = 500


def api(service: str, **kwargs: dict[str, str]):
    """
    Wrapper for a boto3 client that uses the humps library to automatically
    convert API keys from pascal case to snake cake
    """
    service, func = service.split(':')
    client = boto3_client(service)
    kwargs = pascalize(kwargs)
    response = getattr(client, func)(**kwargs)
    depascalized_response = depascalize(response)
    return depascalized_response


def paged_api(service: str,
              key: str,
              page_limit: int = DEFAULT_PAGINATION_LIMIT,
              **kwargs):
    """
    A paginated version of the api function. Takes a key argument that
    is used to determine what to pull from the response, as well as a
    page_limit argument.
    """
    service, func = service.split(':')
    client = boto3_client(service)
    kwargs = pascalize(kwargs)
    paginator = client.get_paginator(func)
    pagination_config = {'MaxItems': page_limit}
    page_iterator = paginator.paginate(PaginationConfig=pagination_config,
                                       **kwargs)
    depascalized_responses = []
    for page in page_iterator:
        depascalized_page = depascalize(page).get(key)
        depascalized_responses.extend(depascalized_page)
    return depascalized_responses


def ugly_api(service: str, **kwargs: dict[str, str]):
    """
    Wrapper for a boto3 client that does NOT use the humps library to
    automatically convert API keys from pascal case to snake cake
    """
    service, func = service.split(':')
    client = boto3_client(service)
    response = getattr(client, func)(**kwargs)
    return response
