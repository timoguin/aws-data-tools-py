"""
Dataclass models for working with AWS Organizations APIs
"""

from dataclasses import dataclass, field
from typing import Dict, List

from .base import ModelBase


@dataclass
class ParChild(ModelBase):
    """A parent or child representation for a node"""

    id: str
    type: str


@dataclass
class EffectivePolicy(ModelBase):
    """An effective policy applied to a node (root, OU, or account)"""

    last_updated_timestamp: str
    policy_content: str
    target_id: str
    policy_type: str


@dataclass
class PolicySummary(ModelBase):
    """Properties of a policy, minus the policy content"""

    arn: str
    aws_managed: bool
    description: str
    id: str
    name: str
    type: str


@dataclass
class PolicySummaryForTarget(ModelBase):
    """A policy id and type for a policy attached to a target"""

    id: str
    type: str


@dataclass
class PolicyTargetSummary(ModelBase):
    """A summary of a target attached to a policy"""

    arn: str
    name: str
    target_id: str
    type: str


@dataclass
class PolicyTypeSummary(ModelBase):
    """The status of a policy type for an organization or root"""

    status: str
    type: str


@dataclass
class Policy(ModelBase):
    """A policy in an organization"""

    policy_summary: PolicySummary

    # We allow content to be None because ListPolicies doesn't return the content data.
    # Instead you have to DescribePolicie to get the content.
    content: str = field(default=None)

    # Optional properties generally populated after initialization
    tags: Dict[str, str] = field(default=None)
    targets: List[PolicyTargetSummary] = field(default=None)

    def to_target(self):
        """Return the Policy as a PolicySummaryForTarget object"""
        return PolicySummaryForTarget(
            id=self.policy_summary.id, type=self.policy_summary.type
        )


@dataclass
class Root(ModelBase):
    """The root in an organization"""

    arn: str
    id: str
    name: str
    policy_types: List[PolicyTypeSummary]

    # Optional properties generally populated after initialization
    children: List[ParChild] = field(default=None)
    policies: List[PolicySummaryForTarget] = field(default=None)

    def to_parchild_dict(self) -> Dict[str, str]:
        """Return the root as a ParChild (parent) dict"""
        return {"id": self.id, "type": "ROOT"}

    def to_parchild(self) -> ParChild:
        """Return the root as a ParChild (parent) object"""
        return ParChild(**self.to_parchild_dict())


@dataclass
class OrganizationalUnit(ModelBase):
    """An organizational unit in an organization"""

    arn: str
    id: str
    name: str

    # Optional properties generally populated after initialization
    children: List[ParChild] = field(default=None)
    parent: ParChild = field(default=None)
    policies: List[PolicySummaryForTarget] = field(default=None)
    tags: Dict[str, str] = field(default=None)

    def to_parchild_dict(self) -> Dict[str, str]:
        """Return the OU as a ParChild (parent) dict"""
        return {"id": self.id, "type": "ORGANIZATIONAL_UNIT"}

    def to_parchild(self) -> ParChild:
        """Return the OU as a ParChild (parent) object"""
        return ParChild(**self.to_parchild_dict())


@dataclass
class Account(ModelBase):
    """An account in an organization"""

    arn: str
    email: str
    id: str
    joined_timestamp: str
    name: str
    joined_method: str
    status: str

    # Optional properties generally populated after initialization
    effective_policies: List[EffectivePolicy] = field(default=None)
    parent: ParChild = field(default=None)
    policies: List[PolicySummaryForTarget] = field(default=None)
    tags: Dict[str, str] = field(default=None)

    def to_parchild_dict(self) -> Dict[str, str]:
        """Return the account as a ParChild (parent) dict"""
        return {"id": self.id, "type": "ACCOUNT"}

    def to_parchild(self) -> ParChild:
        """Return the account as a ParChild (parent) object"""
        return ParChild(**self.to_parchild_dict())


@dataclass
class Organization(ModelBase):
    """Represents an organization and all it's nodes and edges"""

    # We allow all these fields to default to None so we can support initializing an
    # organization object with empty data.
    arn: str = field(default=None)
    available_policy_types: List[PolicyTypeSummary] = field(default=None)
    feature_set: str = field(default=None)
    id: str = field(default=None)
    master_account_arn: str = field(default=None)
    master_account_email: str = field(default=None)
    master_account_id: str = field(default=None)

    # Optional properties generally populated after initialization

    # TODO: These collections should be converted to container data classes to be able
    # to better able to handle operations against specific fields. Currently,
    # serializing/deserializing these collections indepently requires passing the
    # "field_name" kwarg to the `to_dict()` function from ModelBase. It's already
    # getting hacky.
    accounts: List[Account] = field(default=None)
    organizational_units: List[OrganizationalUnit] = field(default=None)
    policies: List[Policy] = field(default=None)
    root: Root = field(default=None)

    # Mappings that represent node -> edge relationships in the organization
    _parent_child_tree: Dict[str, ParChild] = field(
        default=None, init=False, repr=False
    )
    _child_parent_tree: Dict[str, ParChild] = field(
        default=None, init=False, repr=False
    )
    _policy_target_tree: Dict[str, ParChild] = field(
        default=None, init=False, repr=False
    )

    # Mappings that hold a reference to the index of each node in a list
    _account_index_map: Dict[str, int] = field(default=None, init=False, repr=False)
    _ou_index_map: Dict[str, int] = field(default=None, init=False, repr=False)
    _policy_index_map: Dict[str, int] = field(default=None, init=False, repr=False)
