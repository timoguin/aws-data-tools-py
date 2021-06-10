from json import dumps as json_dumps
from sys import stdout
from traceback import format_exc
from typing import Any, Dict, Union

from botocore.exceptions import ClientError, NoCredentialsError
from structlog import configure, processors, dev, get_logger
from yaml import dump as yaml_dump

from click import (
    argument,
    command,
    echo,
    group,
    open_file,
    option,
    pass_context,
    secho,
    version_option,
    Choice,
    Path,
)

from .. import get_version
from ..builders.organizations import OrganizationDataBuilder as odb


configure(
    processors=[
        processors.add_log_level,
        processors.StackInfoRenderer(),
        dev.set_exc_info,
        processors.format_exc_info,
        processors.TimeStamper(),
        processors.JSONRenderer(),
        dev.ConsoleRenderer(),
    ],
    cache_logger_on_first_use=True,
)
log = get_logger()


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


def handle_error(ctx, errmsg, tb):
    if errmsg is not None:
        secho(errmsg, fg="red")
        if tb is not None:
            echo()
            secho(tb, fg="red")
        ctx.exit(1)


@organization.command()
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
    format: str,
    out_file: str,
) -> Union[str, None]:
    """Dump a JSON representation of the organization"""
    errmsg = None
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
        org = odb(**kwargs)
        if format == "JSON":
            s_func = org.as_json
        elif format == "YAML":
            s_func = org.as_yaml
        data = s_func()
        if out_file is None:
            out_file = "-"
        with open_file(out_file, mode="wb") as f:
            f.write(bytes(s_func(), "utf-8"))
    except ClientError as exc_info:
        errmsg = f"Service Error: {str(exc_info)}"
    except NoCredentialsError as exc_info:
        errmsg = f"Error: Unable to locate AWS credentials"
    except Exception as exc_info:
        errmsg = f"Unknown Error: {str(exc_info)}"
        tb = format_exc()
    handle_error(ctx, errmsg, tb)


if __name__ == "__main__":
    cli(ctx, auto_envvar_prefix="AWSDATA")
