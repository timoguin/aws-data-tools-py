# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!--
Notes for any unreleased changes do here. When a new release is cut, move these from
the unreleased section to the section for the new release.
-->

### Added

- New extras available for installation: "graphviz" and "all."

### Changed

- Changed the `Account.joined_timestamp` field from datetime to str to fix DynamoDB
  (de)serialization. Since boto3 returns the field as datetime, also added config to
  from_dict() to cast it to string.
- Updates `ModelBase.from_dict()` to accept and pass through kwargs
- Changed the `Organization` model to allow fields to be null for empty init
- Fixes broken logic in `ModelBase.to_dict()` when passing field_name, removes unused
  flatten kwarg
- Upgrades all dependencies
- Moves doc tooling into a "docs" dependency group instead of an extra
- To use the `Organization.to_dot()` functionality, you must now specify the graphviz
  dependency during installation: `pip install aws-data-tools[graphviz]`

### Removed

- The graphviz library is no longer installed by default.
- The devtools and docs extras have been removed

## [0.1.1] - 2021-11-23

### Added

- Adds support for generating a Graphviz diagram of an Organization with the new
  `OrganizationDataBuilder.to_dot()` function
- Adds `DOT` as a supported output format for the `organization dump-all` command
- Adds models for AWS Config notifications
- Adds models for SQS and SNS messages
- Adds methods to ModelBase to allow (de)serializing JSON or YAML strings
- Adds ModelBase.from_dict() to initialize a model from a dict using dacite
- Adds CodeQL analysis workflow for GitHub Actions

### Changed

- breaking: Renames `organization dump-json` CLI command to `organization dump-all`
- Moves buiders into the models namespace

## [0.1.0-beta2] - 2021-06-16

### Added

- Adds an `organization lookup-accounts` CLI command
- Adds a `field` argument to `ModelBase.as_dict()` to dump a single field in a model
- Adds configurations for tox and other testing tools
- Adds a quickstart to the top of the README
- Adds an `organizations write-accounts-to-dynamodb` CLI command
- Adds an `organizations read-accounts-from-dynamodb` CLI command
- Adds DynamoDB (de)serialization functions and requests helpers to utils

### Changed

- Refactors `OrganizationDataBuilder` to allow more control over pulling data
- Updates the Makefile to allow setting a custom PYTHONBREAKPOINT when debugging
- Updates `OrganizationDataBuilder` to allow setting the client during init
- Updates `OrganizationDataBuilder` to allow excluding account parent data lookups
- Renames `ModelBase` serialization function prefixes from `as_` to `to_`
- Updates `APIClient.api()` to only pascalize keys in kwargs, not the values. This
  fixes a bug that was causing items being inserted into DynamoDB to be pascalized.
- Updates `APIClient()` and `APIClient.Connect()` to skip creating the client if it
  already exists

## [0.1.0-beta1] - 2021-06-09

### Changed

- Moves APIClient class to `aws_data_tools.client.APIClient`
- Cleans up README
- Bumps version to 0.1.0-beta1
- Adds a CI config for Semantic Pull Requests

## [0.1.0-alpha4] - 2021-06-09

Initial alpha release

### Added

- Adds the APIClient class for simplying creation of sessions, connections, and
  making API calls
- Adds the ModelBase dataclass for data models to inherit from
- Adds dataclasses for Organizations data models: Organization, Account,
  OrganizationalUnit, etc
- Adds the OrganizationsDataBuilder class for querying the Organizations APIs to build
  up the data model
- Adds a CLI tool as an extra that can be installed
- Adds configuration for packaging and publishing to PyPI
- Adds Git pre-commit config w/ linting

<!--
These Markdown anchors provide a link to the diff for each release. They should be
updated any time a new release is cut.
-->
[Unreleased]: https://github.com/timoguin/aws-org-tools-py/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/timoguin/aws-org-tools-py/compare/v0.1.0-beta2...v0.1.1
[0.1.0-beta2]: https://github.com/timoguin/aws-org-tools-py/compare/v0.1.0-beta1...v0.1.0-beta2
[0.1.0-beta1]: https://github.com/timoguin/aws-org-tools-py/compare/v0.1.0-alpha4...v0.1.0-beta1
[0.1.0-alpha4]: https://github.com/timoguin/aws-org-tools-py/releases/tag/v0.1.0-alpha4
