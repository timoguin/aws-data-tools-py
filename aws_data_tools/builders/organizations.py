from dataclasses import asdict, dataclass, field, InitVar
from json import dumps as json_dumps
from typing import Any, ClassVar, Dict, List, Union

from botocore.session import Session
from botocore.client import BaseClient

from .. import APIClient

from ..models.organizations import (
    Account,
    Organization,
    OrganizationalUnit,
    ParChild,
    Policy,
    PolicySummary,
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
            policies.append(self.api('list_policies', filter=p.type))
        return policies

    def __t_policies(self) -> List[Policy]:
        return [Policy(policy_summary=pol) for pol in self.__e_policies()]

    def __l_policies(self) -> None:
        self.dm.policies = self.__t_policies()

    def init_policies(self) -> None:
        """Initialize the list of Policy objects in the organization"""
        self.__l_policies()

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
            breakpoint()
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
        breakpoint()
        self.dm.root.children = self.dm.parent_child_tree[self.dm.root.id]
        self.dm.organizational_units = ous

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
        breakpoint()
        for result in data:
            breakpoint()
            account = result
            account.parent = self.dm.child_parent_tree[account.id]
            accounts.append(account)
        self.dm.accounts = accounts

    def init_accounts(self) -> None:
        """Initialize the list of Account objects in the organizations"""
        self.__l_accounts()
