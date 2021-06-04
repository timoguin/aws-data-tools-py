from dataclasses import asdict, dataclass, field
from json import dumps as json_dumps
from typing import Any, Dict, List, Optional

from botocore.client import BaseClient
# from marshmallow_dataclass import dataclass
# from marshmallow_enum import EnumField

from ...utils import tag_list_to_dict
from ... import APIClient

from .base import (
    NodeChildren,
    NodeEffectivePolicy,
    NodeParent,
    NodePolicy,
    PolicySummary,
    PolicyTargetSummary,
    PolicyTypeSummary
)

# from .enums import (
#     AccountJoinedMethodType,
#     AccountStatusType,
#     OrganizationFeatureSetType
# )


SERVICE_NAME = 'organizations'
ORGANIZATIONAL_UNIT_MAXDEPTH = 5


@dataclass
class Policy:
    content: str = field(default=None)
    policy_summary: PolicySummary = field(default=None)
    tags: Optional[Dict[str, str]] = field(default=None)
    targets: Optional[List[PolicyTargetSummary]] = field(default=None)


@dataclass
class Root:
    arn: str
    id: str
    name: str
    policy_types: List[PolicyTypeSummary]
    children: Optional[NodeChildren] = field(default=None)
    policies: Optional[List[str]] = field(default=None)


@dataclass
class OrganizationalUnit:
    """An organizational unit in an organization"""
    arn: str
    id: str
    name: str
    children: Optional[NodeChildren] = field(default=None)
    parent: Optional[NodeParent] = field(default=None)
    policies: Optional[List[str]] = field(default=None)
    tags: Optional[Dict[str, str]] = field(default=None)


@dataclass
class Account:
    """An account in an organization"""
    arn: str
    email: str
    id: str
    joined_timestamp: str
    name: str
    joined_method: str # = EnumField(AccountJoinedMethodType)
    status: str # = EnumField(AccountStatusType)
    effective_policies: Optional[List[NodeEffectivePolicy]] = field(default=None)
    parent: Optional[NodeParent] = field(default=None)
    policies: Optional[List[str]] = field(default=None)
    tags: Optional[Dict[str, str]] = field(default=None)


