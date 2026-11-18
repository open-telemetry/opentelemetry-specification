# Semantic Conventions

**Status**: [Mixed](document-status.md)

The **Semantic Conventions** define the keys and values which describe commonly observed concepts, protocols, and operations used by applications.

OpenTelemetry defines its semantic conventions in a separate repository:
[https://github.com/open-telemetry/semantic-conventions](https://github.com/open-telemetry/semantic-conventions).

## Reserved Attributes

**Status**: [Stable](document-status.md)

Semantic conventions MUST provide the following attributes:

- [`error.type`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/error.md#error-type)
- [`exception.message`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/exception.md#exception-message)
- [`exception.stacktrace`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/exception.md#exception-stacktrace)
- [`exception.type`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/exception.md#exception-type)
- [`server.address`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/server.md#server-address)
- [`server.port`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/server.md#server-port)
- [`service.name`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/service.md#service-name)
- [`service.instance.id`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/service.md#service-instance-id)
- [`telemetry.sdk.language`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/telemetry.md#telemetry-sdk-language)
- [`telemetry.sdk.name`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/telemetry.md#telemetry-sdk-name)
- [`telemetry.sdk.version`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/telemetry.md#telemetry-sdk-version)
- [`url.scheme`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/url.md#url-scheme)

Semantic conventions MUST provide the following events:

- [`exception`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-spans.md)

## Reserved Namespace

**Status**: [Development](document-status.md)

The [`otel.*`](https://opentelemetry.io/docs/specs/semconv/registry/attributes/otel/)
namespace is reserved for defining compatibility with non-OpenTelemetry
technologies.
