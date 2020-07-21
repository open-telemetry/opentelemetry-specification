# OpenTelemetry Environment Variable Specification

The goal of this specification is to unify the environment variable names between different OpenTelemetry SDK implementations. SDKs MAY choose to allow configuration via the environment variables in this specification, but are not required to. If they do, they SHOULD use the names listed in this document.

## General SDK Configuration

| Name                 | Description                                      | Default                           | Notes                                                                                       |
| -------------------- | ------------------------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------------- |
| OTEL_RESOURCE_LABELS | Key-value pairs to be used as resource labels    |                                   | Spec details TBD. Proposal in [OTEP-111](https://github.com/open-telemetry/oteps/pull/111). |
| OTEL_LOG_LEVEL       | Log level used by the SDK logger                 | "info"                            |                                                                                             |
| OTEL_PROPAGATORS     | Propagators to be used as a comma separated list | "tracecontext,correlationcontext" |                                                                                             |

## Batch Span Processor

| Name                           | Description                                    | Default | Notes                                                 |
| ------------------------------ | ---------------------------------------------- | ------- | ----------------------------------------------------- |
| OTEL_BSP_SCHEDULE_DELAY_MILLIS | Delay interval between two consecutive exports | 5000    |                                                       |
| OTEL_BSP_EXPORT_TIMEOUT_MILLIS | Maximum allowed time to export data            | 30000   |                                                       |
| OTEL_BSP_MAX_QUEUE_SIZE        | Maximum queue size                             | 2048    |                                                       |
| OTEL_BSP_MAX_EXPORT_BATCH_SIZE | Maximum batch size                             | 512     | Must be less than or equal to OTEL_BSP_MAX_QUEUE_SIZE |

## OTLP Span Exporter

| Name                             | Description                                | Default |
| -------------------------------- | ------------------------------------------ | ------- |
| OTEL_EXPORTER_OTLP_SPAN_TIMEOUT  | Max waiting time to export each span batch | -       |
| OTEL_EXPORTER_OTLP_SPAN_ENDPOINT | Ingest endpoint for OTLP spans             | -       |

## OTLP Metric Exporter

| Name                               | Description                                  | Default |
| ---------------------------------- | -------------------------------------------- | ------- |
| OTEL_EXPORTER_OTLP_METRIC_TIMEOUT  | Max waiting time to export each metric batch | -       |
| OTEL_EXPORTER_OTLP_METRIC_ENDPOINT | Ingest endpoint for OTLP metrics             | -       |

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

## Language Specific Environment Variables

To ensure consistent naming across projects, this specification recommends that language specific environment variables are formed using the following convention:

```
OTEL_{LANGUAGE}_{FEATURE}
```
