from dacite import from_dict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from json import dumps as json_dumps
from typing import Dict, Optional, Any

from ..utils import api, paged_api


@dataclass
class OrganizationNodeChildren:
    accounts: List[Any] = field(default_factory=list)
    organizational_units: List[Any] = field(default_factory=list)

    @staticmethod
    def fetch_children(resource_id: str,
                       accounts: bool = False,
                       organizational_units: bool = False) -> Dict[str, List[dict]]:
        """
        Query children for a resource ID (root or OU) and return as a dict of accounts
        and OUs
        """
        ret = {}
        if organizational_units:
            data = paged_api('organizations:list_organizational_units_for_parent',
                             'organizational_units',
                             parent_id=resource_id)
            ret['organizational_units'] = data
        if accounts:
            data = paged_api('organizations:list_accounts_for_parent',
                             'accounts',
                             parent_id=resource_id)
            ret['organizational_units'] = data
        if not organizational_unit and not accounts:
            return None
        return ret

    def __init__(self,
                 parent_id: str,
                 init_ous: bool = False,
                 init_accounts: bool = False,
                 init_all: bool = False)
        if init_ous or init_all:
            child_ous = self.fetch_children(parent_id, organizational_units=True)
            self.organizational_units = 
        if init_accounts or init_all:
            child_accounts = self.fetch_children(parent_id, accounts=True)
            self.organizational_units = 


@dataclass
class OrganizationNode:
    """
    Base class for nodes in an organization: root, ou, policy, or account
    """
    children: OrganizationNodeChildren = field(default_factory=OrganizationNodeChildren)

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        """Return an instance of the dataclass created from a dict"""
        return from_dict(data_class=cls, data=data)

    @staticmethod
    def fetch_tags(resource_id: str) -> Dict[str, str]:
        """
        Query tags for a resource ID and return as a dict of tags
        """
        data = paged_api('organizations:list_tags_for_resource',
                         key='tags',
                         resource_id=self.id)
        return {tag['Key']: tag['Value'] for tag in data}

    def set_tags(self):
        """
        Sets self.tags based on return from self.fetch_tags
        """
        self.tags = self.fetch_tags(self.id)

    @staticmethod
    def fetch_children(resource_id: str,
                       accounts: bool = True,
                       organizational_units: bool = True) -> Dict[str, List[dict]]:
        """
        Query children for a resource ID (root or OU) and return as a dict of accounts
        and OUs
        """
        ret = {}
        if organizational_units:
            data = paged_api('organizations:list_organizational_units_for_parent',
                             'organizational_units',
                             parent_id=resource_id)
            ret['organizational_units'] = data
        if accounts:
            data = paged_api('organizations:list_accounts_for_parent',
                             'accounts',
                             parent_id=resource_id)
            ret['organizational_units'] = data
        return ret

    def set_child_accounts(self):
        """
        Sets self.tags based on return from self.fetch_tags
        """
        self.tags = self.fetch_tags(self.id)


@dataclass
class OrganizationRoot(OrganizationNode):
    """
    Represents a root object in an AWS Organization
    """
    arn: str
    id: str
    name: str
    policy_types: list[Dict[str, str]] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def fetch_data():
        return = api('organizations:list_roots', data_key='roots')[0]

    def __init__(self):
        if 



@dataclass
class OrganizationOU(OrganizationNode):
    """
    Represents an AWS Organizations OU

    An additional parent_id field is added.
    """
    arn: str
    id: str
    name: str
    parent_id: str = field(default=None)
    tags: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def fetch_data():
        return api('organizations:describe_organizational_unit',
                   data_key='organizational_unit')

    @classmethod
    def init(self, id: str, parent_id: str = None):
        data = AWSOrganizationOU.fetch_data(organizational_unit_id=id)
        if parent_id is not None:
            data.update({'parent_id': parent_id})
        return from_dict(data_class=AWSOrganizationOU, data=data)

    def __init__(self,
                 parent_id: str = None,
                 init_all: bool = False, 
                 init_description: bool = False,
                 init_child_ous: bool = False,
                 init_child_accounts: bool = False,
                 init_tags: bool = False,
                 **kwargs):
        if parent_id is not None:
            self.parent_id = parent_id
        if init_description or init_all:
            description = self.fetch_data()
            for k, v in description_data.items():
                setattr(self, k, v)
        if init_child_ous or init_all:
            child_ous = self.fetch_children(self.parent_id, organizational_units=True)
            self.
        if init_child_accounts or init_all:
            pass
        if init_tags or init_all:
            pass


