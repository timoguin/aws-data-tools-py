# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!--
Notes for any unreleased changes do here. When a new release is cut, move these from
the unreleased section to the section for the new release.
-->

No unreleased changes.

### Added

- Adds an `organization lookup-accounts` CLI command
- Adds a `field` argument to `ModelBase.as_dict()` to dump a single field in a model
- Adds configurations for tox and other testing tools
- Adds a quickstart to the top of the README

### Changed

- Refactors `OrganizationDataBuilder` to allow more control over pulling data

## [0.1.0-beta1] - 2020-06-09

### Changed

- Moves APIClient class to `aws_data_tools.client.APIClient`
- Cleans up README
- Bumps version to 0.1.0-beta1
- Adds a CI config for Semantic Pull Requests

## [0.1.0-alpha4] - 2020-06-09

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
[Unreleased]: https://github.com/timoguin/aws-org-tools-py/compare/v0.1.0-beta-1...HEAD
[0.1.0-beta1]: https://github.com/timoguin/aws-org-tools-py/compare/v0.1.0-alpha4...v0.1.0-beta1
[0.1.0-alpha4]: https://github.com/timoguin/aws-org-tools-py/releases/tag/v0.1.0-alpha4
