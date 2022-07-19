<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Process
--->

# Semantic Conventions for OS Process Metrics

**Status**: [Experimental](../../document-status.md)

This document describes instruments and attributes for common OS process level
metrics in OpenTelemetry. Also consider the [general metric semantic
conventions](README.md#general-metric-semantic-conventions) when creating
instruments not explicitly defined in this document. OS process metrics are
not related to the runtime environment of the program, and should take
measurements from the operating system. For runtime environment metrics see
[semantic conventions for runtime environment
metrics](runtime-environment-metrics.md).

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [Process](#process)
- [Attributes](#attributes)

<!-- tocstop -->

## Metric Instruments

### Process

Below is a table of Process metric instruments.

| Name                              | Instrument Type ([*](README.md#instrument-types)) | Units | Description                                                                                                                         | Labels                                                                                                                                                                                          |
| --------------------------------- | ------------------------------------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `process.cpu.time`                | Counter                                           | s     | Total CPU seconds broken down by different states.                                                                                  | `state`, if specified, SHOULD be one of: `system`, `user`, `wait`. A process SHOULD be characterized _either_ by data points with no `state` labels, _or only_ data points with `state` labels. |
| `process.cpu.utilization`         | Gauge                                             | s     | Difference in process.cpu.time since the last measurement, divided by the elapsed time and number of CPUs available to the process. | `state`, if specified, SHOULD be one of: `system`, `user`, `wait`. A process SHOULD be characterized _either_ by data points with no `state` labels, _or only_ data points with `state` labels. |
| `process.memory.usage`            | UpDownCounter                                     | By    | The amount of physical memory in use.                                                                                               |                                                                                                                                                                                                 |
| `process.memory.virtual`          | UpDownCounter                                     | By    | The amount of committed virtual memory.                                                                                             |                                                                                                                                                                                                 |
| `process.disk.io` (deprecated)    | Counter                                           | By    | Disk bytes transferred.                                                                                                             | `direction` SHOULD be one of: `read`, `write`                                                                                                                                                   |
| `process.disk.io.read`            | Counter                                           | By    | Disk bytes read.                                                                                                                    |                                                                                                                                                                                                 |
| `process.disk.io.write`           | Counter                                           | By    | Disk bytes written.                                                                                                                 |                                                                                                                                                                                                 |
| `process.network.io` (deprecated) | Counter                                           | By    | Network bytes transferred.                                                                                                          | `direction` SHOULD be one of: `receive`, `transmit`                                                                                                                                             |
| `process.network.io.receive`      | Counter                                           | By    | Network bytes received.                                                                                                             |                                                                                                                                                                                                 |
| `process.network.io.transmit`     | Counter                                           | By    | Network bytes transmitted.                                                                                                          |                                                                                                                                                                                                 |

## Attributes

Process metrics SHOULD be associated with a [`process`](../../resource/semantic_conventions/process.md#process) resource whose attributes provide additional context about the process.
