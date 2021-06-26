import os
from pathlib import Path
from typing import Union

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


@pytest.fixture(scope="session")
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


def process_ou_paths(paths: list[str]) -> dict[str, dict[str, str]]:
    """Convert a list of OU paths into a tree"""
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
        parent_path = f"{str.join('/', elements[:-1])}"
        if parent_path == "":
            parent_path = "/"
        if path_tree.get(parent_path) is None:
            if parent_path == "/":
                path_tree[parent_path] = {"depth": 0}
            else:
                path_tree[parent_path] = {}
        if path_tree[parent_path].get("children") is None:
            path_tree[parent_path]["children"] = []
        path_tree[parent_path]["children"].append(path_name)
        path_tree[path] = {
            "depth": len(elements) - 1,
            "name": path_name,
            "parent_path": parent_path,
        }
    return path_tree


def process_account_paths(paths: list[str]) -> dict[str, dict[str, str]]:
    """Process a list of account paths in a list of account dicts"""
    if paths is None:
        paths = []
    processed_paths = []
    # [
    #   {
    #     "name": "acct-1",
    #     "path": "/GrumpySysadmins/acct-1",
    #     "parent_path": "/GrumptySysadmins"
    #   },
    #   {
    #     "name": "acct-2",
    #     "path": "/GrumpySysadmins/Services/acct-2",
    #     "parent_path": "/GrumpySysadmins/Services"
    #   }
    # ]
    for path in paths:
        elements = path.split("/")
        parent_path = f"{str.join('/', elements[:-1])}"
        if parent_path == "":
            parent_path = "/"
        processed_paths.append(
            {"name": elements[-1], "path": path, "parent_path": parent_path}
        )
    return processed_paths


def process_pathfile(
    filepath: str, path_type: str
) -> Union[dict[str, dict[str, str]], list[dict[str, str]]]:
    """Read a file that's a list of paths and generate a map or list of maps"""
    paths = None
    with open(filepath, "r") as f:
        paths = [line.rstrip("\n") for line in f.readlines()]
    if path_type == "ou":
        return process_ou_paths(paths)
    elif path_type == "account":
        return process_account_paths(paths)
    else:
        raise Exception(f"Invalid path type {path_type}")


# @pytest.fixture(scope="session")
def ou_paths():
    """A tree of OUs to create"""
    path = Path(__file__).parent / "fixtures" / "ou_paths.txt"
    return process_pathfile(path.absolute(), path_type="ou")


# @pytest.fixture(scope="session")
def account_paths():
    """A list of accounts to create with populated parent data"""
    path = Path(__file__).parent / "fixtures" / "account_paths.txt"
    return process_pathfile(path.absolute(), path_type="account")


@pytest.fixture(scope="session")
def organization_data_builder(apiclient, aws_credentials):
    """Instance of an OrganizationDataBuilder with mocked Organizations APIClient"""
    return OrganizationDataBuilder(client=apiclient)
