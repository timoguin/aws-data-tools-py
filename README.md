# AWS Data Tools

<!-- Badges -->
[![Actions Status][gh-actions-badge]][gh-actions-link]
[![PyPI][pypi-badge]][pypi-link]
[![License][license-badge]][license-link]

A set of opinioned (but flexible) Python libraries for querying and transforming data
from various AWS APIs, as well as a CLI interface.

This is in early development.

## Installation

Using pip should work on any system with at least Python 3.9:

```
$ pip install aws-data-tools
```

By default, the CLI is not installed. To include it, you can specify it as an extra:

```
$ pip install aws-data-tools[cli]
```

## Quickstart

The quickest entrypoints are using the data builders and the CLI.

To dump a data representation of an AWS Organization, you can do the following using
the builder:

```python
from aws_data_tools.builders.organizations import OrganizationDataBuilder

odb = OrganizationDataBuilder(init_all=True)
organization = odb.as_json()
```

Here is how to do the same thing with the CLI:

```
$ awsdata organization dump-json
```

## Usage

There are currently 4 main components of the package: helpers for working with AWS
session and APIs, data models for API data types, builders to query AWS APIs and
perform deserialization and ETL operations of raw data, and a CLI tool to further
abstract some of these operations.

### Builders

While it is possible to directly utilize and interact with the data models, probably
the largest benefit is the [builders](aws_data_tools/builders) package. It abstracts
any API operations and data transformations required to build data models. The models
can then be serialized to dicts, as well as JSON or YAML strings.

A full model of an AWS Organization can be constructed using the
`OrganizationDataBuilder` class. It handles recursing the organizational tree and
populating any relational data between the various nodes, e.g., parent-child
relationships between an OU and an account.

The simplest example pulls all supported organizational data and creates the related
data models:

```python
from aws_data_tools.builders.organizations import OrganizationDataBuilder as odb

org = odb(init_all=True)
```

Note that this makes many API calls to get this data. For example, every OU, policy,
and account requires an API call to pull any associated tags, so every node requires at
least `n+3` API calls. Parallel operations are not supported, so everything runs
serially.

To get a sense of the number of API calls required to populate organization data, an
organization with 50 OUs, 5 policies, 200 accounts, and with all policy types activated
requires 316 API calls! That's why this library was created.

For more control over the process, you can init each set of components as desired:

```python
from aws_data_tools.builders.organizations import OrganizationDataBuilder as odb

org = odb()
org.init_connection()
org.init_organization()
org.init_root()
org.init_policies()
org.init_policy_tags()
org.init_ous()
org.init_ou_tags()
org.init_accounts()
org.init_account_tags()
org.init_policy_targets()
org.init_effective_policies()
```

### CLI

As noted above, the CLI is an optional component that can be installed using pip's
bracket notation for extras:

```
$ pip install aws-data-tools[cli]
```

With no arguments or flags, help content is displayed by default. You can also pass the
`--help` flag for the help content of any commands or subcommands.

```
$ awsdata
Usage: awsdata [OPTIONS] COMMAND [ARGS]...

  A command-line tool to interact with data from AWS APIs

Options:
  --version    Show the version and exit.
  -d, --debug  Enable debug mode
  -h, --help   Show this message and exit.

Commands:
  organization  Interact with data from AWS Organizations APIs
```

Here is how to dump a JSON representation of an AWS Organization to stdout:

The `organization` subcommand allows dumping organization data to a file or to stdout:

```
$ awsdata organization dump-json --format json
Usage: awsdata organization dump-json [OPTIONS]

  Dump a JSON representation of the organization

Options:
  --no-accounts             Exclude account data from the model
  --no-policies             Exclude policy data from the model
  -f, --format [JSON|YAML]  The output format for the data
  -o, --out-file TEXT       File path to write data instead of stdout
  -h, --help                Show this message and exit.
```

It also supports looking up details about individual accounts:

```
$ awsdata organization lookup-accounts --help
Usage: awsdata organization lookup-accounts [OPTIONS]

  Query for account details using a list of account IDs

Options:
  -a, --accounts TEXT           A space-delimited list of account IDs
                                [required]
  --include-effective-policies  Include effective policies for the accounts
  --include-parents             Include parent data for the accounts
  --include-tags                Include tags applied to the accounts
  --include-policies            Include policies attached to the accounts
  -h, --help                    Show this message and exit.
```

### API Client

The [APIClient](aws_data_models/client.py) class wraps the initialization of a boto3
session and a low-level client for a named service. It contains a single `api()`
function that takes the name of an API operation and any necessary request data as
kwargs.

