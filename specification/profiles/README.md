<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/profiles/_index.md
  to: profiles/README.md
--->

# OpenTelemetry Profiles

**Status**: [Development](/docs/specs/otel/document-status/)

> [!NOTE]
>
> The profiles signal is still experimental and under active development.
> Breaking changes may be introduced in future versions.

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Design goals](#design-goals)
- [Data Model](#data-model)
- [Known values](#known-values)
- [Specifications](#specifications)
- [References](#references)

<!-- tocstop -->

</details>

## Overview

A **profile** is a collection of stack traces with associated values
representing resource consumption, collected from a running program. Profiling
is the process of collecting such profiles, typically by sampling program state
at regular intervals.

For a general introduction to OpenTelemetry profiling and how it complements other
observability signals, see [Profiles concepts](/docs/concepts/signals/profiles).

## Design goals

The profiles signal is designed with the following goals in mind:

- **Low overhead**: Enable profiling agents to operate continuously in production
  environments without materially impacting application performance.
- **Efficient representation**: Reduces volume of data stored and transmitted,
  by using dictionary tables to deduplicate repeated information across samples.
- **Compatibility with existing formats**: The data model is a superset of
  established profiling formats such as [pprof](https://github.com/google/pprof)
  and in most cases supports lossless conversions to and from these formats.
  If that's not possible (e.g. custom extensions), the `original_payload_format`
  field can be used to transmit the original information for future lossless
  export or reinterpretation.
- **Correlation with other signals**: Profiles MUST be linkable to logs, metrics
  and traces through shared resource context and, where applicable,
  direct trace/span references. This is the primary differentiator of OpenTelemetry
  profiles compared to standalone profiling solutions.

## Data model

The OpenTelemetry profiles data model is defined [here](./data-model.md).
It builds on the [pprof protobuf format](https://github.com/google/pprof/tree/main/proto)
and extends it with:

- **Resource and scope context**: Each batch of profiles is associated with a
  [Resource](/docs/specs/otel/resource/) and an
  [InstrumentationScope](/docs/specs/otel/common/instrumentation-scope/),
  consistent with logs, metrics and traces.
- **Generalized dictionary**: Deduplicates not only strings but also other messages
  that exhibit redundancy.
- **Generalized attributes**: Most messages can carry attributes following the
  same conventions as other signals, augmented with Unit information (`KeyValueAndUnit`).
- **Span context references**: Samples MAY include a `Link` (span ID and trace ID),
  enabling direct linking between a profile sample and the trace/span during
  which it was captured.

For details on the required attributes for `Mapping` messages and the custom
hashing scheme for build id generation, see [Mappings](./mappings.md).

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
| original_payload_format | [pprof](https://github.com/google/pprof/tree/main/proto), [jfr](https://en.wikipedia.org/wiki/JDK_Flight_Recorder) or [linux_perf](https://perfwiki.github.io/) |

## Specifications

* [Profiles Data Model](./data-model.md)
* [Profiles Mappings Attributes](./mappings.md)
* [Profiles Pprof Compatibility](./pprof.md)

## References

- [Profiles Concepts](/docs/concepts/signals/profiles)
- [Profiles Semantic Conventions](/docs/specs/semconv/general/profiles)
- [OTEP0212 OpenTelemetry Profiles Vision](../../oteps/profiles/0212-profiling-vision.md)
- [OTEP0239 OpenTelemetry Profiles Data Model](../../oteps/profiles/0239-profiles-data-model.md)
