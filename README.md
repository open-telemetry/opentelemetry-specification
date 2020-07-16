# OpenTelemetry Specification

![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/open-telemetry/specification.svg) ![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/tag-pre/open-telemetry/specification.svg)

![OpenTelemetry Logo](https://opentelemetry.io/img/logos/opentelemetry-horizontal-color.png)

The OpenTelemetry specification describes the cross-language requirements and expectations for all OpenTelemetry implementations. Substantive changes to the specification must be proposed using the [OpenTelemetry Enhancement Proposal](https://github.com/open-telemetry/oteps) process. Small changes, such as clarifications, wording changes, spelling/grammar corrections, etc. can be made directly via pull requests.

## Table of Contents

- [Overview](specification/overview.md)
- [Glossary](specification/glossary.md)
- [Library Guidelines](specification/library-guidelines.md)
  - [Package/Library Layout](specification/library-layout.md)
  - [Concurrency and Thread-Safety](specification/concurrency.md)
- API Specification
  - [CorrelationContext](specification/correlationcontext/api.md)
    - [Propagators](specification/context/api-propagators.md)
  - [Tracing](specification/trace/api.md)
  - [Metrics](specification/metrics/api.md)
- SDK Specification
  - [Tracing](specification/trace/sdk.md)
  - [Resource](specification/resource/sdk.md)
  - [Configuration](specification/sdk-configuration.md)
- Data Specification
  - [Semantic Conventions](specification/overview.md#semantic-conventions.md)
  - [Protocol](specification/protocol/README.md)
- About the Project
  - [Timeline](#project-timeline)
  - [Notation Conventions and Compliance](#notation-conventions-and-compliance)
  - [Versioning](#versioning)
  - [Acronym](#acronym)
  - [Contributions](#contributions)
  - [License](#license)

## Project Timeline

The current project status as well as information on notable past releases is found at
[the OpenTelemetry project page](https://opentelemetry.io/project-status/).

Information about current work and future development plans is found at the
[specification development milestones](https://github.com/open-telemetry/opentelemetry-specification/milestones).

## Notation Conventions and Compliance

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in the [specification](./specification) are to be interpreted as described in [BCP 14](https://tools.ietf.org/html/bcp14) [[RFC2119](https://tools.ietf.org/html/rfc2119)] [[RFC8174](https://tools.ietf.org/html/rfc8174)] when, and only when, they appear in all capitals, as shown here.

An implementation of the [specification](./specification) is not compliant if it fails to satisfy one or more of the "MUST", "MUST NOT", "REQUIRED", "SHALL", or "SHALL NOT" requirements defined in the [specification](./specification).
Conversely, an implementation of the [specification](./specification) is compliant if it satisfies all the "MUST", "MUST NOT", "REQUIRED", "SHALL", and "SHALL NOT" requirements defined in the [specification](./specification).

## Versioning

Changes to the [specification](./specification) are versioned according to [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html) and described in [CHANGELOG.md](CHANGELOG.md). Layout changes are not versioned. Specific implementations of the specification should specify which version they implement.

Changes to the change process itself are not currently versioned but may be independently versioned in the future.

## Acronym

The official acronym used by the OpenTelemetry project is "OTel".

Please refrain from using "OT" in order to avoid confusion with the now deprecated "OpenTracing" project.

## Contributions

The change process is still evolving. For the short term, please use [issues](https://github.com/open-telemetry/specification/issues) to suggest changes and [pull requests](https://github.com/open-telemetry/specification/pulls) to suggest implementations of changes that have been discussed in a relevant issue.

We will be setting up a more complete RFC process to streamline the discussion of changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details on contribution process.

## License

By contributing to OpenTelemetry Specification repository, you agree that your contributions will be licensed under its [Apache 2.0 License](https://github.com/open-telemetry/specification/blob/master/LICENSE).