@dataclass
class OrganizationOUs:
    """
    Represents a list of AWS Organization OUs

    OU objects are obtained from the
    organizations:ListOrganizationalUnitsForParent API action.
    """
    ous: list[AWSOrganizationOU]

    @staticmethod
    def fetch_data(parent_id: str):
        data = paged_api('organizations:list_organizational_units_for_parent',
                         'organizational_units',
                         parent_id=parent_id)
        return data

    @classmethod
    def init(cls, parent_id: str, *args, **kwargs):
        child_ous = cls.fetch_data(parent_id)
        ous = []
        for ou in child_ous:
            ous.append(AWSOrganizationOU.init(id=ou['id'], parent_id=parent_id))
        return from_dict(data_class=AWSOrganizationOUs, data={'ous': ous})


@dataclass
class OrganizationAccount:
    """Represents the metadata for an AWS account"""
    arn: str
    email: str
    uid: str
    joined_method: str
    joined_timestamp: datetime
    name: str
    status: str

    # Optional fields
    parent_id: Optional[str]
    parent_name: Optional[str]
    shortname: Optional[str]
    tags: Optional[Dict[str, str]]

    __defaults = {
        'parent_id': None,
        'parent_name': None,
        'shortname': None,
        'tags': None
    }

@dataclass
class OrganizationAccounts:
    """
    Represents a list of AWS Organization accounts

    Account objects can be obtained two ways:
    - From the organizations:ListAccountsForParent API action.
    - From the organizations:ListAccounts API action
    """
    accounts: list[AWSOrganizationAccount]

    @staticmethod
    def fetch_data(parent_id: str):
        """
        Fetch a list of accounts by calling organizations:ListAccountsForParent
        with a parent_id argument.
        """
        data = paged_api('organizations:list_accounts_for_parent',
                         'accounts',
                         parent_id=parent_id)
        return data

    @classmethod
    def init(cls, parent_id: str):
        """
        Fetch list of accounts and return a list of dataclass objects
        """
        raw_data = cls.fetch_data(parent_id)
        accounts = []
        for account in raw_data:
            accounts.append({**account, **{'parent_id': parent_id}})
        return from_dict(data_class=cls, data={'accounts': accounts})


@dataclass
class OrganizationDescription:
    """
    Represents the description for an AWS Organization, as taken from an API call to
    organizations:DescribeOrganization
    """
    arn: str
    feature_set: str
    id: str
    master_account_arn: str
    available_policy_types: list[Dict[str, str]]
    master_account_email: str
    master_account_id: str


@dataclass
class Organization:
    """
    Represents the metadata for an AWS Organization
    """
    description: Optional[OrganizationDescription]
    root: Optional[OrganizationRoot]
    ou_tree: Optional[Dict[str, list[OrganizationOU]]]
    ous: Optional[list[OrganizationOU]]
    account_tree: Optional[Dict[str, list[OrganizationOU]]]
    accounts: Optional[list[OrganizationAccount]]

    def __init_description(self):
        data = api('organizations:describe_organization').get('organization')
        self.description = from_dict(data_class=AWSOrganizationDescription, data=data)

    def __init_root(self):

        data = api('organizations:list_roots').get('roots')[0]
        self.root = from_dict(data_class=AWSOrganizationRoot, data=data)

    def __init_ous(self, parents=None, depth=1, maxdepth=5):
        if depth > maxdepth:
            return
        if parents is None:
            parents = [self.root]
        children = []
        for parent in parents:
            parent_children = AWSOrganizationOUs.init(parent_id=parent.id).ous
            children.extend(parent_children)
            self.ous.extend(parent_children)
            self.ou_tree.update({parent.id: parent_children})
        self.__init_ous(parents=children, depth=depth+1)

    def __init_accounts(self):
        for oid in self.ou_tree.keys():
            child_accounts = AWSOrganizationAccounts.init(parent_id=oid).accounts
            self.account_tree.update({oid: child_accounts})
            self.accounts.extend(child_accounts)

    def __init_tags(self, resource_ids: list[str] = None):
        # root starts with "r-"
        # ou starts with "ou-"
        # policy starts with "p-"
        # account is a 13-digit string
        init_all = False
        if resource_ids is None:
            init_all = True
        if init_all:
            self.root.idget_resource_tags
            - get root tags

    def init_accounts(self):
        self.__init_accounts()

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json_dumps(self.as_dict(),
                          indent=4,
                          sort_keys=True,
                          default=str)

    def print_json(self):
        print(self.as_json())

    def __init__(self,
                 init_description: bool = True,
                 init_root: bool = True,
                 init_ou_tags: bool = False,
                 init_ous: bool = True,
                 init_account_tags: bool = False,
                 init_accounts: bool = False):
        self.ou_tree = {}
        self.ous = []
        self.account_tree = {}
        self.accounts = []

        if init_description:
            self.__init_description()
        if init_root:
            self.__init_root()
        if init_ous:
            self.__init_ous()
            if init_ou_tags:
                self.__init_tags(resource_ids=self.ou_ids())
        if init_accounts:
            self.__init_accounts()
            if init_account_tags:
                self.__init_tags(resource_ids=self.account_ids())
