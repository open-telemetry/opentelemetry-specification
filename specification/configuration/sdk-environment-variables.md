<!--- Hugo front matter used to generate the website version of this page:
title: Environment Variable Specification
linkTitle: Env var
aliases:
  - /docs/reference/specification/sdk-environment-variables
  - /docs/specs/otel/sdk-environment-variables
--->

# OpenTelemetry Environment Variable Specification

**Status**: [Stable](../document-status.md) except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [OpenTelemetry Environment Variable Specification](#opentelemetry-environment-variable-specification)
  - [Implementation guidelines](#implementation-guidelines)
  - [Parsing empty value](#parsing-empty-value)
  - [Configuration types](#configuration-types)
    - [Boolean](#boolean)
    - [Numeric](#numeric)
      - [Integer](#integer)
      - [Duration](#duration)
      - [Timeout](#timeout)
    - [String](#string)
      - [Enum](#enum)
  - [General SDK Configuration](#general-sdk-configuration)
  - [Batch Span Processor](#batch-span-processor)
  - [Batch LogRecord Processor](#batch-logrecord-processor)
  - [Attribute Limits](#attribute-limits)
  - [Span Limits](#span-limits)
  - [LogRecord Limits](#logrecord-limits)
  - [OTLP Exporter](#otlp-exporter)
  - [Zipkin Exporter](#zipkin-exporter)
  - [Prometheus Exporter](#prometheus-exporter)
  - [Exporter Selection](#exporter-selection)
    - [In-development Exporter Selection](#in-development-exporter-selection)
  - [Metrics SDK Configuration](#metrics-sdk-configuration)
    - [Exemplar](#exemplar)
    - [Periodic exporting MetricReader](#periodic-exporting-metricreader)
  - [Declarative configuration](#declarative-configuration)
  - [Language Specific Environment Variables](#language-specific-environment-variables)

<!-- tocstop -->

</details>

The goal of this specification is to unify the environment variable names between different OpenTelemetry implementations.

Implementations MAY choose to allow configuration via the environment variables in this specification, but are not required to.
If they do, they SHOULD use the names listed in this document.

## Implementation guidelines

Environment variables MAY be handled (implemented) directly by a component, in the SDK, or in a separate component (e.g. environment-based autoconfiguration component).

The environment-based configuration MUST have a direct code configuration equivalent.

## Parsing empty value

The SDK MUST interpret an empty value of an environment variable the same way as when the variable is unset.

## Configuration types

### Boolean

Any value that represents a Boolean MUST be set to true only by the
case-insensitive string `"true"`, meaning `"True"` or `"TRUE"` are also
accepted, as true. An implementation MUST NOT extend this definition and define
additional values that are interpreted as true. Any value not explicitly defined
here as a true value, including unset and empty values, MUST be interpreted as
false. If any value other than a true value, case-insensitive string `"false"`,
empty, or unset is used, a warning SHOULD be logged to inform users about the
fallback to false being applied. All Boolean environment variables SHOULD be
named and defined such that false is the expected safe default behavior.
Renaming or changing the default value MUST NOT happen without a major version
upgrade.

### Numeric

Variables accepting numeric values are sub-classified into:

* [Integer](#integer)
* [Duration](#duration)
* [Timeout](#timeout)

The following guidance applies to all numeric types.

> The following paragraph was added after stabilization and the requirements are
> thus qualified as "SHOULD" to allow implementations to avoid breaking changes.
> For new
> implementations, these should be treated as MUST requirements.

For variables accepting a numeric value, if the user provides a value the
implementation cannot parse, or which is outside the valid range for the
configuration item, the implementation SHOULD generate a warning and gracefully
ignore the setting, i.e., treat them as not set. In particular, implementations
SHOULD NOT assign a custom interpretation e.g. to negative values if a negative
value does not naturally apply to a configuration and does not have an
explicitly specified meaning, but treat it like any other invalid value.

For example, a value specifying a buffer size must naturally be non-negative.
Treating a negative value as "buffer everything" would be an example of such a
discouraged custom interpretation. Instead the default buffer size should be
used.

Note that this could make a difference even if the custom interpretation is
identical with the default value, because it might reset a value set from other
configuration sources with the default.

#### Integer

If an implementation chooses to support an integer-valued environment variable,
it SHOULD support non-negative values between 0 and 2³¹ − 1 (inclusive).
Individual SDKs MAY choose to support a larger range of values.

#### Duration

Any value that represents a duration MUST be an integer representing a number of
milliseconds. The value is non-negative - if a negative value is provided, the
implementation MUST generate a warning, gracefully ignore the setting and use
the default value if it is defined.

For example, the value `12000` indicates 12000 milliseconds, i.e., 12 seconds.

#### Timeout

Timeout values are similar to [duration](#duration) values, but are treated as a
separate type because of differences in how they interpret timeout zero values (
see below).

Any value that represents a timeout MUST be an integer representing a number of
milliseconds. The value is non-negative - if a negative value is provided, the
implementation MUST generate a warning, gracefully ignore the setting and use
the default value if it is defined.

For example, the value `12000` indicates 12000 milliseconds, i.e., 12 seconds.

Implementations SHOULD interpret timeout zero values (i.e. `0` indicating 0
milliseconds) as no limit (i.e. infinite). In practice, implementations MAY
treat no limit as "a very long time" and substitute a very large duration (
e.g. the maximum milliseconds representable by a 32-bit integer).

### String

String values are sub-classified into:

* [Enum][].

Normally, string values include notes describing how they are interpreted by
implementations.

#### Enum

Enum values SHOULD be interpreted in a case-insensitive manner.

For variables which accept a known value out of a set, i.e., an enum value,
implementations MAY support additional values not listed here.

For variables accepting an enum value, if the user provides a value
the implementation does not recognize, the implementation MUST generate
a warning and gracefully ignore the setting.
When reporting configuration errors, implementations SHOULD display the original
user-provided value to aid debugging.

If a null object (empty, no-op) value is acceptable, then the enum value
representing it MUST be `"none"`.

## General SDK Configuration

| Name                     | Description                                                                                                                                                 | Default                                                                                                                                                                                            | Type         | Notes                                                                                                                                                                                                                                                                                    |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| OTEL_SDK_DISABLED        | Disable the SDK for all signals                                                                                                                             | false                                                                                                                                                                                              | [Boolean][]  | If "true", a no-op SDK implementation will be used for all telemetry signals. Any other value or absence of the variable will have no effect and the SDK will remain enabled. This setting has no effect on propagators configured through the OTEL_PROPAGATORS variable.                |
| OTEL_ENTITIES            | Entity information to be associated with the resource                                                                                                       |                                                                                                                                                                                                    | [String][]   | See [Entities SDK](../entities/entity-propagation.md#specifying-entity-information-via-an-environment-variable) for more details.                                                                                                                                                        |
| OTEL_RESOURCE_ATTRIBUTES | Key-value pairs to be used as resource attributes                                                                                                           | See [Resource semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#semantic-attributes-with-dedicated-environment-variable) for details. | [String][]   | See [Resource SDK](../resource/sdk.md#specifying-resource-information-via-an-environment-variable) for more details.                                                                                                                                                                     |
| OTEL_SERVICE_NAME        | Sets the value of the [`service.name`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#service) resource attribute |                                                                                                                                                                                                    | [String][]   | If `service.name` is also provided in `OTEL_RESOURCE_ATTRIBUTES`, then `OTEL_SERVICE_NAME` takes precedence.                                                                                                                                                                             |
| OTEL_LOG_LEVEL           | Log level used by the [SDK internal logger](../error-handling.md#self-diagnostics)                                                                          | "info"                                                                                                                                                                                             | [Enum][]     |                                                                                                                                                                                                                                                                                          |
| OTEL_PROPAGATORS         | Propagators to be used as a comma-separated list                                                                                                            | "tracecontext,baggage"                                                                                                                                                                             | [Enum][]     | Values MUST be deduplicated in order to register a `Propagator` only once.                                                                                                                                                                                                               |
| OTEL_TRACES_SAMPLER      | Sampler to be used for traces                                                                                                                               | "parentbased_always_on"                                                                                                                                                                            | [Enum][]     | See [Sampling](../trace/sdk.md#sampling)                                                                                                                                                                                                                                                 |
| OTEL_TRACES_SAMPLER_ARG  | Value to be used as the sampler argument                                                                                                                    |                                                                                                                                                                                                    | See footnote | The specified value will only be used if OTEL_TRACES_SAMPLER is set. Each Sampler type defines its own expected input, if any. Invalid or unrecognized input MUST be logged and MUST be otherwise ignored, i.e. the implementation MUST behave as if OTEL_TRACES_SAMPLER_ARG is not set. |

Known values for `OTEL_PROPAGATORS` are:

- `"tracecontext"`: [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- `"baggage"`: [W3C Baggage](https://www.w3.org/TR/baggage/)
- `"b3"`: [B3 Single](../context/api-propagators.md#configuration)
- `"b3multi"`: [B3 Multi](../context/api-propagators.md#configuration)
- `"jaeger"`: [Jaeger](https://www.jaegertracing.io/sdk-migration/#propagation-format)
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
  - `endpoint`: the endpoint in form of `scheme://host:port` of gRPC server that serves the sampling strategy for the service ([sampling.proto](https://github.com/jaegertracing/jaeger-idl/blob/main/proto/api_v2/sampling.proto)).
  - `pollingIntervalMs`:  in milliseconds indicating how often the sampler will poll the backend for updates to sampling strategy.
  - `initialSamplingRate`:  in the [0..1] range, which is used as the sampling probability when the backend cannot be reached to retrieve a sampling strategy. This value stops having an effect once a sampling strategy is retrieved successfully, as the remote strategy will be used until a new update is retrieved.
  - Example: `endpoint=http://localhost:14250,pollingIntervalMs=5000,initialSamplingRate=0.25`

## Batch Span Processor

| Name                           | Description                                                      | Default | Type         | Notes                                                                             |
|--------------------------------|------------------------------------------------------------------|---------|--------------|-----------------------------------------------------------------------------------|
| OTEL_BSP_SCHEDULE_DELAY        | Delay interval (in milliseconds) between two consecutive exports | 5000    | [Duration][] |                                                                                   |
| OTEL_BSP_EXPORT_TIMEOUT        | Maximum allowed time (in milliseconds) to export data            | 30000   | [Timeout][]  |                                                                                   |
| OTEL_BSP_MAX_QUEUE_SIZE        | Maximum queue size                                               | 2048    | [Integer][]  | Valid values are positive.                                                        |
| OTEL_BSP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                                               | 512     | [Integer][]  | Must be less than or equal to OTEL_BSP_MAX_QUEUE_SIZE. Valid values are positive. |

## Batch LogRecord Processor

| Name                            | Description                                                      | Default | Type         | Notes                                                                              |
|---------------------------------|------------------------------------------------------------------|---------|--------------|------------------------------------------------------------------------------------|
| OTEL_BLRP_SCHEDULE_DELAY        | Delay interval (in milliseconds) between two consecutive exports | 1000    | [Duration][] |                                                                                    |
| OTEL_BLRP_EXPORT_TIMEOUT        | Maximum allowed time (in milliseconds) to export data            | 30000   | [Timeout][]  |                                                                                    |
| OTEL_BLRP_MAX_QUEUE_SIZE        | Maximum queue size                                               | 2048    | [Integer][]  | Valid values are positive.                                                         |
| OTEL_BLRP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                                               | 512     | [Integer][]  | Must be less than or equal to OTEL_BLRP_MAX_QUEUE_SIZE. Valid values are positive. |

## Attribute Limits

Implementations SHOULD only offer environment variables for the types of attributes, for
which that SDK implements truncation mechanism.

See the SDK [Attribute Limits](../common/README.md#attribute-limits) section for the definition of the limits.

| Name                              | Description                          | Default  | Type        | Notes                          |
|-----------------------------------|--------------------------------------|----------|-------------|--------------------------------|
| OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size | no limit | [Integer][] | Valid values are non-negative. |
| OTEL_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed attribute count      | 128      | [Integer][] | Valid values are non-negative. |

## Span Limits

See the SDK [Span Limits](../trace/sdk.md#span-limits) section for the definition of the limits.

| Name                                   | Description                                    | Default  | Type        | Notes                          |
|----------------------------------------|------------------------------------------------|----------|-------------|--------------------------------|
| OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size           | no limit | [Integer][] | Valid values are non-negative. |
| OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed span attribute count           | 128      | [Integer][] | Valid values are non-negative. |
| OTEL_SPAN_EVENT_COUNT_LIMIT            | Maximum allowed span event count               | 128      | [Integer][] | Valid values are non-negative. |
| OTEL_SPAN_LINK_COUNT_LIMIT             | Maximum allowed span link count                | 128      | [Integer][] | Valid values are non-negative. |
| OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT       | Maximum allowed attribute per span event count | 128      | [Integer][] | Valid values are non-negative. |
| OTEL_LINK_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed attribute per span link count  | 128      | [Integer][] | Valid values are non-negative. |

## LogRecord Limits

See the SDK [LogRecord Limits](../logs/sdk.md#logrecord-limits) section for the definition of the limits.

| Name                                        | Description                                | Default  | Type        | Notes                          |
|---------------------------------------------|--------------------------------------------|----------|-------------|--------------------------------|
| OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size       | no limit | [Integer][] | Valid values are non-negative. |
| OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed log record attribute count | 128      | [Integer][] | Valid values are non-negative. |

## OTLP Exporter

See [OpenTelemetry Protocol Exporter Configuration Options](../protocol/exporter.md).

## Zipkin Exporter

**Status**: [Deprecated](../document-status.md)

| Name                          | Description                                                                        | Default                              | Type        |
|-------------------------------|------------------------------------------------------------------------------------|--------------------------------------|-------------|
| OTEL_EXPORTER_ZIPKIN_ENDPOINT | Endpoint for Zipkin traces                                                         | `http://localhost:9411/api/v2/spans` | [String][]  |
| OTEL_EXPORTER_ZIPKIN_TIMEOUT  | Maximum time (in milliseconds) the Zipkin exporter will wait for each batch export | 10000                                | [Timeout][] |

Additionally, the following environment variables are reserved for future
usage in Zipkin Exporter configuration:

- `OTEL_EXPORTER_ZIPKIN_PROTOCOL`

This will be used to specify whether or not the exporter uses v1 or v2, json,
thrift or protobuf.  As of 1.0 of the specification, there
_is no specified default, or configuration via environment variables_.

## Prometheus Exporter

**Status**: [Development](../document-status.md)

| Name                          | Description                          | Default     | Type        |
|-------------------------------|--------------------------------------|-------------|-------------|
| OTEL_EXPORTER_PROMETHEUS_HOST | Host used by the Prometheus exporter | "localhost" | [String][]  |
| OTEL_EXPORTER_PROMETHEUS_PORT | Port used by the Prometheus exporter | 9464        | [Integer][] |

## Exporter Selection

We define environment variables for setting one or more exporters per signal.

| Name                  | Description                 | Default | Type     |
|-----------------------|-----------------------------|---------|----------|
| OTEL_TRACES_EXPORTER  | Trace exporter to be used   | "otlp"  | [Enum][] |
| OTEL_METRICS_EXPORTER | Metrics exporter to be used | "otlp"  | [Enum][] |
| OTEL_LOGS_EXPORTER    | Logs exporter to be used    | "otlp"  | [Enum][] |

The implementation MAY accept a comma-separated list to enable setting multiple exporters.

Known values for `OTEL_TRACES_EXPORTER` are:

- `"otlp"`: [OTLP](https://opentelemetry.io/docs/specs/otlp/)
- `"zipkin"`: [Zipkin](https://zipkin.io/zipkin-api/) (Defaults to [protobuf](https://github.com/openzipkin/zipkin-api/blob/master/zipkin.proto) format)
- `"console"`: [Standard Output](../trace/sdk_exporters/stdout.md)
- `"logging"`: [Standard Output](../trace/sdk_exporters/stdout.md). It is a deprecated value left for backwards compatibility. It SHOULD
NOT be supported by new implementations.
- `"none"`: No automatically configured exporter for traces.

Known values for `OTEL_METRICS_EXPORTER` are:

- `"otlp"`: [OTLP](https://opentelemetry.io/docs/specs/otlp/)
- `"prometheus"`: [Prometheus](https://github.com/prometheus/docs/blob/main/docs/instrumenting/exposition_formats.md)
- `"console"`: [Standard Output](../metrics/sdk_exporters/stdout.md)
- `"logging"`: [Standard Output](../metrics/sdk_exporters/stdout.md). It is a deprecated value left for backwards compatibility. It SHOULD
NOT be supported by new implementations.
- `"none"`: No automatically configured exporter for metrics.

Known values for `OTEL_LOGS_EXPORTER` are:

- `"otlp"`: [OTLP](https://opentelemetry.io/docs/specs/otlp/)
- `"console"`: [Standard Output](../logs/sdk_exporters/stdout.md)
- `"logging"`: [Standard Output](../logs/sdk_exporters/stdout.md). It is a deprecated value left for backwards compatibility. It SHOULD
NOT be supported by new implementations.
- `"none"`: No automatically configured exporter for logs.

### In-development Exporter Selection

**Status**: [Development](../document-status.md)

In addition to the above, the following environment variables are added for in-development exporter selection:

Additional known values for `OTEL_TRACES_EXPORTER` are:

- `"otlp/stdout"`: [OTLP File](../protocol/file-exporter.md) writing to standard output

Additional known values for `OTEL_METRICS_EXPORTER` are:

- `"otlp/stdout"`: [OTLP File](../protocol/file-exporter.md) writing to standard output

Additional known values for `OTEL_LOGS_EXPORTER` are:

- `"otlp/stdout"`: [OTLP File](../protocol/file-exporter.md) writing to standard output

## Metrics SDK Configuration

### Exemplar

| Name                           | Description                                         | Default         | Type     |
|--------------------------------|-----------------------------------------------------|-----------------|----------|
| `OTEL_METRICS_EXEMPLAR_FILTER` | Filter for which measurements can become Exemplars. | `"trace_based"` | [Enum][] |

Known values for `OTEL_METRICS_EXEMPLAR_FILTER` are:

- `"always_on"`: [AlwaysOn](../metrics/sdk.md#alwayson)
- `"always_off"`: [AlwaysOff](../metrics/sdk.md#alwaysoff)
- `"trace_based"`: [TraceBased](../metrics/sdk.md#tracebased)

### Periodic exporting MetricReader

Environment variables specific for the push metrics exporters (OTLP, stdout, in-memory)
that use [periodic exporting MetricReader](../metrics/sdk.md#periodic-exporting-metricreader).

| Name                          | Description                                                                   | Default | Type         |
|-------------------------------|-------------------------------------------------------------------------------|---------|--------------|
| `OTEL_METRIC_EXPORT_INTERVAL` | The time interval (in milliseconds) between the start of two export attempts. | 60000   | [Duration][] |
| `OTEL_METRIC_EXPORT_TIMEOUT`  | Maximum allowed time (in milliseconds) to export data.                        | 30000   | [Timeout][]  |

## Declarative configuration

**Status**: [Development](../document-status.md)

Environment variables involved in [declarative configuration](./README.md#declarative-configuration).

| Name                          | Description                                                                                                                                                                   | Default | Type       | Notes     |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|------------|-----------|
| OTEL_EXPERIMENTAL_CONFIG_FILE | The path of the configuration file used to configure the SDK. If set, the configuration in this file takes precedence over all other SDK configuration environment variables. |         | [String][] | See below |

If `OTEL_EXPERIMENTAL_CONFIG_FILE` is set, the file at the specified path is used to
call [Parse](./sdk.md#parse). The
resulting [configuration model](./sdk.md#in-memory-configuration-model) is
used to call [Create](./sdk.md#create) to produce fully configured
SDK components.

When `OTEL_EXPERIMENTAL_CONFIG_FILE` is set, all other environment variables
besides those referenced in the configuration file
for [environment variable substitution](./data-model.md#environment-variable-substitution)
MUST be ignored. Ignoring the environment variables is necessary because
there is no intuitive way to merge the flat environment variable scheme with the
structured file configuration scheme in all cases. Users that require merging
multiple sources of configuration are encouraged to customize the configuration
model returned by `Parse` before `Create` is called. For example, a user may
call `Parse` on multiple files and define logic from merging the resulting
configuration models, or overlay values from environment variables on top of a
configuration model. Implementations MAY provide a mechanism to customize the
configuration model parsed from `OTEL_EXPERIMENTAL_CONFIG_FILE`.

Users are encouraged to
use [`sdk-migration-config.yaml`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/examples/sdk-migration-config.yaml)
as a starting point for `OTEL_EXPERIMENTAL_CONFIG_FILE`. This file represents a
common SDK configuration scenario, and includes environment variable
substitution references to environment variables which are otherwise ignored.
Alternatively, [`sdk-config.yaml`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/examples/sdk-config.yaml)
offers a common SDK configuration starting point without environment variable
substitution references.

TODO: deprecate env vars which are not
compatible ([#3967](https://github.com/open-telemetry/opentelemetry-specification/issues/3967))

## Language Specific Environment Variables

To ensure consistent naming across projects, this specification recommends that language specific environment variables are formed using the following convention:

```
OTEL_{LANGUAGE}_{FEATURE}
```

[Boolean]: #boolean
[Float]: #float
[Integer]: #integer
[Duration]: #duration
[Timeout]: #timeout
[String]: #string
[Enum]: #enum
