# Semantic conventions for Resource metrics

This document describes metrics created about [Resources](../../resource/sdk.md), the entities
producing telemetry in a system.

## Labels

The current Resource metrics do not have any explicit labels. They SHOULD inherit the [attributes
of the encapsulating](../../resource/semantic_conventions/README.md) Resource when being exported.

## Metric Instruments

The following metric instruments SHOULD be synthesized every time a Resource produces some
telemetry.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `resource.up` | ValueRecorder | 1 | A value of `1` indicates the Resource is healthy, `0` if the Resource is unhealthy. |

