# OpenTelemetry Specification

![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/open-telemetry/specification.svg) ![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/tag-pre/open-telemetry/specification.svg)

![OpenTelemetry Logo](https://opentelemetry.io/img/logos/opentelemetry-horizontal-color.png)

* [Layout](#layout)
  * [Terminology](#terminology)
  * [Specification](#specification)
  * [Semantic Conventions](#semantic-conventions)
* [Work Status](#work-status)
* [Versioning](#versioning)
* [Change Process](#change-process)
* [License](#license)

## Layout

### Terminology

[terminology.md](./terminology.md) provides a glossary for language commonly used throughout the OpenTelemetry project.

### Specification

The [specification directory](./specification/README.md) is the versioned OpenTelemetry standard, explaining the cross-language requirements and expectations for implementations.

### Semantic Conventions

[semantic-conventions.md](./semantic-conventions.md) describes conventional tags, log keys, etc. that should be used for common scenarios to ensure a consistent usage experience.

## Work Status

Check out [current milestones](milestones.md).

## Versioning

Changes to the content of the [specification](./specification.md) itself, including changes to [terminology](./terminology.md) and [semantic conventions](./semantic-conventions.md), are versioned according to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and described in [CHANGELOG.md](./changelog.md). Layout changes are not versioned. Specific implementations of the specification should specify which version they implement.

Changes to the change process itself are not currently versioned but may be independently versioned in the future.

## Change Process

The change process is still evolving. For the short term, please use [issues](https://github.com/open-telemetry/specification/issues) to suggest changes and [pull requests](https://github.com/open-telemetry/specification/pulls) to suggest implementations of changes that have been discussed in a relevant issue.

We will be setting up a more complete RFC process to streamline the discussion of changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details on contribution process.

## License

By contributing to OpenTelemetry Specification repository, you agree that your contributions will be licensed under its [Apache 2.0 License](https://github.com/open-telemetry/specification/blob/master/LICENSE).
