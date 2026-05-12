# Self-Observability

**Status**: [Development](document-status.md)

OpenTelemetry SDKs MAY emit self-observability ("internal") telemetry about
their own behavior — for example, metrics, logs, and other signals describing
the state of processors, exporters, and metric readers — to help operators
monitor the health of the OpenTelemetry pipeline itself.

This is closely related to the
[self-diagnostics](error-handling.md#self-diagnostics) guidance in the error
handling document.

## SDK Self-Observability Metrics

The names, attributes, and values used for SDK self-observability metrics are
defined in the OpenTelemetry semantic conventions:
[SDK Metrics](https://opentelemetry.io/docs/specs/semconv/otel/sdk-metrics/).
SDKs that implement self-observability metrics SHOULD follow these conventions.
