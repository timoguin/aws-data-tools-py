"""
Dataclass builders and models for working with AWS Organizations APIs
"""

from datetime import datetime
from dataclasses import dataclass, field, InitVar
import logging
from typing import Any, Union

# Make this an optional dependency and handle import failure
import graphviz

from ..client import APIClient
from ..utils.tags import query_tags
from .base import ModelBase

logging.getLogger(__name__).addHandler(logging.NullHandler())


_SERVICE_NAME = "organizations"
_OU_MAXDEPTH = 5


@dataclass
class ParChild(ModelBase):
    """A parent or child representation for a node"""

    id: str
    type: str

    _valid_types = ["ACCOUNT", "ORGANIZATIONAL_UNIT", "ROOT"]

    def __post_init__(self):
        if self.type not in self._valid_types:
            raise Exception(
                f"Invalid type {self.type}. Valid types: {self._valid_types}."
            )


_VALID_POLICY_TYPES = [
    "AISERVICES_OPT_OUT_POLICY",
    "BACKUP_POLICY",
    "SERVICE_CONTROL_POLICY",
    "TAG_POLICY",
]

# Effective policies
_VALID_EFFECTIVE_POLICY_TYPES = [
    policy_type
    for policy_type in _VALID_POLICY_TYPES
    if policy_type != "SERVICE_CONTROL_POLICY"
]


def get_valid_policy_types(effective: bool = True) -> list[str]:
    if effective:
        return _VALID_EFFECTIVE_POLICY_TYPES
    return _VALID_POLICY_TYPES


def get_valid_effective_policy_types() -> list[str]:
    return get_valid_policy_types(effective=True)


class InvalidEffectivePolicyType(TypeError):
    pass


@dataclass
class EffectivePolicy(ModelBase):
    """An effective policy applied to a node (root, OU, or account)"""

    last_updated_timestamp: str
    policy_content: str
    target_id: str
    policy_type: str

    _valid_policy_types = [
        "AISERVICES_OPT_OUT_POLICY",
        "BACKUP_POLICY",
        "TAG_POLICY",
    ]

    @classmethod
    def __ensure_valid_policy_type(
        cls, p_type: str
    ) -> Union[None, InvalidEffectivePolicyType]:
        """Validate the policy_type field"""
        valid_policy_types = cls._valid_policy_types
        if p_type in valid_policy_types:
            return
        raise InvalidEffectivePolicyType(
            f'Invalid type {p_type}. Valid values are {", ".join(valid_policy_types)}'
        )

    @classmethod
    def fetch_data(
        cls, policy_type: str, target_id: str, client: APIClient, **kwargs
    ) -> dict[str]:
        """Return raw dict from DescribeEffectivePolicy API call"""
        cls.__ensure_valid_policy_type(policy_type)
        data = client.api(
            "describe_effective_policy", policy_type=policy_type, target_id=target_id
        )
        return data.get("effective_policy")

    @classmethod
    def from_api(cls, **kwargs):
        """Return an EffectivePolicy instance from API calls"""
        data = cls.fetch_data(**kwargs)
        return cls.from_dict(data)

    def __post_init__(self):
        self.__ensure_valid_policy_type(self.policy_type)


@dataclass
class EffectivePolicies(ModelBase):
    """A collection of effective policies"""

    policies: list[EffectivePolicy]

    policy_types: list[str]
    target_id: str

    _policy_types: list[str] = field(init=False, repr=False)
    _target_id: InitVar[str] = field(init=False, repr=False)

    @property
    def policy_types(self) -> list[str]:
        return self._policy_types

    @policy_types.setter
    def policy_types(self, policy_types: list[str]) -> None:
        self._policy_types = policy_types

    @property
    def target_id(self) -> str:
        return self._target_id

    @target_id.setter
    def target_id(self, target_id: str) -> None:
        self._target_id = target_id

    def fetch_data(self, policy_types: list[str], target_id: str) -> dict[str, str]:
        policies = []
        for policy_type in self.policy_types:
            data = self.api(
                "describe_effective_policy",
                policy_type=policy_type,
                target_id=self.target_id,
            )
            policies.append(EffectivePolicy.from_dict(data))
        self.policies = policies

    @classmethod
    def from_api(cls, target_id: str, policy_types: list[str] = None):
        raise NotImplementedError
        # if policy_types is None:
        #     policy_types = get_valid_effective_policy_types()
        # effective_policy = cls(policy_types=policy_types, target_id=target_id)

        # klass = cls(policy_types=policy_types)
        # self.fetch()


