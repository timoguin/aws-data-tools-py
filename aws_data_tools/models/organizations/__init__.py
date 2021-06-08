from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ParChild:
    """A parent or child representation for a node"""
    id: str
    type: str


# @dataclass
# class Children:
#     """The child accounts and OUs for a node"""
#     accounts: Optional[List[str]] = field(default=None)
#     organizational_units: Optional[List[str]] = field(default=None)
# 
#     def add_child(self, child: Child) -> None:
#         if child.type == ChildType.ACCOUNT:
#             self.accounts.append(child.id)
#         elif child.type == ChildType.ORGANIZATIONAL_UNIT:
#             self.organizational_units.append(child.id)
#         return
# 
#     def add_children(self, children: List[Child]) -> None:
#         for child in children:
#             self.add_child(child)
#         return
# 
# 
# @dataclass
# class Parent:
#     """The parent object for a node"""
#     id: str
#     type: str


@dataclass
class EffectivePolicy:
    """An effective policy applied to a node (root, OU, or account)"""
    last_updated_timestamp: str
    policy_content: str
    target_id: str
    policy_type: str


@dataclass
class PolicySummary:
    """Properties of a policy, minus the policy content"""
    arn: str
    aws_managed: bool
    description: str
    id: str
    name: str
    type: str


@dataclass
class PolicySummaryForTarget:
    """A policy id and type for a policy attached to a target"""
    id: str
    type: str


@dataclass
class PolicyTargetSummary:
    """A summary of a target attached to a policy"""
    arn: str
    name: str
    target_id: str
    type: str


@dataclass
class PolicyTypeSummary:
    """The status of a policy type for an organization or root"""
    status: str
    type: str


@dataclass
class Policy:
    policy_summary: PolicySummary

    # We allow content to be None because ListPolicies doesn't return the content data.
    # Instead you have to DescribePolicie to get the content.
    content: str = field(default=None)

    # Optional properties generally populated after initialization
    tags: Optional[Dict[str, str]] = field(default=None)
    targets: Optional[List[PolicyTargetSummary]] = field(default=None)

    def as_target(self):
        return PolicySummaryForTarget(id=self.policy_summary.id,
                                      type=self.policy_summary.type)


# @dataclass
# class PolicyForTarget:
#     """A policy attached to a target node"""
#     last_updated_timestamp: str
#     policy_content: str
#     target_id: str
#     policy_type: str


@dataclass
class Root:
    arn: str
    id: str
    name: str
    policy_types: List[PolicyTypeSummary]

    # Optional properties generally populated after initialization
    children: Optional[List[ParChild]] = field(default=None)
    policies: Optional[List[PolicySummaryForTarget]] = field(default=None)

    def as_parchild_dict(self) -> Dict[str, str]:
        return {'id': self.id, 'type': 'ROOT'}

    def as_parchild(self) -> ParChild:
        return ParChild(**self.as_parchild_dict())


@dataclass
class OrganizationalUnit:
    """An organizational unit in an organization"""
    arn: str
    id: str
    name: str

    # Optional properties generally populated after initialization
    children: Optional[List[ParChild]] = field(default=None)
    parent: Optional[ParChild] = field(default=None)
    policies: Optional[List[PolicySummaryForTarget]] = field(default=None)
    tags: Optional[Dict[str, str]] = field(default=None)

    def as_parchild_dict(self) -> Dict[str, str]:
        return {'id': self.id, 'type': 'ORGANIZATIONAL_UNIT'}

    def as_parchild(self) -> ParChild:
        return ParChild(**self.as_parchild_dict())


@dataclass
class Account:
    """An account in an organization"""
    arn: str
    email: str
    id: str
    joined_timestamp: str
    name: str
    joined_method: str
    status: str

    # Optional properties generally populated after initialization
    effective_policies: Optional[List[EffectivePolicy]] = field(default=None)
    parent: Optional[ParChild] = field(default=None)
    policies: Optional[List[PolicySummaryForTarget]] = field(default=None)
    tags: Optional[Dict[str, str]] = field(default=None)

    def as_parchild_dict(self) -> Dict[str, str]:
        return {'id': self.id, 'type': 'ACCOUNT'}

    def as_parchild(self) -> ParChild:
        return ParChild(**self.as_parchild_dict())


