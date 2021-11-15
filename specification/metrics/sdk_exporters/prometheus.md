# OpenTelemetry Metrics Exporter - Prometheus

**Status**: [Experimental](../../document-status.md)

Prometheus Exporter is a [MetricExporter](../sdk.md#metricexporter) which reacts
to the Prometheus scraper and reports the metrics passively to
[Prometheus](https://prometheus.io/), or [pushes
metrics](https://prometheus.io/docs/instrumenting/pushing/) to a [Prometheus
Pushgateway](https://github.com/prometheus/pushgateway).

Prometheus Exporter SHOULD support [Pull mode](../sdk.md#pull-metric-exporter),
if possible.

Prometheus Exporter MAY support [Push mode](../sdk.md#push-metric-exporter), if
there is a need to support short-lived applications (e.g. short-lived
service-level batch jobs, JavaScript applications running inside web browsers,
etc.).

Prometheus Exporter MUST support version `0.0.4` of the [Text-based
format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#text-based-format).

Prometheus Exporter SHOULD only support [Cumulative
Temporality](../datamodel.md#temporality). Attempt to change the [Aggregation
Temporality](../datamodel.md#temporality) to
[Delta](../datamodel.md#temporality) SHOULD be treated as an error. It is
unspecified _how_ the this error should be handled (e.g. it could fail fast
during the exporter configuration time). Please refer to [Error handling in
OpenTelemetry](../../error-handling.md) for the general guidance.

Prometheus Exporter MAY support [OpenMetrics Text
Format](https://github.com/prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#openmetrics-text-format),
including the
[Exemplars](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars).
