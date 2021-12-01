# OpenTelemetry Metrics Exporter - OTLP

**Status**: [Stable](../../document-status.md)

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

OTLP Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../datamodel.md#temporality).

OTLP Metrics Exporter MUST allow [Aggregation
Temporality](../datamodel.md#temporality) to be specified, as described in
[MetricExporter](../sdk.md#metricexporter).

If the temporality is not specified, OTLP Metrics Exporter SHOULD use Cumulative
as the default temporality.

The exporter MUST provide configuration according to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification.

In addition, the exporter MUST provide the following configuration (note: this
section will be merged to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification once it reaches
[Stable](../../document-status.md)):

| Description | Default | Env variable |
| ----------- | ------- | ------------ |
| The preferred output [Aggregation Temporality](../datamodel.md#temporality), either `CUMULATIVE` or `DELTA` (case insensitive) | `CUMULATIVE` | `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY`
