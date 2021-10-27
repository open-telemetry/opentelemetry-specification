# OpenTelemetry Environment Variable Specification

**Status**: [Mixed](document-status.md)

The goal of this specification is to unify the environment variable names between different OpenTelemetry SDK implementations. SDKs MAY choose to allow configuration via the environment variables in this specification, but are not required to. If they do, they SHOULD use the names listed in this document.

## Special configuration types

**Status**: [Stable](document-status.md)

### Numeric value

If an SDK chooses to support an integer-valued environment variable, it SHOULD support nonnegative values between 0 and 2³¹ − 1 (inclusive). Individual SDKs MAY choose to support a larger range of values.

### Enum value

For variables which accept a known value out of a set, i.e., an enum value, SDK implementations MAY support additional values not listed here.
For variables accepting an enum value, if the user provides a value the SDK does not recognize, the SDK MUST generate a warning and gracefully ignore the setting.

### Duration

Any value that represents a duration, for example a timeout, MUST be an integer representing a number of
milliseconds. The value is non-negative - if a negative value is provided, the SDK MUST generate a warning,
gracefully ignore the setting and use the default value if it is defined.

For example, the value `12000` indicates 12000 milliseconds, i.e., 12 seconds.

## General SDK Configuration

**Status**: [Stable](document-status.md)

