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


SERVICE_NAME = 'organizations'


def init_client() -> APIClient:
    """Return an APIClient for the Organizations service"""
    return APIClient(SERVICENAME)

def query_effective_policies(client: APIClient,
                             policy_types: List[str],
                             target_id: str) -> List[NodeEffectivePolicy]:
    """Return a summary of effective policies attached to a target"""
    effective_policies = []
    for policy_type in policy_types:
        data = client.api('describe_effective_policy',
                          policy_type=policy_type,
                          target_id=target_id)
        for result in data.get('effective_policy'):
            effective_policy = NodeEffectivePolicy(**result)
            effective_policies.append(effective_policy)
    return effective_policies

def query_policies(client: APIClient,
                   policy_types: List[str],
                   target_id: str) -> List[PolicySummary]:
    """Return a summary of policies attached to a target"""
    policies = []
    for policy_type in policy_types:
        data = client.api('list_policies_for_target',
                          filter=policy_type,
                          target_id=target_id)
        for result in data:
            policy = PolicySummary(**result)
            policies.append(policy)
    return policies

def query_organizational_units_for_parent(client: APIClient,
                                          parent_id: str) -> List[OrganizationalUnit]:
    """Return a list of OUs belonging to a parent"""
    data = client.api('list_organizational_units_for_parent', parent_id=parent_id)
    ous = []
    for result in data:
        ou = OrganizationalUnit(**result)
        ous.append(ou)
    return ous
