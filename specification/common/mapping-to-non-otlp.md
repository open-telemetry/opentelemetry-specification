# OpenTelemetry Transformation to non-OTLP Formats

**Status**: [Stable](../document-status.md)

All OpenTelemetry concepts and data recorded using OpenTelemetry API can be
directly and precisely represented using corresponding messages and fields of
OTLP format. However, for other formats this is not always the case. Sometimes a
format will not have a native way to represent a particular OpenTelemetry
concept or a field of a concept.

This document defines the transformation between OpenTelemetry and formats other
than OTLP, for OpenTelemetry fields and concepts that have no direct semantic
equivalent in those other formats.

Note: when a format has a direct semantic equivalent for a particular field or
concept then the recommendation in this document MUST be ignored.

See also additional specific transformation rules for
[Jaeger](../trace/sdk_exporters/jaeger.md) and [Zipkin](../trace/sdk_exporters/zipkin.md).
The specific rules for Jaeger and Zipkin take precedence over the generic rules defined
in this document.

## Mappings

### InstrumentationScope

OpenTelemetry `InstrumentationScope`'s fields MUST be reported as key-value
pairs associated with the Span, Metric Data Point or LogRecord using the following mapping:

| OpenTelemetry InstrumentationScope Field | non-OTLP Key | Notes |
| ------------------- | --- | --- |
| `InstrumentationScope.name`|`otel.scope.name`|since 1.10.0|
| `InstrumentationScope.version`|`otel.scope.version`|since 1.10.0|

The following deprecated aliases MUST also be reported with exact same values for
backward compatibility reasons:

| non-OTLP Key | Alias for | Notes |
| --- | --- | --- |
|`otel.library.name`|`otel.scope.name`|deprecated since 1.10.0|
|`otel.library.version`|`otel.scope.version`|deprecated since 1.10.0|

### Span Status

Span `Status` MUST be reported as key-value pairs associated with the Span,
unless the `Status` is `UNSET`. In the latter case it MUST NOT be reported.

The following table defines the OpenTelemetry `Status`'s mapping to Span's
key-value pairs:

|OpenTelemetry Status Field|non-OTLP Key|non-OTLP Value|
|--|--|--|
|Code | `otel.status_code` | Name of the code, either `OK` or `ERROR`. MUST NOT be set if the code is `UNSET`. |
|Description | `otel.status_description` | Description of the `Status` if it has a value otherwise not set. |

### Dropped Attributes Count

OpenTelemetry dropped attributes count MUST be reported as a key-value
pair associated with the corresponding data entity (e.g. Span, Span Link, Span Event,
Metric data point, LogRecord, etc). The key name MUST be `otel.dropped_attributes_count`.

This key-value pair should only be recorded when it contains a non-zero value.

### Dropped Events Count

OpenTelemetry Span's dropped events count MUST be reported as a key-value pair
associated with the Span. The key name MUST be `otel.dropped_events_count`.

This key-value pair should only be recorded when it contains a non-zero value.

### Dropped Links Count

OpenTelemetry Span's dropped links count MUST be reported as a key-value pair
associated with the Span. The key name MUST be `otel.dropped_links_count`.

This key-value pair should only be recorded when it contains a non-zero value.

### Instrumentation Scope Attributes

Exporters to formats that don't have a concept that is equivalent to the Scope
SHOULD record the attributes at the most suitable place in their corresponding format,
typically at the Span, Metric or LogRecord equivalent.
