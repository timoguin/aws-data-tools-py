"""
CLI interface for working with data from AWS APIs
"""

from itertools import zip_longest
from json import dumps as json_dumps
from json import load as json_load
from re import fullmatch
from traceback import format_exc
from typing import Any, Dict, List

from botocore.exceptions import ClientError, NoCredentialsError

from click import (
    echo,
    group,
    open_file,
    option,
    pass_context,
    secho,
    version_option,
    Choice,
)

from .. import get_version
from ..client import APIClient
from ..builders.organizations import OrganizationDataBuilder
from ..utils import dict_to_dynamodb_item


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@group(context_settings=CONTEXT_SETTINGS)
@version_option(version=get_version())
@option("--debug", "-d", default=False, is_flag=True, help="Enable debug mode")
@pass_context
def cli(ctx, debug):
    """A command-line tool to interact with data from AWS APIs"""
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


@cli.group()
@pass_context
def organization(ctx):
    """Interact with data from AWS Organizations APIs"""
    ctx.ensure_object(dict)


def handle_error(ctx, err_msg, tb=None):
    """Takes an error message and an optional traceback, prints them, and quits"""
    if err_msg is not None:
        secho(err_msg, fg="red")
        if tb is not None:
            echo()
            secho(tb, fg="red")
        ctx.exit(1)


@organization.command(short_help="Dump org data as JSON")
@option(
    "--no-accounts",
    default=False,
    is_flag=True,
    help="Exclude account data from the model",
)
@option(
    "--no-policies",
    default=False,
    is_flag=True,
    help="Exclude policy data from the model",
)
@option(
    "--format",
    "-f",
    "format_",
    default="JSON",
    type=Choice(["JSON", "YAML"], case_sensitive=False),
    help="The output format for the data",
)
@option("--out-file", "-o", help="File path to write data instead of stdout")
@pass_context
def dump_json(
    ctx: Dict[str, Any],
    no_accounts: bool,
    no_policies: bool,
    format_: str,
    out_file: str,
) -> None:
    """Dump a JSON representation of the organization"""
    err_msg = None
    tb = None
    try:
        kwargs = {"init_all": True}
        if no_accounts or no_policies:
            del kwargs["init_all"]
        if no_accounts:
            kwargs["init_accounts"] = False
            kwargs["init_account_tags"] = False
            kwargs["init_effective_policies"] = False
        if no_policies:
            kwargs["init_effective_policies"] = False
            kwargs["init_policies"] = False
            kwargs["init_policy_tags"] = False
            kwargs["init_policy_targets"] = False
        odb = OrganizationDataBuilder(include_account_parents=True, **kwargs)
        if format_ == "JSON":
            s_func = odb.as_json
        elif format_ == "YAML":
            s_func = odb.as_yaml
        if out_file is None:
            out_file = "-"
        with open_file(out_file, mode="wb") as f:
            f.write(bytes(s_func(), "utf-8"))
    except ClientError as exc_info:
        err_msg = f"Service Error: {str(exc_info)}"
    except NoCredentialsError:
        err_msg = "Error: Unable to locate AWS credentials"
    except Exception as exc_info:
        err_msg = f"Unknown Error: {str(exc_info)}"
        tb = format_exc()
    handle_error(ctx, err_msg, tb)


@organization.command(short_help="Query for account details")
@option("--accounts", "-a", required=True, help="A space-delimited list of account IDs")
@option(
    "--include-effective-policies",
    default=False,
    is_flag=True,
    help="Include effective policies for the accounts",
)
@option(
    "--include-parents",
    default=False,
    is_flag=True,
    help="Include parent data for the accounts",
)
@option(
    "--include-tags",
    default=False,
    is_flag=True,
    help="Include tags applied to the accounts",
)
@option(
    "--include-policies",
    default=False,
    is_flag=True,
    help="Include policies attached to the accounts",
)
@pass_context
def lookup_accounts(
    ctx: Dict[str, Any],
    accounts: List[str],
    include_parents: bool,
    include_effective_policies: bool,
    include_policies: bool,
    include_tags: bool,
) -> None:
    """Query for account details using a list of account IDs"""
    accounts_unvalidated = []
    if " " in accounts:
        accounts_unvalidated = accounts.split(" ")
    else:
        accounts_unvalidated = [accounts]
    account_ids = []
    invalid_ids = []
    for account in accounts_unvalidated:
        if fullmatch(r"^[\d]{12}$", account) is not None:
            account_ids.append(account)
        else:
            invalid_ids.append(account)
    if len(invalid_ids) > 0:
        handle_error(
            ctx,
            f"Invalid account IDs included in request: {str.join(' ', invalid_ids)}",
        )
    odb = OrganizationDataBuilder()
    odb.Connect()
    odb.fetch_accounts(include_parents=include_parents)

    exclude_keys = []
    if not include_parents:
        exclude_keys.append("parent")
    if not include_policies:
        exclude_keys.append("policies")
    if not include_effective_policies:
        exclude_keys.append("effective_policies")
    if not include_tags:
        exclude_keys.append("tags")

    if include_policies:
        odb.fetch_policies()
        odb.fetch_policy_targets()
    if include_effective_policies:
        odb.fetch_effective_policies(account_ids=account_ids)
    if include_tags:
        odb.fetch_account_tags(account_ids=account_ids)

    data = [
        {k: v for k, v in acct.as_dict().items() if k not in exclude_keys}
        for acct in odb.dm.accounts
        if acct.id in account_ids
    ]
    echo(json_dumps(data, default=str))


@organization.command()
@option("--table", "-t", required=True, help="Name of the DynamoDB table")
@option(
    "--in-file", "-i", required=True, help="File containing a list of Account objects"
)
@pass_context
def write_accounts_to_dynamodb(
    ctx: Dict[str, Any],
    table: str,
    in_file: str,
) -> None:
    """Write a list of accounts to a DynamoDB table"""
    client = APIClient("dynamodb")
    data = None
    with open_file(in_file, mode="r") as f:
        data = json_load(f)
    ret = {"responses": []}
    for group_ in zip_longest(*[iter(data)] * 25):
        accounts = [
            dict_to_dynamodb_item(account) for account in group_ if account is not None
        ]
        req_data = {table: [{"PutRequest": {"Item": account}} for account in accounts]}
        # TODO: Add handling of any "UnprocessedItems" in the response. Add retry with
        # exponential backoff.
        res = client.api("batch_write_item", request_items=req_data)
        ret["responses"].append(res)
    echo(json_dumps(ret))
