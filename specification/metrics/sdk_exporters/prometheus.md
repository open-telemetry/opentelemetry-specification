<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Prometheus
--->

# Metrics Exporter - Prometheus

**Status**: [Development](../../document-status.md)

A Prometheus Exporter MUST be a [Pull Metric Exporter](../sdk.md#pull-metric-exporter)
which responds to HTTP requests with Prometheus metrics in the appropriate format.

OpenTelemetry metrics MUST be converted to Prometheus metrics according to the
[Prometheus Compatibility specification](../../compatibility/prometheus_and_openmetrics.md).

A Prometheus Exporter SHOULD use
[Prometheus client libraries](https://prometheus.io/docs/instrumenting/clientlibs/)
for serving Prometheus metrics. This allows the prometheus client to negotiate
the [format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md)
of the response using the `Content-Type` header. If a prometheus client library
is used, the OpenTelemetry Prometheus Exporter SHOULD be modeled as a
[custom Collector](https://prometheus.io/docs/instrumenting/writing_clientlibs/#overall-structure)
so it can be used in conjunction with existing Prometheus instrumentation.

Regardless of whether a Prometheus client library is used, the Prometheus
Exporter MUST support version `0.0.4` of the
[Text-based format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#text-based-format).
A Prometheus Exporter MAY support Exemplars and Exponential Histograms,
which are [not currently supported by the Prometheus text format](../../compatibility/prometheus_and_openmetrics.md#differences-between-prometheus-formats),
by supporting other Protocols, but is not required to implement them.

A Prometheus Exporter for an OpenTelemetry metrics SDK MUST NOT use
[Prometheus Remote Write format](https://github.com/prometheus/prometheus/blob/main/prompb/remote.proto)
or [OpenMetrics protobuf format](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#protobuf-format).

A Prometheus Exporter for an OpenTelemetry metrics SDK MUST NOT add
[explicit timestamps on Metric points](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metric).

There MUST be at most one `target` info metric exposed by an SDK
Prometheus exporter.

## Configuration

A Prometheus Exporter SHOULD support a configuration option to set the host
metrics are served on. The option MAY be named `host`, and MUST be `localhost`
by default.

A Prometheus Exporter SHOULD support a configuration option to set the port
metrics are served on. The option MAY be named `port`, and MUST be `9464` by
default.

A Prometheus Exporter MAY offer configuration to add resource attributes as metric attributes.
By default, it MUST NOT add any resource attributes as metric attributes.
The configuration SHOULD allow the user to select which resource attributes to copy (e.g.
include / exclude or regular expression based). Copied Resource attributes MUST NOT be
excluded from the `target` info metric. The option MAY be named `with_resource_constant_labels`.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [unit suffix](../../compatibility/prometheus_and_openmetrics.md#metric-metadata)
or UNIT metadata. The option MAY be named `without_units`, and MUST be `false` by default.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [type suffix](../../compatibility/prometheus_and_openmetrics.md#metric-metadata).
The option MAY be named `without_type_suffix`, and MUST be `false` by default.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [scope info](../../compatibility/prometheus_and_openmetrics.md#instrumentation-scope-1)
metric, or scope labels. The option MAY be named `without_scope_info`, and MUST be `false` by default.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [target info](../../compatibility/prometheus_and_openmetrics.md#resource-attributes-1)
metric. The option MAY be named `without_target_info`, and MUST be `false` by default.
