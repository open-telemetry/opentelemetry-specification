# OpenTelemetry Environment Variable Specification

The goal of this specification is to unify the environment variable names between different OpenTelemetry SDK implementations. SDKs MAY choose to allow configuration via the environment variables in this specification, but are not required to. If they do, they SHOULD use the names listed in this document.

## General SDK Configuration

| Name                     | Description                                       | Default                           | Notes                               |
| ------------------------ | ------------------------------------------------- | --------------------------------- | ----------------------------------- |
| OTEL_RESOURCE_ATTRIBUTES | Key-value pairs to be used as resource attributes |                                   | See [Resource SDK](./resource/sdk.md#specifying-resource-information-via-an-environment-variable) for more details. |
| OTEL_LOG_LEVEL           | Log level used by the SDK logger                  | "info"                            |                                     |
| OTEL_PROPAGATORS         | Propagators to be used as a comma separated list  | "tracecontext,baggage"            | Values MUST be deduplicated in order to register a `Propagator` only once. Unrecognized values MUST generate a warning and be gracefully ignored. |
| OTEL_TRACE_SAMPLER       | Sampler to be used for traces                     | "parentbased_always_on"                       | See [Sampling](./trace/sdk.md#sampling) |
| OTEL_TRACE_SAMPLER_ARG   | String value to be used as the sampler argument   |                                   | The specified value will only be used if OTEL_TRACE_SAMPLER is set. Each Sampler type defines its own expected input, if any. Invalid or unrecognized input MUST be logged and MUST be otherwise ignored, i.e. the SDK MUST behave as if OTEL_TRACE_SAMPLER_ARG is not set.  |

Known values for OTEL_PROPAGATORS are: "tracecontext", "baggage", "b3", "jaeger".
Additional values can be specified in the respective SDK's documentation, in case third party `Propagator`s are supported, such as "xray" or "ottracer".

Known values for `OTEL_TRACE_SAMPLER` are:

- `"always_on"`: `AlwaysOnSampler`
- `"always_off"`: `AlwaysOffSampler`
- `"traceidratio"`: `TraceIdRatioBased`
- `"parentbased_always_on"`: `ParentBased(root=AlwaysOnSampler)`
- `"parentbased_always_off"`: `ParentBased(root=AlwaysOffSampler)`
- `"parentbased_traceidratio"`: `ParentBased(root=TraceIdRatioBased)`

Depending on the value of `OTEL_TRACE_SAMPLER`, `OTEL_TRACE_SAMPLER_ARG` may be set as follows:

- For `traceidratio` and `parentbased_traceidratio` samplers: Sampling probability, a number in the [0..1] range, e.g. "0.25".

## Batch Span Processor

| Name                           | Description                                    | Default | Notes                                                 |
| ------------------------------ | ---------------------------------------------- | ------- | ----------------------------------------------------- |
| OTEL_BSP_SCHEDULE_DELAY_MILLIS | Delay interval between two consecutive exports | 5000    |                                                       |
| OTEL_BSP_EXPORT_TIMEOUT_MILLIS | Maximum allowed time to export data            | 30000   |                                                       |
| OTEL_BSP_MAX_QUEUE_SIZE        | Maximum queue size                             | 2048    |                                                       |
| OTEL_BSP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                             | 512     | Must be less than or equal to OTEL_BSP_MAX_QUEUE_SIZE |

## Span Collection Limits

| Name                            | Description                          | Default | Notes |
| ------------------------------- | ------------------------------------ | ------- | ----- |
| OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT | Maximum allowed span attribute count | 1000    |       |
| OTEL_SPAN_EVENT_COUNT_LIMIT     | Maximum allowed span event count     | 1000    |       |
| OTEL_SPAN_LINK_COUNT_LIMIT      | Maximum allowed span link count      | 1000    |       |

## OTLP Exporter

See [OpenTelemetry Protocol Exporter Configuration Options](./protocol/exporter.md).

## Jaeger Exporter

| Name                            | Description                                       | Default                                                                                          |
| ------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| OTEL_EXPORTER_JAEGER_AGENT_HOST | Hostname for the Jaeger agent                     | "localhost"                                                                                      |
| OTEL_EXPORTER_JAEGER_AGENT_PORT | Port for the Jaeger agent                         | 6832                                                                                             |
| OTEL_EXPORTER_JAEGER_ENDPOINT   | HTTP endpoint for Jaeger traces                   | <!-- markdown-link-check-disable --> "http://localhost:14250"<!-- markdown-link-check-enable --> |
| OTEL_EXPORTER_JAEGER_USER       | Username to be used for HTTP basic authentication | -                                                                                                |
| OTEL_EXPORTER_JAEGER_PASSWORD   | Password to be used for HTTP basic authentication | -                                                                                                |

## Zipkin Exporter

| Name                          | Description                | Default                                                                                                      |
| ----------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| OTEL_EXPORTER_ZIPKIN_ENDPOINT | Endpoint for Zipkin traces | <!-- markdown-link-check-disable --> "http://localhost:9411/api/v2/spans"<!-- markdown-link-check-enable --> |

## Prometheus Exporter

| Name                          | Description                     | Default                      |
| ----------------------------- | --------------------------------| ---------------------------- |
| OTEL_EXPORTER_PROMETHEUS_HOST | Host used by the Prometheus exporter | All addresses: "0.0.0.0"|
| OTEL_EXPORTER_PROMETHEUS_PORT | Port used by the Prometheus exporter | 9464                    |

## Exporter Selection

| Name          | Description                                                                  | Default |
| ------------- | ---------------------------------------------------------------------------- | ------- |
| OTEL_EXPORTER | Exporter to be used, can be a comma-separated list to use multiple exporters | "otlp"  |

Known values for OTEL_EXPORTER are: "otlp", "jaeger", "zipkin", "prometheus", "otlp_span", "otlp_metric".

Note: "otlp" is equivalent to "otlp_span,otlp_metric".

## Language Specific Environment Variables

To ensure consistent naming across projects, this specification recommends that language specific environment variables are formed using the following convention:

```
OTEL_{LANGUAGE}_{FEATURE}
```
