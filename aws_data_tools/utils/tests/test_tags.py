from moto import mock_organizations
import pytest


from aws_data_tools.client import APIClient
from aws_data_tools.utils.tags import query_tags, tag_list_to_dict


@pytest.fixture()
def tag_list_map():
    return {
        "empty": [],
        "not_empty": [
            {"Key": "Test", "Value": "True"},
            {"Key": "TestTwo", "Value": "yes"},
            {"Key": "TestAgain", "Value": "Here we go again"},
        ],
    }


@pytest.fixture()
def expected_tags_map(request):
    return {
        "empty": {},
        "not_empty": {
            "Test": "True",
            "TestTwo": "yes",
            "TestAgain": "Here we go again",
        },
    }


@pytest.mark.parametrize("tags_type", ["empty", "not_empty"])
@mock_organizations
def test_query_tags(aws_credentials, tag_list_map, expected_tags_map, tags_type):
    client = APIClient("organizations")
    tag_list = tag_list_map[tags_type]
    expected_tags = expected_tags_map[tags_type]
    _ = client.api("create_organization", feature_set="ALL")
    account = client.api(
        "create_account",
        account_name="TestAccount",
        email="example@example.com",
        iam_user_access_to_billing="ALLOW",
        tags=tag_list,
    ).get("create_account_status")
    tags = query_tags(client=client, resource_id=account["account_id"])
    assert tags == expected_tags


@pytest.mark.parametrize("tags_type", ["empty", "not_empty"])
def test_tag_list_to_dict(tag_list_map, expected_tags_map, tags_type):
    tag_list = tag_list_map[tags_type]
    expected_tags = expected_tags_map[tags_type]
    tags = tag_list_to_dict(tag_list)
    assert tags == expected_tags
