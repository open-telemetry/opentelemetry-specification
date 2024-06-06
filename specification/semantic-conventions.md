# Semantic Conventions

**Status**: [Development](document-status.md)

The **Semantic Conventions** define the keys and values which describe commonly observed concepts, protocols, and operations used by applications.

OpenTelemetry defines its semantic conventions in a separate repository:
[https://github.com/open-telemetry/semantic-conventions](https://github.com/open-telemetry/semantic-conventions).

## Reserved Attributes

Semantic conventions MUST provide the following attributes:

- Resource
  - `service.name`
  - `telemetry.sdk.language`
  - `telemetry.sdk.name`
  - `telemetry.sdk.version`
- Event
  - `exception.escaped`
  - `exception.message`
  - `exception.stacktrace`
  - `exception.type`

## In-development Reserved Attributes

Semantic conventions MUST provide the following attributes:

- Resource
  - `server.address`
  - `server.port`
  - `service.instance.id`
  - `url.scheme`

## Reserved Namespace

The `otel.*` namespace is reserved for defining compatibility with
non-opentelemetry technologies.
