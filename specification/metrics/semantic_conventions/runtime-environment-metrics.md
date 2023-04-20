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
  * [Metric: `process.runtime.jvm.memory.usage`](#metric-processruntimejvmmemoryusage)
  * [Metric: `process.runtime.jvm.memory.init`](#metric-processruntimejvmmemoryinit)
  * [Metric: `process.runtime.jvm.memory.committed`](#metric-processruntimejvmmemorycommitted)
  * [Metric: `process.runtime.jvm.memory.limit`](#metric-processruntimejvmmemorylimit)
  * [Metric: `process.runtime.jvm.memory.usage_after_last_gc`](#metric-processruntimejvmmemoryusage_after_last_gc)
  * [Metric: `process.runtime.jvm.gc.duration`](#metric-processruntimejvmgcduration)
  * [Metric: `process.runtime.jvm.threads.count`](#metric-processruntimejvmthreadscount)
  * [Metric: `process.runtime.jvm.classes.loaded`](#metric-processruntimejvmclassesloaded)
  * [Metric: `process.runtime.jvm.classes.unloaded`](#metric-processruntimejvmclassesunloaded)
  * [Metric: `process.runtime.jvm.classes.current_loaded`](#metric-processruntimejvmclassescurrent_loaded)
  * [Metric: `process.runtime.jvm.cpu.utilization`](#metric-processruntimejvmcpuutilization)
  * [Metric: `process.runtime.jvm.system.cpu.utilization`](#metric-processruntimejvmsystemcpuutilization)
  * [Metric: `process.runtime.jvm.system.cpu.load_1m`](#metric-processruntimejvmsystemcpuload_1m)
  * [Metric: `process.runtime.jvm.buffer.usage`](#metric-processruntimejvmbufferusage)
  * [Metric: `process.runtime.jvm.buffer.limit`](#metric-processruntimejvmbufferlimit)
  * [Metric: `process.runtime.jvm.buffer.count`](#metric-processruntimejvmbuffercount)

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

### Metric: `process.runtime.jvm.memory.usage`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.memory.usage(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.memory.usage` | UpDownCounter | `By` | Measure of memory used. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.memory.usage(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `type` | string | The type of memory. | `heap`; `non_heap` | Recommended |
| `pool` | string | Name of the memory pool. [1] | `G1 Old Gen`; `G1 Eden space`; `G1 Survivor Space` | Recommended |

**[1]:** Pool names are generally obtained via [MemoryPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/MemoryPoolMXBean.html#getName()).

`type` MUST be one of the following:

| Value  | Description |
|---|---|
| `heap` | Heap memory. |
| `non_heap` | Non-heap memory |
<!-- endsemconv -->

### Metric: `process.runtime.jvm.memory.init`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.memory.init(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.memory.init` | UpDownCounter | `By` | Measure of initial memory requested. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.memory.init(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `type` | string | The type of memory. | `heap`; `non_heap` | Recommended |
| `pool` | string | Name of the memory pool. [1] | `G1 Old Gen`; `G1 Eden space`; `G1 Survivor Space` | Recommended |

**[1]:** Pool names are generally obtained via [MemoryPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/MemoryPoolMXBean.html#getName()).

`type` MUST be one of the following:

| Value  | Description |
|---|---|
| `heap` | Heap memory. |
| `non_heap` | Non-heap memory |
<!-- endsemconv -->

### Metric: `process.runtime.jvm.memory.committed`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.memory.committed(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.memory.committed` | UpDownCounter | `By` | Measure of memory committed. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.memory.committed(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `type` | string | The type of memory. | `heap`; `non_heap` | Recommended |
| `pool` | string | Name of the memory pool. [1] | `G1 Old Gen`; `G1 Eden space`; `G1 Survivor Space` | Recommended |

**[1]:** Pool names are generally obtained via [MemoryPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/MemoryPoolMXBean.html#getName()).

`type` MUST be one of the following:

| Value  | Description |
|---|---|
| `heap` | Heap memory. |
| `non_heap` | Non-heap memory |
<!-- endsemconv -->

### Metric: `process.runtime.jvm.memory.limit`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.memory.limit(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.memory.limit` | UpDownCounter | `By` | Measure of max obtainable memory. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.memory.limit(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `type` | string | The type of memory. | `heap`; `non_heap` | Recommended |
| `pool` | string | Name of the memory pool. [1] | `G1 Old Gen`; `G1 Eden space`; `G1 Survivor Space` | Recommended |

**[1]:** Pool names are generally obtained via [MemoryPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/MemoryPoolMXBean.html#getName()).

`type` MUST be one of the following:

| Value  | Description |
|---|---|
| `heap` | Heap memory. |
| `non_heap` | Non-heap memory |
<!-- endsemconv -->

### Metric: `process.runtime.jvm.memory.usage_after_last_gc`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.memory.usage_after_last_gc(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.memory.usage_after_last_gc` | UpDownCounter | `By` | Measure of memory used, as measured after the most recent garbage collection event on this pool. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.memory.usage_after_last_gc(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `type` | string | The type of memory. | `heap`; `non_heap` | Recommended |
| `pool` | string | Name of the memory pool. [1] | `G1 Old Gen`; `G1 Eden space`; `G1 Survivor Space` | Recommended |

**[1]:** Pool names are generally obtained via [MemoryPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/MemoryPoolMXBean.html#getName()).

`type` MUST be one of the following:

| Value  | Description |
|---|---|
| `heap` | Heap memory. |
| `non_heap` | Non-heap memory |
<!-- endsemconv -->

### Metric: `process.runtime.jvm.gc.duration`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.gc.duration(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.gc.duration` | Histogram | `ms` | Duration of JVM garbage collection actions. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.gc.duration(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `gc` | string | Name of the garbage collector. [1] | `G1 Young Generation`; `G1 Old Generation` | Recommended |
| `action` | string | Name of the garbage collector action. [2] | `end of minor GC`; `end of major GC` | Recommended |

**[1]:** Garbage collector name is generally obtained via [GarbageCollectionNotificationInfo#getGcName()](https://docs.oracle.com/en/java/javase/11/docs/api/jdk.management/com/sun/management/GarbageCollectionNotificationInfo.html#getGcName()).

**[2]:** Garbage collector action is generally obtained via [GarbageCollectionNotificationInfo#getGcAction()](https://docs.oracle.com/en/java/javase/11/docs/api/jdk.management/com/sun/management/GarbageCollectionNotificationInfo.html#getGcAction()).
<!-- endsemconv -->

### Metric: `process.runtime.jvm.threads.count`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.threads.count(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.threads.count` | UpDownCounter | `{thread}` | Number of executing threads. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.threads.count(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `daemon` | boolean | Whether the thread is daemon or not. |  | Recommended |
<!-- endsemconv -->

### Metric: `process.runtime.jvm.classes.loaded`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.classes.loaded(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.classes.loaded` | Counter | `{class}` | Number of classes loaded since JVM start. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.classes.loaded(full) -->
<!-- endsemconv -->

### Metric: `process.runtime.jvm.classes.unloaded`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.classes.unloaded(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.classes.unloaded` | Counter | `{class}` | Number of classes unloaded since JVM start. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.classes.unloaded(full) -->
<!-- endsemconv -->

### Metric: `process.runtime.jvm.classes.current_loaded`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.classes.current_loaded(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.classes.current_loaded` | UpDownCounter | `{class}` | Number of classes currently loaded. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.classes.current_loaded(full) -->
<!-- endsemconv -->

### Metric: `process.runtime.jvm.cpu.utilization`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.cpu.utilization(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.cpu.utilization` | Gauge | `1` | Recent CPU utilization for the process. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.cpu.utilization(full) -->
<!-- endsemconv -->

### Metric: `process.runtime.jvm.system.cpu.utilization`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.system.cpu.utilization(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.system.cpu.utilization` | Gauge | `1` | Recent CPU utilization for the whole system. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.system.cpu.utilization(full) -->
<!-- endsemconv -->

### Metric: `process.runtime.jvm.system.cpu.load_1m`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.system.cpu.load_1m(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.system.cpu.load_1m` | Gauge | `1` | Average CPU load of the whole system for the last minute. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.system.cpu.load_1m(full) -->
<!-- endsemconv -->

### Metric: `process.runtime.jvm.buffer.usage`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.buffer.usage(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.buffer.usage` | UpDownCounter | `By` | Measure of memory used by buffers. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.buffer.usage(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `pool` | string | Name of the memory pool. [1] | `mapped`; `direct` | Recommended |

**[1]:** Pool names are generally obtained via [BufferPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/BufferPoolMXBean.html#getName()).
<!-- endsemconv -->

### Metric: `process.runtime.jvm.buffer.limit`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.buffer.limit(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.buffer.limit` | UpDownCounter | `By` | Measure of total memory capacity of buffers. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.buffer.limit(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `pool` | string | Name of the memory pool. [1] | `mapped`; `direct` | Recommended |

**[1]:** Pool names are generally obtained via [BufferPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/BufferPoolMXBean.html#getName()).
<!-- endsemconv -->

### Metric: `process.runtime.jvm.buffer.count`

This metric is [recommended](../metric-requirement-level.md#recommended).

<!-- semconv metric.process.runtime.jvm.buffer.count(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `process.runtime.jvm.buffer.count` | UpDownCounter | `{buffer}` | Number of buffers in the pool. |
<!-- endsemconv -->

<!-- semconv metric.process.runtime.jvm.buffer.count(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `pool` | string | Name of the memory pool. [1] | `mapped`; `direct` | Recommended |

**[1]:** Pool names are generally obtained via [BufferPoolMXBean#getName()](https://docs.oracle.com/en/java/javase/11/docs/api/java.management/java/lang/management/BufferPoolMXBean.html#getName()).
<!-- endsemconv -->
