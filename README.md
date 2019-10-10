# OpenTelemetry Specification

![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/open-telemetry/specification.svg) ![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/tag-pre/open-telemetry/specification.svg)

![OpenTelemetry Logo](https://opentelemetry.io/img/logos/opentelemetry-horizontal-color.png)

The OpenTelemetry specification describes the cross-language requirements and expectations for all OpenTelemetry implementations.

## Table of Contents
- [Overview](specification/overview.md)
- [Library Guidelines](specification/library-guidelines.md)
  - [Package/Library Layout](specification/library-layout.md)
  - [Concurrency and Thread-Safety](specification/concurrency.md)
- API Specification
  - [DistributedContext](specification/api-distributedcontext.md)
    - [Propagators](specification/api-propagators.md)
  - [Tracing](specification/api-tracing.md)
  - [Metrics](specification/api-metrics.md)
    - [User-Facing API](specification/api-metrics-user.md)
    - [Meter API](specification/api-metrics-meter.md)
- SDK Specification
  - [Resource](specification/sdk-resource.md)
- Data Specification
  - [Semantic Conventions](specification/data-semantic-conventions.md)
  - [Protocol](specification/protocol.md)
- About the Project
  - [Timeline](#project-timeline)
  - [Versioning](#versioning)
  - [Contributions](#contributions)
  - [License](#license)

## Project Timeline

OpenTelemetry is currently under development. Check out our [current milestones](milestones.md).

## Versioning

Changes to the [specification](./specification) are versioned according to [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html) and described in [CHANGELOG.md](CHANGELOG.md). Layout changes are not versioned. Specific implementations of the specification should specify which version they implement.

Changes to the change process itself are not currently versioned but may be independently versioned in the future.

## Contributions

The change process is still evolving. For the short term, please use [issues](https://github.com/open-telemetry/specification/issues) to suggest changes and [pull requests](https://github.com/open-telemetry/specification/pulls) to suggest implementations of changes that have been discussed in a relevant issue.

We will be setting up a more complete RFC process to streamline the discussion of changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details on contribution process.

## License

By contributing to OpenTelemetry Specification repository, you agree that your contributions will be licensed under its [Apache 2.0 License](https://github.com/open-telemetry/specification/blob/master/LICENSE).
