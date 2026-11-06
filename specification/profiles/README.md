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
  * [Sample types](#sample-types)
    + [Sampled values](#sampled-values)
    + [CPU profiles](#cpu-profiles)
    + [Wall-clock profiles](#wall-clock-profiles)
    + [Off-CPU profiles](#off-cpu-profiles)
    + [Event profiles](#event-profiles)
    + [Allocation profiles](#allocation-profiles)
    + [Contention profiles](#contention-profiles)
  * [Period types](#period-types)
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

`Profile.sample_type` and `Profile.period_type` are [`ValueType`](./data-format.md#message-valuetype)
entries consisting of a type and a unit. These fields are openly defined and not
limited to the values listed below. Producers MAY emit custom values.

The listed values originate from the conventions of [pprof](https://github.com/google/pprof)
and its most common producers, notably Go's
[`runtime/pprof`](https://pkg.go.dev/runtime/pprof). When a producer measures one
of the concepts listed below, it SHOULD use the respective `(type, unit)` pair
so that profiles can be interpreted by backends without producer-specific
configuration.

The unit is part of the value's identity. `cpu`/`nanoseconds` and
`cpu`/`milliseconds` describe the same concept. While [pprof](https://github.com/google/pprof)
converts between time units (`seconds`, `milliseconds`, `microseconds`,
`nanoseconds`) and byte units when displaying profiles, producers SHOULD emit
the units used by the listed values: `nanoseconds`, `bytes` or `count`.

| Profile field | Known values |
| ------------- | ------------ |
| original_payload_format | [pprof](https://github.com/google/pprof/tree/main/proto), [jfr](https://en.wikipedia.org/wiki/JDK_Flight_Recorder) or [linux_perf](https://perfwiki.github.io/) |
| sample_type | See [sample types](#sample-types) |
| period_type | See [period types](#period-types) |

### Sample types

The following sections group the known `(type, unit)` pairs of
`Profile.sample_type` by profile family. The family names are used for
organization only. `sample_type` is always an exact `(type, unit)` pair, never
a family name such as `allocation` or `contention`.

#### Sampled values

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `samples` | `count` | Number of observations made by a sampling profiler. The value is typically interpreted together with `period_type` and `period` to estimate the sampled quantity, e.g., with `period_type`/`period` of `cpu`/`nanoseconds`/10000000 the estimated CPU time is `samples` × 10 ms. |

#### CPU profiles

CPU profiles measure CPU time consumed by the application.

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `cpu` | `nanoseconds` | CPU time samples |

#### Wall-clock profiles

Wall-clock (wall time) profiles measure elapsed time.

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `wall` | `nanoseconds` | Wall clock time samples |

#### Off-CPU profiles

Off-CPU profiles measure time spent not running on the CPU (e.g., waiting for
I/O, locks or scheduling).

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `off_cpu` | `nanoseconds` | Off-CPU time |

#### Event profiles

Event profiles count occurrences of traced events. In contrast to
[sampled values](#sampled-values), the count is the measured quantity itself:
no `period_type`/`period` is needed or used to derive it.

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `events` | `count` | Number of traced events (e.g., kprobe or uprobe hits) |

#### Allocation profiles

Allocation profiles measure memory allocation and the memory held live by the
program, attributed to the code that allocated it.

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `alloc_objects` | `count` | Number of allocations, including freed ones |
| `alloc_space` | `bytes` | Allocated bytes, including freed ones |
| `inuse_objects` | `count` | Number of allocations live at the time of profile collection |
| `inuse_space` | `bytes` | Bytes live at the time of profile collection |

Memory access profiling is a separate profile family. It samples individual load
and store operations to report access latency and where an access was served
from (e.g. `perf mem` or `perf c2c`). Its values are not covered by the known
values listed here.

#### Contention profiles

Contention profiles measure time spent blocked on synchronization primitives,
such as block, mutex or lock profiles.

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `contentions` | `count` | Number of blocking events |
| `delay` | `nanoseconds` | Time spent blocked or waiting |

### Period types

`Profile.period_type`, together with `Profile.period`, describes the sampling
interval of a periodic sampling profile: the quantity that elapses between
sampled occurrences. What triggers a sample is independent of what a sample
records, so `period_type` and `sample_type` can name the same `(type, unit)`
pair or different ones:

- `sample_type`=(`cpu`, `nanoseconds`) with `period_type`=(`cpu`,
  `nanoseconds`) describes a profile that records CPU time and samples it every
  fixed amount of CPU time.
- `sample_type`=(`off_cpu`, `nanoseconds`) with
  `period_type`=(`context_switch`, `count`) describes a profile that samples
  every so many context switches but records the time spent off CPU.
- `sample_type`=(`inuse_space`, `bytes`) with `period_type`=(`space`, `bytes`)
  describes an allocation profile where the recorded value is the live heap,
  while sampling is done by the number of cumulatively allocated bytes.

The known values are:

| Type | Unit | Description |
| ---- | ---- | ----------- |
| `cpu` | `nanoseconds` | Sampled every fixed amount of CPU time |
| `wall` | `nanoseconds` | Sampled every fixed amount of wall-clock time |
| `space` | `bytes` | Sampled every fixed amount of allocated bytes |
| `contentions` | `count` | Sampled every fixed number of blocking events |
| `context_switch` | `count` | Sampled every fixed number of context switches |

## Specifications

* [Profiles Data Format](./data-format.md)
* [Profiles Mappings Attributes](./mappings.md)
* [Profiles Pprof Compatibility](./pprof.md)

## References

- [Profiles Concepts](https://opentelemetry.io/docs/concepts/signals/profiles/)
- [Profiles Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/general/profiles/)
- [OTEP0212 OpenTelemetry Profiles Vision](../../oteps/profiles/0212-profiling-vision.md)
