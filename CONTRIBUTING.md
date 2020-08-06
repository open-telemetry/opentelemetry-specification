# Contributing

Welcome to OpenTelemetry specifications repository!

Before you start - see OpenTelemetry general
[contributing](https://github.com/open-telemetry/community/blob/master/CONTRIBUTING.md)
requirements and recommendations.

## Sign the CLA

Before you can contribute, you will need to sign the [Contributor License
Agreement](https://identity.linuxfoundation.org/projects/cncf).

## Proposing a change

Significant changes should go through the [RFC process](https://github.com/open-telemetry/rfcs).

## Writing specs

Specification is written in markdown format. Please make sure files are rendered
OK on GitHub.

Be sure to clearly define the specification requirements using the key words
defined in [BCP 14](https://tools.ietf.org/html/bcp14)
[[RFC2119](https://tools.ietf.org/html/rfc2119)]
[[RFC8174](https://tools.ietf.org/html/rfc8174)] while making sure to heed the
guidance laid out in [RFC2119](https://tools.ietf.org/html/rfc2119) about the
sparing use of imperatives:

> Imperatives of the type defined in this memo must be used with care
> and sparingly.  In particular, they MUST only be used where it is
> actually required for interoperation or to limit behavior which has
> potential for causing harm (e.g., limiting retransmisssions)  For
> example, they must not be used to try to impose a particular method
> on implementors where the method is not required for
> interoperability.

It is important to build a specification that is clear and useful, not
one that is needlessly restrictive and complex.

### Markdown style

Markdown files should be properly formatted before a pull request is sent out.
In this repository we follow the
[markdownlint rules](https://github.com/DavidAnson/markdownlint#rules--aliases)
with some customizations. See [markdownlint](.markdownlint.yaml) or
[settings](.vscode/settings.json) for details.

We highly encourage to use line breaks in markdown files at `80` characters
wide. There are tools that can do it for you effectively. Please submit proposal
to include your editor settings required to enable this behavior so the out of
the box settings for this repository will be consistent.

To check for style violations, use

```bash
# Ruby and gem are required for mdl
gem install mdl
mdl -c .mdlrc .
```

To fix style violations, follow the
[instruction](https://github.com/DavidAnson/markdownlint#optionsresultversion)
with the Node version of markdownlint. If you are using Visual Studio Code,
you can also use the `fixAll` command of the
[vscode markdownlint extension](https://github.com/DavidAnson/vscode-markdownlint).

### Misspell check

In addition, please make sure to clean up typos before you submit the change.

To check for typos, use

```bash
# Golang is needed for the misspell tool.
make install-misspell
make misspell
```

To quickly fix typos, use

```bash
make misspell-correction
```

## Pull Requests

### How to create a PR

Everyone is welcome to contribute to the OpenTelemetry specification via GitHub
pull requests (PRs).

To [create a new
PR](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request),
fork the project in GitHub and clone the upstream repo:

```sh
git clone https://github.com/open-telemetry/opentelemetry-specification.git
```

Add your fork as a remote:

```sh
git remote add fork https://github.com/YOUR_GITHUB_USERNAME/opentelemetry-specification.git
```

Check out a new branch, make modifications and push the branch to your fork:

```sh
$ git checkout -b feature
# edit files
$ git commit
$ git push fork feature
```

Open a pull request against the main `opentelemetry-specification` repo.

If the PR is not ready for review, please mark it as
[`draft`](https://github.blog/2019-02-14-introducing-draft-pull-requests/).

Please make sure CLA is signed and CI is clear. We don't expect people to review
and comment on a PR that doesn't have CLA signed.

### How to get your PR merged

A PR is considered to be **ready to merge** when:

* It has received more than two approvals from the [code
  owners](./.github/CODEOWNERS) (if approvals are from only one company, it
  won't count).
* There is no `request changes` from the [code owners](./.github/CODEOWNERS).
* It has been at least two working days since the last modification (except for
  the trivial updates, such like typo, cosmetic, rebase, etc.). This gives
  people reasonable time to review.
* Trivial changes (typos, cosmetic changes, CI improvements, etc.) don't have to
  wait for two days.

Any [spec
maintainers](https://github.com/open-telemetry/community/blob/master/community-members.md#specifications-and-proto) can
merge the PR once it is **ready to merge**.

If a PR has been stuck (e.g. there are lots of debates and people couldn't agree
on each other), the owner should try to get people aligned by:

* Consolidating the perspectives and putting a summary in the PR. It is
  recommended to add a link into the PR description, which points to a comment
  with a summary in the PR conversation.
* Tagging subdomain experts (by looking at the change history) in the PR asking
  for suggestion.
* Reaching out to more people on the [gitter
  channel](https://gitter.im/open-telemetry/opentelemetry-specification).
* Stepping back to see if it makes sense to narrow down the scope of the PR or
  split it up.

If none of the above worked and the PR has been stuck for more than 2 weeks, the
owner should bring it to the [OpenTelemetry Specification SIG
meeting](https://github.com/open-telemetry/community#cross-language-specification).
