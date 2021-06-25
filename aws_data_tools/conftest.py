import os
from typing import Dict, List

import pytest
from moto import mock_organizations

from aws_data_tools.client import APIClient
from aws_data_tools.models.organizations import OrganizationDataBuilder


@pytest.fixture(scope="session")
def apiclient_client_kwargs():
    return dict(endpoint_url="http://localhost:5000")


@pytest.fixture(scope="session")
def apiclient_session_kwargs():
    return dict(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        aws_session_token="testing",
        region_name="us-east-1",
    )


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="session")
@mock_organizations
def apiclient(
    apiclient_client_kwargs,
    apiclient_session_kwargs,
    aws_credentials,
):
    """An APIClient instance with a mocked Organizations client"""
    return APIClient(
        "organizations",
        client_kwargs=apiclient_client_kwargs,
        session_kwargs=apiclient_session_kwargs,
    )


def paths_to_tree(paths: List[str]) -> Dict[str, Dict[str, str]]:
    """Convert a list of paths into a tree"""
    if paths is None:
        paths = []
    path_tree = {}
    # {
    #   "/GrumpySysadmins": {
    #     "name": "GrumpySysadmins",
    #     "parent_path": "/"
    #   }
    #   "/GrumpySysadmins/Services": {
    #     "name": "Services",
    #     "parent_path": "/GrumpySysadmins"
    #   }
    # }
    for path in paths:
        elements = path.split("/")
        path_name = elements[-1]
        parent_path = str.format("/%s", str.join("/", elements[:-1]))
        if path_tree[parent_path]["children"] is None:
            path_tree[parent_path]["children"] = []
        path_tree[parent_path]["children"].append(path_name)
        path_tree[path] = {
            "depth": len(elements),
            "name": path_name,
            "parent_path": parent_path,
        }
    return path_tree


def pathfile_to_tree(filepath: str) -> Dict[str, Dict[str, str]]:
    """Read a file that's a list of paths and generate a tree"""
    paths = None
    with open(filepath, "rb") as f:
        paths = f.readlines()
    return paths_to_tree(paths)


@pytest.fixture(scope="session")
def ou_paths():
    """A tree of OUs to create"""
    return pathfile_to_tree("ou_paths.txt")


@pytest.fixture(scope="session")
def account_paths():
    """A tree of accounts to create"""
    return pathfile_to_tree("account_paths.txt")


@pytest.fixture(scope="session")
def organization_data_builder(apiclient, aws_credentials):
    """Instance of an OrganizationDataBuilder with mocked Organizations APIClient"""
    return OrganizationDataBuilder(client=apiclient)
