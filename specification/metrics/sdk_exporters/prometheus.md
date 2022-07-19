<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Prometheus
--->

# OpenTelemetry Metrics Exporter - Prometheus

**Status**: [Experimental](../../document-status.md)

A Prometheus Exporter is a [Pull Metric Exporter](../sdk.md#pull-metric-exporter)
which reports metrics by responding to the [Prometheus](https://prometheus.io/)
scraper requests.

A Prometheus Exporter MUST support [Pull mode](../sdk.md#pull-metric-exporter).

A Prometheus Exporter MUST NOT support [Push
mode](../sdk.md#push-metric-exporter).

A Prometheus Exporter MUST only support [Cumulative
Temporality](../data-model.md#temporality).

A Prometheus Exporter MUST support version `0.0.4` of the [Text-based
format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#text-based-format).

A Prometheus Exporter MAY support [OpenMetrics Text
Format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#openmetrics-text-format),
including the
[Exemplars](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars).
