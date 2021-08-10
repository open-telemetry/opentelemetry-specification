# OpenTelemetry Metrics Exporter - In-memory

**Status**: [Experimental](../../document-status.md)

Note: this specification is subject to major changes. To avoid thrusting
language client maintainers, we don't recommend OpenTelemetry clients to start
the implementation unless explicitly communicated.

The in-memory exporter accumulates telemetry data in the local memory and allows
to inspect it (useful for e.g. unit tests).

The in-memory exporter MUST support both [pull](../sdk.md#pull-metric-exporter)
mode and [push](../sdk.md#push-metric-exporter) mode.
