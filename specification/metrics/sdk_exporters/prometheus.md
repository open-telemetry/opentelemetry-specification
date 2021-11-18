# OpenTelemetry Metrics Exporter - Prometheus

**Status**: [Experimental](../../document-status.md)

Prometheus Exporter is a [Pull Metric Exporter](../sdk.md#pull-metric-exporter)
which reports metrics by responding to the [Prometheus](https://prometheus.io/)
scraper requests.

Prometheus Exporter MUST support [Pull mode](../sdk.md#pull-metric-exporter).

Prometheus Exporter MUST NOT support [Push
mode](../sdk.md#push-metric-exporter).

Prometheus Exporter MUST only support [Cumulative
Temporality](../datamodel.md#temporality).

Prometheus Exporter MUST support version `0.0.4` of the [Text-based
format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#text-based-format).

Prometheus Exporter MAY support [OpenMetrics Text
Format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#openmetrics-text-format),
including the
[Exemplars](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars).
