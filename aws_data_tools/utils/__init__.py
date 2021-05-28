from boto3 import client as boto3_client
from humps import depascalize, pascalize


DEFAULT_PAGINATION_LIMIT = 500


def api(service: str, data_key: str = None, **kwargs):
    """
    Wrapper for a boto3 client that uses the humps library to automatically
    convert API keys from pascal case to snake cake
    """
    service, func = service.split(':')
    client = boto3_client(service)
    kwargs = pascalize(kwargs)
    response = getattr(client, func)(**kwargs)
    depascalized_response = depascalize(response)
    if data_key is not None:
        return depascalized_response.get('data_key')
    return depascalized_response


def paged_api(service: str,
              data_key: str = None,
              data_index: int = None,
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
        if data_key is not None:
            depascalized_page = depascalize(page).get(key)
        else:
            depascalized_page = depascalize(page)
        depascalized_responses.extend(depascalized_page)
    if data_index is not None:
        return depascalized_responses[0]
    return depascalized_responses


@dataclass
class OrganizationSession:
    session: botocore.session.Session
    client: boto3.client
    paginator: botocore.paginate.Paginator
    pagination_config: Dict[str, int] = field(default={'MaxItems': DEFAULT_PAGINATION_LIMIT})

    def __get_page_iterator

    def __init__(self, pagination_config: Dict[str, int] = None, **kwargs):
        self.session = botocore.session.Session()
        self.client = self.session.client('organizations')
        self.paginator = self.client.get_paginator()
        if pagination_config is not None:
            self.pagination_config = pagination_config


def ugly_api(service: str, **kwargs: dict[str, str]):
    """
    Wrapper for a boto3 client that does NOT use the humps library to
    automatically convert API keys from pascal case to snake cake
    """
    service, func = service.split(':')
    client = boto3_client(service)
    response = getattr(client, func)(**kwargs)
    return response
