# OpenTelemetry Metrics Exporter - OTLP

**Status**: [Stable](../../document-status.md)

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

OTLP Metrics Exporter MUST support both Cumulative and Delta
[Aggregation Temporality](../datamodel.md#temporality).

OTLP Metrics Exporter MUST allow the default [Aggregation
Temporality](../datamodel.md#temporality) to be specified on a
per-instrument basis, as described in
[MetricExporter](../sdk.md#metricexporter).

If the default Aggregation Temporality preference is not specified,
OTLP Metrics Exporter SHOULD use Cumulative as the default aggregation
temporality.

The exporter MUST provide configuration according to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification.
