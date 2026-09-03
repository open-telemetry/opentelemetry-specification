<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/profiles/_index.md
  to: profiles/README.md
--->

# OpenTelemetry Profiles

**Status**: [Alpha](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- START doctoc -->

- [Overview](#overview)
- [Design goals](#design-goals)
- [Data Format](#data-format)
- [Known values](#known-values)
  * [CPU profiles](#cpu-profiles)
  * [Wall-clock profiles](#wall-clock-profiles)
  * [Off-CPU profiles](#off-cpu-profiles)
  * [Heap profiles](#heap-profiles)
  * [Block contention profiles](#block-contention-profiles)
  * [Mutex profiles](#mutex-profiles)
- [Specifications](#specifications)
- [References](#references)

<!-- END doctoc -->

</details>

## Overview

A **profile** is a collection of stack traces with associated values
representing resource consumption and code execution, collected from a
running program. Profiling is the process of collecting such profiles,
typically by sampling program state at regular intervals.

For a general introduction to OpenTelemetry profiling and how it complements other
observability signals, see [Profiles concepts](https://opentelemetry.io/docs/concepts/signals/profiles/).

## Design goals

The profiles signal is designed with the following goals in mind:

- **Low overhead**: Enable profiling agents to operate continuously in production
  environments without materially impacting application performance.
- **Efficient representation**: Reduces volume of data stored and transmitted,
  by using dictionary tables to deduplicate repeated information across samples.
- **Compatibility with existing formats**: The data format is a superset of
  established profiling formats such as [pprof](https://github.com/google/pprof)
  and in most cases supports lossless conversions to and from these formats.
  If that's not possible (e.g. custom extensions), the `original_payload_format`
  field can be used to transmit the original information for future lossless
  export or reinterpretation.
- **Correlation with other signals**: Profiles MUST be linkable to logs, metrics
  and traces through shared resource context and, where applicable,
  direct trace/span references.

## Data Format

The OpenTelemetry profiles data format is [here](./data-format.md).
It builds on the [pprof protobuf format](https://github.com/google/pprof/tree/main/proto)
and extends it with:

- **Resource and scope context**: Each batch of profiles is associated with a
  [Resource](../resource/README.md) and an [InstrumentationScope](../common/instrumentation-scope.md),
  consistent with logs, metrics and traces.
- **Generalized dictionary**: Deduplicates not only strings but also other messages
  that exhibit redundancy.
- **Generalized attributes**: Most messages can carry attributes following the
  same conventions as other signals, augmented with Unit information (`KeyValueAndUnit`).
- **Span context references**: Samples MAY include a `Link` (span ID and trace ID),
  enabling direct linking between a profile sample and the trace/span during
  which it was captured.

For details on the required attributes for `Mapping` messages and the custom
hashing scheme for build ID generation, see [Mappings](./mappings.md).

For more information on compatibility with [pprof](https://github.com/google/pprof),
see [pprof](./pprof.md).

## Known values

[OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
are vital for profiles to correlate with other OpenTelemetry signals, enabling
unified analysis of traces, metrics, logs, and profiles for a holistic
system understanding.

To enhance the compatibility of OpenTelemetry Profiles with existing profiling
tools, known values are utilized.

| Profile field | Known values |
| ------------- | ------------ |
| Profile.original_payload_format | [pprof](https://github.com/google/pprof/tree/main/proto), [jfr](https://en.wikipedia.org/wiki/JDK_Flight_Recorder) or [linux_perf](https://perfwiki.github.io/) |
| Profile.sample_type | [cpu](#cpu-profiles), [wall](#wall-clock-profiles), [off_cpu](#off-cpu-profiles), [heap](#heap-profiles), [block](#block-contention-profiles), [mutex](#mutex-profiles) |

### CPU profiles

CPU profiles measure CPU time consumed by the application. Common values:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| cpu | nanoseconds | CPU time samples |

### Wall-clock profiles

Wall-clock (wall time) profiles measure elapsed time. Common values:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| wall | nanoseconds | Wall clock time in nanoseconds |

### Off-CPU profiles

Off-CPU profiles measure time spent not running on the CPU (e.g., waiting for I/O or locks). Common values:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| off_cpu | nanoseconds | Off-CPU time |

### Heap profiles

Heap profiles measure memory allocation and usage. Common values:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| inuse_space | bytes | In-use memory at the time of profile collection |
| inuse_objects | count | Number of in-use allocations |
| alloc_space | bytes | Total allocated memory (including freed) |
| alloc_objects | count | Total number of allocations (including freed) |
| allocated_space | bytes | Allocated memory |
| allocated_objects | count | Number of allocated objects |
| space | bytes | Generic memory measurement |

### Block contention profiles

Block (contention) profiles measure time spent blocked on synchronization primitives. Common values:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| block | nanoseconds | Block wait time |

### Mutex profiles

Mutex profiles measure lock contention and time spent waiting on mutexes. Common values:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| mutex | nanoseconds | Time spent in mutex contention |

## Specifications

* [Profiles Data Format](./data-format.md)
* [Profiles Mappings Attributes](./mappings.md)
* [Profiles Pprof Compatibility](./pprof.md)

## References

- [Profiles Concepts](https://opentelemetry.io/docs/concepts/signals/profiles/)
- [Profiles Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/general/profiles/)
- [OTEP0212 OpenTelemetry Profiles Vision](../../oteps/profiles/0212-profiling-vision.md)
