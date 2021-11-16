# OpenTelemetry Metrics Exporter - In-memory

**Status**: [Feature-freeze](../../document-status.md)

In-memory Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which accumulates metrics data in the
local memory and allows to inspect it (useful for e.g. unit tests).

In-memory Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../datamodel.md#temporality).

In-memory Metrics Exporter MUST allow [Aggregation
Temporality](../datamodel.md#temporality) to be specified, as described in
[MetricExporter](../sdk.md#metricexporter).
