# OpenTelemetry Metrics Exporter - OTLP

**Status**: [Stable](../../document-status.md)

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

If a language provides a mechanism to automatically configure a
[MetricReader](../sdk.md#metricreader) to pair with the exporter (e.g., using
the
[`OTEL_METRICS_EXPORTER` environment variable](../../sdk-environment-variables.md#exporter-selection)),
by default the exporter MUST be paired with a
[periodic exporting MetricReader](../sdk.md#periodic-exporting-metricreader).

OTLP Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../datamodel.md#temporality).

OTLP Metrics Exporter MUST allow the default [Aggregation
Temporality](../datamodel.md#temporality) to be specified on the basis of 
instrument kind, as described in [MetricExporter](../sdk.md#metricexporter).

If the default Aggregation Temporality is not specified, OTLP Metrics
Exporter SHOULD use Cumulative as the default.

The exporter MUST provide configuration according to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification.
