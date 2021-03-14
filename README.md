# Repo Template

This repository is a very basic template for a new repository hosted on GitHub. It
contains the following boilerplate:

- CHANGELOG.md
- LICENSE
- README.md
- GitHub CODEOWNERS
- Code of Conduct
- Contributing Guide
- Security Guide
- Empty dirs for GitHub Issue and PR templates
- Empty dir for GitHub Actions workflows
- Large .gitignore file

## Usage

I highly recommened the [GitHub CLI](https://cli.github.com) for interacting with the
various GitHub APIs.

To create a new repository from this template, you can do the following:

```
$ gh repo create YOUR_GITHUB_USER/YOUR_GITHUB_REPO --description "A description of your repository" --template timoguin/repo-template --confirm
```

Since this is a very basic template, you will need to populate or modify some aspects
of the repo contents after initial creation.

Here are the steps:

- Update this [README].
- Update [CODEOWNERS]. This is used by GitHub for code reviews.
- Update the [LICENSE]. By default, this template includes the MIT license text.
- Update the [CHANGELOG] to include links for your specific repository. 
- Update the [Contributing Guide]. By default, this template includes text describing
  an opinionated fork-based workflow.
- Update the [Code of Conduct] and insert your preferred contact method in the
  [Enforcement] section. By default, this template includes the text from v2.0 of the
  [Contributor Covenant].
- Update the [Security Guide] to detail the process for reporting security issues.
- If you want to use [Issue Templates], add them to the [ISSUE_TEMPLATE] directory.
- If you want to use [Pull Request Templates], add them to the
  [PULL_REQUEST_TEMPLATE] directory.
- If you want to use [GitHub Actions], add workflow definitions to the [workflows]
  directory.
- Edit the [gitignore] file to your preferences. The included on is quite large and
  includes a swath of patterns for various languages, tooling, and operating systems.

And here is a sed-based method example to help with some of the more basic
search-and-replace tasks:

```
$ export NAME="Your Name"
$ export EMAIL="example@example.com"
$ export GITHUB_USER="YOUR_GITHUB_USER"
$ export GITHUB_REPO="YOUR_REPO"

# For OS X, use gsed. Otherwise you will get the error "invalid command code C".  See
# the below this code snippet.
alias sed=gsed

$ echo -e "# $GITHUB_REPO\n\nThis is my README, and I hope you will READ it." > README.md
$ sed -i "s/@timoguin/@$GITHUB_USER/; s/Tim O'Guin/$NAME/; s/timoguin@gmail.com/$EMAIL/; s/timoguin\/repo-template/$GITHUB_USER\/$GITHUB_REPO/; s/2021 /$(date +'%Y') /" CHANGELOG.md LICENSE .github/CODEOWNERS .github/*.md
```

**NOTE**: if you are using OS X, you will need [GNU Sed] to support the -i flag for
in-place file modifications.


<!-- Markdown anchors -->
[README]: README.md
[CODEOWNERS]: .github/CODEOWNERS
[LICENSE]: LICENSE
[CHANGELOG]: CHANGELOG.md
[Contributing Guide]: .github/CONTRIBUTING.md
[Code of Conduct]: .github/CODE_OF_CONDUCT.md
[Enforcement]: .github/CODE_OF_CONDUCT.md#Enforcement
[Contributor Covenant]: https://www.contributor-covenant.org/version/2/0/code_of_conduct/
[Security Guide]: .github/SECURITY.md
[Issue Templates]: https://docs.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository
[ISSUE_TEMPLATE]: .github/ISSUE_TEMPLATE
[Pull Request Templates]: https://docs.github.com/en/github/building-a-strong-community/creating-a-pull-request-template-for-your-repository
[PULL_REQUEST_TEMPLATE]: .github/PULL_REQUEST_TEMPLATE
[GitHub Actions]: https://docs.github.com/en/actions
[workflows]: .github/workflows
[gitignore]: .gitignore
[GNU Sed]: https://formulae.brew.sh/formula/gnu-sed
