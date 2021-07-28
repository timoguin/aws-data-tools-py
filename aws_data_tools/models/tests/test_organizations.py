# flake8: noqa: F401
from typing import Union
from unittest import mock

import graphviz
from humps import depascalize
from moto import mock_organizations
import pytest

from aws_data_tools.conftest import FIXTURES_PATH
from aws_data_tools.client import APIClient
from aws_data_tools.models.organizations import (
    Account,
    EffectivePolicy,
    Organization,
    OrganizationDataBuilder,
    OrganizationalUnit,
    ParChild,
    Policy,
    PolicySummary,
    PolicySummaryForTarget,
    PolicyTargetSummary,
    PolicyTypeSummary,
    Root,
)


class TestParChild:
    """Test the ParChild model"""

    @pytest.mark.parametrize("type_", ["ACCOUNT", "INVALID_TYPE"])
    def test_init(self, type_):
        if type_ == "ACCOUNT":
            parchild = ParChild(id="123456", type=type_)
            assert isinstance(parchild, ParChild)
            assert parchild.to_dict() == {"id": "123456", "type": type_}
        elif type_ == "INVALID_TYPE":
            with pytest.raises(Exception):
                parchild = ParChild(id="123456", type=type_)


class TestPolicy:
    """Test the Policy model"""

    @pytest.fixture
    def policy(self):
        policy_summary = {
            "arn": "arn:aws:us-east-1:organizations:policy/p-asdfjkl",
            "aws_managed": False,
            "description": "Just a test policy summary",
            "id": "p-asdfjkl",
            "name": "TestPolicy",
            "type": "SERVICE_CONTROL_POLICY",
        }
        return Policy(policy_summary=PolicySummary(**policy_summary))

    @property
    def expected_to_target(self, policy):
        return PolicySummaryForTarget(id=policy["id"], type=policy["type"])

    def test_to_target(self, policy):
        assert isinstance(policy, Policy)
        assert isinstance(policy["policy_summary"], PolicySummary)
        pol_to_target = policy.to_target()
        assert isinstance(pol_to_target, PolicySummaryForTarget)
        assert pol_to_target == self.expected_to_target


class TestEffectivePolicy:
    """Test the EffectivePolicy model"""

    @pytest.mark.parametrize("type_", ["SERVICE_CONTROL_POLICY", "TAG_POLICY"])
    def test_init(self, type_):
        p_data = {
            "last_updated_timestamp": "2018-05-14 22:17:25.989000-05:00",
            "policy_content": '{"Statement":[{"Effect":"Allow","Action":["*"],"Resource":["*"]}]}',
            "policy_type": type_,
            "target_id": "123456789012",
        }
        if type_ == "TAG_POLICY":
            effective_policy = EffectivePolicy(**p_data)
            assert isinstance(effective_policy, EffectivePolicy)
        elif type_ == "SERVICE_CONTROL_POLICY":
            with pytest.raises(Exception):
                effective_policy = EffectivePolicy(**p_data)


class TestPolicySummary:
    """Test the PolicySummary model"""

    @pytest.fixture
    def policy_summary_map(self):
        data = {
            "arn": "arn:aws:us-east-1:organizations:policy/p-asdfjkl",
            "aws_managed": False,
            "description": "Just a test policy summary",
            "id": "p-asdfjkl",
            "name": "TestPolicy",
            "type": "SERVICE_CONTROL_POLICY",
        }
        invalid_data = data.copy()
        invalid_data["type"] = "INVALID_TYPE"
        return {
            "valid": data,
            "invalid": invalid_data,
        }

    @pytest.mark.parametrize("type_", ["valid", "invalid"])
    def test_init(self, policy_summary_map, type_):
        if type_ == "valid":
            policy_summary = PolicySummary(**policy_summary_map["valid"])
            assert isinstance(policy_summary, PolicySummary)
        elif type_ == "invalid":
            with pytest.raises(Exception):
                policy_summary = PolicySummary(**policy_summary_map["invalid"])


class TestPolicySummaryForTarget:
    """Test the PolicySummaryForTarget model"""

    def test_init(self):
        assert True is True


class TestPolicyTargetSummary:
    """Test the PolicyTargetSummary model"""

    def test_init(self):
        assert True is True


class TestPolicyTypeSummary:
    """Test the PolicyTypeSummary model"""

    def test_init(self):
        assert True is True


class TestPolicy:
    """Test the Policy model"""

    def test_to_target(self):
        assert True is True


class TestRoot:
    """Test the Root model"""

    def test_to_parchild_dict(self):
        assert True is True

    def test_to_parchild(self):
        assert True is True


class TestOrganizationalUnit:
    """Test the OrganizationalUnit model"""

    def test_to_parchild_dict(self):
        assert True is True

    def test_to_parchild(self):
        assert True is True


