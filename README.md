# AWS Data Tools

An set of opinioned (but flexible) Python libraries for querying and transforming data
from various AWS APIs, as well as a CLI interface.

This is in early development.

## Data Types and Sources

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

## Installing

---

**NOTE**: None of the following installation methods actually work. This is stubbed out
to include possible future installation methods.

---

Using pip should work on any system with at least Python 3.9:

`$ pip install aws-data-tools`

### MacOS

With homebrew:

`$ brew install aws-data-tools-py`

Using the pkg installer:

(This isn't how we'll want to do this. We want to bundle the application with _all_ its
dependencies, including Python itself. This probably means using pyInstaller to bundle
an "app" image.)

```
$ LATEST=$(gh release list --repo timoguin/aws-data-tools-py | grep 'Latest' | cut -f1)
$ curl -sL https://github.com/segmentio/aws-okta/releases/download/aws-data-tools-py.pkg --output aws-data-tools-py_$LATEST.pkg
$ installer -pkg aws-data-tools.py_$LATEST.pkg -target /usr/local/bin
```

### Windows

With chocolatey:

`$ choco install aws-data-tools-py`

## Usage

Empty.

## Testing

### Organizations Data ETL

- Bring up localstack instance (Pro) running IAM and Organizations (master account)
- Seed instance with Organization data (OUs, accounts, policies)
- Run script that performs ETL against data from the AWS Organizations APIs
- Ensure generated data is the same as the seed data
