from dacite import from_dict
from dataclasses import asdict, dataclass
from json import dumps as json_dumps
from typing import Dict, Optional

from ..utils import api, paged_api


@dataclass
class AWSOrganizationRoot:
    """
    Represents a root object in an AWS Organization
    """
    id: str
    arn: str
    name: str
    policy_types: list[Dict[str, str]]


@dataclass
class AWSOrganizationRoots:
    """
    Represents a list of AWS Organization roots

    Root objects are obtained from the organizations:ListRoots API action.
    """
    roots: list[AWSOrganizationRoot]

    @staticmethod
    def fetch_data():
        return api('organizations:list_roots')

    @classmethod
    def init(self):
        data = AWSOrganizationRoots.fetch_data()
        return from_dict(data_class=AWSOrganizationRoots, data=data)


@dataclass
class AWSOrganizationOU:
    """
    Represents an AWS Organizations OU

    An additional parent_id field is added.
    """
    arn: str
    id: str
    name: str
    parent_id: Optional[str]

    @staticmethod
    def fetch_data(**kwargs: dict):
        data = api('organizations:describe_organizational_unit', **kwargs)
        return data.get('organizational_unit')

    @classmethod
    def init(self, id: str, parent_id: str = None):
        data = AWSOrganizationOU.fetch_data(organizational_unit_id=id)
        if parent_id is not None:
            data.update({'parent_id': parent_id})
        return from_dict(data_class=AWSOrganizationOU, data=data)


@dataclass
class AWSOrganizationOUs:
    """
    Represents a list of AWS Organization OUs

    OU objects are obtained from the
    organizations:ListOrganizationalRootsForParent API action.
    """
    ous: list[AWSOrganizationOU]

    @staticmethod
    def fetch_data(parent_id: str):
        # data = api('organizations:list_organizational_units_for_parent',
        #            parent_id=parent_id)
        # return data.get("organizational_units")
        data = paged_api('organizations:list_organizational_units_for_parent',
                         'organizational_units',
                         parent_id=parent_id)
        return data

    @classmethod
    def init(self, parent_id: str, *args, **kwargs):
        child_ous = AWSOrganizationOUs.fetch_data(parent_id).get("children")
        ous = []
        for ou in child_ous:
            ous.append(AWSOrganizationOU.init(organizational_unit_id=ou['id']))
        return from_dict(data_class=AWSOrganizationOUs, data={'ous': ous})


@dataclass
class AWSOrganizationAccount:
    """Represents the metadata for an AWS account"""
    arn: Optional[str]
    email: str
    id: Optional[str]
    joined_method: Optional[str]
    joined_timestamp: Optional[str]
    name: str
    parent_id: Optional[str]
    parent_name: Optional[str]
    shortname: Optional[str]
    status: Optional[str]
    tags: Dict[str, str]


@dataclass
class AWSOrganizationAccounts:
    """
    Represents a list of AWS Organization accounts

    Account objects can be obtained two ways:
    - From the organizations:ListAccountsForParent API action.
    - From the organizations:ListAccounts API action
    """
    accounts: list[AWSOrganizationAccount]

    @staticmethod
    def fetch_data():
        """
        Fetch a list of accounts by calling organizations:ListAccounts
        """
        # data = api('organizations:list_accounts')
        # return data.get("accounts")
        data = paged_api('organizations:list_accounts', 'accounts')
        return data

    @staticmethod
    def fetch_data_from_parent(parent_id: str):
        """
        Fetch a list of accounts by calling organizations:ListAccountsForParent
        with a parent_id argument.
        """
        # data = api('organizations:list_accounts_for_parent',
        #            parent_id=parent_id)
        # return data.get("accounts")
        data = paged_api('organizations:list_accounts_for_parent',
                         'accounts',
                         parent_id=parent_id)
        return data

    @classmethod
    # def init(self, parent_id: str = None):
    def init(self):
        """
        Fetch list of accounts and return a list of dataclass objects
        """
        data = AWSOrganizationAccounts.fetch_data()
        # if parent_id is None:
        #     data = AWSOrganizationAccounts.fetch_data()
        # else:
        #     parent_id = kwargs.get('parent_id')
        #     data = AWSOrganizationAccounts.fetch_data_from_parent(parent_id)
        return from_dict(data_class=AWSOrganizationAccounts, data=data)


@dataclass
class AWSOrganization:
    """
    Represents the metadata for an AWS Organization
    """
    arn: str
    feature_set: str
    id: str
    master_account_arn: str
    available_policy_types: list[Dict[str, str]]
    master_account_email: str
    master_account_id: str

    root_id: Optional[str]
    ous: Optional[list[AWSOrganizationOU]]
    accounts: Optional[list[AWSOrganizationAccount]]

    # accounts_from_root: bool = True

    @staticmethod
    def fetch_data():
        data = api('organizations:describe_organization')
        return data.get('organization')

    @classmethod
    def init(self, **kwargs: Optional[dict]):
        # self.accounts_from_root = kwargs.get('accounts_from_root', True)
        data = AWSOrganization.fetch_data()
        return from_dict(data_class=AWSOrganization, data=data)

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json_dumps(self.as_dict(),
                          indent=4,
                          sort_keys=True,
                          default=str)

    def print_json(self):
        print(self.as_json())

    def get_root_id(self):
        roots = asdict(AWSOrganizationRoots.init()).get('roots')
        self.root_id = roots[0]['id']

    def get_ous(self):
        # Get data from root of the Organization
        data = AWSOrganizationOUs.fetch_data(parent_id=self.root_id)
        self.ous = data
        # # Get data from
        # ous = AWSOrganizationOUs.init(parent_id=self.root_id)
        # self.ous = ous

    def get_accounts(self):
        data = AWSOrganizationAccounts.fetch_data()
        # if self.accounts_from_root:
        #   data = AWSOrganizationAccounts.fetch_data()
        # else:
        #     raise Exception("Not implemented. Remove accounts_from_root kwarg")  #noqa
        self.accounts = data

    @staticmethod
    def list_children_for_parent(parent_id: str, child_type: str):
        # children = api('organizations:list_children',
        #                parent_id=parent_id,
        #                child_type=child_type).get('children')
        # return [child['id'] for child in children]
        children = paged_api('organizations:list_children',
                             'children',
                             parent_id=parent_id,
                             child_type=child_type)
        return [child['id'] for child in children]

    # def get_ous(self):
    #     # - must first know the root id
    #     # - list OU children for root id
    #     # - list OU children for any child OUs
    #     # - continue until no more nested OUs
    #     return asdict(AWSOrganizationOUs.init())

    def __post_init__(self):
        self.get_root_id()
        # if not self.accounts_from_root:
        #     self.get_ous()
        self.get_accounts()