@dataclass
class Organization:
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
    accounts: Optional[List[Account]] = field(default=None)
    organizational_units: Optional[List[OrganizationalUnit]] = field(default=None)
    policies: Optional[List[Policy]] = field(default=None)
    root: Optional[Root] = field(default=None)

    # Mappings that represent node -> edge relationships in the organization
    parent_child_tree: Optional[Dict[str, ParChild]] = field(default=None)
    child_parent_tree: Optional[Dict[str, ParChild]] = field(default=None)
    policy_target_tree: Optional[Dict[str, ParChild]] = field(default=None)

    # Mappings that hold a reference to the index of each node in a list
    account_index_map: Optional[Dict[str, int]] = field(default=None)
    ou_index_map: Optional[Dict[str, int]] = field(default=None)
    policy_index_map: Optional[Dict[str, int]] = field(default=None)

#     def get_description(self) -> None:
#         data = self.api('describe_organization').get('organization')
#         for k, v in data.items():
#             # Convert avail policy types to PolicyTypeSummary objects
#             if k == 'available_policy_types':
#                 setattr(self, k, [PolicyTypeSummary(**p) for p in v])
#                 continue
#             setattr(self, k, v)
#         return
# 
#     def get_root(self) -> None:
#         data = self.api('list_roots')
#         # root = root.Schema().load(data[0])
#         root = Root(**data[0])
#         root.policies = self.query_policies_for_target(root.id)
#         self.root = root
#         return
# 
#     def recurse_tree(self,
#                      parents: List[NodeParent] = None,
#                      depth: int = 0,
#                      maxdepth: int = _ORGANIZATIONAL_UNIT_MAXDEPTH,
#                      query_accounts: bool = True) -> None:
#         """Recurse the organization tree to get all OUs and accounts"""
#         if depth > maxdepth:
#             return
#         if parents is None:
#             # parents = [Root.Schema().load({'id': self.root.id, 'type': 'ROOT'})]
#             parents = [NodeParent(**{'id': self.root.id, 'type': 'ROOT'})]
#         else:
#             if len(parents) == 0:
#                 return
#         new_parents = []
#         for parent in parents:
#             ous = self.query_organizational_units_for_parent(parent_id=parent.id)
#             for ou in ous:
#                 ou.parent = parent
#                 # ou_as_parent = Parent.Schema().load({'id': ou.id, 'type': 'ORGANIZATIONAL_UNIT'})
#                 ou_as_parent = NodeParent(**{'id': ou.id, 'type': 'ORGANIZATIONAL_UNIT'})
#                 new_parents.append(ou_as_parent)
#                 if self.organizational_units is None:
#                     self.organizational_units = []
#                 self.organizational_units.append(ou)
#             if query_accounts:
#                 accounts = self.query_accounts_for_parent(parent_id=parent.id)
#                 for account in accounts:
#                     account.parent = parent
#                     if self.accounts is None:
#                         self.accounts = []
#                     self.accounts.append(account)
#         self.recurse_tree(parents=new_parents, depth=depth+1)
# 
#     def get_policies(self) -> None:
#         """Get policies for the organization, as well as their tags and targets"""
#         policies = []
#         avail_policy_types = [p_type.type for p_type in self.available_policy_types]
#         for policy_type in avail_policy_types:
#             data = self.api('list_policies', filter=policy_type)
#             for result in data:
#                 pid = result.get('id')
#                 aws_managed = bool(result.get('aws_managed'))
#                 # We issue an additional describe call to get the policy contents.
#                 # Since the list call already contains the policy_summary data, we only
#                 # need to grab the 'content' key from the response.
#                 desc = self.api('describe_policy', policy_id=pid).get('policy')
#                 content = desc.get('content')
#                 targets = self.api('list_targets_for_policy', policy_id=pid)
#                 # Only query for tags if it's not an AWS-managed policy
#                 tags = self.query_tags_for_resource(pid) if not aws_managed else None
#                 policy_data = {
#                     'policy_summary': result,
#                     'content': content,
#                     'targets': targets,
#                     'tags': tags
#                 }
#                 policy = Policy(**policy_data)
#                 if self.policies is None:
#                     self.policies = []
#                 self.policies.append(policy)
#         return
# 
#     def as_dict(self) -> Dict[str, Any]:
#         return asdict(self)
# 
#     def as_json(self) -> str:
#         return json_dumps(asdict(self))
