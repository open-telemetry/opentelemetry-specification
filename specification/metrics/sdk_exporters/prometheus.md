<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Prometheus
--->

# Metrics Exporter - Prometheus

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

A Prometheus Exporter MAY offer configuration to add resource attributes as metric attributes.
By default, it MUST NOT add any resource attributes as metric attributes.
The configuration SHOULD allow the user to select which resource attributes to copy (e.g.
include / exclude or regular expression based). Copied Resource attributes MUST NOT be
excluded from target_info.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [unit suffix](../../compatibility/prometheus_and_openmetrics.md#metric-metadata)
or UNIT metadata. The option MAY be named `without_units`, and MUST be `false` by default.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [type suffix](../../compatibility/prometheus_and_openmetrics.md#metric-metadata).
The option MAY be named `without_type_suffix`, and MUST be `false` by default.

A Prometheus Exporter MAY support a configuration option to produce metrics without a [scope info](../../compatibility/prometheus_and_openmetrics.md#instrumentation-scope)
metric. The option MAY be named `without_scope_info`, and MUST be `false` by default.
