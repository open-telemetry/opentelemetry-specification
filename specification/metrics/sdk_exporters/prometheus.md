# OpenTelemetry Metrics Exporter - Prometheus

**Status**: [Experimental](../../document-status.md)

Prometheus Exporter is a [MetricExporter](../sdk.md#metricexporter) which reacts
to the Prometheus scraper and reports the metrics passively to
[Prometheus](https://prometheus.io/), or [pushes
metrics](https://prometheus.io/docs/instrumenting/pushing/) to a [Prometheus
Pushgateway](https://github.com/prometheus/pushgateway).

Prometheus Exporter SHOULD support [Pull mode](../sdk.md#pull-metric-exporter),
if possible.

Support for [Push mode](../sdk.md#push-metric-exporter) is out of scope for the
initial release.

Prometheus Exporter MUST support version `0.0.4` of the [Text-based
format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#text-based-format).

Prometheus Exporter SHOULD only support [Cumulative
Temporality](../datamodel.md#temporality).

Prometheus Exporter MAY support [OpenMetrics Text
Format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#openmetrics-text-format),
including the
[Exemplars](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars).
