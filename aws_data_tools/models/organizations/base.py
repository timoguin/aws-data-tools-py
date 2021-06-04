from dataclasses import dataclass, field
from typing import Dict, List, Optional

# from marshmallow_enum import EnumField
# from marshmallow_dataclass import dataclass

# from .. import ModelBase

# from .enums import (
#     ChildType,
#     ParentType,
#     PolicyStatus,
#     PolicyTargetType,
#     PolicyType
# )


@dataclass
class NodeChild:
    """A child object for a node"""
    id: str
    type: str # ChildType = EnumField(ChildType)


@dataclass
class NodeChildren:
    """The child accounts and OUs for a node"""
    accounts: Optional[List[str]] = field(default=None)
    organizational_units: Optional[List[str]] = field(default=None)

    def add_child(self, child: NodeChild) -> None:
        if child.type == ChildType.ACCOUNT:
            self.accounts.append(child.id)
        elif child.type == ChildType.ORGANIZATIONAL_UNIT:
            self.organizational_units.append(child.id)
        return

    def add_children(self, children: List[NodeChild]) -> None:
        for child in children:
            self.add_child(child)
        return


@dataclass
class NodeParent:
    """The parent object for a node"""
    id: str
    type: str # ParentType = EnumField(ParentType)


@dataclass
class PolicyTypeSummary:
    status: str # PolicyStatus = EnumField(PolicyStatus)
    type: str # PolicyType = EnumField(PolicyType)


@dataclass
class PolicyTypeSummary:
    """The status of a policy type for an organization or root"""
    status: str # PolicyStatus = EnumField(PolicyStatus)
    type: str # PolicyType = EnumField(PolicyType)


@dataclass
class NodePolicy:
    """A policy attached to a node"""
    last_updated_timestamp: str
    policy_content: str
    target_id: str
    policy_type: str # PolicyType = EnumField(PolicyType)


@dataclass
class NodeEffectivePolicy:
    """An effective policy applied to a node (root, OU, or account)"""
    last_updated_timestamp: str
    policy_content: str
    target_id: str
    policy_type: str # PolicyType = EnumField(PolicyType)


@dataclass
class PolicySummary:
    arn: str
    aws_managed: bool
    description: str
    id: str
    name: str
    type: str


@dataclass
class PolicyTargetSummary:
    arn: str
    name: str
    target_id: str
    type: str # PolicyTargetType = EnumField(PolicyTargetType)
