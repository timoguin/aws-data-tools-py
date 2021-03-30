from os import getenv
from typing import Optional

from .models import AWSOrganization


def build_organization_data():
    return AWSOrganization.init()


def dump_organization_data():
    debug = bool(getenv('DEBUG', 0))
    if debug:
        breakpoint()
    organization = build_organization_data()
    organization.print_json()
