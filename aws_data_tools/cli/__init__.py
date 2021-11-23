"""
CLI interface for working with data from AWS APIs
"""

import itertools
import json
import os
import re
import traceback
from typing import Any

from botocore.exceptions import ClientError, NoCredentialsError

import click
import click_completion
import click_completion.core

from .. import get_version
from ..client import APIClient
from ..models.organizations import Account, OrganizationDataBuilder

from ..utils.dynamodb import (
    deserialize_dynamodb_items,
    prepare_dynamodb_batch_put_request,
)


def custom_startswith(string, incomplete):
    """A custom completion matching that supports case insensitive matching"""
    if os.environ.get("_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE"):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


click_completion.core.startswith = custom_startswith
click_completion.init()

completion_cmd_help = """Shell completion for click-completion-command
Available shell types:
    \b
      %s
      Default type: auto
      """ % "\n  ".join(
    "{:<12} {}".format(k, click_completion.core.shells[k])
    for k in sorted(click_completion.core.shells.keys())
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=get_version())
@click.option("--debug", "-d", default=False, is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, debug):
    """A command-line tool to interact with data from AWS APIs"""
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


@cli.group(hidden=True)
@click.option(
    "-i",
    "--case-insensitive/--no-case-insensitive",
    default=True,
    help="Case insensitive completion",
)
@click.pass_context
def completion(ctx, case_insensitive, help=completion_cmd_help):
    """Commands for shell completion"""
    extra_env = (
        {"_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"}
        if case_insensitive
        else {}
    )
    ctx.obj["EXTRA_ENV"] = extra_env


@completion.command()
@click.pass_context
def bash(ctx):
    """Print BASH completion script for sourcing"""
    extra_env = ctx.obj["EXTRA_ENV"]
    click.echo(click_completion.core.get_code("bash", extra_env=extra_env))


@completion.command()
@click.pass_context
def zsh(ctx):
    """Print ZSH completion script for sourcing"""
    extra_env = ctx.obj["EXTRA_ENV"]
    click.echo(click_completion.core.get_code("zsh", extra_env=extra_env))


@completion.command()
@click.pass_context
def fish(ctx):
    """Print fish completion script for sourcing"""
    extra_env = ctx.obj["EXTRA_ENV"]
    click.echo(click_completion.core.get_code("fish", extra_env=extra_env))


@completion.command()
@click.pass_context
def powershell(ctx):
    """Print Powershell completion script for sourcing"""
    extra_env = ctx.obj["EXTRA_ENV"]
    click.echo(click_completion.core.get_code("powershell", extra_env=extra_env))


@cli.group()
@click.pass_context
def organization(ctx):
    """Interact with data from AWS Organizations APIs"""
    ctx.ensure_object(dict)


def handle_error(ctx, err_msg, tb=None):
    """Takes an error message and an optional traceback, prints them, and quits"""
    if err_msg is not None:
        click.secho(err_msg, fg="red")
        if tb is not None:
            click.echo()
            click.secho(tb, fg="red")
        ctx.exit(1)


@organization.command(short_help="Dump org data as JSON")
@click.option(
    "--format",
    "-f",
    "format_",
    default="JSON",
    type=click.Choice(["DOT", "JSON", "YAML"], case_sensitive=False),
    help="The output format for the data",
)
@click.option(
    "--no-accounts",
    default=False,
    is_flag=True,
    help="Exclude account data from the model",
)
@click.option(
    "--no-policies",
    default=False,
    is_flag=True,
    help="Exclude policy data from the model",
)
@click.option("--out-file", "-o", help="File path to write data instead of stdout")
@click.option(
    "--flatten", default=False, is_flag=True, help="Flatten nested model keys"
)
@click.pass_context
def dump_all(
    ctx: dict[str, Any],
    format_: str,
    no_accounts: bool,
    no_policies: bool,
    out_file: str,
    flatten: bool,
) -> None:
    """Dump a data representation of the organization"""
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
            s_func = odb.to_json
        elif format_ == "YAML":
            s_func = odb.to_yaml
        elif format_ == "DOT":
            s_func = odb.to_dot
        if out_file is None:
            out_file = "-"
        with click.open_file(out_file, mode="wb") as f:
            f.write(bytes(s_func(flatten=flatten), "utf-8"))
    except ClientError as exc_info:
        err_msg = f"Service Error: {str(exc_info)}"
    except NoCredentialsError:
        err_msg = "Error: Unable to locate AWS credentials"
    except Exception as exc_info:
        err_msg = f"Unknown Error: {str(exc_info)}"
        tb = traceback.format_exc()
    handle_error(ctx, err_msg, tb)


@organization.command(short_help="Query for account details")
@click.option(
    "--accounts", "-a", required=True, help="A space-delimited list of account IDs"
)
@click.option(
    "--include-effective-policies",
    default=False,
    is_flag=True,
    help="Include effective policies for the accounts",
)
@click.option(
    "--include-parents",
    default=False,
    is_flag=True,
    help="Include parent data for the accounts",
)
@click.option(
    "--include-tags",
    default=False,
    is_flag=True,
    help="Include tags applied to the accounts",
)
@click.option(
    "--include-policies",
    default=False,
    is_flag=True,
    help="Include policies attached to the accounts",
)
@click.pass_context
def lookup_accounts(
    ctx: dict[str, Any],
    accounts: list[str],
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
        if re.fullmatch(r"^[\d]{12}$", account) is not None:
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
        {k: v for k, v in acct.to_dict().items() if k not in exclude_keys}
        for acct in odb.dm.accounts
        if acct.id in account_ids
    ]
    click.echo(json.dumps(data, default=str))


@organization.command()
@click.option("--table", "-t", required=True, help="Name of the DynamoDB table")
@click.option(
    "--in-file", "-i", required=True, help="File containing a list of Account objects"
)
@click.pass_context
def write_accounts_to_dynamodb(
    ctx: dict[str, Any],
    table: str,
    in_file: str,
) -> None:
    """Write a list of accounts to a DynamoDB table"""
    data = None
    with click.open_file(in_file, mode="r") as f:
        data = json.load(f)
    odb = OrganizationDataBuilder()
    if not isinstance(data, list):
        handle_error(err_msg="Data is not a list")
    odb.dm.accounts = [Account(**account) for account in data]
    accounts = odb.to_dynamodb(field_name="accounts")
    client = APIClient("dynamodb")
    ret = {"responses": []}
    # Group into batches of 25 since that's the max for BatchWriteItem
    for group_ in itertools.zip_longest(*[iter(accounts)] * 25):
        items = prepare_dynamodb_batch_put_request(table=table, items=group_)
        res = client.api("batch_write_item", request_items=items)
        # TODO: Add handling of any "UnprocessedItems" in the response. Add retry with
        # exponential backoff.
        ret["responses"].append(res)
    click.echo(json.dumps(ret))


@organization.command()
@click.option("--table", "-t", required=True, help="Name of the DynamoDB table")
@click.pass_context
def read_accounts_from_dynamodb(
    ctx: dict[str, Any],
    table: str,
) -> None:
    """Fetch a list of accounts from a DynamoDB table"""
    client = APIClient("dynamodb")
    res = client.api("scan", table_name=table)
    accounts = [Account(**account) for account in deserialize_dynamodb_items(res)]
    odb = OrganizationDataBuilder()
    odb.dm.accounts = accounts
    click.echo(odb.to_json(field_name="accounts"))
