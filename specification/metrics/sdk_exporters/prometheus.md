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
for serving Prometheus metrics. This allows the Prometheus client to negotiate
the [format](https://github.com/prometheus/docs/blob/main/docs/instrumenting/exposition_formats.md)
of the response using the `Content-Type` header. If a Prometheus client library
is used, the OpenTelemetry Prometheus Exporter SHOULD be modeled as a
[custom Collector](https://prometheus.io/docs/instrumenting/writing_clientlibs/#overall-structure)
so it can be used in conjunction with existing Prometheus instrumentation.

Regardless of whether a Prometheus client library is used, the Prometheus
Exporter MUST support version `0.0.4` of the
[Text-based format](https://github.com/prometheus/docs/blob/main/docs/instrumenting/exposition_formats.md#text-based-format).
A Prometheus Exporter MAY support Exemplars and Exponential Histograms,
which are [not currently supported by the Prometheus text format](../../compatibility/prometheus_and_openmetrics.md#differences-between-prometheus-formats),
by supporting other Protocols, but is not required to implement them.

A Prometheus Exporter for an OpenTelemetry metrics SDK MUST NOT use
[Prometheus Remote Write format](https://github.com/prometheus/prometheus/blob/main/prompb/remote.proto)
or [OpenMetrics protobuf format](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#protobuf-format).

A Prometheus Exporter for an OpenTelemetry metrics SDK MUST NOT add
[explicit timestamps on Metric points](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#metric).

There MUST be at most one `target` info metric exposed by an SDK
Prometheus exporter.

A Prometheus Exporter MUST set
the [MetricReader](../sdk.md#metricreader) `temporality` as a function of
instrument kind to be `cumulative` for all instrument kinds.

## Configuration

A Prometheus Exporter SHOULD support a configuration option to set the host
that metrics are served on. The option MAY be named `host`, and MUST be `localhost`
by default.

A Prometheus Exporter SHOULD support a configuration option to set the port
that metrics are served on. The option MAY be named `port`, and MUST be `9464` by
default.

A Prometheus Exporter SHOULD support a configuration option to set
the [MetricReader](../sdk.md#metricreader) default `aggregation` as a function
of instrument kind. This option MAY be named `default_aggregation`, and MUST use
the [default aggregation](../sdk.md#default-aggregation) by default.

A Prometheus Exporter MAY offer configuration to add resource attributes as metric attributes.
By default, it MUST NOT add any resource attributes as metric attributes.
The configuration SHOULD allow the user to select which resource attributes to copy (e.g.
include / exclude or regular expression based). Copied Resource attributes MUST NOT be
excluded from the `target` info metric. The option MAY be named `with_resource_constant_labels`.

A Prometheus Exporter MAY support a configuration option that controls the translation of metric names from OpenTelemetry Naming Conventions to [Prometheus Naming conventions](https://prometheus.io/docs/practices/naming/).
If the Prometheus exporter supports such configuration it MUST be named to something that resembles Prometheus configuration option `translation_strategy`, and the translation options MUST be:

- `UnderscoreEscapingWithSuffixes`, the default. This fully escapes metric names for classic Prometheus metric name compatibility, and includes appending type and unit suffixes.
- `UnderscoreEscapingWithoutSuffixes`, metric names will continue to escape special characters to `_`, but suffixes won't be attached.
- `NoUTF8EscapingWithSuffixes` will disable changing special characters to `_`. Special suffixes like units and `_total` for counters will be attached.
- `NoTranslation`. This strategy bypasses all metric and label name translation, passing them through unaltered.

A Prometheus Exporter MAY support a configuration option to produce metrics without [scope labels](../../compatibility/prometheus_and_openmetrics.md#instrumentation-scope-1).
The option MAY be named `without_scope_info`, and MUST be `false` by default.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [target info](../../compatibility/prometheus_and_openmetrics.md#resource-attributes-1)
metric. The option MAY be named `without_target_info`, and MUST be `false` by default.

## Content Negotiation

A Prometheus Exporter MUST support content negotiation to allow clients to request
metrics in different formats based on the `Accept` header in HTTP requests. Content
negotiation MUST follow [Prometheus Content Negotiation guidelines](https://prometheus.io/docs/instrumenting/content_negotiation/).

### Interaction with Translation Strategy

Although a Prometheus Exporter MAY be configured with a `translation_strategy` for internal metric processing, the final output format and character escaping MUST follow what the content negotiation process determines based on the client's `Accept` header. The content negotiation requirements MUST take precedence over the configured translation strategy when determining the final output format.

Examples:

- If configured with `NoTranslation` but the client requests `escaping=underscores`, the exporter MUST apply underscore escaping.
- If configured with `UnderscoreEscapingWithSuffixes` but the client requests `escaping=allow-utf8`, there's no need to revert what has been translated since the exporter will continue to be compliant.
