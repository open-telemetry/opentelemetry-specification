<!--- Hugo front matter used to generate the website version of this page:
title: Environment Variable Specification
linkTitle: Env var
aliases:
  - /docs/reference/specification/sdk-environment-variables
  - /docs/specs/otel/sdk-environment-variables
--->

# OpenTelemetry Environment Variable Specification

**Status**: [Mixed](../document-status.md)

The goal of this specification is to unify the environment variable names between different OpenTelemetry implementations.

Implementations MAY choose to allow configuration via the environment variables in this specification, but are not required to.
If they do, they SHOULD use the names listed in this document.

## Implementation guidelines

**Status**: [Stable](../document-status.md)

Environment variables MAY be handled (implemented) directly by a component, in the SDK, or in a separate component (e.g. environment-based autoconfiguration component).

The environment-based configuration MUST have a direct code configuration equivalent.

## Parsing empty value

**Status**: [Stable](../document-status.md)

The SDK MUST interpret an empty value of an environment variable the same way as when the variable is unset.

## Special configuration types

**Status**: [Stable](../document-status.md)

### Boolean value

Any value that represents a Boolean MUST be set to true only by the case-insensitive string `"true"`, meaning `"True"` or `"TRUE"` are also accepted, as true.
An implementation MUST NOT extend this definition and define additional values that are interpreted as true.
Any value not explicitly defined here as a true value, including unset and empty values, MUST be interpreted as false.
If any value other than a true value, case-insensitive string `"false"`, empty, or unset is used, a warning SHOULD be logged to inform users about the fallback to false being applied.
All Boolean environment variables SHOULD be named and defined such that false is the expected safe default behavior.
Renaming or changing the default value MUST NOT happen without a major version upgrade.

### Numeric value

If an implementation chooses to support an integer-valued environment variable, it SHOULD support nonnegative values between 0 and 2³¹ − 1 (inclusive). Individual SDKs MAY choose to support a larger range of values.

> The following paragraph was added after stabilization and the requirements are
thus qualified as "SHOULD" to allow implementations to avoid breaking changes.
For new
implementations, these should be treated as MUST requirements.

For variables accepting a numeric value, if the user provides a value the implementation cannot parse,
or which is outside the valid range for the configuration item, the implementation SHOULD
generate a warning and gracefully ignore the setting, i.e., treat them as not set.
In particular, implementations
SHOULD NOT assign a custom interpretation e.g. to negative values if a negative
value does not naturally apply to a configuration and does not have an explicitly specified meaning, but treat it like any other
invalid value.

For example, a value specifying a buffer size must naturally be non-negative.
Treating a negative value as "buffer everything" would be an example of such a discouraged custom interpretation.
Instead the default buffer size should be used.

Note that this could make a difference even if the custom interpretation is identical with the default value,
because it might reset a value set from other configuration sources with the default.

### Enum value

For variables which accept a known value out of a set, i.e., an enum value, implementations MAY support additional values not listed here.
For variables accepting an enum value, if the user provides a value the implementation does not recognize, the implementation MUST generate a warning and gracefully ignore the setting.

If a null object (empty, no-op) value is acceptable, then the enum value representing it MUST be `"none"`.

### Duration

Any value that represents a duration, for example a timeout, MUST be an integer representing a number of
milliseconds. The value is non-negative - if a negative value is provided, the implementation MUST generate a warning,
gracefully ignore the setting and use the default value if it is defined.

For example, the value `12000` indicates 12000 milliseconds, i.e., 12 seconds.

## General SDK Configuration

**Status**: [Stable](../document-status.md)

