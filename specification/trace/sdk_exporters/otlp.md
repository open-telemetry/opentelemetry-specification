# OpenTelemetry Protocol Collector Exporter

This document specifies the configuration options available to the OpenTelemetry Protocol ([OTLP](https://github.com/open-telemetry/oteps/blob/master/text/0035-opentelemetry-protocol.md)) [Collector](https://github.com/open-telemetry/opentelemetry-collector) `SpanExporter` and `MetricsExporter` as well as the retry behavior.

## Configuration Options

The configuration options are configurable separately for the `SpanExporter` and the `MetricsExporter`.

| Configuration Option | Description                                                  | Default           | Env variable                                                 |
| -------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Endpoint             | Target to which the exporter is going to send spans or metrics. | `localhost:55680` | `OTEL_EXPORTER_OTLP_SPAN_ENDPOINT` `OTEL_EXPORTER_OTLP_METRIC_ENDPOINT` |
| Protocol             | The protocol used to send data to the collector. One of `grpc`,`http/json`,`http/proto`. | `grpc`               | `OTEL_EXPORTER_OTLP_SPAN_PROTOCOL` `OTEL_EXPORTER_OTLP_METRIC_PROTOCOL` |
| Insecure             | Whether to enable client transport security for the exporter's `grpc` or `http` connection. See [grpc.WithInsecure()](https://godoc.org/google.golang.org/grpc#WithInsecure). | `false`           | `OTEL_EXPORTER_OTLP_SPAN_INSECURE` `OTEL_EXPORTER_OTLP_METRIC_INSECURE` |
| Certificate File     | Certificate file for TLS credentials of gRPC client. Should only be used if `insecure` is set to `false`. | n/a               | `OTEL_EXPORTER_OTLP_SPAN_CERTIFICATE` `OTEL_EXPORTER_OTLP_METRIC_CERTIFICATE` |
| Headers              | The headers associated with gRPC or HTTP requests.                   | n/a               | `OTEL_EXPORTER_OTLP_SPAN_HEADERS` `OTEL_EXPORTER_OTLP_METRIC_HEADERS` |
| Compression          | Compression key for supported compression types within collector. Supported compression: `gzip`| no compression              | `OTEL_EXPORTER_OTLP_SPAN_COMPRESSION` `OTEL_EXPORTER_OTLP_METRIC_COMPRESSION` |
| Timeout              | Max waiting time for the collector to process each spans or metrics batch. | 60s               | `OTEL_EXPORTER_OTLP_SPAN_TIMEOUT` `OTEL_EXPORTER_OTLP_METRIC_TIMEOUT` |

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
