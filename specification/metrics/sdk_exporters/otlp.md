<!--- Hugo front matter used to generate the website version of this page:
linkTitle: OTLP
--->

# Metrics Exporter - OTLP

**Status**: [Stable](../../document-status.md)

## General

OTLP Metrics Exporter is a [Push Metric
Exporter](../sdk.md#push-metric-exporter) which sends metrics via the
[OpenTelemetry Protocol](../../protocol/README.md).

OTLP Metrics Exporter MUST provide configuration to influence
the [MetricReader](../sdk.md#metricreader) output `temporality` as a function of
instrument kind. This option MAY be named `temporality`, and MUST set
temporality preference to Cumulative for all instrument kinds by default.

OTLP Metrics Exporter MUST provide configuration to influence
the [MetricReader](../sdk.md#metricreader) default `aggregation` as a function
of instrument kind. This option MAY be named `default_aggregation`, and MUST set
the [default aggregation](../sdk.md#default-aggregation) for all instrument kinds by default.

The exporter MUST provide configuration according to the [OpenTelemetry Protocol
Exporter](../../protocol/exporter.md) specification.

If a language provides a mechanism to automatically configure a
[MetricReader](../sdk.md#metricreader) to pair with the associated
Exporter (e.g., using the [`OTEL_METRICS_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)),
then by default:

* The exporter MUST be paired with a [periodic exporting
  MetricReader](../sdk.md#periodic-exporting-metricreader).
* The exporter MUST configure the default aggregation temporality on the
  basis of instrument kind using the
  `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` variable as described
  below.
* The exporter MUST configure the default aggregation on the basis of instrument kind using
  the `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION` variable as described below if it is implemented.

## Additional Environment Variable Configuration

| Name                                                       | Description                                                                                            | Default                     |
|------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|-----------------------------|
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE`        | Configure the exporter's aggregation `temporality` option (see above) on the basis of instrument kind. | `cumulative`                |
| `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION` | Configure the exporter's `default_aggregation` option (see above) for Histogram instrument kind.   | `explicit_bucket_histogram` |

The recognized (case-insensitive) values for `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` are:

* `Cumulative`: Choose cumulative aggregation temporality for all instrument kinds.
* `Delta`: Choose Delta aggregation temporality for Counter, Asynchronous Counter and Histogram instrument kinds, choose
  Cumulative aggregation for UpDownCounter and Asynchronous UpDownCounter instrument kinds.
* `LowMemory`: This configuration uses Delta aggregation temporality for Synchronous Counter and Histogram and uses Cumulative aggregation temporality for Synchronous UpDownCounter, Asynchronous Counter, and Asynchronous UpDownCounter instrument kinds.

The "LowMemory" choice is so-named because the SDK can under certain
conditions use less memory in this configuration than the others.
Comparatively, the "cumulative" choice forces the SDK to maintain a
delta-to-cumulative conversion for Synchronous Counter and Histogram
instruments, while the "delta" choice forces the SDK to maintain a
cumulative-to-delta conversion for Asynchronous Counter instruments.

The recognized (case-insensitive) values for `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION` are:

* `explicit_bucket_histogram`:
  Use [Explicit Bucket Histogram Aggregation](../sdk.md#explicit-bucket-histogram-aggregation).
* `base2_exponential_bucket_histogram`:
  Use [Base2 Exponential Bucket Histogram Aggregation](../sdk.md#base2-exponential-bucket-histogram-aggregation).

## References

- [OTEP0131 OTLP Exporters Configurable Export Behavior](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0131-otlp-export-behavior.md)
