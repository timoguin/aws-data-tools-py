from dataclasses import asdict, dataclass, field, InitVar
from json import dumps as json_dumps
from typing import Any, ClassVar, Dict, List, Union

from botocore.session import Session
from botocore.client import BaseClient

from .. import APIClient
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


_SERVICE_NAME = 'organizations'
_OU_MAXDEPTH = 5


# def query_effective_policies(client: APIClient,
#                              policy_types: List[str],
#                              target_id: str) -> List[NodeEffectivePolicy]:
#     """Return a summary of effective policies attached to a target"""
#     effective_policies = []
#     for policy_type in policy_types:
#         data = client.api('describe_effective_policy',
#                           policy_type=policy_type,
#                           target_id=target_id)
#         for result in data.get('effective_policy'):
#             effective_policy = NodeEffectivePolicy(**result)
#             effective_policies.append(effective_policy)
#     return effective_policies
# 
# def query_policies(client: APIClient,
#                    policy_types: List[str],
#                    target_id: str) -> List[PolicySummary]:
#     """Return a summary of policies attached to a target"""
#     policies = []
#     for policy_type in policy_types:
#         data = client.api('list_policies_for_target',
#                           filter=policy_type,
#                           target_id=target_id)
#         for result in data:
#             policy = PolicySummary(**result)
#             policies.append(policy)
#     return policies
# 
# def query_organizational_units_for_parent(client: APIClient,
#                                           parent_id: str) -> List[OrganizationalUnit]:
#     """Return a list of OUs belonging to a parent"""
#     data = client.api('list_organizational_units_for_parent', parent_id=parent_id)
#     ous = []
#     for result in data:
#         ou = OrganizationalUnit(**result)
#         ous.append(ou)
#     return ous
# 
# def query_accounts_for_parent(client: APIClient, parent_id: str) -> List[Any]:
#     data = self.api('list_accounts_for_parent', parent_id=parent_id)
#     accounts = []
#     for result in data:
#         account = Account(**result)
#         accounts.append(account)
#     return accounts