@dataclass
class PolicySummary(ModelBase):
    """Properties of a policy, minus the policy content"""

    arn: str
    aws_managed: bool
    id: str
    name: str
    type: str

    description: str = field(default=None)

    _valid_types = [
        "AISERVICES_OPT_OUT_POLICY",
        "BACKUP_POLICY",
        "SERVICE_CONTROL_POLICY",
        "TAG_POLICY",
    ]

    def __post_init__(self):
        if self.type not in self._valid_types:
            raise Exception(
                f"Invalid type {self.type}. Valid types: {self._valid_types}."
            )


@dataclass
class PolicySummaryForTarget(ModelBase):
    """A policy id and type for a policy attached to a target"""

    id: str
    type: str


@dataclass
class PolicyTargetSummary(ModelBase):
    """A summary of a target attached to a policy. Returned by ListPoliciesForTarget"""

    arn: str
    name: str
    target_id: str
    type: str

    _valid_types = [
        "ACCOUNT",
        "ORGANIZATIONAL_UNIT",
        "ROOT",
    ]

    def __post_init__(self):
        if self.type not in self._valid_types:
            raise Exception(
                f"Invalid type {self.type}. Valid types: {self._valid_types}."
            )


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
    # Instead you have to DescribePolicy to get the content. Listing policies generally
    # needs to be done first to get the IDs.
    content: str = field(default=None)

    # Optional properties generally populated after initialization
    tags: dict[str, str] = field(default=None)
    targets: list[PolicyTargetSummary] = field(default=None)


@dataclass
class Root(ModelBase):
    """The root in an organization"""

    arn: str
    id: str
    name: str
    policy_types: list[PolicyTypeSummary]

    # Optional properties generally populated after initialization
    children: list[ParChild] = field(default=None)
    policies: list[PolicySummaryForTarget] = field(default=None)

    def to_parchild_dict(self) -> dict[str, str]:
        """Return the root as a ParChild (parent) dict"""
        return {"id": self.id, "type": "ROOT"}

    def to_parchild(self) -> ParChild:
        """Return the root as a ParChild (parent) object"""
        return ParChild.from_dict(self.to_parchild_dict())

    def fetch_tags(self) -> None:
        raise NotImplementedError
        # data = query_tags(client=AddApiClientHere, resource_id=self.id)
        # return data

    def fetch_policies(self) -> None:
        raise NotImplementedError

    def fetch_child_ous(self) -> None:
        raise NotImplementedError

    def fetch_child_accounts(self) -> None:
        raise NotImplementedError

    def fetch_children(self) -> None:
        raise NotImplementedError

    def fetch(self) -> None:
        raise NotImplementedError

    def fetch_all(self) -> None:
        raise NotImplementedError

    @classmethod
    def from_api(cls):
        raise NotImplementedError


@dataclass
class OrganizationalUnit(ModelBase):
    """An organizational unit in an organization"""

    arn: str
    id: str
    name: str

    # Optional properties generally populated after initialization
    children: list[ParChild] = field(default=None)
    parent: ParChild = field(default=None)
    policies: list[PolicySummaryForTarget] = field(default=None)
    tags: dict[str, str] = field(default=None)

    def to_parchild_dict(self) -> dict[str, str]:
        """Return the OU as a ParChild (parent) dict"""
        return {"id": self.id, "type": "ORGANIZATIONAL_UNIT"}

    def to_parchild(self) -> ParChild:
        """Return the OU as a ParChild (parent) object"""
        return ParChild.from_dict(self.to_parchild_dict())


@dataclass
class Account(ModelBase):
    """An account in an organization"""

    arn: str
    email: str
    id: str
    joined_timestamp: datetime
    name: str
    joined_method: str
    status: str

    # Optional properties generally populated after initialization
    effective_policies: list[EffectivePolicy] = field(default=None)
    parent: ParChild = field(default=None)
    policies: list[PolicySummaryForTarget] = field(default=None)
    tags: dict[str, str] = field(default=None)

    def to_parchild_dict(self) -> dict[str, str]:
        """Return the account as a ParChild (parent) dict"""
        return {"id": self.id, "type": "ACCOUNT"}

    def to_parchild(self) -> ParChild:
        """Return the account as a ParChild (parent) object"""
        return ParChild.from_dict(self.to_parchild_dict())