| Name                     | Description                                                                                                   | Default                                                                                                                                          | Notes                                                                                                                                                                                                                                                                                    |
|--------------------------|---------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| OTEL_SDK_DISABLED        | Disable the SDK for all signals                                                                               | false                                                                                                                                            | Boolean value. If "true", a no-op SDK implementation will be used for all telemetry signals. Any other value or absence of the variable will have no effect and the SDK will remain enabled. This setting has no effect on propagators configured through the OTEL_PROPAGATORS variable. |
| OTEL_RESOURCE_ATTRIBUTES | Key-value pairs to be used as resource attributes                                                             | See [Resource semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#semantic-attributes-with-dedicated-environment-variable) for details. | See [Resource SDK](../resource/sdk.md#specifying-resource-information-via-an-environment-variable) for more details.                                                                                                                                                                     |
| OTEL_SERVICE_NAME        | Sets the value of the [`service.name`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#service) resource attribute |                                                                                                                                                  | If `service.name` is also provided in `OTEL_RESOURCE_ATTRIBUTES`, then `OTEL_SERVICE_NAME` takes precedence.                                                                                                                                                                             |
| OTEL_LOG_LEVEL           | Log level used by the SDK logger                                                                              | "info"                                                                                                                                           |                                                                                                                                                                                                                                                                                          |
| OTEL_PROPAGATORS         | Propagators to be used as a comma-separated list                                                              | "tracecontext,baggage"                                                                                                                           | Values MUST be deduplicated in order to register a `Propagator` only once.                                                                                                                                                                                                               |
| OTEL_RESPONSE_PROPAGATORS| Response propagators to be used as a comma-separated list                                                     |                                                                                                                                                  | Values MUST be deduplicated in order to register a `ResponsePropagator` only once.                                                                                                                                                                                                       |
| OTEL_TRACES_SAMPLER      | Sampler to be used for traces                                                                                 | "parentbased_always_on"                                                                                                                          | See [Sampling](../trace/sdk.md#sampling)                                                                                                                                                                                                                                                 |
| OTEL_TRACES_SAMPLER_ARG  | String value to be used as the sampler argument                                                               |                                                                                                                                                  | The specified value will only be used if OTEL_TRACES_SAMPLER is set. Each Sampler type defines its own expected input, if any. Invalid or unrecognized input MUST be logged and MUST be otherwise ignored, i.e. the implementation MUST behave as if OTEL_TRACES_SAMPLER_ARG is not set.            |

Known values for `OTEL_PROPAGATORS` are:

- `"tracecontext"`: [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- `"baggage"`: [W3C Baggage](https://www.w3.org/TR/baggage/)
- `"b3"`: [B3 Single](../context/api-propagators.md#configuration)
- `"b3multi"`: [B3 Multi](../context/api-propagators.md#configuration)
- `"jaeger"`: [Jaeger](https://www.jaegertracing.io/docs/1.21/client-libraries/#propagation-format)
- `"xray"`: [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html#xray-concepts-tracingheader) (_third party_)
- `"ottrace"`: [OT Trace](https://github.com/opentracing?q=basic&type=&language=) (_third party_)
- `"none"`: No automatically configured propagator.

Known values for `OTEL_TRACES_SAMPLER` are:

- `"always_on"`: `AlwaysOnSampler`
- `"always_off"`: `AlwaysOffSampler`
- `"traceidratio"`: `TraceIdRatioBased`
- `"parentbased_always_on"`: `ParentBased(root=AlwaysOnSampler)`
- `"parentbased_always_off"`: `ParentBased(root=AlwaysOffSampler)`
- `"parentbased_traceidratio"`: `ParentBased(root=TraceIdRatioBased)`
- `"parentbased_jaeger_remote"`: `ParentBased(root=JaegerRemoteSampler)`
- `"jaeger_remote"`: `JaegerRemoteSampler`
- `"xray"`: [AWS X-Ray Centralized Sampling](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-sampling.html) (_third party_)

Depending on the value of `OTEL_TRACES_SAMPLER`, `OTEL_TRACES_SAMPLER_ARG` may be set as follows:

- For `traceidratio` and `parentbased_traceidratio` samplers: Sampling probability, a number in the [0..1] range, e.g. "0.25". Default is 1.0 if unset.
- For `jaeger_remote` and `parentbased_jaeger_remote`: The value is a comma separated list:
  - `endpoint`: the endpoint in form of `scheme://host:port` of gRPC server that serves the sampling strategy for the service ([sampling.proto](https://github.com/jaegertracing/jaeger-idl/blob/master/proto/api_v2/sampling.proto)).
  - `pollingIntervalMs`:  in milliseconds indicating how often the sampler will poll the backend for updates to sampling strategy.
  - `initialSamplingRate`:  in the [0..1] range, which is used as the sampling probability when the backend cannot be reached to retrieve a sampling strategy. This value stops having an effect once a sampling strategy is retrieved successfully, as the remote strategy will be used until a new update is retrieved.
  - Example: `endpoint=http://localhost:14250,pollingIntervalMs=5000,initialSamplingRate=0.25`

## Batch Span Processor

**Status**: [Stable](../document-status.md)

| Name                           | Description                                                      | Default  | Notes                                                 |
| ------------------------------ | ---------------------------------------------------------------- | -------  | ----------------------------------------------------- |
| OTEL_BSP_SCHEDULE_DELAY        | Delay interval (in milliseconds) between two consecutive exports | 5000     |                                                       |
| OTEL_BSP_EXPORT_TIMEOUT        | Maximum allowed time (in milliseconds) to export data            | 30000    |                                                       |
| OTEL_BSP_MAX_QUEUE_SIZE        | Maximum queue size                                               | 2048     |                                                       |
| OTEL_BSP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                                               | 512      | Must be less than or equal to OTEL_BSP_MAX_QUEUE_SIZE |

## Batch LogRecord Processor

**Status**: [Stable](../document-status.md)

| Name                            | Description                                                      | Default  | Notes                                                  |
| ------------------------------- | ---------------------------------------------------------------- | -------  | ------------------------------------------------------ |
| OTEL_BLRP_SCHEDULE_DELAY        | Delay interval (in milliseconds) between two consecutive exports | 1000     |                                                        |
| OTEL_BLRP_EXPORT_TIMEOUT        | Maximum allowed time (in milliseconds) to export data            | 30000    |                                                        |
| OTEL_BLRP_MAX_QUEUE_SIZE        | Maximum queue size                                               | 2048     |                                                        |
| OTEL_BLRP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                                               | 512      | Must be less than or equal to OTEL_BLRP_MAX_QUEUE_SIZE |

## Attribute Limits

Implementations SHOULD only offer environment variables for the types of attributes, for
which that SDK implements truncation mechanism.

See the SDK [Attribute Limits](../common/README.md#attribute-limits) section for the definition of the limits.

| Name                              | Description                          | Default | Notes |
| --------------------------------- | ------------------------------------ | ------- | ----- |
| OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size | no limit|       |
| OTEL_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed attribute count      | 128     |       |

## Span Limits

**Status**: [Stable](../document-status.md)

See the SDK [Span Limits](../trace/sdk.md#span-limits) section for the definition of the limits.

| Name                                   | Description                                    | Default | Notes |
| -------------------------------------- | ---------------------------------------------- | ------- | ----- |
| OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size           | no limit |       |
| OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed span attribute count           | 128     |       |
| OTEL_SPAN_EVENT_COUNT_LIMIT            | Maximum allowed span event count               | 128     |       |
| OTEL_SPAN_LINK_COUNT_LIMIT             | Maximum allowed span link count                | 128     |       |
| OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT       | Maximum allowed attribute per span event count | 128     |       |
| OTEL_LINK_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed attribute per span link count  | 128     |       |

## LogRecord Limits

**Status**: [Stable](../document-status.md)

See the SDK [LogRecord Limits](../logs/sdk.md#logrecord-limits) section for the definition of the limits.

| Name                                        | Description                                | Default  | Notes |
| ------------------------------------------- | -------------------------------------------| -------- | ----- |
| OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size       | no limit |       |
| OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed log record attribute count | 128      |       |

## OTLP Exporter

See [OpenTelemetry Protocol Exporter Configuration Options](../protocol/exporter.md).

## Zipkin Exporter

**Status**: [Stable](../document-status.md)

| Name                          | Description                                                                        | Default                              |
| ----------------------------- | ---------------------------------------------------------------------------------- |------------------------------------- |
| OTEL_EXPORTER_ZIPKIN_ENDPOINT | Endpoint for Zipkin traces                                                         | `http://localhost:9411/api/v2/spans` |
| OTEL_EXPORTER_ZIPKIN_TIMEOUT  | Maximum time (in milliseconds) the Zipkin exporter will wait for each batch export | 10000                                |

Additionally, the following environment variables are reserved for future
usage in Zipkin Exporter configuration:

- `OTEL_EXPORTER_ZIPKIN_PROTOCOL`

This will be used to specify whether or not the exporter uses v1 or v2, json,
thrift or protobuf.  As of 1.0 of the specification, there
_is no specified default, or configuration via environment variables_.

## Prometheus Exporter

**Status**: [Experimental](../document-status.md)

| Name                          | Description                     | Default                      |
| ----------------------------- | --------------------------------| ---------------------------- |
| OTEL_EXPORTER_PROMETHEUS_HOST | Host used by the Prometheus exporter | "localhost"             |
| OTEL_EXPORTER_PROMETHEUS_PORT | Port used by the Prometheus exporter | 9464                    |

## Exporter Selection

**Status**: [Stable](../document-status.md)

We define environment variables for setting one or more exporters per signal.

| Name          | Description                                                                  | Default |
| ------------- | ---------------------------------------------------------------------------- | ------- |
| OTEL_TRACES_EXPORTER | Trace exporter to be used | "otlp"  |
| OTEL_METRICS_EXPORTER | Metrics exporter to be used | "otlp"  |
| OTEL_LOGS_EXPORTER | Logs exporter to be used | "otlp"  |

The implementation MAY accept a comma-separated list to enable setting multiple exporters.

Known values for `OTEL_TRACES_EXPORTER` are:

- `"otlp"`: [OTLP](../protocol/otlp.md)
- `"zipkin"`: [Zipkin](https://zipkin.io/zipkin-api/) (Defaults to [protobuf](https://github.com/openzipkin/zipkin-api/blob/master/zipkin.proto) format)
- `"console"`: [Standard Output](../trace/sdk_exporters/stdout.md)
- `"logging"`: [Standard Output](../trace/sdk_exporters/stdout.md). It is a deprecated value left for backwards compatibility. It SHOULD
NOT be supported by new implementations.
- `"none"`: No automatically configured exporter for traces.

Known values for `OTEL_METRICS_EXPORTER` are:

- `"otlp"`: [OTLP](../protocol/otlp.md)
- `"prometheus"`: [Prometheus](https://github.com/prometheus/docs/blob/master/content/docs/instrumenting/exposition_formats.md)
- `"console"`: [Standard Output](../metrics/sdk_exporters/stdout.md)
- `"logging"`: [Standard Output](../metrics/sdk_exporters/stdout.md). It is a deprecated value left for backwards compatibility. It SHOULD
NOT be supported by new implementations.
- `"none"`: No automatically configured exporter for metrics.

Known values for `OTEL_LOGS_EXPORTER` are:

- `"otlp"`: [OTLP](../protocol/otlp.md)
- `"console"`: [Standard Output](../logs/sdk_exporters/stdout.md)
- `"logging"`: [Standard Output](../logs/sdk_exporters/stdout.md). It is a deprecated value left for backwards compatibility. It SHOULD
NOT be supported by new implementations.
- `"none"`: No automatically configured exporter for logs.

## Metrics SDK Configuration

**Status**: [Mixed](../document-status.md)

### Exemplar

**Status**: [Experimental](../document-status.md)

| Name            | Description | Default | Notes |
|-----------------|---------|-------------|---------|
| `OTEL_METRICS_EXEMPLAR_FILTER` | Filter for which measurements can become Exemplars. | `"trace_based"` | |

Known values for `OTEL_METRICS_EXEMPLAR_FILTER` are:

- `"always_on"`: [AlwaysOn](../metrics/sdk.md#alwayson)
- `"always_off"`: [AlwaysOff](../metrics/sdk.md#alwaysoff)
- `"trace_based"`: [TraceBased](../metrics/sdk.md#tracebased)

### Periodic exporting MetricReader

**Status**: [Stable](../document-status.md)

Environment variables specific for the push metrics exporters (OTLP, stdout, in-memory)
that use [periodic exporting MetricReader](../metrics/sdk.md#periodic-exporting-metricreader).

| Name                          | Description                                                                   | Default | Notes |
| ----------------------------- | ----------------------------------------------------------------------------- | ------- | ----- |
| `OTEL_METRIC_EXPORT_INTERVAL` | The time interval (in milliseconds) between the start of two export attempts. | 60000   |       |
| `OTEL_METRIC_EXPORT_TIMEOUT`  | Maximum allowed time (in milliseconds) to export data.                        | 30000   |       |

## Language Specific Environment Variables

To ensure consistent naming across projects, this specification recommends that language specific environment variables are formed using the following convention:

```
OTEL_{LANGUAGE}_{FEATURE}
```