It supports automatic pagination of any API operations that support it. The pagination
config is set to `{'MaxItems': 500}` by default, but a `pagination_config` dict can be
passed for any desired customizations.

When initializing the class, it will create a session and a client.

```python
from aws_data_tools.client import APIClient

client = APIClient("organizations")
org = client.api("describe_organization").get("organization")
roots = client.api("list_roots")
ous = client.api("list_organizational_units_for_parent", parent_id="r-abcd").get(
    "organizational_units"
)
```

Note that, generally, any list operations will return a list with no further filtering
required, while describe calls will have the data keyed under the name of the object
being described. For example, describing an organization returns the relavant data
under an `organization` key.

Furthermore, you may notice above that API operations and their corresponding arguments
support `snake_case` format. Arguments can also be passed in the standard `PascalCase`
format that the APIs utilize. Any returned data has any keys converted to `snake_case`.

The raw boto3 session is available as the `session` field, and the raw, low-level
client is available as the `client` field.

### Data Models

The [models](aws_data_tools/models) package contains a collection of opinionated models
implemented as data classes. There is a package for each available service. Each one is
named after the service that would be passed when creating a boto3 client using
`boto3.client('service_name')`.

Most data types used with the Organizations APIs are supported. The top-level
`Organization` class is the most useful, as it also acts as a container for all other
related data in the organization.

The following data types and operations are currently not supported:

- Viewing organization handshakes (for creating and accepting account invitations)
- Viewing the status of accounts creations
- Viewing organization integrations with AWS services (for org-wide implementations of
  things like CloudTrail, Config, etc.)
- Viewing delegated accounts and services
- Any operations that are not read-only

All other data types are supported.

```python
from aws_data_tools.client import APIClient
from aws_data_tools.models.organizations import Organization

client = APIClient("organizations")
data = client.api("describe_organization").get("organization")
org = Organization(**data)
org.as_json()
```

View the [package](aws_data_tools/models/organization/__init__.py) for the full list of
models.

## Roadmap

The goal of this package is to provide consistent, enriched schemas for data from both
raw API calls and data from logged events. We should also be able to unwrap and parse
data from messaging and streaming services like SNS, Kinesis, and EventBridge.

Here are some examples:

- Query Organizations APIs to build consistent, denormalized models of organizations
- Validate and enrich data from CloudTrail log events
- Parse S3 and ELB access logs into JSON

This initial release only contains support for managing data from AWS Organizations
APIs.

The following table shows what kinds of things may be supported in the future:

| Library Name  | Description                                                       | Data Type | Data Sources                                                  | Supported |
|---------------|-------------------------------------------------------------------|-----------|---------------------------------------------------------------|-----------|
| organizations | Organization and OU hierarchy, policies, and accounts             | API       | Organizations APIs                                            | ☑         |
| cloudtrail    | Service API calls recorded by CloudTrail                          | Log       | S3 / SNS / SQS / CloudWatch Logs / Kinesis / Kinesis Firehose | ☐         |
| s3            | Access logs for S3 buckets                                        | Log       | S3 / SNS / SQS                                                | ☐         |
| elb           | Access logs from Classic, Application, and Network Load Balancers | Log       | S3 / SNS / SQS                                                | ☐         |
| vpc_flow      | Traffic logs from VPCs                                            | Log       | S3 / CloudWatch Logs / Kinesis / Kinesis Firehose             | ☐         |
| config        | Resource state change events from AWS Config                      | Log       | S3 / SNS / SQS                                                | ☐         |
| firehose      | Audit logs for Firehose delivery streams                          | Log       | CloudWatch Logs / Kinesis / Kinesis Firehose                  | ☐         |
| ecs           | Container state change events                                     | Log       | CloudWatch Events / EventBridge                               | ☐         |
| ecr           | Repository events for stored images                               | Log       | CloudWatch Events / EventBridge                               | ☐         |

References:

- CloudWatch Logs: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/aws-services-sending-logs.html
- CloudWatch Events: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html

## Contributing

View the [Contributing Guide](.github/CONTRIBUTING.md) to learn about giving back.


<!-- Markown anchors -->
[gh-actions-badge]: https://github.com/timoguin/aws-data-tools-py/actions/workflows/ci.yml/badge.svg
[gh-actions-link]: https://github.com/timoguin/aws-data-tools-py/actions
[license-badge]: https://img.shields.io/github/license/timoguin/aws-data-tools-py.svg
[license-link]: https://github.com/timoguin/aws-data-tools-py/blob/main/LICENSE
[pypi-badge]: https://badge.fury.io/py/aws-data-tools.svg
[pypi-link]: https://pypi.python.org/pypi/aws-data-tools
