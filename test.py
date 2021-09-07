from moto import mock_organizations

from aws_data_tools.models import (
    Account,
    OrganizationalUnit,
    OrganizationDataBuilder,
)
from aws_data_tools import conftest

ou_paths = conftest.ou_paths()
account_paths = conftest.account_paths()

mock = mock_organizations()
mock.start()

odb = OrganizationDataBuilder()
odb.api("create_organization", feature_set="ALL")
odb.fetch_organization()
odb.fetch_root()


def create_ous(ou_paths: dict[str, dict[str, str]]):
    created = {}
    maxdepth = 5
    for i in range(1, maxdepth):
        tree = {k: v for k, v in ou_paths.items() if v["depth"] == i}
        for k, v in tree.items():
            ou_name = v["name"]
            parent_id = None
            parent_path = v["parent_path"]
            if parent_path == "/":
                parent_id = odb.dm.root.id
            else:
                parent_id = created_ous[parent_path].id
            data = odb.api(
                "create_organizational_unit", name=ou_name, parent_id=parent_id
            ).get("organizational_unit")
            created[k] = OrganizationalUnit(**data)
    return created


created_ous = create_ous(ou_paths)
parent_map = {"/": odb.dm.root.id}
for ou_path, ou in created_ous.items():
    parent_map[ou_path] = ou.id


def create_accounts(account_paths: list[dict[str, str]], parent_map: dict[str, str]):
    created = {}
    for account in account_paths:
        account_name = account["name"]
        email = account["name"] + "@example.com"
        parent_id = parent_map[account["parent_path"]]
        create_account_status = odb.api(
            "create_account",
            account_name=account_name,
            email=email,
        ).get("create_account_status")
        account_id = create_account_status["account_id"]
        move_account = odb.api(
            "move_account",
            account_id=account_id,
            destination_parent_id=parent_id,
            source_parent_id=odb.dm.root.id,
        )
        if move_account["response_metadata"]["http_status_code"] != 200:
            raise Exception(f"Error creating account {account_name}")
        data = odb.api("describe_account", account_id=account_id).get("account")
        created[account["path"]] = Account(**data)
    return created


created_accounts = create_accounts(account_paths, parent_map)

odb.fetch_ous()
odb.fetch_policies()
odb.fetch_accounts()
odb.fetch_policy_targets()
odb.fetch_effective_policies()
odb.fetch_all_tags()

with open("test-organization.yaml", "wb") as f:
    f.write(odb.to_json().encode())

mock.stop()
