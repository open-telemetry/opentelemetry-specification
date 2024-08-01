<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Stdout
--->

# Metrics Exporter - Standard output

**Status**: [Stable](../../document-status.md)

"Standard output" Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which outputs the metrics to
stdout/console.

[OpenTelemetry SDK](../../overview.md#sdk) authors MAY choose the best idiomatic
name for their language. For example, ConsoleExporter, StdoutExporter,
StreamExporter, etc.

"Standard output" Metrics Exporter MUST provide configuration to set
the [MetricReader](../sdk.md#metricreader) output `temporality` as a function of
instrument kind. This option MAY be named `temporality`, and MUST set
temporality to Cumulative for all instrument kinds by default.

"Standard output" Metrics Exporter MAY provide configuration to set
the [MetricReader](../sdk.md#metricreader) default `aggregation` as a function
of instrument kind. This option MAY be named `default_aggregation`, and MUST use
the [default aggregation](../sdk.md#default-aggregation) by default.

If a language provides a mechanism to automatically configure a
[MetricReader](../sdk.md#metricreader) to pair with the associated
exporter (e.g., using the [`OTEL_METRICS_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)), by
default the exporter MUST be paired with a [periodic exporting
MetricReader](../sdk.md#periodic-exporting-metricreader)
with a default `exportIntervalMilliseconds` of 10000.
