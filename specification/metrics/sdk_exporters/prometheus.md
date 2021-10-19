# OpenTelemetry Metrics Exporter - Prometheus

**Status**: [Experimental](../../document-status.md)

Prometheus Exporter is a [Pull Metric Exporter](../sdk.md#pull-metric-exporter)
which reacts to the Prometheus scraper and report the metrics passively to
[Prometheus](https://prometheus.io/).

Prometheus Exporter MUST export Meter `name` and `version` information when
enabled by the [Metrics SDK Configuration](../../sdk-environment-variables.md#metrics-sdk-configuration).
The Prometheus Exporter MUST respect the configuration preferences of the application
provide a method to configure whether these data are exported as
[Attributes](../common/common.md#attributes). The `name` and `version` information
will follow the same naming as [trace exporters.](../../trace/sdk_exporters/non-otlp.md#instrumentationlibrary)