@dataclass
class Organization(ModelBase):
    """Represents an organization and all it's nodes and edges"""

    arn: str
    available_policy_types: list[PolicyTypeSummary]
    feature_set: str
    id: str
    master_account_arn: str
    master_account_email: str
    master_account_id: str

    # TODO: These collections should be converted to container data classes to be able
    # to better able to handle operations against specific fields. Currently,
    # serializing/deserializing these collections indepently requires passing the
    # "field_name" kwarg to the `to_dict()` function from ModelBase. It's already
    # getting hacky.
    accounts: list[Account] = field(default=None)
    organizational_units: list[OrganizationalUnit] = field(default=None)
    policies: list[Policy] = field(default=None)
    root: Root = field(default=None)

    # Mappings that represent node -> edge relationships in the organization
    _parent_child_tree: dict[str, ParChild] = field(
        default=None, init=False, repr=False
    )
    _child_parent_tree: dict[str, ParChild] = field(
        default=None, init=False, repr=False
    )
    _policy_target_tree: dict[str, ParChild] = field(
        default=None, init=False, repr=False
    )

    # Mappings that hold a reference to the index of each node in a list
    _account_index_map: dict[str, int] = field(default=None, init=False, repr=False)
    _ou_index_map: dict[str, int] = field(default=None, init=False, repr=False)
    _policy_index_map: dict[str, int] = field(default=None, init=False, repr=False)

    def fetch_description(self, include_policies: bool = True) -> None:
        org = self.api("describe_organization").get("organization")
        root = self.api("list_roots")[0]
        policies = {}
        if include_policies:
            responses = []
            for policy_type in _VALID_POLICY_TYPES:
                response = self.api("list_policies", filter=policy_type)
                responses.append(response)
            policies["policies"] = [
                {"policy_summary": policy_summary} for policy_summary in responses
            ]
        return Organization.from_dict({**org, **root, **policies})

    @classmethod
    def from_api(include_policies: bool = True):
        """Initialize the organization object from the Organizations API(s)"""
        raise NotImplementedError
        # self.fetch_description()

    def to_dot(self) -> str:
        """Return the organization as a GraphViz DOT diagram"""
        graph = graphviz.Digraph("Organization", filename="organization.dot")
        nodes = []
        nodes.append(self.root)
        nodes.extend(self.organizational_units)
        nodes.extend(self.accounts)
        for node in nodes:
            if getattr(node, "parent", None) is None:
                continue
            shape = None
            if isinstance(node, Root):
                shape = "circle"
            elif isinstance(node, OrganizationalUnit):
                shape = "box"
            elif isinstance(node, Account):
                shape = "ellipse"
            else:
                continue
            graph.node(node.id, label=node.name, shape=shape)
            graph.edge(node.parent.id, node.id)
        return graphviz.unflatten(
            graph.source,
            stagger=10,
            fanout=10,
            chain=10,
        )

    def __post_init__(self) -> None:
        # fetch desc
        pass


