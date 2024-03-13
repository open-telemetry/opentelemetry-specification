<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Stdout
--->

# OpenTelemetry Metrics Exporter - Standard output

**Status**: [Stable](../../document-status.md)

"Standard output" Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which outputs the metrics to
stdout/console.

The output format of the exporter is unspecified. The exporter SHOULD be
documented that its output is not a standardized format across OpenTelemetry,
nor is it a performance optimized or stable format. The documentation SHOULD
suggest the OTLP exporter for users that want a performance optimized, stable,
and standarized output format.

[OpenTelemetry SDK](../../overview.md#sdk) authors MAY choose the best idiomatic
name for their language. For example, ConsoleExporter, StdoutExporter,
StreamExporter, etc.

"Standard output" Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../data-model.md#temporality).

If a language provides a mechanism to automatically configure a
[MetricReader](../sdk.md#metricreader) to pair with the associated
exporter (e.g., using the [`OTEL_METRICS_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)), by
default the exporter MUST be paired with a [periodic exporting
MetricReader](../sdk.md#periodic-exporting-metricreader)
with a default `exportIntervalMilliseconds` of 10000.
