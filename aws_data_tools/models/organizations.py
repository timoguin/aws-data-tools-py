from dataclasses import dataclass, field
from typing import Any, Dict

from python_jsonschema_objects.util import Namespace

from .. import APIClient


SERVICE_NAME = 'organizations'
ORGANIZATIONAL_UNIT_MAXDEPTH = 5


@dataclass
class Organization:
    client: APIClient = field(default=None)

    def get_model(self, name: str):
        """Return a schema model by name"""
        return getattr(self.client.schema_models, name)

    def get_models(self):
        """Return a dict of schema model names to the corresponding object types"""
        return {
            schema: getattr(self.client.schema_models, schema)
            for schema in dir(self.client.schema_models)
        }

    def get_meta(self):
        return self.client.api('describe_organization', data_key='organization').get('organization')

    def set_meta(self):
        self.organization.meta = self.get_meta()

    def get_roots(self):
        parent = {'parent': {'id': self.meta.id, 'type': 'ORGANIZATION'}}
        roots = [{**root, **parent} for root in self.client.api('list_roots')]
        return roots

    def set_roots(self):
        roots = self.get_roots()
        self.organization.roots = self.get_roots()

    def __recurse_ous(self,
                      parent_ids = None,
                      depth: int = 1,
                      maxdepth: int = ORGANIZATIONAL_UNIT_MAXDEPTH):
        if depth > maxdepth:
            return
        parent_type = None
        if parents is None:
            parents = [self.root.id]
            parent_type = 'ROOT'
        else:
            parent_type = 'ORGANIZATIONAL_UNIT'
        children = []
        for parent_id in parent_ids:
            p_children = self.client.api('list_organizational_units_for_parent',
                                         parent_id=parent_id)
            child_ous = []
            for child_ou in p_children:
                parent = {'parent': {'id': ou.meta.id, 'type': parent_type}}
                child_ou_data = {**child_ou, **parent}
                ou = self.get_model('OrganizationalUnit')(child_ou_data)
                child_ous.append(ou)
        if depth >= maxdepth:
            self.__recurse_ous(parent_ids=, children=children) 

    def get_organizational_units(self):

    @property
    def meta(self):
        return self.organization.meta

    @property
    def root(self):
        return self.organization.roots[0]

    def __post_init__(self):
        self.client = APIClient(SERVICE_NAME)
        self.organization = self.client.schema_models.Organization()
        self.set_meta()
        self.set_roots()
        self.set_organizational_units()
