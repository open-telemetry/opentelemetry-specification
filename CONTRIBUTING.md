# Contributing

Welcome to OpenTelemetry specifications repository!

Before you start - see OpenTelemetry general
[contributing](https://github.com/open-telemetry/community/blob/master/CONTRIBUTING.md)
requirements and recommendations.

## Proposing a change

Significant changes should go through the [RFC process](https://github.com/open-telemetry/rfcs).

## Writing specs

Specification is written in markdown format. Please make sure files are rendered
OK on GitHub.

We highly encourage to use line breaks in markdown files at `80` characters
wide. There are tools that can do it for you effectively. Please submit proposal
to include your editor settings required to enable this behavior so the out of
the box settings for this repository will be consistent.

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

## Sign the CLA

Before you can contribute, you will need to sign the [Contributor License
Agreement](https://identity.linuxfoundation.org/projects/cncf).