@dataclass
class Organization:
    arn: str = field(default=None)
    available_policy_types: List[PolicyTypeSummary] = field(default=None)
    feature_set: str = field(default=None) # OrganizationFeatureSetType = field(default=None)
    id: str = field(default=None)
    master_account_arn: str = field(default=None)
    master_account_email: str = field(default=None)
    master_account_id: str = field(default=None)
    accounts: Optional[List[Account]] = field(default=None)
    organizational_units: Optional[List[OrganizationalUnit]] = field(default=None)
    policies: Optional[List[Policy]] = field(default=None)
    root: Optional[Root] = field(default=None)
    client: BaseClient = field(default=None, metadata={'load_only': True})

    def query_tags_for_resource(self, resource_id: str) -> Dict[str, str]:
        tags = self.client.api('list_tags_for_resource', resource_id=resource_id)
        if len(tags) == 0:
            return {}
        return tag_list_to_dict(tags)

    def query_effective_policies_for_target(self, target_id: str) -> List[NodeEffectivePolicy]:
        effective_policies = []
        avail_policy_types = [
            p_type.type
            for p_type in self.available_policy_types
            if p_type.type != 'SERVICE_CONTROL_POLICY'
        ]
        for p_type in avail_policy_types:
            data = self.client.api('describe_effective_policy',
                                   policy_type=policy_type,
                                   target_id=target_id)
            for result in data.get('effective_policy'):
                # effective_policy = NodeEffectivePolicy.Schema().load(result)
                effective_policy = NodeEffectivePolicy(**result)
                effective_policies.append(effective_policy)
        return effective_policies

    def query_policies_for_target(self, target_id: str) -> List[NodePolicy]:
        avail_policy_types = [p_type.type for p_type in self.available_policy_types]
        for p_type in avail_policy_types:
            data = self.client.api('list_policies_for_target',
                                   filter=p_type,
                                   target_id=target_id)
        policies = []
        for result in data:
            # policy = PolicySummary.Schema().load(result)
            policy = PolicySummary(**result)
            policies.append(policy)
        return policies

    def query_organizational_units_for_parent(self, parent_id: str) -> List[OrganizationalUnit]:
        # print('...')
        data = self.client.api('list_organizational_units_for_parent', parent_id=parent_id)
        ous = []
        for result in data:
            # print('......')
            # ou = OrganizationalUnit.Schema().load(result)
            ou = OrganizationalUnit(**result)
            ou.tags = self.query_tags_for_resource(resource_id=ou.id)
            ou.policies = self.query_policies_for_target(ou.id)
            ous.append(ou)
            # print('......')
        return ous

    def query_accounts_for_parent(self, parent_id: str):
        # print('...')
        data = self.client.api('list_accounts_for_parent', parent_id=parent_id)
        accounts = []
        # for result in data.get('accounts'):
        for result in data:
            # print('......')
            # account = Account.Schema().load(result)
            account = Account(**result)
            account.tags = self.query_tags_for_resource(resource_id=account.id)
            account.effective_policy = self.query_effective_policies_for_target(account.id)
            account.policies = self.query_policies_for_target(account.id)
            accounts.append(account)
            # print('......')
        return accounts

    def get_description(self) -> None:
        data = self.client.api('describe_organization').get('organization')
        for k, v in data.items():
            # Convert avail policy types to PolicyTypeSummary objects
            if k == 'available_policy_types':
                setattr(self, k, [PolicyTypeSummary(**p) for p in v])
                continue
            setattr(self, k, v)
        return

    def get_root(self) -> None:
        data = self.client.api('list_roots')
        # root = root.Schema().load(data[0])
        root = Root(**data[0])
        root.policies = self.query_policies_for_target(root.id)
        self.root = root
        return

    def recurse_tree(self,
                     parents: List[NodeParent] = None,
                     depth: int = 0,
                     maxdepth: int = ORGANIZATIONAL_UNIT_MAXDEPTH,
                     query_accounts: bool = True) -> None:
        """Recurse the organization tree to get all OUs and accounts"""
        if depth > maxdepth:
            return
        if parents is None:
            # parents = [Root.Schema().load({'id': self.root.id, 'type': 'ROOT'})]
            parents = [NodeParent(**{'id': self.root.id, 'type': 'ROOT'})]
        else:
            if len(parents) == 0:
                return
        # print('...')
        new_parents = []
        for parent in parents:
            ous = self.query_organizational_units_for_parent(parent_id=parent.id)
            for ou in ous:
                ou.parent = parent
                # ou_as_parent = Parent.Schema().load({'id': ou.id, 'type': 'ORGANIZATIONAL_UNIT'})
                ou_as_parent = NodeParent(**{'id': ou.id, 'type': 'ORGANIZATIONAL_UNIT'})
                new_parents.append(ou_as_parent)
                if self.organizational_units is None:
                    self.organizational_units = []
                self.organizational_units.append(ou)
            if query_accounts:
                accounts = self.query_accounts_for_parent(parent_id=parent.id)
                for account in accounts:
                    account.parent = parent
                    if self.accounts is None:
                        self.accounts = []
                    self.accounts.append(account)
        self.recurse_tree(parents=new_parents, depth=depth+1)

    def get_policies(self) -> None:
        """Get policies for the organization, as well as their tags and targets"""
        policies = []
        avail_policy_types = [p_type.type for p_type in self.available_policy_types]
        # print('...')
        for policy_type in avail_policy_types:
            data = self.client.api('list_policies', filter=policy_type)
            for result in data:
                # print('......')
                pid = result.get('id')
                aws_managed = bool(result.get('aws_managed'))
                # We issue an additional describe call to get the policy contents.
                # Since the list call already contains the policy_summary data, we only
                # need to grab the 'content' key from the response.
                desc = self.client.api('describe_policy', policy_id=pid).get('policy')
                content = desc.get('content')
                targets = self.client.api('list_targets_for_policy', policy_id=pid)
                # Only query for tags if it's not an AWS-managed policy
                tags = self.query_tags_for_resource(pid) if not aws_managed else None
                policy_data = {
                    'policy_summary': result,
                    'content': content,
                    'targets': targets,
                    'tags': tags
                }
                policy = Policy(**policy_data)
                if self.policies is None:
                    self.policies = []
                self.policies.append(policy)
                # print('......')
        return

    def get_client(self) -> None:
        self.client = APIClient(SERVICE_NAME)
        return

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def as_json(self) -> str:
        return json_dumps(asdict(self))
    
    def __post_init__(self, **kwargs):
        print('Initializing client')
        self.get_client()
        if self.id is None:
            print('Fetching initial data')
            self.get_description()
        if self.root is None:
            print('Fetching root data')
            self.get_root()
        if self.policies is None:
            print('Fetching policy data')
            self.get_policies()
#         if self.organizational_units is None or self.accounts is None:
#             print('Fetching OU and account data')
#             self.recurse_tree()
