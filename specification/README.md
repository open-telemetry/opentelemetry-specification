# OpenTelemetry Specification

## Contents

- [Overview](overview.md)
- [Glossary](glossary.md)
- [Versioning and stability for OpenTelemetry clients](versioning-and-stability.md)
- [Library Guidelines](library-guidelines.md)
  - [Package/Library Layout](library-layout.md)
  - [General error handling guidelines](error-handling.md)
- API Specification
  - [Context](context/context.md)
    - [Propagators](context/api-propagators.md)
  - [Baggage](baggage/api.md)
  - [Tracing](trace/api.md)
  - [Metrics](metrics/api.md)
- SDK Specification
  - [Tracing](trace/sdk.md)
  - [Metrics](metrics/sdk.md)
  - [Resource](resource/sdk.md)
  - [Configuration](sdk-configuration.md)
- Data Specification
  - [Semantic Conventions](overview.md#semantic-conventions)
  - [Protocol](protocol/README.md)
    - [Metrics](metrics/datamodel.md)
    - [Logs](logs/data-model.md)

## Notation Conventions and Compliance

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in the
[specification][] are to be interpreted as described in [BCP
14](https://tools.ietf.org/html/bcp14)
[[RFC2119](https://tools.ietf.org/html/rfc2119)]
[[RFC8174](https://tools.ietf.org/html/rfc8174)] when, and only when, they
appear in all capitals, as shown here.

An implementation of the [specification][] is not compliant if it fails to
satisfy one or more of the "MUST", "MUST NOT", "REQUIRED", "SHALL", or "SHALL
NOT" requirements defined in the [specification][]. Conversely, an
implementation of the [specification][] is compliant if it satisfies all the
"MUST", "MUST NOT", "REQUIRED", "SHALL", and "SHALL NOT" requirements defined in
the [specification][].

## Acronym

- The official acronym used by the OpenTelemetry project is "OTel".
- Refrain from using "OT" in order to avoid confusion with the now deprecated
  "OpenTracing" project.

## About the project

See the [project repository][] for information about the following, and more:

- [Change / contribution process](../README.md#change--contribution-process)
- [Project timeline](../README.md#project-timeline)
- [Versioning the specification](../README.md#versioning-the-specification)
- [License](../README.md#license)

[project repository]: https://github.com/open-telemetry/opentelemetry-specification
[specification]: overview.md
