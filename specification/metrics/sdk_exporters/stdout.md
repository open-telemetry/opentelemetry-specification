# OpenTelemetry Metrics Exporter - Standard output

**Status**: [Experimental](../../document-status.md)

"Standard output" Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which outputs the metrics to
stdout/console.

[OpenTelemetry SDK](../../overview.md#sdk) authors MAY choose the best idiomatic
name for their language. For example, ConsoleExporter, StdoutExporter,
StreamExporter, etc.

"Standard output" Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../datamodel.md#temporality).

"Standard output" Metrics Exporter MUST allow [Aggregation
Temporality](../datamodel.md#temporality) to be specified, as described in
[MetricExporter](../sdk.md#metricexporter).
