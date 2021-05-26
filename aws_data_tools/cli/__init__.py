import click
import structlog
from json import dumps
from traceback import format_exc

from botocore.exceptions import ClientError, NoCredentialsError

from ..models import AWSOrganization
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(),
        structlog.processors.JSONRenderer(),
        structlog.dev.ConsoleRenderer()
    ],
    cache_logger_on_first_use=True
)
log = structlog.get_logger()


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    """A command-line tool to interact with data from AWS APIs"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

@cli.group()
@click.pass_context
def organization(ctx):
    """Interact with data from AWS Organizations APIs"""
    ctx.ensure_object(dict)


def handle_error(ctx, errmsg, tb):
    if errmsg is not None:
        click.secho(errmsg, fg='red')
        if tb is not None:
            click.echo()
            click.secho(tb, fg='red')
        ctx.exit(1)

@organization.command()
@click.option('--include-accounts/--no-include-accounts', default=True)
@click.pass_context
def dump_json(ctx, include_accounts):
    """Dump a JSON representation of the organization"""
    errmsg = None
    tb = None
    try:
        org = AWSOrganization(init_accounts=include_accounts)
        click.echo(org.as_json())
    except ClientError as exc_info:
        errmsg = f'Service Error: {str(exc_info)}'
    except NoCredentialsError as exc_info:
        errmsg = f'Error: Unable to locate AWS credentials'
    except Exception as exc_info:
        errmsg = f'Unknown Error: {str(exc_info)}'
        tb = format_exc()
    handle_error(ctx, errmsg, tb)

if __name__ == '__main__':
    cli(obj={})
