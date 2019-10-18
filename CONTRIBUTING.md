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
guidance layed out in [RFC2119](https://tools.ietf.org/html/rfc2119) about the
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
with some customizations. See [mdlstyle](.mdlstyle.rb) or
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
[vscode markdownlint extension](hhttps://github.com/DavidAnson/vscode-markdownlint).

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