class TestAccount:
    """Test the Account model"""

    def test_to_parchild_dict(self):
        assert True is True

    def test_to_parchild(self):
        assert True is True


class TestOrganization:
    """Test the Organization model"""

    def test_init(self):
        assert True is True


class TestOrganizationDataBuilder:
    """Test the OrganizationDataBuilder class"""

    @pytest.fixture(scope="class")
    def client(
        self,
        apiclient_session_kwargs,
        aws_credentials,
    ) -> APIClient:
        """An APIClient instance with a mocked Organizations client"""
        return APIClient(
            "organizations",
            client_kwargs=apiclient_session_kwargs,
            session_kwargs=apiclient_session_kwargs,
        )

    @pytest.fixture(scope="function")
    def builder(self, client):
        return OrganizationDataBuilder(client=client)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def process_pathfile(
        filepath: str, path_type: str
    ) -> Union[dict[str, dict[str, str]], list[dict[str, str]]]:
        """Read a file that's a list of paths and generate a map or list of maps"""
        paths = None
        with open(filepath, "r") as f:
            paths = [line.rstrip("\n") for line in f.readlines()]
        if path_type == "ou":
            return self.process_ou_paths(paths)
        elif path_type == "account":
            return self.process_account_paths(paths)
        else:
            raise Exception(f"Invalid path type {path_type}")

    @pytest.fixture(scope="class")
    def ou_paths(self):
        """A tree of OUs to create"""
        path = FIXTURES_PATH / "ou_paths.txt"
        return self.process_pathfile(path, path_type="ou")

    @pytest.fixture(scope="class")
    def account_paths(self):
        """A list of accounts to create with populated parent path data"""
        path = FIXTURES_PATH / "account_paths.txt"
        return self.process_pathfile(path, path_type="account")

    @staticmethod
    def create_test_organization(aws_credentials, client) -> Organization:
        create_org = client.api("create_organization", feature_set="ALL").get(
            "organization"
        )
        org = Organization.from_dict(create_org)
        list_roots = client.api("list_roots")[0]
        org.root = Root.from_dict(list_roots)
        return org

    @pytest.fixture(scope="class")
    def root(self, organization) -> Root:
        return organization.root

    @pytest.fixture(scope="class")
    @mock_organizations
    def organizational_units(
        self, client, root, ou_paths
    ) -> dict[str, OrganizationalUnit]:
        """Create the test OUs"""
        created_ous = {}
        maxdepth = 5
        for i in range(1, maxdepth):
            tree = {k: v for k, v in ou_paths.items() if v["depth"] == i}
            for k, v in tree.items():
                ou_name = v["name"]
                parent_id = None
                parent_path = v["parent_path"]
                if parent_path == "/":
                    parent_id = root.id
                else:
                    parent_id = created_ous[parent_path].id
                data = client.api(
                    "create_organizational_unit", name=ou_name, parent_id=parent_id
                ).get("organizational_unit")
                created_ous[k] = OrganizationalUnit.from_dict(data)
        return created_ous

    @pytest.fixture(scope="class")
    def account_parent_map(self, organization, organizational_units):
        """Creates a map of parent path to parent id to be used in account creation"""
        data = {"/": organization.root.id}
        for ou_path, ou in organizational_units.items():
            data[ou_path] = ou.id
        return data

    @pytest.fixture(scope="class")
    @mock_organizations
    def accounts(
        self,
        client,
        organization,
        organizational_units,
        account_parent_map,
        account_paths,
    ) -> dict[str, Account]:
        """Create the test accounts"""
        created_accounts = {}
        for account in account_paths:
            account_name = account["name"]
            email = account["name"] + "@example.com"
            parent_id = account_parent_map[account["parent_path"]]
            create_account_status = client.api(
                "create_account",
                account_name=account_name,
                email=email,
            ).get("create_account_status")
            account_id = create_account_status["account_id"]
            move_account = client.api(
                "move_account",
                account_id=account_id,
                destination_parent_id=parent_id,
                source_parent_id=odb.dm.root.id,
            )
            if move_account["response_metadata"]["http_status_code"] != 200:
                raise Exception(f"Error creating account {account_name}")
            data = client.api("describe_account", account_id=account_id).get("account")
            created_accounts[account["path"]] = Account.from_dict(data)
        return created_accounts

    @pytest.fixture(scope="class")
    @mock_organizations
    def policies(self, client, organization):
        """Return policies in the test organization"""
        policies = []
        for p_type in organization.root.policy_types:
            p_type_policies = []
            data = client.api("list_policies", filter=p_type.type)
            for p_summary in data:
                p_desc = self.api("descibe_policy", policy_id=p_summary["id"]).get(
                    "policy"
                )
                p_type_policies.append(Policy.from_data(p_desc))
            policies.extend(p_type_policies)
        return policies

    @mock_organizations
    def test_fetch_organization(self, builder, organization):
        builder.fetch_organization()
        organization.root = None
        assert isinstance(builder.dm, Organization)
        assert builder.dm == organization

    @mock_organizations
    def test_fetch_root(self, builder, root):
        builder.fetch_organization()
        builder.fetch_root()
        assert isinstance(builder.dm.root, Root)
        assert builder.dm.root == root

    @mock_organizations
    def test_fetch_policies(self, builder, policies):
        builder.fetch_organization()
        builder.fetch_root()
        builder.fetch_policies()
        for policy in builder.dm.policies:
            assert isinstance(policy, Policy)
        assert builder.dm.policies == policies

    @mock_organizations
    def test_fetch_policy_targets(
        self,
        builder,
        root,
        organizational_units,
        accounts,
        policies,
    ):
        expected_targets = [root]
        expected_targets.extend(organizational_units)
        expected_targets.extend(accounts)
        expected = {}
        for target in expected_targets:
            target_type = depascalize(type(target))
            expected[target.id] = target_type
        builder.fetch_organization()
        builder.fetch_root()
        builder.fetch_policies()
        # TODO: This test isn't fleshed out. We're not yet creating any policies of our
        # own when seeding the test organization, so the only policy that will exist is
        # the default p-AWSFullAccess policy. We're only grabbing the first element.
        assert builder.dm.policies[0] == policies[0]
        fetched = {}
        for target in builder.dm.policies[0].targets:
            fetched[target.id] = target.type
            assert isinstance(target, PolicyTargetSummary)
        assert fetched == expected

    @mock_organizations
    def test_fetch_ous(self, builder, organizational_units):
        expected = {ou.id: ou for ou in organizational_units.values()}
        builder.fetch_organization()
        builder.fetch_root()
        builder.fetch_ous()
        fetched = {}
        for ou in builder.dm.organizational_units:
            fetched[ou.id] = ou
            assert isinstance(ou, OrganizationalUnit)
        assert fetched == expected

    @mock_organizations
    def test_fetch_ou_tags(self, builder, organizational_units):
        builder.fetch_ous()
        builder.fetch_ou_tags()
        expected = {ou.id: ou.tags for ou in organizational_units.values()}
        fetched = {ou.id: ou.tags for ou in builder.dm.organizational_units}
        assert fetched == expected

    @pytest.mark.parametrize("include_parents", [True, False])
    @mock_organizations
    def test_fetch_accounts(self, builder, accounts, include_parents):
        expected = {}
        if include_parents:
            expected = {account.id: account for account in accounts.values()}
        else:
            for account in accounts.values():
                account_no_parent = account
                account_no_parent.parent = None
                expected[account_no_parent.id] = account_no_parent
        builder.fetch_organization()
        builder.fetch_root()
        builder.fetch_accounts(include_parents=include_parents)
        fetched = {}
        for account in builder.dm.accounts:
            fetched[account.id] = account
            assert isinstance(account, Account)
        assert fetched == expected

    @mock_organizations
    def test_fetch_account_tags(self, builder, accounts):
        builder.fetch_accounts()
        builder.fetch_account_tags()
        expected = {account.id: account.tags for account in accounts.values()}
        fetched = {account.id: account.tags for account in builder.dm.accounts}
        assert fetched == expected

    @mock_organizations
    def test_fetch_effective_policies(self, builder, accounts):
        builder.fetch_accounts(include_parents=False)
        builder.fetch_effective_policies()
        # TODO: Again, since we're not actually creating any policies when seeding the
        # test organization, there shouldn't actually be any effective policies. This
        # test is naive.
        expected = {
            accounts.id: account.effective_policies for account in accounts.values()
        }
        fetched = {
            account.id: account.effective_policies for account in builder.dm.accounts
        }
        assert fetched == expected

    def test_fetch_root_tags(self, odb):
        assert True is True

    def test_fetch_policy_tags(self, odb):
        assert True is True

    def test_fetch_all_tags(self, odb):
        assert True is True

    @mock_organizations
    def test_fetch_all(
        self,
        builder,
        organization,
        root,
        organizational_units,
        policies,
        accounts,
    ):
        builder.fetch_all()
        org = organization
        org.root = root
        org.organizational_units = organizational_units.values()
        org.policies = policies
        org.accounts = accounts.values()
        assert builder.dm == org

    @mock.patch("builtins.open", create=True)
    @mock_organizations
    def test_to_dot(self, builder, organization):
        builder.fetch_all()
        source_str = builder.to_dot()
        source = graphviz.Source(source_str, filename="test.png", format="png")
        output = source.render()
