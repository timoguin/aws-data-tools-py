# AWS Organizations Tools Python

An opionated Python package with libraries for querying and transforming data from the
AWS Organizations APIs, as well as a CLI interface.

This is in early development.

## Installing

---

**NOTE**: None of the following installation methods actually work. This is stubbed out
to include possible future installation methods.

---

Using pip should work on any system with at least Python 3.9:

`$ pip install aws-org-tools`

### MacOS

With homebrew:

`$ brew install aws-org-tools-py`

Using the pkg installer:

(This isn't how we'll want to do this. We want to bundle the application with _all_ its
dependencies, including Python itself. This probably means using pyInstaller to bundle
an "app" image.)

```
$ LATEST=$(gh release list --repo timoguin/aws-org-tools-py | grep 'Latest' | cut -f1)
$ curl -sL https://github.com/segmentio/aws-okta/releases/download/aws-org-tools-py.pkg --output aws-org-tools-py_$LATEST.pkg
$ installer -pkg aws-org-tools.py_$LATEST.pkg -target /usr/local/bin
```

### Windows

With chocolatey:

`$ choco install aws-org-tools-py`

With MSI:

## Usage

Empty.
