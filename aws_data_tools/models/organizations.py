from dataclasses import dataclass, field
from typing import Any, Dict, List

from python_jsonschema_objects.util import Namespace

from .. import APIClient


SERVICE_NAME = 'organizations'
ORGANIZATIONAL_UNIT_MAXDEPTH = 5


@dataclass(init=False)
class Organization:
    client: APIClient = field(default=None)

    @property
    def models(self):
        return self.client.schema_models
    
    def __get_meta(self):
        data = self.client.api('describe_organization',
                               data_key='organization')
        return data.get('organization')

    def __set_meta(self):
        self.__org.meta = self.__get_meta()

    @property
    def meta(self):
        return self.__org.meta

    def __get_roots(self):
        parent = {
            'parent': self.models.Parent(id=str(self.__org.meta.id), type='ORGANIZATION')
        }
        roots = [{**{'meta': root}, **parent} for root in self.client.api('list_roots')]
        return roots

    def __set_roots(self):
        roots = self.__get_roots()
        self.__org.roots = roots

    @property
    def root(self):
        if len(self.__org.roots) == 0:
            return None
        return self.__org.roots[0]

    def __recurse_tree(self,
                       unvisited_nodes = None,
                       visited_nodes = None,
                       depth: int = 0,
                       maxdepth: int = ORGANIZATIONAL_UNIT_MAXDEPTH):
        import ipdb; ipdb.set_trace()
        if unvisited_nodes is None:
            unvisited_nodes = [self.__org.roots[0]]
        if visited_nodes is None:
            visited_nodes = []
        if depth > maxdepth or len(unvisited_nodes) == 0:
            return visited_nodes
        new_unvisited_nodes = []
        for node in unvisited_nodes:
            child_ous = self.client.api('list_organizational_units_for_parent',
                                        parent_id=node.meta.id)
            for child_ou in child_ous:
                # Each child becomes a new Child object added to the parent node (root or ou)
                child = self.models.Child({
                    'id': child['id'],
                    'type': 'ORGANIZATIONAL_UNIT'
                })
                node.children.append(child)

                # Each child becomes a new OU object
                ou = self.models.OrganizationalUnit(meta=child_ou)
                ou.parent = self.models.Parent(id=node.meta.id)
                ou.parent.type = 'ROOT' if str(node.meta.id).startswith('r-') else 'ORGANIZATIONAL_UNIT'
                new_unvisited_nodes.append(ou)
            visited_nodes.append(node)
        __recurse_tree(unvisited_nodes=new_unvisited_nodes,
                          visited_nodes=visited_nodes,
                          depth=depth+1)

    def __build_ou_tree(self):
        """Recurse from the Root or OU to find all children and transform data"""
        nodes = self.__recurse_tree()
        for node in nodes:
            if node.meta.id == self.root.meta.id:
                self.__org.roots[0].children = node.children
            else:
                self.__org.organizational_units.append(node)

    @property
    def organizational_units(self):
        return self.__org.organizational_units

    def __get_accounts_from_tree(self):
        nodes = [self.__org.roots[0]] + self.__org.organizational_units
        for node in nodes:
            res = self.client.api('list_accounts_for_parent', parent_id=node.meta.id)
            for data in res:
                account = self.models.Account(data)
                account.parent.id = node.meta.id
                account.parent.type = 'ROOT' if str(node.meta.id).startswith('r-') else 'ORGANIZATIONAL_UNIT'
                yield account

    def __set_accounts_from_tree(self):
        accounts = list(self.__get_accounts_from_tree())
        for account in accounts:
            child = self.models.Child(id=account.meta.id, type='ACCOUNT')
            if self.parent.type == 'ROOT':
                self.__org.roots[0].children.append(child)
            else:
                ou_index = None
                for i, ou in enumerate(self.__org.organizational_units):
                    if ou.id == account.parent.id:
                        ou_index = i
                        break
                if ou_index is not None:
                    self.__org.organizational_units[ou_index].children.append(child)
            self.__org.accounts.append(account)

    @property
    def accounts(self):
        return self.__org.accounts

    def __get_tags_for_resource_ids(self, resource_ids: List[str] = None):
        if resource_ids is None:
            resource_ids = []
        for resource_id in resource_ids:
            data = self.client.api('list_tags_for_resource',
                                   data_key='tags',
                                   resource_id=resource_id)
            tags = [self.model.Tag(tag) for tag in data]
            yield {'id': resource_id, 'tags': tags}

    def __set_tags(self):
        resource_ids = [self.__org.roots[0].meta.id]
        resource_ids.extend([ou.meta.id for ou in self.__org.organizational_units])
        resource_ids.extend([account.meta.id for account in self.__org.accounts])
        resource_tags = list(self.__get_tags_for_resource_ids(resource_ids=resource_ids))
        # Root tags
        if str(resource_id).startswith('r-'):
            self.__org.roots[0].tags = resource_tags
        # OU tags
        elif str(resource_id).startswith('ou-'):
            ou_index = None
            for i, ou in enumerate(self.__org.organizational_units):
                if ou.meta.id == resource_id:
                    ou_index = i
                    break
            if ou_index is not None:
                self.__org.organizational_units[ou_index].tags = resource_tags
        # Account tags
        elif str(resource_id).isdigit():
            account_index = None
            for i, account in enumerate(self.__org.accounts):
                if account.meta.id == resource_id:
                    account_index = i
                    break
            if account_index is not None:
                self.__org.accounts[account_index].tags = resource_tags

    def __init__(self, init_tags: List[str] = None):
        self.client = APIClient(SERVICE_NAME)
        self.__org = self.models.Organization()
        self.__set_meta()
        self.__set_roots()
        self.__build_ou_tree()
        self.__set_accounts_from_tree()
        self.__set_tags()
