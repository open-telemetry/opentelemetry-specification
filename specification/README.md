<!--- Hugo front matter used to generate the website version of this page:
linkTitle: OTel spec
no_list: true
cascade:
  body_class: otel-docs-spec
  github_repo: &repo https://github.com/open-telemetry/opentelemetry-specification
  github_subdir: specification
  path_base_for_github_subdir: tmp/otel/specification
  github_project_repo: *repo
path_base_for_github_subdir:
  from: tmp/otel/specification/_index.md
  to: README.md
--->

# OpenTelemetry Specification

## Contents

- [Overview](overview.md)
- [Glossary](glossary.md)
- [Versioning and stability for OpenTelemetry clients](versioning-and-stability.md)
- [Library Guidelines](library-guidelines.md)
  - [Package/Library Layout](library-layout.md)
  - [General error handling guidelines](error-handling.md)
- API Specification
  - [Context](context/README.md)
    - [Propagators](context/api-propagators.md)
  - [Baggage](baggage/api.md)
  - [Tracing](trace/api.md)
  - [Metrics](metrics/api.md)
  - [Logs](logs/README.md)
    - [API](logs/api.md)
    - [Event API](logs/event-api.md)
- SDK Specification
  - [Tracing](trace/sdk.md)
  - [Metrics](metrics/sdk.md)
  - [Logs](logs/sdk.md)
  - [Resource](resource/sdk.md)
  - [Configuration](configuration/README.md)
- Data Specification
  - [Semantic Conventions](overview.md#semantic-conventions)
  - [Protocol](protocol/README.md)
    - [Metrics](metrics/data-model.md)
    - [Logs](logs/data-model.md)
  - Compatibility
    - [OpenCensus](compatibility/opencensus.md)
    - [OpenTracing](compatibility/opentracing.md)
    - [Prometheus and OpenMetrics](compatibility/prometheus_and_openmetrics.md)
    - [Trace Context in non-OTLP Log Formats](compatibility/logging_trace_context.md)

## Notation Conventions and Compliance

The keywords "MUST", "MUST NOT", "REQUIRED", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in the
[specification][] are to be interpreted as described in [BCP
14](https://tools.ietf.org/html/bcp14)
[[RFC2119](https://tools.ietf.org/html/rfc2119)]
[[RFC8174](https://tools.ietf.org/html/rfc8174)] when, and only when, they
appear in all capitals, as shown here.

An implementation of the [specification][] is not compliant if it fails to
satisfy one or more of the "MUST", "MUST NOT", "REQUIRED",
requirements defined in the [specification][]. Conversely, an
implementation of the [specification][] is compliant if it satisfies all the
"MUST", "MUST NOT", "REQUIRED", requirements defined in the [specification][].

## Project Naming

- The official project name is "OpenTelemetry" (with no space between "Open" and
  "Telemetry").
- The official acronym used by the OpenTelemetry project is "OTel". "OT" MAY be
  used only as a part of a longer acronym, such as OTCA (OpenTelemetry Certified Associate).
- The official names for sub-projects, like language specific implementations,
  follow the pattern of "OpenTelemetry {the name of the programming language,
  runtime or component}", for example, "OpenTelemetry Python", "OpenTelemetry
  .NET" or "OpenTelemetry Collector".

## About the project

See the [project repository][] for information about the following, and more:

- [Change / contribution process](../README.md#change--contribution-process)
- [Project timeline](../README.md#project-timeline)
- [Versioning the specification](../README.md#versioning-the-specification)
- [License](../README.md#license)

[project repository]: https://github.com/open-telemetry/opentelemetry-specification
[specification]: overview.md