@dataclass
class OrganizationDataBuilder:
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
    client: APIClient = field(default=None)
    dm: Organization = field(default_factory=Organization)

    def Connect(self):
        """Initialize an authenticated session"""
        self.client = APIClient(_SERVICE_NAME)

    def api(self, func: str, **kwargs) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Make arbitrary API calls with the session client"""
        return self.client.api(func, **kwargs)

    def __e_organization(self) -> Dict[str, str]:
        """Extract org description data from the DescribeOrganization API"""
        return self.api('describe_organization').get('organization')

    def __t_organization(self) -> Dict[str, Union[str, List[PolicySummary]]]:
        """Deserialize org description data and perform any transformations"""
        data = {}
        for k, v in self.__e_organization().items():
            # Convert avail policy types to PolicyTypeSummary objects
            if k == 'available_policy_types':
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
        return self.api('list_roots')

    def __t_roots(self) -> Root:
        """Deserialize and transform org roots data into a single Root object"""
        return [Root(**root) for root in self.__e_roots()][0]

    def __l_roots(self) -> None:
        """Init the Root instance of the dm.root field"""
        self.dm.root = self.__t_roots()

    def init_root(self) -> None:
        """Initialize the organization's root object"""
        self.__l_roots()

    def __e_policies(self) -> List[Dict[str, Any]]:
        policies = []
        for p in self.dm.available_policy_types:
            policies.extend(self.api('list_policies', filter=p.type))
        return policies

    def __t_policies(self) -> List[Policy]:
        policies = []
        for p in self.__e_policies():
            policy = Policy(policy_summary=PolicySummary(**p))
            policies.append(policy)
        return policies

    def __l_policies(self) -> None:
        self.dm.policies = self.__t_policies()
        if self.dm.policy_index_map is None:
            self.dm.policy_index_map = {}
        for i, policy in enumerate(self.dm.policies):
            self.dm.policy_index_map[policy.policy_summary.id] = i

    def init_policies(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policies()

    def __e_policy_targets_for_id(self, policy_id: str) -> List[PolicyTargetSummary]:
        return self.api('list_targets_for_policy', policy_id=policy_id)

    def __e_policy_targets(self) -> Dict[str, List[PolicyTargetSummary]]:
        ret = {}
        breakpoint()
        if self.dm.policies is None:
            self.init_policies()
        for policy in self.dm.policies:
            pid = policy.policy_summary.id
            data = self.__e_policy_targets_for_id(policy_id=pid)
            for target in data:
                if ret.get(pid) is None:
                    ret[pid] = []
                ret[pid].append(PolicyTargetSummary(**target))
        return ret

    def __lookup_obj_index(self, obj_type: str, obj_id: str) -> int:
        map_field = None
        if obj_type == 'account':
            map_field = self.dm.account_index_map
        elif obj_type == 'ou' or obj_type == 'organizational_unit':
            map_field = self.dm.ou_index_map
        elif obj_type == 'policy':
            map_field = self.dm.policy_index_map
        return map_field[obj_id]

    def __lookup_account_index(self, account_id: str) -> int:
        return self.__lookup_obj_index('account', account_id)

    def __lookup_ou_index(self, ou_id: str) -> int:
        return self.__lookup_obj_index('ou', ou_id)

    def __lookup_policy_index(self, policy_id: str) -> int:
        return self.__lookup_obj_index('policy', policy_id)

    def __t_policy_targets(self) -> Dict[str, List[PolicySummaryForTarget]]:
        ret = {}
        for pid, p_targets in self.__e_policy_targets().items():
            p_index = self.__lookup_policy_index(pid)
            p_type = self.dm.policies[p_index].policy_summary.type
            p_summary_for_target = PolicySummaryForTarget(id=pid, type=p_type)
            ret[pid] = {
                'policy_target_summaries': p_targets,
                'policy_summary_for_targets': p_summary_for_target
            }
        return ret

    def __l_policy_targets(self) -> None:
        data = self.__t_policy_targets()
        for pid, d in data.items():
            p_index = self.__lookup_policy_index(pid)
            # Update "targets" for Policy objects
            self.dm.policies[p_index].targets = d['policy_target_summaries']
            # Update "policies" for target objects
            for target in d['policy_target_summaries']:
                if target.type == 'ROOT':
                    if self.dm.root.policies is None:
                        self.dm.root.policies = []
                    self.dm.root.policies.append(d['policy_summary_for_targets'])
                elif target.type == 'ORGANIZATIONAL_UNIT':
                    ou_index = self.__lookup_ou_index(target.target_id)
                    if self.dm.organizational_units[ou_index].policies is None:
                        self.dm.organizational_units[ou_index].policies = []
                    self.dm.organizational_units[ou_index].policies.append(d['policy_summary_for_targets'])
                elif target.type == 'ACCOUNT':
                    acct_index = self.__lookup_account_index(target.target_id)
                    if self.dm.accounts[acct_index].policies is None:
                        self.dm.accounts[acct_index].policies = []
                    self.dm.accounts[acct_index].policies.append(d['policy_summary_for_targets'])

    def init_policy_targets(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policy_targets()

    def __e_ous_recurse(self,
                        parents: List[ParChild] = None,
                        ous: List[OrganizationalUnit] = None,
                        depth: int = 0,
                        maxdepth: int = _OU_MAXDEPTH) -> List[OrganizationalUnit]:
        """Recurse the org tree and return a list of OU dicts"""
        if parents is None:
            if self.dm.root is None:
                self.init_root()
            parents = [self.dm.root.as_parchild()]
        if self.dm.parent_child_tree is None:
            self.dm.parent_child_tree = {}
        if self.dm.child_parent_tree is None:
            self.dm.child_parent_tree = {}
        if self.dm.organizational_units is None:
            self.dm.organizational_units = []
        if depth == maxdepth or len(parents) == 0:
            return ous
        if ous is None:
            ous = []
        next_parents = []
        for parent in parents:
            if self.dm.parent_child_tree.get(parent.id) is None:
                self.dm.parent_child_tree[parent.id] = []
            ou_results = self.api('list_organizational_units_for_parent', parent_id=parent.id)
            for ou_result in ou_results:
                ou = OrganizationalUnit(parent=parent, **ou_result)
                ou_as_parchild = ou.as_parchild()
                self.dm.parent_child_tree[parent.id].append(ou_as_parchild)
                self.dm.child_parent_tree[ou.id] = parent
                ous.append(ou)
                next_parents.append(ou_as_parchild)
            acct_results = self.api('list_accounts_for_parent', parent_id=parent.id)
            for acct_result in acct_results:
                account = Account(parent=parent, **acct_result)
                self.dm.parent_child_tree[parent.id].append(account.as_parchild())
                self.dm.child_parent_tree[account.id] = parent
        return self.__e_ous_recurse(parents=next_parents, ous=ous, depth=depth+1)

    def __e_ous(self) -> List[OrganizationalUnit]:
        return self.__e_ous_recurse()

    def __t_ous(self) -> List[OrganizationalUnit]:
        data = self.__e_ous()
        ous = []
        for ou in data:
            ou.children = self.dm.parent_child_tree[ou.id]
            ous.append(ou)
        return ous

    def __l_ous(self) -> None:
        ous = self.__t_ous()
        self.dm.root.children = self.dm.parent_child_tree[self.dm.root.id]
        self.dm.organizational_units = ous
        if self.dm.ou_index_map is None:
            self.dm.ou_index_map = {}
        for i, ou in enumerate(self.dm.organizational_units):
            self.dm.ou_index_map[ou.id] = i

    def init_ous(self) -> None:
        """Recurse all OUs in the organization"""
        self.__l_ous()

    def __e_accounts(self) -> List[Dict[str, Any]]:
        return self.api('list_accounts')

    def __t_accounts(self) -> List[Account]:
        return [Account(**account) for account in self.__e_accounts()]

    def __l_accounts(self) -> None:
        data = self.__t_accounts()
        accounts = []
        for result in data:
            account = result
            account.parent = self.dm.child_parent_tree[account.id]
            accounts.append(account)
        self.dm.accounts = accounts
        if self.dm.account_index_map is None:
            self.dm.account_index_map = {}
        for i, account in enumerate(self.dm.accounts):
            self.dm.account_index_map[account.id] = i

    def init_accounts(self) -> None:
        """Initialize the list of Account objects in the organizations"""
        self.__l_accounts()

    def __e_effective_policies_for_target(self, target_id: str) -> List[EffectivePolicy]:
        effective_policies = []
        pol_types = [p.type for p in self.dm.available_policy_types if p.type != 'SERVICE_CONTROL_POLICY']
        for pol_type in pol_types:
            data = self.api('describe_effective_policy', policy_type=pol_type, target_id=target_id)
            effective_policies.append(EffectivePolicy(**data))
        return effective_policies

    def __e_effective_policies(self) -> Dict[int, List[EffectivePolicy]]:
        ret = {}
        if self.dm.accounts is None:
            self.init_accounts()
        for account in self.dm.accounts:
            ret[account.id] = self.__e_effective_policies_for_target(account.id)
        return ret

    def __l_effective_policies(self) -> None:
        for acct_id, effective_policies in self.__e_effective_policies().items():
            acct_index = self.__lookup_account_index(acct_id)
            self.dm.accounts[acct_index].effective_policies = effective_policies

    def init_effective_policies(self) -> None:
        self.__l_effective_policies()

    def __e_tags_for_resource_ids(self,
                                  resource_ids: List[str]
                                  ) -> Dict[str, Dict[str, str]]:
        ret = {}
        for resource_id in resource_ids:
            ret[resource_id] = query_tags(self.client, resource_id)
        return ret

    def __et_tags(self, obj_type: str) -> Dict[str, Dict[str, str]]:
        obj_type = obj_type.upper()
        resource_ids = None
        if obj_type == 'ROOT' or obj_type == 'ROOTS':
            if self.dm.root is None:
                self.init_root()
            resource_ids = [self.dm.root.id]
        elif (
                 obj_type == 'ORGANIZATIONAL_UNIT' or
                 obj_type == 'ORGANIZATIONAL_UNITS' or
                 obj_type == 'OU' or
                 obj_type == 'OUS'
            ):
            if self.dm.organizational_units is None:
                self.init_ous()
            resource_ids = [ou.id for ou in self.dm.organizational_units]
        elif obj_type == 'ACCOUNT' or obj_type == 'ACCOUNTS':
            if self.dm.accounts is None:
                self.init_accounts()
            resource_ids = [acct.id for acct in self.dm.accounts]
        return self.__e_tags_for_resource_ids(resource_ids=resource_ids)

    def __l_account_tags(self) -> None:
        for acct_id, tags in self.__et_tags('accounts').items():
            acct_index = self.__lookup_account_index(acct_id)
            self.dm.accounts[acct_index].tags = tags

    def init_account_tags(self) -> None:
        self.__l_account_tags()

    def __l_ou_tags(self) -> None:
        for ou_id, tags in self.__et_tags('ous').items():
            ou_index = self.__lookup_ou_index(ou_id)
            self.dm.organizational_units[ou_index].tags = tags

    def init_ou_tags(self) -> None:
        self.__l_ou_tags()

    def __l_root_tags(self) -> None:
        if self.dm.root is None:
            self.init_root()
        self.dm.root.tags = self.__et_tags('root')[self.dm.root.id]

    def init_root_tags(self) -> None:
        self.__l_root_tags()

    def init_all_tags(self) -> None:
        self.init_root_tags()
        self.init_ou_tags()
        self.init_account_tags()
