# OpenTelemetry Protocol Collector Exporter

This document specifies the configuration options available to the OpenTelemetry Protocol (OTLP) Collector `SpanExporter` and `MetricsExporter` as well as the retry behavior.

## Configuration Options

The configuration options are configurable separately for the `SpanExporter` and the `MetricsExporter`.

| Configuration Option | Description                                                  | Default           | Env variable                                                 |
| -------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Endpoint             | target to which the exporter is going to send spans or metrics using the gRPC protocol. The valid syntax is described at https://github.com/grpc/grpc/blob/master/doc/naming.md. | `localhost:55680` | `OTEL_EXPORTER_OTLP_SPAN_ENDPOINT` `OTEL_EXPORTER_OTLP_METRIC_ENDPOINT` |
| Insecure             | whether to enable client transport security for the exporter's gRPC connection. See [grpc.WithInsecure()](https://godoc.org/google.golang.org/grpc#WithInsecure). | `false`           | `OTEL_EXPORTER_OTLP_SPAN_INSECURE` `OTEL_EXPORTER_OTLP_METRIC_INSECURE` |
| Certificate File     | certificate file for TLS credentials of gRPC client. Should only be used if `insecure` is set to `false`. | n/a               | `OTEL_EXPORTER_OTLP_SPAN_CERTIFICATE` `OTEL_EXPORTER_OTLP_METRIC_CERTIFICATE` |
| Headers              | the headers associated with gRPC requests.                   | n/a               | `OTEL_EXPORTER_OTLP_SPAN_HEADERS` `OTEL_EXPORTER_OTLP_METRIC_HEADERS` |
| Compression          | compression key for supported compression types within collector | gzip              | `OTEL_EXPORTER_OTLP_SPAN_COMPRESSION` `OTEL_EXPORTER_OTLP_METRIC_COMPRESSION` |
| Timeout              | max waiting time for the collector to process each spans or metrics batch | 60s               | `OTEL_EXPORTER_OTLP_SPAN_TIMEOUT` `OTEL_EXPORTER_OTLP_METRIC_TIMEOUT` |

## Retry

Transient errors MUST be handled with a retry strategy. This retry strategy MUST implement an exponential back-off with jitter to avoid overwhelming the destination until the network is restored or the destination has recovered.

