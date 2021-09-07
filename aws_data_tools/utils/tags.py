import logging

from humps import depascalize

from ..client import APIClient

logging.getLogger(__name__).addHandler(logging.NullHandler())


def tag_list_to_dict(tags: list[dict[str, str]]) -> dict[str, str]:
    """Convert a list of tag objects to a dict"""
    return {tag["key"]: tag["value"] for tag in depascalize(tags)}


def query_tags(client: APIClient, resource_id: str) -> dict[str, str]:
    """Get a dict of tags for a resource"""
    tags = client.api("list_tags_for_resource", resource_id=resource_id)
    if len(tags) == 0:
        return {}
    return tag_list_to_dict(tags)
