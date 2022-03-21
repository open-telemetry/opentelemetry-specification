# OpenTelemetry Metrics Exporter - OTLP

**Status**: [Stable](../../document-status.md)

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

OTLP Metrics Exporter MUST support both Cumulative and Delta
[Aggregation Temporality](../datamodel.md#temporality).

The exporter MUST provide configuration according to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification.

If a language provides a mechanism to automatically configure a
[MetricReader](../sdk.md#metricreader) to pair with the associated
Exporter (e.g., using the [`OTEL_METRICS_EXPORTER` environment
variable](../../sdk-environment-variables.md#exporter-selection)),
then by default:

* The exporter MUST be paired with a [periodic exporting
MetricReader](../sdk.md#periodic-exporting-metricreader).
* The exporter MUST configure the default aggregation temporality on the
  basis of instrument kind using the
  `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` variable as described
  below, otherwise the exporter MUST use Cumulative as the default
  aggregation temporality for all instrument kinds.

The `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` environment variable
defines the default aggregation temporality policy
to use on the basis of instrument kind.  The recognized (case-insensitive) values are:

| Value      | Definition                                                                                                    |
|------------|---------------------------------------------------------------------------------------------------------------|
| CUMULATIVE | Choose Cumulative aggregation temporality for all instrument kinds.                                           |
| DELTA      | Choose Delta aggregation temporality for Counter, Asynchronous Counter and Histogram instrument kinds, choose Cumulative aggregation temporality for UpDownCounter and Asynchronous UpDownCounter instrument kinds. |
