# Self-Observability

**Status**: [Development](document-status.md)

OpenTelemetry SDKs SHOULD emit self-observability ("internal") telemetry about
their own behavior (for example, metrics, logs, and other signals describing
the state of processors, exporters, and metric readers) to help operators
monitor the health of the OpenTelemetry pipeline itself.

This is closely related to the
[self-diagnostics](error-handling.md#self-diagnostics) guidance in the error
handling document.

## SDK Self-Observability Metrics

The names, attributes, and values used for SDK self-observability metrics are
defined in the OpenTelemetry semantic conventions:
[SDK Metrics](https://opentelemetry.io/docs/specs/semconv/otel/sdk-metrics/).
SDKs that implement self-observability metrics SHOULD follow these conventions.

Self-observability telemetry emitted during SDK startup and shutdown is
best-effort, because the SDK that records this telemetry may not yet be
initialized or may have already been shut down.

For non-normative implementation advice, see the
[Self-Observability Supplementary Guidelines](self-observability-supplementary-guidelines.md).
