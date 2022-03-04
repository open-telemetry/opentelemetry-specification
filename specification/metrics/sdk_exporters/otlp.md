1# OpenTelemetry Metrics Exporter - OTLP

**Status**: [Stable](../../document-status.md)

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

OTLP Metrics Exporter MUST support both Cumulative and Delta
[Temporality](../datamodel.md#temporality).

OTLP Metrics Exporter MUST allow [Preferred Aggregation
Temporality](../datamodel.md#preferred-aggregation-temporality) to be specified, as described in
[MetricReader](../sdk.md#metricreader).

If the temporality preference is not specified, OTLP Metrics Exporter SHOULD use Cumulative
as the default aggregation temporality preference.

The exporter MUST provide configuration according to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification.

In addition, the exporter MUST provide the following configuration (note: this
section will be merged to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification once it reaches
[Stable](../../document-status.md)):

| Description | Default | Env variable |
| ----------- | ------- | ------------ |
| The preferred output [Aggregation Temporality](../datamodel.md#temporality), either `CUMULATIVE` or `DELTA` (case insensitive) | `CUMULATIVE` | `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY`
