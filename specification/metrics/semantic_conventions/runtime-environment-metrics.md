<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Runtime Environment
--->

# Semantic Conventions for Runtime Environment Metrics

**Status**: [Experimental](../../document-status.md)

This document includes semantic conventions for runtime environment level
metrics in OpenTelemetry. Also consider the [general
metric](README.md#general-metric-semantic-conventions), [system
metrics](system-metrics.md) and [OS Process metrics](process-metrics.md)
semantic conventions when instrumenting runtime environments.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [Runtime Environment Specific Metrics - `process.runtime.{environment}.`](#runtime-environment-specific-metrics---processruntimeenvironment)
- [Attributes](#attributes)
- [JVM Metrics](#jvm-metrics)

<!-- tocstop -->

## Metric Instruments

Runtime environments vary widely in their terminology, implementation, and
relative values for a given metric. For example, Go and Python are both
garbage collected languages, but comparing heap usage between the Go and
CPython runtimes directly is not meaningful. For this reason, this document
does not propose any standard top-level runtime metric instruments. See [OTEP
108](https://github.com/open-telemetry/oteps/pull/108/files) for additional
discussion.

### Runtime Environment Specific Metrics - `process.runtime.{environment}.`

Metrics specific to a certain runtime environment should be prefixed with
`process.runtime.{environment}.` and follow the semantic conventions outlined in
[general metric semantic
conventions](README.md#general-metric-semantic-conventions). Authors of
runtime instrumentations are responsible for the choice of `{environment}` to
avoid ambiguity when interpreting a metric's name or values.

For example, some programming languages have multiple runtime environments
that vary significantly in their implementation, like [Python which has many
implementations](https://wiki.python.org/moin/PythonImplementations). For
such languages, consider using specific `{environment}` prefixes to avoid
ambiguity, like `process.runtime.cpython.` and `process.runtime.pypy.`.

There are other dimensions even within a given runtime environment to
consider, for example pthreads vs green thread implementations.

## Attributes

[`process.runtime`](../../resource/semantic_conventions/process.md#process-runtimes) resource attributes SHOULD be included on runtime metric events as appropriate.

## JVM Metrics

**Description:** Java Virtual Machine (JVM) metrics captured under `process.runtime.jvm.`

All JVM metric attributes are required unless otherwise indicated.

| Name                                       | Description                                              | Unit    | Unit ([UCUM](README.md#instrument-units)) | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values      |
|--------------------------------------------|----------------------------------------------------------|---------|-------------------------------------------|---------------------------------------------------|------------|---------------|-----------------------|
| process.runtime.jvm.memory.usage           | Measure of memory used                                   | Bytes   | `By`                                      | UpDownCounter                                     | Int64      | type          | `"heap"`, `"nonheap"` |
|                                            |                                                          |         |                                           |                                                   |            | pool          | Name of pool [1]      |
| process.runtime.jvm.memory.init            | Measure of initial memory requested                      | Bytes   | `By`                                      | UpDownCounter                                     | Int64      | type          | `"heap"`, `"nonheap"` |
|                                            |                                                          |         |                                           |                                                   |            | pool          | Name of pool [1]      |
| process.runtime.jvm.memory.committed       | Measure of memory committed                              | Bytes   | `By`                                      | UpDownCounter                                     | Int64      | type          | `"heap"`, `"nonheap"` |
|                                            |                                                          |         |                                           |                                                   |            | pool          | Name of pool [1]      |
| process.runtime.jvm.memory.limit           | Measure of max obtainable memory                         | Bytes   | `By`                                      | UpDownCounter                                     | Int64      | type          | `"heap"`, `"nonheap"` |
|                                            |                                                          |         |                                           |                                                   |            | pool          | Name of pool [1]      |
| process.runtime.jvm.threads.count          | Number of executing threads                              | threads | `{threads}`                               | UpDownCounter                                     | Int64      |               |                       |
| process.runtime.jvm.classes.loaded         | Number of classes loaded since JVM start                 | classes | `{classes}`                               | Counter                                           | Int64      |               |                       |
| process.runtime.jvm.classes.unloaded       | Number of classes unloaded since JVM start               | classes | `{classes}`                               | Counter                                           | Int64      |               |                       |
| process.runtime.jvm.classes.current_loaded | Number of classes currently loaded                       | classes | `{classes}`                               | UpDownCounter                                     | Int64      |               |                       |
| process.runtime.jvm.cpu.utilization        | Recent cpu utilization for the process [2]               | 1       | 1                                         | Asynchronous Gauge                                | Double     |               |                       |
| process.runtime.jvm.system.cpu.utilization | Recent cpu utilization for the whole system [2]          | 1       | 1                                         | Asynchronous Gauge                                | Double     |               |                       |
| process.runtime.jvm.system.cpu.load_1m     | Average CPU load of the whole system for the last minute | 1       | 1                                         | Asynchronous Gauge                                | Double     |               |                       |
| process.runtime.jvm.buffer.usage           | Measure of memory used by buffers                        | Bytes   | `By`                                      | UpDownCounter                                     | Int64      | pool          | Name of pool[3]       |
| process.runtime.jvm.buffer.limit           | Measure of total memory capacity of buffers              | Bytes   | `By`                                      | UpDownCounter                                     | Int64      | pool          | Name of pool[3]       |
| process.runtime.jvm.buffer.count           | Number of buffers in the pool                            | buffers | `{buffers}`                               | UpDownCounter                                     | Int64      | pool          | Name of pool[3]       |

**[1]**: Pool names are generally obtained via [MemoryPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/MemoryPoolMXBean.html#getName()).
Examples include `G1 Old Gen`, `G1 Eden space`, `G1 Survivor Space`, `Metaspace`, etc.
**[2]**: These utilizations are not defined as being for the specific interval since last measurement (unlike `system.cpu.utilization`).
**[3]**: Pool names are generally obtained via [BufferPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/BufferPoolMXBean.html#getName()).