@dataclass
class OrganizationDataBuilder(ModelBase):
    """
    Performs read-only operations against the Organizations APIs to construct data
    models of organizations objects. It can populate data for most supported objects:

    - Organization (the org itself)
    - Roots
    - Organizational Units
    - Policies
    - Accounts
    - Effective Policies
    - Tags

    It currently doesn't support getting data about delegated administrators or
    services, handshakes, account creation statuses, or AWS service integrations.

    Provides serialization to dicts and JSON.
    """

    client: APIClient = field(default=None, repr=False)
    # dm: Organization = field(default_factory=Organization.from_api)
    dm: Organization = field(default=None)

    # Used by __post_init__() to determine what data to initialize (default is none)
    init_all: InitVar[bool] = field(default=False)
    init_connection: InitVar[bool] = field(default=True)
    init_organization: InitVar[bool] = field(default=False)
    init_policies: InitVar[bool] = field(default=False)
    init_policy_tags: InitVar[bool] = field(default=False)
    init_ous: InitVar[bool] = field(default=False)
    init_ou_tags: InitVar[bool] = field(default=False)
    init_accounts: InitVar[bool] = field(default=False)
    init_account_tags: InitVar[bool] = field(default=False)
    init_policy_targets: InitVar[bool] = field(default=False)
    init_effective_policies: InitVar[bool] = field(default=False)

    include_account_parents: bool = field(default=False)

    @property
    def enabled_policy_types(self) -> list[str]:
        """Enabled policy types in the organization"""
        # TODO (@timoguin): Follow up on AWS support request seeking clarification on
        # discrepancies between available policy types between Org and Root.
        #
        # Apparently, you can enable policy types on a root that do not reflect in the
        # available policy types for the organization, so DescribeOrganization and
        # ListRoots will answer differently.
        #
        # Pendind clarifications, just return a list of policy types that are enabled
        # on the root.
        if self.dm is None:
            self.fetch_organization()
        return [p.type for p in self.dm.root.policy_types if p.status == "ENABLED"]

    def Connect(self):
        """Initialize an authenticated session"""
        if self.client is None:
            self.client = APIClient(_SERVICE_NAME)

    def api(self, func: str, **kwargs) -> Union[list[dict[str, Any]], dict[str, Any]]:
        """Make arbitrary API calls with the session client"""
        if self.client is None:
            self.Connect()
        return self.client.api(func, **kwargs)

    # @staticmethod
    def fetch_organization(self, include_policies: bool = True) -> None:
        """Initialize the organization object from the Organizations API(s)"""
        # TODO: Was trying to convert this to a static method
        # raise NotImplementedError
        org = self.api("describe_organization").get("organization")
        root = self.api("list_roots")[0]
        policies = {}
        if include_policies:
            responses = []
            for policy_type in _VALID_POLICY_TYPES:
                response = self.api("list_policies", filter=policy_type)
                responses.extend(response)
            policies["policies"] = [
                {"policy_summary": policy_summary} for policy_summary in responses
            ]
        root = {"root": root}
        self.dm = Organization.from_dict({**org, **root, **policies})

    def __e_policies(self) -> list[dict[str, Any]]:
        """Extract organization policy data from ListPolicies and DescribePolicy"""
        ret = []
        for p_type in self.enabled_policy_types:
            policies = []
            p_summaries = self.api("list_policies", filter=p_type)
            for p_summary in p_summaries:
                p_detail = self.api("describe_policy", policy_id=p_summary["id"]).get(
                    "policy"
                )
                policies.append(p_detail)
            ret.extend(policies)
        return ret

    def __t_policies(self) -> list[Policy]:
        """Deserialize list of policy dicts into a list of Policy objects"""
        return [Policy.from_dict(policy) for policy in self.__e_policies()]

    def __l_policies(self) -> None:
        """Load policy objects into dm.policies field"""
        self.dm.policies = self.__t_policies()
        if self.dm._policy_index_map is None:
            self.dm._policy_index_map = {}
        for i, policy in enumerate(self.dm.policies):
            self.dm._policy_index_map[policy.policy_summary.id] = i

    def fetch_policies(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policies()

    def __e_policy_targets_for_id(self, policy_id: str) -> list[PolicyTargetSummary]:
        """Extract a list of policy targets from ListTargetsForPolicy"""
        return self.api("list_targets_for_policy", policy_id=policy_id)

    def __e_policy_targets(self) -> dict[str, list[dict[str, Any]]]:
        """Extract target summary data for all policies"""
        ret = {}
        if self.dm.policies is None:
            self.fetch_policies()
        for policy in self.dm.policies:
            pid = policy.policy_summary.id
            data = self.__e_policy_targets_for_id(policy_id=pid)
            for target in data:
                if ret.get(pid) is None:
                    ret[pid] = []
                ret[pid].append(target)
        return ret

    def __lookup_obj_index(self, obj_type: str, obj_id: str) -> int:
        """Lookup the list index of a type of node in the data model"""
        map_field = None
        if obj_type == "account":
            map_field = self.dm._account_index_map
        elif obj_type == "ou" or obj_type == "organizational_unit":
            map_field = self.dm._ou_index_map
        elif obj_type == "policy":
            map_field = self.dm._policy_index_map
        return map_field[obj_id]

    def __lookup_account_index(self, account_id: str) -> int:
        """Lookup the index of an account object in the dm.accounts field"""
        return self.__lookup_obj_index("account", account_id)

    def __lookup_ou_index(self, ou_id: str) -> int:
        """Lookup the list index of an OU in the dm.organizational_units field"""
        return self.__lookup_obj_index("ou", ou_id)

    def __lookup_policy_index(self, policy_id: str) -> int:
        """Lookup the list index of an account in dm.accounts"""
        return self.__lookup_obj_index("policy", policy_id)

    def __t_policy_targets(
        self,
    ) -> dict[str, dict[str, list[Union[PolicySummaryForTarget, PolicySummary]]]]:
        """
        Deserialize policy targets into a dict of PolicySummaryForTarget and
        PolicyTargetSummary objects
        """
        data = {}
        for pid, p_targets in self.__e_policy_targets().items():
            p_index = self.__lookup_policy_index(pid)
            p_type = self.dm.policies[p_index].policy_summary.type
            for p_target in p_targets:
                p_summary_for_target = PolicySummaryForTarget.from_dict(
                    {"id": pid, "type": p_type}
                )
                if data.get(pid) is None:
                    data[pid] = {
                        "policy_index": p_index,
                        "policy_summary_for_targets": p_summary_for_target,
                        "target_details": [],
                    }
                data[pid]["target_details"].append(
                    PolicyTargetSummary.from_dict(p_target)
                )
        return data

    def __l_policy_targets(self) -> None:
        """Load policy target objects and data into the data model"""
        data = self.__t_policy_targets()
        for pid, d in data.items():
            p_index = d["policy_index"]
            # Update "targets" for Policy objects
            self.dm.policies[p_index].targets = d["target_details"]
            # Update "policies" for target objects
            for target in d["target_details"]:
                if target.type == "ROOT":
                    if self.dm.root.policies is None:
                        self.dm.root.policies = []
                    self.dm.root.policies.append(d["policy_summary_for_targets"])
                elif target.type == "ORGANIZATIONAL_UNIT":
                    ou_index = self.__lookup_ou_index(target.target_id)
                    if self.dm.organizational_units[ou_index].policies is None:
                        self.dm.organizational_units[ou_index].policies = []
                    self.dm.organizational_units[ou_index].policies.append(
                        d["policy_summary_for_targets"]
                    )
                elif target.type == "ACCOUNT":
                    acct_index = self.__lookup_account_index(target.target_id)
                    if self.dm.accounts[acct_index].policies is None:
                        self.dm.accounts[acct_index].policies = []
                    self.dm.accounts[acct_index].policies.append(
                        d["policy_summary_for_targets"]
                    )

    def fetch_policy_targets(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policy_targets()

    def __e_ous_recurse(
        self,
        parents: list[ParChild] = None,
        ous: list[OrganizationalUnit] = None,
        depth: int = 0,
        maxdepth: int = _OU_MAXDEPTH,
    ) -> list[OrganizationalUnit]:
        """Recurse the org tree and return a list of OU dicts"""
        if parents is None:
            parents = [self.dm.root.to_parchild()]
        if self.dm._parent_child_tree is None:
            self.dm._parent_child_tree = {}
        if self.dm._child_parent_tree is None:
            self.dm._child_parent_tree = {}
        if self.dm.organizational_units is None:
            self.dm.organizational_units = []
        if depth == maxdepth or len(parents) == 0:
            return ous
        if ous is None:
            ous = []
        next_parents = []
        for parent in parents:
            if self.dm._parent_child_tree.get(parent.id) is None:
                self.dm._parent_child_tree[parent.id] = []
            ou_results = self.api(
                "list_organizational_units_for_parent", parent_id=parent.id
            )
            for ou_result in ou_results:
                ou = OrganizationalUnit.from_dict(ou_result)
                ou.parent = parent
                ou_to_parchild = ou.to_parchild()
                self.dm._parent_child_tree[parent.id].append(ou_to_parchild)
                self.dm._child_parent_tree[ou.id] = parent
                ous.append(ou)
                next_parents.append(ou_to_parchild)
            acct_results = self.api("list_accounts_for_parent", parent_id=parent.id)
            for acct_result in acct_results:
                account = Account.from_dict(acct_result)
                account.parent = parent
                self.dm._parent_child_tree[parent.id].append(account.to_parchild())
                self.dm._child_parent_tree[account.id] = parent
        return self.__e_ous_recurse(parents=next_parents, ous=ous, depth=depth + 1)

    def __e_ous(self) -> list[OrganizationalUnit]:
        """Extract the OU tree recursively, including OUs and child accounts"""
        return self.__e_ous_recurse()

    def __t_ous(self) -> list[OrganizationalUnit]:
        """Transform OU objects by populating child relationships"""
        data = self.__e_ous()
        ous = []
        for ou in data:
            ou.children = self.dm._parent_child_tree[ou.id]
            ous.append(ou)
        return ous

    def __l_ous(self) -> None:
        """Load deserialized org tree into data models (root and OUs)"""
        ous = self.__t_ous()
        self.dm.root.children = self.dm._parent_child_tree[self.dm.root.id]
        self.dm.organizational_units = ous
        if self.dm._ou_index_map is None:
            self.dm._ou_index_map = {}
        for i, ou in enumerate(self.dm.organizational_units):
            self.dm._ou_index_map[ou.id] = i

    def fetch_ous(self) -> None:
        """Recurse the org tree and populate relationship data for nodes"""
        self.__l_ous()

    def __e_accounts(self) -> list[dict[str, Any]]:
        """Extract the list of accounts in the org"""
        return self.api("list_accounts")

    def __t_accounts(self) -> list[Account]:
        """Transform account data into a list of Account objects"""
        return [Account.from_dict(account) for account in self.__e_accounts()]

    def __l_accounts(self, include_parents: bool = False) -> None:
        """Load account objects with parent relationship data"""
        data = self.__t_accounts()
        accounts = []
        for result in data:
            account = result
            if include_parents or self.include_account_parents:
                if self.dm._child_parent_tree is None:
                    self.fetch_ous()
                account.parent = self.dm._child_parent_tree[account.id]
            accounts.append(account)
        self.dm.accounts = accounts
        if self.dm._account_index_map is None:
            self.dm._account_index_map = {}
        for i, account in enumerate(self.dm.accounts):
            self.dm._account_index_map[account.id] = i

    def fetch_accounts(self, **kwargs) -> None:
        """Initialize the list of Account objects in the organization"""
        self.__l_accounts(**kwargs)

    def __e_effective_policies_for_target(
        self, target_id: str
    ) -> list[EffectivePolicy]:
        """Extract a list of effective policies for a target node"""
        effective_policies = []
        for p_type in self.enabled_policy_types:
            # SCPs aren't supported for effective policies
            if p_type == "SERVICE_CONTROL_POLICY":
                continue
            data = self.api(
                "describe_effective_policy", policy_type=p_type, target_id=target_id
            )
            effective_policies.append(data)
        return effective_policies

    def __e_effective_policies(
        self, account_ids: list[str] = None
    ) -> dict[int, list[dict[str, Any]]]:
        """Extract the effective policies for accounts or a list of account IDs"""
        ret = {}
        if self.dm.accounts is None:
            self.fetch_accounts()
        if account_ids is None:
            account_ids = [account.id for account in self.dm.accounts]
        for account_id in account_ids:
            ret[account_id] = self.__e_effective_policies_for_target(account_id)
        return ret

    def __t_effective_policies(self, **kwargs) -> dict[int, list[EffectivePolicy]]:
        """Transform effective policy data into a list of EffectivePolicy"""
        return [EffectivePolicy.from_dict(d) for d in self.__e_effective_policies()]

    def __l_effective_policies(self, **kwargs) -> None:
        """Load effective policy objects into the account tree"""
        for acct_id, effective_policies in self.__e_effective_policies().items():
            acct_index = self.__lookup_account_index(acct_id)
            self.dm.accounts[acct_index].effective_policies = effective_policies

    def fetch_effective_policies(self, **kwargs) -> None:
        """Initialize effective policy data for accounts in the org"""
        self.__l_effective_policies(**kwargs)

    def __et_tags(self, resource_ids: list[str]) -> dict[str, dict[str, str]]:
        """Extract and transform tags for a list of resource IDs"""
        ret = {}
        for resource_id in resource_ids:
            ret[resource_id] = query_tags(self.client, resource_id)
        return ret

    def __l_account_tags(self, account_ids: list[str] = None, **kwargs) -> None:
        """Load tags for accounts in the organization"""
        if self.dm.accounts is None:
            self.fetch_accounts()
        if account_ids is None:
            account_ids = [account.id for account in self.dm.accounts]
        data = self.__et_tags(resource_ids=account_ids)
        for acct_id, tags in data.items():
            acct_index = self.__lookup_account_index(acct_id)
            self.dm.accounts[acct_index].tags = tags

    def fetch_account_tags(self, **kwargs) -> None:
        """Initialize tags for accounts in the organization"""
        self.__l_account_tags(**kwargs)

    def __l_ou_tags(self, ou_ids: list[str] = None) -> None:
        """Load tags for OUs in the organization"""
        if self.dm.organizational_units is None:
            self.fetch_organizational_units()
        if ou_ids is None:
            ou_ids = [ou.id for ou in self.dm.organizational_units]
        data = self.__et_tags(resource_ids=ou_ids)
        for ou_id, tags in data.items():
            ou_index = self.__lookup_ou_index(ou_id)
            self.dm.organizational_units[ou_index].tags = tags

    def fetch_ou_tags(self, **kwargs) -> None:
        """Initialize tags for OUs in the organization"""
        self.__l_ou_tags(**kwargs)

    def __l_root_tags(self) -> None:
        """Load tags for the organization root"""
        data = self.__et_tags(resource_ids=[self.dm.root.id])
        self.dm.root.tags = data[self.dm.root.id]

    @property
    def is_initialized(self) -> bool:
        if self.dm is None:
            return False
        return True

    def fetch_root_tags(self) -> None:
        """Initialize tags for the organization root"""
        self.__l_root_tags()

    def __l_policy_tags(self, policy_ids: list[str] = None) -> None:
        """Load tags for policies in the organization"""
        if self.dm.policies is None:
            self.fetch_policies()
        if policy_ids is None:
            policy_ids = [
                policy.policy_summary.id
                for policy in self.dm.policies
                if not policy.policy_summary.aws_managed
            ]
        data = self.__et_tags(resource_ids=policy_ids)
        for policy_id, tags in data.items():
            policy_index = self.__lookup_policy_index(policy_id)
            self.dm.policies[policy_index].tags = tags

    def fetch_policy_tags(self, **kwargs) -> None:
        """Initialize tags for policies in the organization"""
        self.__l_policy_tags(**kwargs)

    def fetch_all_tags(self) -> None:
        """Initialize and populate tags for all taggable objects in the organization"""
        self.fetch_root_tags()
        self.fetch_policy_tags()
        self.fetch_ou_tags()
        self.fetch_account_tags()

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Return the data model for the organization as a dictionary"""
        return self.dm.to_dict(**kwargs)

    def to_dynamodb(self, **kwargs) -> dict[str, Any]:
        """Return the data model for the organization as a DynamoDB Item"""
        return self.dm.to_dynamodb(**kwargs)

    def to_json(self, **kwargs) -> str:
        """Return the data model for the organization as a JSON string"""
        return self.dm.to_json(**kwargs)

    def to_yaml(self, **kwargs) -> str:
        """Return the data model for the organization as a YAML string"""
        return self.dm.to_yaml(**kwargs)

    def fetch_all(self) -> None:
        """Initialize all data for nodes and edges in the organization"""
        self.Connect()
        self.fetch_organization()
        self.fetch_root_tags()
        self.fetch_policies()
        self.fetch_policy_tags()
        self.fetch_ous()
        self.fetch_ou_tags()
        self.fetch_accounts()
        self.fetch_account_tags()
        self.fetch_policy_targets()
        self.fetch_effective_policies()

    def __post_init__(
        self,
        init_all: bool,
        init_connection: bool,
        init_organization: bool,
        init_policies: bool,
        init_policy_tags: bool,
        init_ous: bool,
        init_ou_tags: bool,
        init_accounts: bool,
        init_account_tags: bool,
        init_policy_targets: bool,
        init_effective_policies: bool,
    ) -> None:
        """Initialize all or selected data for the organization"""
        if init_all:
            self.fetch_all()
            return
        if init_connection:
            self.Connect()
        if init_organization:
            self.fetch_organization()
        if init_policies:
            self.fetch_policies()
        if init_policy_tags:
            self.fetch_policy_tags()
        if init_ous:
            self.fetch_ous()
        if init_ou_tags:
            self.fetch_ou_tags()
        if init_accounts:
            self.fetch_accounts()
        if init_account_tags:
            self.fetch_account_tags()
        if init_policy_targets:
            self.fetch_policy_targets()
        if init_effective_policies:
            self.fetch_effective_policies()
