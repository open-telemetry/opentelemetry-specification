# Semantic Conventions

**Status**: [Mixed](document-status.md)

The **Semantic Conventions** define the keys and values which describe commonly observed concepts, protocols, and operations used by applications.

OpenTelemetry defines its semantic conventions in a separate repository:
[https://github.com/open-telemetry/semantic-conventions](https://github.com/open-telemetry/semantic-conventions).

## Signal Requirements

**Status**: [Stable](document-status.md), except where otherwise specified

### Spans

Semantic conventions:

- SHOULD define span names that are the most general string identifying a
  class of spans and do not include high-cardinality values, see
  [span name](trace/api.md#span);
- (**Development**) SHOULD define the [span kind](trace/api.md#spankind) for
  each span they define;
- (**Development**) SHOULD define when span status is set to `Error` and the
  possible values of its `Description`;
- SHOULD NOT define conditions for setting span status to `Ok`, since
  instrumentations [leave it `Unset`](trace/api.md#set-status) unless
  configured otherwise;
- (**Development**) SHOULD define a [span type](trace/api.md#span-type) that
  uniquely identifies the span structure. A defined span type MUST have low
  cardinality and MUST conform to the
  [span type syntax](trace/api.md#span-type-syntax).

### Metrics

Semantic conventions:

- (**Development**) SHOULD choose metric instruments following the
  [instrument selection](metrics/supplementary-guidelines.md#instrument-selection)
  guidelines;
- MUST define metric names and units that follow the
  [instrument name syntax](metrics/api.md#instrument-name-syntax) and
  [instrument unit](metrics/api.md#instrument-unit) rules.

### Events

Semantic conventions:

- SHOULD define log records as [Events](logs/data-model.md#events);
- SHOULD define [event names](logs/data-model.md#field-eventname) that uniquely
  identify the event structure, including its attributes and body.

See the [Event format](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md)
for requirements and details.

## Reserved Attributes

**Status**: [Development](document-status.md)

Semantic conventions MUST provide the following attributes:

- [`error.type`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/error.md#error-type)
- [`exception.message`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/exception.md#exception-message)
- [`exception.stacktrace`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/exception.md#exception-stacktrace)
- [`exception.type`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/exception.md#exception-type)
- [`server.address`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/server.md#server-address)
- [`server.port`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/server.md#server-port)
- [`service.name`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/service.md#service-name)
- [`telemetry.sdk.language`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/telemetry.md#telemetry-sdk-language)
- [`telemetry.sdk.name`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/telemetry.md#telemetry-sdk-name)
- [`telemetry.sdk.version`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/telemetry.md#telemetry-sdk-version)
- [`url.scheme`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/url.md#url-scheme)

Semantic conventions MUST provide the following events:

- [`exception`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-spans.md)

## In-development Reserved Attributes

**Status**: [Development](document-status.md)

Semantic conventions MUST provide the following attributes:

- [`service.instance.id`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/service.md#service-instance-id)

## Reserved Namespace

**Status**: [Development](document-status.md)

The `otel.*` namespace is reserved for defining compatibility with
non-OpenTelemetry technologies.
