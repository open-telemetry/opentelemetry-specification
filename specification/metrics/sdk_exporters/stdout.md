<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Stdout
--->

# Metrics Exporter - Standard output

**Status**: [Stable](../../document-status.md)

"Standard output" Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which outputs the metrics to
stdout/console.

The exporter's output format is unspecified and can vary between
implementations. Documentation SHOULD warn users about this. The following
wording is recommended (modify as needed):

> This exporter is intended for debugging and learning purposes. It is not
> recommended for production use. The output format is not standardized and can
> change at any time.
>
> If a standardized format for exporting metrics to stdout is desired, consider
> using the [File Exporter](../../protocol/file-exporter.md), if available.
> However, please review the status of the File Exporter and verify if it is
> stable and production-ready.

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
