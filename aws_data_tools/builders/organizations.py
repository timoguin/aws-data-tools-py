from dataclasses import dataclass, field, InitVar
from typing import Any, Dict, List, Union

from botocore.session import Session
from botocore.client import BaseClient

from .. import APIClient
from ..models import ModelBase
from ..utils import tag_list_to_dict, query_tags

from ..models.organizations import (
    Account,
    EffectivePolicy,
    Organization,
    OrganizationalUnit,
    ParChild,
    Policy,
    PolicySummary,
    PolicySummaryForTarget,
    PolicyTargetSummary,
    PolicyTypeSummary,
    Root,
)


_SERVICE_NAME = "organizations"
_OU_MAXDEPTH = 5


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

    client: APIClient = field(default=None, init=False, repr=False)
    dm: Organization = field(default_factory=Organization)

    # Used by __post_init__() to determine what data to initialize (default is none)
    init_all: InitVar[bool] = field(default=False)
    init_connection: InitVar[bool] = field(default=None)
    init_organization: InitVar[bool] = field(default=False)
    init_root: InitVar[bool] = field(default=False)
    init_policies: InitVar[bool] = field(default=False)
    init_policy_tags: InitVar[bool] = field(default=False)
    init_ous: InitVar[bool] = field(default=False)
    init_ou_tags: InitVar[bool] = field(default=False)
    init_accounts: InitVar[bool] = field(default=False)
    init_account_tags: InitVar[bool] = field(default=False)
    init_policy_targets: InitVar[bool] = field(default=False)
    init_effective_policies: InitVar[bool] = field(default=False)

    def Connect(self):
        """Initialize an authenticated session"""
        self.client = APIClient(_SERVICE_NAME)

    def api(self, func: str, **kwargs) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Make arbitrary API calls with the session client"""
        if self.client is None:
            self.Connect()
        return self.client.api(func, **kwargs)

    def __e_organization(self) -> Dict[str, str]:
        """Extract org description data from the DescribeOrganization API"""
        return self.api("describe_organization").get("organization")

    def __t_organization(self) -> Dict[str, Union[str, List[PolicySummary]]]:
        """Deserialize org description data and perform any transformations"""
        data = {}
        for k, v in self.__e_organization().items():
            # Convert avail policy types to PolicyTypeSummary objects
            if k == "available_policy_types":
                data[k] = [PolicyTypeSummary(**pol) for pol in v]
                continue
            data[k] = v
        return data

    def __l_organization(self) -> None:
        """Init the Organization instance on the dm field"""
        self.dm = Organization(**self.__t_organization())

    def init_organization(self) -> None:
        """Initialize the organization object with minimal data"""
        self.__l_organization()

    def __e_roots(self) -> List[Dict[str, Any]]:
        """Extract org roots from the ListRoots API"""
        return self.api("list_roots")

    def __t_roots(self) -> Root:
        """Deserialize and transform org roots data into a single Root object"""
        return [Root(**root) for root in self.__e_roots()][0]

    def __l_roots(self) -> None:
        """Init the Root instance of the dm.root field"""
        self.dm.root = self.__t_roots()

    def init_root(self) -> None:
        """Initialize the organization's root object"""
        if self.dm.id is None:
            self.init_organization()
        self.__l_roots()

    def __e_policies(self) -> List[Dict[str, Any]]:
        """Extract organization policy data from ListPolicies and DescribePolicy"""
        ret = []
        for p in self.dm.available_policy_types:
            policies = []
            breakpoint()
            p_summaries = self.api("list_policies", filter=p.type)
            for p_summary in p_summaries:
                p_detail = self.api("describe_policy", policy_id=p_summary["id"]).get(
                    "policy"
                )
                policies.append(p_detail)
            ret.extend(policies)
        return ret

    def __t_policies(self) -> List[Policy]:
        """Deserialize list of policy dicts into a list of Policy objects"""
        ret = []
        for p in self.__e_policies():
            p_summary = PolicySummary(**p["policy_summary"])
            policy = Policy(policy_summary=p_summary, content=p["content"])
            ret.append(policy)
        return ret

    def __l_policies(self) -> None:
        """Load policy objects into dm.policies field"""
        self.dm.policies = self.__t_policies()
        if self.dm._policy_index_map is None:
            self.dm._policy_index_map = {}
        for i, policy in enumerate(self.dm.policies):
            self.dm._policy_index_map[policy.policy_summary.id] = i

    def init_policies(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policies()

    def __e_policy_targets_for_id(self, policy_id: str) -> List[PolicyTargetSummary]:
        """Extract a list of policy targets from ListTargetsForPolicy"""
        return self.api("list_targets_for_policy", policy_id=policy_id)

    def __e_policy_targets(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract target summary data for all policies"""
        ret = {}
        if self.dm.policies is None:
            self.init_policies()
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
    ) -> Dict[str, Dict[str, List[Union[PolicySummaryForTarget, PolicySummary]]]]:
        """
        Deserialize policy targets into a dict of PolicySummaryForTarget and
        PolicyTargetSummary objects
        """
        data = {}
        for pid, p_targets in self.__e_policy_targets().items():
            p_index = self.__lookup_policy_index(pid)
            p_type = self.dm.policies[p_index].policy_summary.type
            for p_target in p_targets:
                p_summary_for_target = PolicySummaryForTarget(id=pid, type=p_type)
                if data.get(pid) is None:
                    data[pid] = {
                        "policy_index": p_index,
                        "policy_summary_for_targets": p_summary_for_target,
                        "target_details": [],
                    }
                data[pid]["target_details"].append(PolicyTargetSummary(**p_target))
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

    def init_policy_targets(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policy_targets()

    def __e_ous_recurse(
        self,
        parents: List[ParChild] = None,
        ous: List[OrganizationalUnit] = None,
        depth: int = 0,
        maxdepth: int = _OU_MAXDEPTH,
    ) -> List[OrganizationalUnit]:
        """Recurse the org tree and return a list of OU dicts"""
        if parents is None:
            if self.dm.root is None:
                self.init_root()
            parents = [self.dm.root.as_parchild()]
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
                ou = OrganizationalUnit(parent=parent, **ou_result)
                ou_as_parchild = ou.as_parchild()
                self.dm._parent_child_tree[parent.id].append(ou_as_parchild)
                self.dm._child_parent_tree[ou.id] = parent
                ous.append(ou)
                next_parents.append(ou_as_parchild)
            acct_results = self.api("list_accounts_for_parent", parent_id=parent.id)
            for acct_result in acct_results:
                account = Account(parent=parent, **acct_result)
                self.dm._parent_child_tree[parent.id].append(account.as_parchild())
                self.dm._child_parent_tree[account.id] = parent
        return self.__e_ous_recurse(parents=next_parents, ous=ous, depth=depth + 1)

    def __e_ous(self) -> List[OrganizationalUnit]:
        """Extract the OU tree recursively, including OUs and child accounts"""
        return self.__e_ous_recurse()

    def __t_ous(self) -> List[OrganizationalUnit]:
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

    def init_ous(self) -> None:
        """Recurse the org tree and populate relationship data for nodes"""
        self.__l_ous()

    def __e_accounts(self) -> List[Dict[str, Any]]:
        """Extract the list of accounts in the org"""
        return self.api("list_accounts")

    def __t_accounts(self) -> List[Account]:
        """Transform account data into a list of Account objects"""
        return [Account(**account) for account in self.__e_accounts()]

    def __l_accounts(self) -> None:
        """Load account objects with parent relationship data"""
        data = self.__t_accounts()
        accounts = []
        for result in data:
            account = result
            account.parent = self.dm._child_parent_tree[account.id]
            accounts.append(account)
        self.dm.accounts = accounts
        if self.dm._account_index_map is None:
            self.dm._account_index_map = {}
        for i, account in enumerate(self.dm.accounts):
            self.dm._account_index_map[account.id] = i

    def init_accounts(self) -> None:
        """Initialize the list of Account objects in the organization"""
        self.__l_accounts()

    def __e_effective_policies_for_target(
        self, target_id: str
    ) -> List[EffectivePolicy]:
        """Extract a list of effective policies for a target node"""
        effective_policies = []
        for p in self.dm.available_policy_types:
            # SCPs aren't supported for effective policies
            if p.type == "SERVICE_CONTROL_POLICY":
                continue
            data = self.api(
                "describe_effective_policy", policy_type=p.type, target_id=target_id
            )
            effective_policies.append(data)
        return effective_policies

    def __e_effective_policies(self) -> Dict[int, List[Dict[str, Any]]]:
        """Extract the effective policies for accounts"""
        ret = {}
        if self.dm.accounts is None:
            self.init_accounts()
        for account in self.dm.accounts:
            ret[account.id] = self.__e_effective_policies_for_target(account.id)
        return ret

    def __t_effective_policies(self) -> Dict[int, List[EffectivePolicy]]:
        """Transform effective policy data into a list of EffectivePolicy"""
        return [EffectivePolicy(**d) for d in self.__e_effective_policies()]

    def __l_effective_policies(self) -> None:
        """Load effective policy objects into the account tree"""
        for acct_id, effective_policies in self.__e_effective_policies().items():
            acct_index = self.__lookup_account_index(acct_id)
            self.dm.accounts[acct_index].effective_policies = effective_policies

    def init_effective_policies(self) -> None:
        """Initialize effective policy data for accounts in the org"""
        self.__l_effective_policies()

    def __e_tags_for_resource_ids(
        self, resource_ids: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """Fetch tags for a list of resource IDs (root, OUs, policies, accounts)"""
        ret = {}
        for resource_id in resource_ids:
            ret[resource_id] = query_tags(self.client, resource_id)
        return ret

    def __et_tags(self, obj_type: str) -> Dict[str, Dict[str, str]]:
        """Extract and transform tags for a specific node type"""
        obj_type = obj_type.upper()
        resource_ids = None
        if obj_type == "ROOT" or obj_type == "ROOTS":
            if self.dm.root is None:
                self.init_root()
            resource_ids = [self.dm.root.id]
        elif (
            obj_type == "ORGANIZATIONAL_UNIT"
            or obj_type == "ORGANIZATIONAL_UNITS"
            or obj_type == "OU"
            or obj_type == "OUS"
        ):
            if self.dm.organizational_units is None:
                self.init_ous()
            resource_ids = [ou.id for ou in self.dm.organizational_units]
        elif obj_type == "POLICY" or obj_type == "POLICIES":
            if self.dm.policies is None:
                self.init_policies()
            resource_ids = [
                pol.policy_summary.id
                for pol in self.dm.policies
                if not pol.policy_summary.aws_managed
            ]
        elif obj_type == "ACCOUNT" or obj_type == "ACCOUNTS":
            if self.dm.accounts is None:
                self.init_accounts()
            resource_ids = [acct.id for acct in self.dm.accounts]
        return self.__e_tags_for_resource_ids(resource_ids=resource_ids)

    def __l_account_tags(self) -> None:
        """Load tags for accounts in the organization"""
        for acct_id, tags in self.__et_tags("accounts").items():
            acct_index = self.__lookup_account_index(acct_id)
            self.dm.accounts[acct_index].tags = tags

    def init_account_tags(self) -> None:
        """Initialize tags for accounts in the organization"""
        self.__l_account_tags()

    def __l_ou_tags(self) -> None:
        """Load tags for OUs in the organization"""
        for ou_id, tags in self.__et_tags("ous").items():
            ou_index = self.__lookup_ou_index(ou_id)
            self.dm.organizational_units[ou_index].tags = tags

    def init_ou_tags(self) -> None:
        """Initialize tags for OUs in the organization"""
        self.__l_ou_tags()

    def __l_root_tags(self) -> None:
        """Load tags for the organization root"""
        if self.dm.root is None:
            self.init_root()
        self.dm.root.tags = self.__et_tags("root")[self.dm.root.id]

    def init_root_tags(self) -> None:
        """Initialize tags for the organization root"""
        self.__l_root_tags()

    def __l_policy_tags(self) -> None:
        """Load tags for policies in the organization"""
        if self.dm.policies is None:
            self.init_policies()
        for policy_id, tags in self.__et_tags("policies").items():
            policy_index = self.__lookup_policy_index(policy_id)
            self.dm.policies[policy_index].tags = tags

    def init_policy_tags(self) -> None:
        """Initialize tags for policies in the organization"""
        self.__l_policy_tags()

    def init_all_tags(self) -> None:
        """Initialize and populate tags for all taggable objects in the organization"""
        self.init_root_tags()
        self.init_policy_tags()
        self.init_ou_tags()
        self.init_account_tags()

    def as_dict(self) -> Dict[str, Any]:
        """Return the data model for the organization as a dictionary"""
        return self.dm.as_dict()

    def as_json(self) -> str:
        """Return the data model for the organization as a JSON string"""
        return self.dm.as_json()

    def as_yaml(self) -> str:
        """Return the data model for the organization as a YAML string"""
        return self.dm.as_yaml()

    def init_all(self) -> None:
        """Initialize all data for nodes and edges in the organization"""
        self.Connect()
        self.init_organization()
        self.init_root()
        self.init_root_tags()
        self.init_policies()
        self.init_policy_tags()
        self.init_ous()
        self.init_ou_tags()
        self.init_accounts()
        self.init_account_tags()
        self.init_policy_targets()
        self.init_effective_policies()

    def __post_init__(
        self,
        init_all: bool,
        init_connection: bool,
        init_organization: bool,
        init_root: bool,
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
            self.init_all()
            return
        if init_connection:
            self.Connect()
        if init_organization:
            self.init_organization()
        if init_root:
            self.init_root()
        if init_policies:
            self.init_policies()
        if init_policy_tags:
            self.init_policy_tags()
        if init_ous:
            self.init_ous()
        if init_ou_tags:
            self.init_ou_tags()
        if init_accounts:
            self.init_accounts()
        if init_account_tags:
            self.init_account_tags()
        if init_policy_targets:
            self.init_policy_targets()
        if init_effective_policies:
            self.init_effective_policies()
