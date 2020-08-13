# OpenTelemetry Protocol Exporter

This document specifies the configuration options available to the OpenTelemetry Protocol ([OTLP](https://github.com/open-telemetry/oteps/blob/master/text/0035-opentelemetry-protocol.md)) Exporter as well as the retry behavior.

## Configuration Options

The following configuration options MUST be available to configure the OTLP exporter. Each configuration option MUST be overridable by a signal specific option.

| Configuration Option | Description                                                  | Default           | Env variable                                                 |
| -------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Endpoint             | Target to which the exporter is going to send spans or metrics. This MAY be configured to include a path (e.g. `example.com/v1/traces`). | `localhost:55680` | `OTEL_EXPORTER_OTLP_ENDPOINT` `OTEL_EXPORTER_OTLP_SPAN_ENDPOINT` `OTEL_EXPORTER_OTLP_METRIC_ENDPOINT` |
| Protocol             | The protocol used to transmit the data. One of `grpc`,`http/json`,`http/proto`. | `grpc`               | `OTEL_EXPORTER_OTLP_PROTOCOL` `OTEL_EXPORTER_OTLP_SPAN_PROTOCOL` `OTEL_EXPORTER_OTLP_METRIC_PROTOCOL` |
| Insecure             | Whether to enable client transport security for the exporter's `grpc` or `http` connection. | `false`           | `OTEL_EXPORTER_OTLP_INSECURE` `OTEL_EXPORTER_OTLP_SPAN_INSECURE` `OTEL_EXPORTER_OTLP_METRIC_INSECURE` |
| Certificate File     | Certificate file for TLS credentials of gRPC client. Should only be used if `insecure` is set to `false`. | n/a               | `OTEL_EXPORTER_OTLP_CERTIFICATE` `OTEL_EXPORTER_OTLP_SPAN_CERTIFICATE` `OTEL_EXPORTER_OTLP_METRIC_CERTIFICATE` |
| Headers              | The headers associated with gRPC or HTTP requests.                   | n/a               | `OTEL_EXPORTER_OTLP_HEADERS` `OTEL_EXPORTER_OTLP_SPAN_HEADERS` `OTEL_EXPORTER_OTLP_METRIC_HEADERS` |
| Compression          | Compression key for supported compression types. Supported compression: `gzip`| no compression              | `OTEL_EXPORTER_OTLP_COMPRESSION` `OTEL_EXPORTER_OTLP_SPAN_COMPRESSION` `OTEL_EXPORTER_OTLP_METRIC_COMPRESSION` |
| Timeout              | Max waiting time for the backend to process each spans or metrics batch. | 60s               | `OTEL_EXPORTER_OTLP_TIMEOUT` `OTEL_EXPORTER_OTLP_SPAN_TIMEOUT` `OTEL_EXPORTER_OTLP_METRIC_TIMEOUT` |

Example 1

The following configuration sends all signals to the same collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=collector:55680
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

Example 2

Traces and metrics are sent to different collectors using different protocols:

```bash
export OTEL_EXPORTER_OTLP_SPAN_ENDPOINT=collector:55680
export OTEL_EXPORTER_OTLP_SPAN_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_SPAN_INSECURE=true

export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=collector.example.com/v1/metrics
export OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http
```

## Retry

[Transient errors](#transient-errors) MUST be handled with a retry strategy. This retry strategy MUST implement an exponential back-off with jitter to avoid overwhelming the destination until the network is restored or the destination has recovered. 

## Transient Errors
Transient errors are errors which expect the backend to recover. The following status codes are defined as transient errors:

| HTTP Status Code | Description |
| ---------------- | ----------- |
| 408 | Request Timeout |
| 5xx | Server Errors |

| gRPC Status Code | Description |
| ---------------- | ----------- |
| 1  | Cancelled |
| 4  | Deadline Exceeded |
| 7  | Permission Denied |
| 8  | Resource Exhausted |
| 10 | Aborted |
| 10 | Out of Range |
| 14 | Unavailable |
| 15 | Data Loss |
| 16 | Unauthenticated |

Additional details on transient errors can be found in [otep-35](https://github.com/open-telemetry/oteps/blob/master/text/0035-opentelemetry-protocol.md#export-response) for gRPC and [otep-99](https://github.com/open-telemetry/oteps/blob/master/text/0099-otlp-http.md#failures) for HTTP
