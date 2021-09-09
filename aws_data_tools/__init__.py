"""
A library for working with data from AWS APIs
"""
# flake8: noqa: F401

from . import client, models, utils

__VERSION__ = "0.1.0-beta2"


def get_version() -> str:
    """Return the version of the package"""
    return __VERSION__
