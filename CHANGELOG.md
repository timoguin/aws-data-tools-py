# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<!--
Notes for any unreleased changes do here. When a new release is cut, move these from
the unreleased section to the section for the new release.
-->

Upcoming changes.

### Added

### Changed

### Removed

## [0.0.1-alpha3] - 2020-06-09

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
[Unreleased]: https://github.com/timoguin/aws-org-tools-py/compare/v0.0.1-alpha3...HEAD
[0.0.1-alpha3]: https://github.com/timoguin/aws-org-tools-py/releases/tag/v0.0.1-alpha3