| Name                     | Description                                       | Default                           | Notes                               |
| ------------------------ | ------------------------------------------------- | --------------------------------- | ----------------------------------- |
| OTEL_RESOURCE_ATTRIBUTES | Key-value pairs to be used as resource attributes |                                   | See [Resource SDK](./resource/sdk.md#specifying-resource-information-via-an-environment-variable) for more details. |
| OTEL_SERVICE_NAME        | Sets the value of the [`service.name`](./resource/semantic_conventions/README.md#service) resource attribute | | If `service.name` is also provided in `OTEL_RESOURCE_ATTRIBUTES`, then `OTEL_SERVICE_NAME` takes precedence. |
| OTEL_LOG_LEVEL           | Log level used by the SDK logger                  | "info"                            |                                     |
| OTEL_PROPAGATORS         | Propagators to be used as a comma-separated list  | "tracecontext,baggage"            | Values MUST be deduplicated in order to register a `Propagator` only once. |
| OTEL_TRACES_SAMPLER       | Sampler to be used for traces                     | "parentbased_always_on"                       | See [Sampling](./trace/sdk.md#sampling) |
| OTEL_TRACES_SAMPLER_ARG   | String value to be used as the sampler argument   |                                   | The specified value will only be used if OTEL_TRACES_SAMPLER is set. Each Sampler type defines its own expected input, if any. Invalid or unrecognized input MUST be logged and MUST be otherwise ignored, i.e. the SDK MUST behave as if OTEL_TRACES_SAMPLER_ARG is not set.  |

Known values for OTEL_PROPAGATORS are:

- `"tracecontext"`: [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- `"baggage"`: [W3C Baggage](https://www.w3.org/TR/baggage/)
- `"b3"`: [B3 Single](./context/api-propagators.md#configuration)
- `"b3multi"`: [B3 Multi](./context/api-propagators.md#configuration)
- `"jaeger"`: [Jaeger](https://www.jaegertracing.io/docs/1.21/client-libraries/#propagation-format)
- `"xray"`: [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html#xray-concepts-tracingheader) (_third party_)
- `"ottrace"`: [OT Trace](https://github.com/opentracing?q=basic&type=&language=) (_third party_)

Known values for `OTEL_TRACES_SAMPLER` are:

- `"always_on"`: `AlwaysOnSampler`
- `"always_off"`: `AlwaysOffSampler`
- `"traceidratio"`: `TraceIdRatioBased`
- `"parentbased_always_on"`: `ParentBased(root=AlwaysOnSampler)`
- `"parentbased_always_off"`: `ParentBased(root=AlwaysOffSampler)`
- `"parentbased_traceidratio"`: `ParentBased(root=TraceIdRatioBased)`
- `"jaeger_remote"`: `JaegerRemoteSampler`
- `"xray"`: [AWS X-Ray Centralized Sampling](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-sampling.html) (_third party_)

Depending on the value of `OTEL_TRACES_SAMPLER`, `OTEL_TRACES_SAMPLER_ARG` may be set as follows:

- For `traceidratio` and `parentbased_traceidratio` samplers: Sampling probability, a number in the [0..1] range, e.g. "0.25". Default is 1.0 if unset.
- For `jaeger_remote`: The value is a comma separated list:
  - `endpoint`: the endpoint in form of `host:port` of gRPC server that serves the sampling strategy for the service ([sampling.proto](https://github.com/jaegertracing/jaeger-idl/blob/master/proto/api_v2/sampling.proto)).
  - `pollingIntervalMs`:  in milliseconds indicating how often the sampler will poll the backend for updates to sampling strategy.
  - `initialSamplingRate`:  in the [0..1] range, which is used as the sampling probability when the backend cannot be reached to retrieve a sampling strategy. This value stops having an effect once a sampling strategy is retrieved successfully, as the remote strategy will be used until a new update is retrieved.
  - Example: `endpoint=localhost:14250,pollingIntervalMs=5000,initialSamplingRate=0.25`

## Batch Span Processor

**Status**: [Stable](document-status.md)

| Name                           | Description                                    | Default | Notes                                                 |
| ------------------------------ | ---------------------------------------------- | ------- | ----------------------------------------------------- |
| OTEL_BSP_SCHEDULE_DELAY        | Delay interval between two consecutive exports | 5000    |                                                       |
| OTEL_BSP_EXPORT_TIMEOUT        | Maximum allowed time to export data            | 30000   |                                                       |
| OTEL_BSP_MAX_QUEUE_SIZE        | Maximum queue size                             | 2048    |                                                       |
| OTEL_BSP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                             | 512     | Must be less than or equal to OTEL_BSP_MAX_QUEUE_SIZE |

## Attribute Limits

SDKs SHOULD only offer environment variables for the types of attributes, for
which that SDK implements truncation mechanism.

See the SDK [Attribute Limits](common/common.md#attribute-limits) section for the definition of the limits.

| Name                              | Description                          | Default | Notes |
| --------------------------------- | ------------------------------------ | ------- | ----- |
| OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size |         | Empty value is treated as infinity. Non-integer and negative values are invalid. |
| OTEL_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed span attribute count | 128     |       |

## Span Limits <a name="span-collection-limits"></a>

**Status**: [Stable](document-status.md)

See the SDK [Span Limits](trace/sdk.md#span-limits) section for the definition of the limits.

| Name                                   | Description                                    | Default | Notes |
| -------------------------------------- | ---------------------------------------------- | ------- | ----- |
| OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT | Maximum allowed attribute value size           |         | Empty value is treated as infinity. Non-integer and negative values are invalid. |
| OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed span attribute count           | 128     |       |
| OTEL_SPAN_EVENT_COUNT_LIMIT            | Maximum allowed span event count               | 128     |       |
| OTEL_SPAN_LINK_COUNT_LIMIT             | Maximum allowed span link count                | 128     |       |
| OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT       | Maximum allowed attribute per span event count | 128     |       |
| OTEL_LINK_ATTRIBUTE_COUNT_LIMIT        | Maximum allowed attribute per span link count  | 128     |       |

## OTLP Exporter

See [OpenTelemetry Protocol Exporter Configuration Options](./protocol/exporter.md).

## Jaeger Exporter

**Status**: [Stable](document-status.md)

| Name                            | Description                                                      | Default                                                                                          |
|---------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| OTEL_EXPORTER_JAEGER_AGENT_HOST | Hostname for the Jaeger agent                                    | "localhost"                                                                                      |
| OTEL_EXPORTER_JAEGER_AGENT_PORT | Port for the Jaeger agent `compact` Thrift protocol              | 6831                                                                                             |
| OTEL_EXPORTER_JAEGER_ENDPOINT   | HTTP endpoint for Jaeger traces                                  | <!-- markdown-link-check-disable --> "http://localhost:14250"<!-- markdown-link-check-enable --> |
| OTEL_EXPORTER_JAEGER_TIMEOUT    | Maximum time the Jaeger exporter will wait for each batch export | 10s                                                                                              |
| OTEL_EXPORTER_JAEGER_USER       | Username to be used for HTTP basic authentication                | -                                                                                                |
| OTEL_EXPORTER_JAEGER_PASSWORD   | Password to be used for HTTP basic authentication                | -                                                                                                |

See [Jaeger Agent](https://www.jaegertracing.io/docs/latest/deployment/#agent) documentation.

## Zipkin Exporter

**Status**: [Stable](document-status.md)

| Name                          | Description                | Default                                                                                                      |
| ----------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| OTEL_EXPORTER_ZIPKIN_ENDPOINT | Endpoint for Zipkin traces | <!-- markdown-link-check-disable --> "http://localhost:9411/api/v2/spans"<!-- markdown-link-check-enable --> |
| OTEL_EXPORTER_ZIPKIN_TIMEOUT    | Maximum time the Zipkin exporter will wait for each batch export | 10s                                                                                              |

Addtionally, the following environment variables are reserved for future
usage in Zipkin Exporter configuration:

- `OTEL_EXPORTER_ZIPKIN_PROTOCOL`

This will be used to specify whether or not the exporter uses v1 or v2, json,
thrift or protobuf.  As of 1.0 of the specification, there
*is no specified default, or configuration via environment variables*.

## Prometheus Exporter

**Status**: [Experimental](document-status.md)

| Name                          | Description                     | Default                      |
| ----------------------------- | --------------------------------| ---------------------------- |
| OTEL_EXPORTER_PROMETHEUS_HOST | Host used by the Prometheus exporter | All addresses: "0.0.0.0"|
| OTEL_EXPORTER_PROMETHEUS_PORT | Port used by the Prometheus exporter | 9464                    |

## Exporter Selection

**Status**: [Stable](document-status.md)

We define environment variables for setting one or more exporters per signal.

| Name          | Description                                                                  | Default |
| ------------- | ---------------------------------------------------------------------------- | ------- |
| OTEL_TRACES_EXPORTER | Trace exporter to be used | "otlp"  |
| OTEL_METRICS_EXPORTER | Metrics exporter to be used | "otlp"  |

The SDK MAY accept a comma-separated list to enable setting multiple exporters.

Known values for OTEL_TRACES_EXPORTER are:

- `"otlp"`: [OTLP](./protocol/otlp.md)
- `"jaeger"`: [Jaeger gRPC](https://www.jaegertracing.io/docs/1.21/apis/#protobuf-via-grpc-stable)
- `"zipkin"`: [Zipkin](https://zipkin.io/zipkin-api/) (Defaults to [protobuf](https://github.com/openzipkin/zipkin-api/blob/master/zipkin.proto) format)
- `"none"`: No automatically configured exporter for traces.

Known values for OTEL_METRICS_EXPORTER are:

- `"otlp"`: [OTLP](./protocol/otlp.md)
- `"prometheus"`: [Prometheus](https://github.com/prometheus/docs/blob/master/content/docs/instrumenting/exposition_formats.md)
- `"none"`: No automatically configured exporter for metrics.

## Metrics SDK Configuration

**Status**: [Experimental](document-status.md)

| Name            | Description | Default | Notes |
|-----------------|---------|-------------|---------|
| `OTEL_METRICS_EXEMPLAR_FILTER` | Filter for which measurements can become Exemplars. | `"with_sampled_trace"` | |

Known values for `OTEL_METRICS_EXEMPLAR_FILTER` are:

- `"none"`: No measurements are eligble for exemplar sampling.
- `"all"`: All measurements are eligible for exemplar sampling.
- `"with_sampled_trace"`: Only allow measurements with a sampled parent span in context.

### Periodic exporting MetricReader

| Name                          | Description                                                                   | Default | Notes |
| ----------------------------- | ----------------------------------------------------------------------------- | ------- | ----- |
| `OTEL_METRIC_EXPORT_INTERVAL` | The time interval (in milliseconds) between the start of two export attempts. | 60000   |       |
| `OTEL_METRIC_EXPORT_TIMEOUT`  | Maximum allowed time (in milliseconds) to export data.                        | 30000   |       |

## Language Specific Environment Variables

To ensure consistent naming across projects, this specification recommends that language specific environment variables are formed using the following convention:

```
OTEL_{LANGUAGE}_{FEATURE}
```
