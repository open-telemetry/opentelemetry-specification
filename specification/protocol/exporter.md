# OpenTelemetry Protocol Exporter

**Status**: [Stable](../document-status.md)

This document specifies the configuration options available to the OpenTelemetry Protocol ([OTLP](https://github.com/open-telemetry/oteps/blob/main/text/0035-opentelemetry-protocol.md)) Exporter as well as the retry behavior.

## Configuration Options

The following configuration options MUST be available to configure the OTLP exporter. Each configuration option MUST be overridable by a signal specific option.

| Configuration Option | Description                                                  | Default           | Env variable                                                 |
| -------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Endpoint (OTLP/HTTP) | Target URL to which the exporter is going to send spans or metrics. The endpoint MUST be a valid URL with scheme (http or https) and host, MAY contain a port, SHOULD contain a path and MUST NOT contain other parts (such as query string or fragment). A scheme of https indicates a secure connection. When using `OTEL_EXPORTER_OTLP_ENDPOINT`, exporters MUST construct per-signal URLs as  [described below](#per-signal-urls). The per-signal endpoint configuration options take precedence and can be used to override this behavior (the URL is used as-is for them, without any modifications). See the [OTLP Specification][otlphttp-req] for more details. | `https://localhost:4318` [1] | `OTEL_EXPORTER_OTLP_ENDPOINT` `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` |
| Endpoint (OTLP/gRPC) | Target to which the exporter is going to send spans or metrics. The endpoint SHOULD accept any form allowed by the underlying gRPC client implementation. Additionally, the endpoint MUST accept a URL with a scheme of either `http` or `https`. A scheme of `https` indicates a secure connection and takes precedence over the `insecure` configuration setting. If the gRPC client implementation does not support an endpoint with a scheme of `http` or `https` then the endpoint SHOULD be transformed to the most sensible format for that implementation. | `https://localhost:4317` [1] | `OTEL_EXPORTER_OTLP_ENDPOINT` `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` |
| Insecure             | Whether to enable client transport security for the exporter's gRPC connection. This option only applies to OTLP/gRPC - OTLP/HTTP always uses the scheme provided for the `endpoint`. Implementations MAY choose to not implement the `insecure` option if it is not required or supported by the underlying gRPC client implementation. | `false` | `OTEL_EXPORTER_OTLP_INSECURE` `OTEL_EXPORTER_OTLP_SPAN_INSECURE` `OTEL_EXPORTER_OTLP_METRIC_INSECURE` |
| Certificate File     | The trusted certificate to use when verifying a server's TLS credentials. Should only be used for a secure connection. | n/a               | `OTEL_EXPORTER_OTLP_CERTIFICATE` `OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE` `OTEL_EXPORTER_OTLP_METRICS_CERTIFICATE` |
| Headers              | Key-value pairs to be used as headers associated with gRPC or HTTP requests. See [Specifying headers](./exporter.md#specifying-headers-via-environment-variables) for more details.                   | n/a               | `OTEL_EXPORTER_OTLP_HEADERS` `OTEL_EXPORTER_OTLP_TRACES_HEADERS` `OTEL_EXPORTER_OTLP_METRICS_HEADERS` |
| Compression          | Compression key for supported compression types. Supported compression: `gzip`| No value [2]          | `OTEL_EXPORTER_OTLP_COMPRESSION` `OTEL_EXPORTER_OTLP_TRACES_COMPRESSION` `OTEL_EXPORTER_OTLP_METRICS_COMPRESSION` |
| Timeout              | Maximum time the OTLP exporter will wait for each batch export. | 10s               | `OTEL_EXPORTER_OTLP_TIMEOUT` `OTEL_EXPORTER_OTLP_TRACES_TIMEOUT` `OTEL_EXPORTER_OTLP_METRICS_TIMEOUT` |
| Protocol             | The transport protocol. Options MAY include `grpc`, `http/protobuf`, and `http/json`. See [Specify Protocol](./exporter.md#specify-protocol) for more details. | `http/protobuf` [2]        | `OTEL_EXPORTER_OTLP_PROTOCOL` `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL` |

**[1]**: SDKs SHOULD default endpoint variables to use `https` scheme unless as they have good reasons to choose
`http` scheme for the default (e.g., for backward compatibility reasons in a stable SDK release).

**[2]**: If no compression value is explicitly specified, SIGs can default to the value they deem
most useful among the supported options. This is especially important in the presence of technical constraints,
e.g. directly sending telemetry data from mobile devices to backend servers.

Supported values for `OTEL_EXPORTER_OTLP_*COMPRESSION` options:

- `none` if compression is disabled.
- `gzip` is the only specified compression method for now.

<a name="per-signal-urls"></a>

### Endpoint URLs for OTLP/HTTP

Based on the environment variables above, the OTLP/HTTP exporter MUST construct URLs
for each signal as follow:

1. For the per-signal variables (`OTEL_EXPORTER_OTLP_<signal>_ENDPOINT`), the URL
   MUST be used as-is without any modification. The only exception is that if an
   URL contains no path part, the root path `/` MUST be used (see [Example 2](#example-2)).
2. If signals are sent that have no per-signal configuration from the previous point,
   `OTEL_EXPORTER_OTLP_ENDPOINT` is used as a base URL and the signals are sent
   to these paths relative to that:

   * Traces: `v1/traces`
   * Metrics: `v1/metrics`.

   Non-normatively, this could be implemented by ensuring that the base URL ends with
   a slash and then appending the relative URLs as strings.

#### Example 1

The following configuration sends all signals to the same collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318
```

Traces are sent to `http://collector:4318/v1/traces` and metrics to
`http://collector:4318/v1/metrics`.

#### Example 2

Traces and metrics are sent to different collectors and paths:

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://collector:4318
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://collector.example.com/v1/metrics
```

This will send traces directly to the root path `http://collector:4318/`
(`/v1/traces` is only automatically added when using the non-signal-specific
environment variable) and metrics
to `https://collector.example.com/v1/metrics`.

#### Example 3

The following configuration sends all signals except for metrics to the same collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318/mycollector/
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://collector.example.com/v1/metrics/
```

Traces are sent to `http://collector:4318/mycollector/v1/traces`
and metrics to `https://collector.example.com/v1/metrics/`
(other signals, would they be defined, would be sent to their specific paths
relative to `http://collector:4318/mycollector/`).

### Specify Protocol

The `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`, and `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL` environment variables specify the OTLP transport protocol. Supported values:

- `grpc` for protobuf-encoded data using gRPC wire format over HTTP/2 connection
- `http/protobuf` for protobuf-encoded data over HTTP connection
- `http/json` for JSON-encoded data over HTTP connection

**[2]**: SDKs SHOULD support both `grpc` and `http/protobuf` transports and MUST
support at least one of them. If they support only one, it SHOULD be
`http/protobuf`. They also MAY support `http/json`.

If no configuration is provided the default transport SHOULD be `http/protobuf`
unless SDKs have good reasons to choose `grpc` as the default (e.g. for backward
compatibility reasons when `grpc` was already the default in a stable SDK
release).

### Specifying headers via environment variables

The `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_EXPORTER_OTLP_TRACES_HEADERS`, `OTEL_EXPORTER_OTLP_METRICS_HEADERS` environment variables will contain a list of key value pairs, and these are expected to be represented in a format matching to the [W3C Correlation-Context](https://github.com/w3c/baggage/blob/master/baggage/HTTP_HEADER_FORMAT.md), except that additional semi-colon delimited metadata is not supported, i.e.: key1=value1,key2=value2. All attribute values MUST be considered strings.

## Retry

Transient errors MUST be handled with a retry strategy. This retry strategy MUST implement an exponential back-off with jitter to avoid overwhelming the destination until the network is restored or the destination has recovered.

For OTLP/HTTP, the errors `408 (Request Timeout)` and `5xx (Server Errors)` are defined as transient, detailed information about erros can be found in the [HTTP failures section](otlp.md#failures). For the OTLP/gRPC, the full list of the gRPC retryable status codes can be found in the [gRPC response section](otlp.md#otlpgrpc-response).

[otlphttp-req]: otlp.md#otlphttp-request
