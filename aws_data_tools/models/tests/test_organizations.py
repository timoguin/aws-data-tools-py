# flake8: noqa: F401
import pytest


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

    @pytest.fixture()
    def odb(self, aws_credentials, organization_data_builder):
        return organization_data_builder

    @pytest.fixture()
    def org(self, aws_credentials, odb):
        org = Organization(
            **odb.api("create_organization", feature_set="ALL").get("organization"),
        )
        org.available_policy_types = [
            PolicyTypeSummary(**p) for p in org.available_policy_types
        ]
        org.root = Root(**odb.api("list_roots")[0])
        return org

    def test_init(self, odb, org):
        assert True is True

    def test_fetch_organization(self, aws_credentials, odb, org):
        odb.fetch_organization()
        org.root = None
        assert isinstance(odb.dm, Organization)
        assert odb.dm == org

    def test_fetch_root(self, aws_credentials, odb, org):
        odb.fetch_root()
        assert isinstance(odb.dm.root, Root)
        assert odb.dm.root == org.root

    def test_fetch_policies(self, odb):
        assert True is True

    def test_fetch_policy_targets(self, odb):
        assert True is True

    def test_fetch_effective_policies(self, odb):
        assert True is True

    def test_fetch_account_tags(self, odb):
        assert True is True

    def test_fetch_ou_tags(self, odb):
        assert True is True

    def test_fetch_root_tags(self, odb):
        assert True is True

    def test_fetch_policy_tags(self, odb):
        assert True is True

    def test_fetch_all_tags(self, odb):
        assert True is True

    def test_fetch_all(self, odb):
        assert True is True

    def test_to_dot(self, odb):
        assert True is True

    def test_to_json(self, odb):
        assert True is True

    def test_to_yaml(self, odb):
        assert True is True
