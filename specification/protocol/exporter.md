# OpenTelemetry Protocol Exporter

**Status**: [Stable](../document-status.md)

This document specifies the configuration options available to the OpenTelemetry Protocol ([OTLP](https://github.com/open-telemetry/oteps/blob/main/text/0035-opentelemetry-protocol.md)) Exporter as well as the retry behavior.

## Configuration Options

The following configuration options MUST be available to configure the OTLP exporter. Each configuration option MUST be overridable by a signal specific option.

| Configuration Option | Description                                                  | Default           | Env variable                                                 |
| -------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Endpoint (OTLP/HTTP) | Target to which the exporter is going to send spans or metrics. The endpoint MUST be a valid URL with scheme (http or https) and host, and MAY contain a port and path. A scheme of https indicates a secure connection. When using `OTEL_EXPORTER_OTLP_ENDPOINT`, exporters SHOULD follow the collector convention of appending the version and signal to the path (e.g. `v1/traces` or `v1/metrics`), if not present already. The per-signal endpoint configuration options take precedence and can be used to override this behavior. See the [OTLP Specification][otlphttp-req] for more details. | `https://localhost:4317` | `OTEL_EXPORTER_OTLP_ENDPOINT` `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` |
| Endpoint (OTLP/gRPC) | Target to which the exporter is going to send spans or metrics. The endpoint SHOULD accept any form allowed by the underlying gRPC client implementation. Additionally, the endpoint MUST accept a URL with a scheme of either `http` or `https`. A scheme of `https` indicates a secure connection and takes precedence over the `insecure` configuration setting. If the gRPC client implementation does not support an endpoint with a scheme of `http` or `https` then the endpoint SHOULD be transformed to the most sensible format for that implementation. | `https://localhost:4317` | `OTEL_EXPORTER_OTLP_ENDPOINT` `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` |
| Insecure             | Whether to enable client transport security for the exporter's gRPC connection. This option only applies to OTLP/gRPC - OTLP/HTTP always uses the scheme provided for the `endpoint`. Implementations MAY choose to not implement the `insecure` option if it is not required or supported by the underlying gRPC client implementation. | `false` | `OTEL_EXPORTER_OTLP_INSECURE` `OTEL_EXPORTER_OTLP_SPAN_INSECURE` `OTEL_EXPORTER_OTLP_METRIC_INSECURE` |
| Certificate File     | The trusted certificate to use when verifying a server's TLS credentials. Should only be used for a secure connection. | n/a               | `OTEL_EXPORTER_OTLP_CERTIFICATE` `OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE` `OTEL_EXPORTER_OTLP_METRICS_CERTIFICATE` |
| Headers              | Key-value pairs to be used as headers associated with gRPC or HTTP requests. See [Specifying headers](./exporter.md#specifying-headers-via-environment-variables) for more details.                   | n/a               | `OTEL_EXPORTER_OTLP_HEADERS` `OTEL_EXPORTER_OTLP_TRACES_HEADERS` `OTEL_EXPORTER_OTLP_METRICS_HEADERS` |
| Compression          | Compression key for supported compression types. Supported compression: `gzip`| No value              | `OTEL_EXPORTER_OTLP_COMPRESSION` `OTEL_EXPORTER_OTLP_TRACES_COMPRESSION` `OTEL_EXPORTER_OTLP_METRICS_COMPRESSION` |
| Timeout              | Maximum time the OTLP exporter will wait for each batch export. | 10s               | `OTEL_EXPORTER_OTLP_TIMEOUT` `OTEL_EXPORTER_OTLP_TRACES_TIMEOUT` `OTEL_EXPORTER_OTLP_METRICS_TIMEOUT` |

Supported values for `OTEL_EXPORTER_OTLP_*COMPRESSION` options:

- If the value is missing, then compression is disabled.
- `gzip` is the only specified compression method for now. Other options MAY be supported by language SDKs and should be documented for each particular language.

Example 1

The following configuration sends all signals to the same collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
```

Example 2

Traces and metrics are sent to different collectors:

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://collector:4317

export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://collector.example.com/v1/metrics
```

### Specify Protocol

Currently, OTLP supports the following transport protocols:

- `grpc` for protobuf-encoded data using gRPC wire format over HTTP/2 connection
- `http/protobuf` for protobuf-encoded data over HTTP connection
- `http/json` for JSON-encoded data over HTTP connection

SDKs MUST support either `grpc` or `http/protobuf` and SHOULD support both. They also MAY support `http/json`.

As of 1.0 of the specification, there *is no specified default, or configuration via environment variables*.  We
reserve the following environment variables for configuration of protocols in
the future:

- `OTEL_EXPORTER_OTLP_PROTOCOL`
- `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`
- `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL`

SDKs have an unspecified default, if no configuration is provided.

### Specifying headers via environment variables

The `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_EXPORTER_OTLP_TRACES_HEADERS`, `OTEL_EXPORTER_OTLP_METRICS_HEADERS` environment variables will contain a list of key value pairs, and these are expected to be represented in a format matching to the [W3C Correlation-Context](https://github.com/w3c/baggage/blob/master/baggage/HTTP_HEADER_FORMAT.md), except that additional semi-colon delimited metadata is not supported, i.e.: key1=value1,key2=value2. All attribute values MUST be considered strings.

## Retry

Transient errors MUST be handled with a retry strategy. This retry strategy MUST implement an exponential back-off with jitter to avoid overwhelming the destination until the network is restored or the destination has recovered.

For OTLP/HTTP, the errors `408 (Request Timeout)` and `5xx (Server Errors)` are defined as transient, detailed information about erros can be found in the [HTTP failures section](otlp.md#failures). For the OTLP/gRPC, the full list of the gRPC retryable status codes can be found in the [gRPC response section](otlp.md#otlpgrpc-response).

[otlphttp-req]: otlp.md#otlphttp-request
