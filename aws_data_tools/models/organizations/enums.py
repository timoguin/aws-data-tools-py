from enum import Enum


class AccountJoinedMethodType(Enum):
    """The methods by which an account can joined an organization"""
    CREATED = 1
    INVITED = 2


class AccountStatusType(Enum):
    """The statuses of an account"""
    ACTIVE = 1
    SUSPENSED = 2


class ChildType(Enum):
    """The types of children in an organization"""
    ACCOUNT = 1
    ORGANIZATIONAL_UNIT = 1


class EffectivePolicyType(Enum):
    """The types of effective policies in an organization"""
    AISERVICES_OPT_OUT_POLICY = 1
    BACKUP_POLICY = 2
    TAG_POLICY = 3


class NodeType(Enum):
    """The types of nodes in an organization"""
    ACCOUNT = 1
    ORGANIZATIONAL_UNIT = 2
    ROOT = 3


class OrganizationFeatureSetType(Enum):
    """The feature sets for an organization"""
    CONSOLIDATED_BILLING = 1
    ALL = 2


class ParentType(Enum):
    """The types of parents in an organization"""
    ORGANIZATIONAL_UNIT = 2
    ROOT = 1


class PolicyStatus(Enum):
    """The status of a policy in an organization"""
    ENABLED = 1
    PENDING_ENABLE = 2
    PENDING_DISABLE = 3


class PolicyType(Enum):
    """The types of policies in an organization"""
    AISERVICES_OPT_OUT_POLICY = 1
    BACKUP_POLICY = 2
    SERVICE_CONTROL_POLICY = 3
    TAG_POLICY = 4


class PolicyTargetType(Enum):
    """The types of targets for a policy in an organization"""
    ACCOUNT = 1
    ORGANIZATIONAL_UNIT = 2
    ROOT = 3
