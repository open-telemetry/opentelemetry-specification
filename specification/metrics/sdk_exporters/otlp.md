<!--- Hugo front matter used to generate the website version of this page:
linkTitle: OTLP
--->

# OpenTelemetry Metrics Exporter - OTLP

**Status**: [Mixed](../../document-status.md)

## General

**Status**: [Stable](../../document-status.md)

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

OTLP Metrics Exporter MUST support both Cumulative and Delta
[Aggregation Temporality](../data-model.md#temporality).

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
  below.
* The exporter MUST configure the default aggregation on the basis of instrument kind using
  the `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION` variable as described below if it is implemented.

## Additional Configuration

**Status**: [Mixed](../../document-status.md)

| Name                                                | Status       | Description                                                         | Default                     |
|-----------------------------------------------------|--------------|---------------------------------------------------------------------|-----------------------------|
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | Stable       | The aggregation temporality to use on the basis of instrument kind. | `cumulative`                |
| `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION`  | Experimental | The default aggregation to use for histogram instruments.           | `explicit_bucket_histogram` |

The recognized (case-insensitive) values for `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` are:

* `cumulative`: Choose cumulative aggregation temporality for all instrument kinds.
* `delta`: Choose Delta aggregation temporality for Counter, Asynchronous Counter and Histogram instrument kinds, choose
  Cumulative aggregation for UpDownCounter and Asynchronous UpDownCounter instrument kinds.

The recognized (case-insensitive) values for `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION` are:

* `explicit_bucket_histogram`:
  Use [Explicit Bucket Histogram Aggregation](../sdk.md#explicit-bucket-histogram-aggregation).
* `exponential_bucket_histogram`:
  Use [Exponential Bucket Histogram Aggregation](../sdk.md#exponential-bucket-histogram-aggregation).
