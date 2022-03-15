# OpenTelemetry Metrics Exporter - In-memory

**Status**: [Stable](../../document-status.md)

In-memory Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which accumulates metrics data in the
local memory and allows to inspect it (useful for e.g. unit tests).

If a language provides a mechanism to automatically configure a
[MetricReader](../sdk.md#metricreader) to pair with the exporter (e.g., using
the
[`OTEL_METRICS_EXPORTER` environment variable](../../sdk-environment-variables.md#exporter-selection)),
by default the exporter MUST be paired with a
[periodic exporting MetricReader](../sdk.md#periodic-exporting-metricreader)
with a default `exportIntervalMilliseconds` of positive infinity (i.e., a manual
flush of the `MetricReader` is required).

In-memory Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../datamodel.md#temporality).

In-memory Metrics Exporter MUST allow [Aggregation
Temporality](../datamodel.md#temporality) to be specified, as described in
[MetricExporter](../sdk.md#metricexporter).
