# Profiles Data Format

**Status**: [Alpha](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Notable differences compared to other signals](#notable-differences-compared-to-other-signals)
  * [Message embedding](#message-embedding)
  * [Dictionary](#dictionary)
  * [Attributes](#attributes)
  * [Dictionary use in KeyValue](#dictionary-use-in-keyvalue)
- [Message descriptions](#message-descriptions)
  * [Message: `ProfilesData`](#message-profilesdata)
  * [Message: `ProfilesDictionary`](#message-profilesdictionary)
  * [Message: `ResourceProfiles`](#message-resourceprofiles)
  * [Message: `ScopeProfiles`](#message-scopeprofiles)
  * [Message: `Profile`](#message-profile)
  * [Message: `Sample`](#message-sample)
  * [Message: `Link`](#message-link)
  * [Message: `Stack`](#message-stack)
  * [Message: `Location`](#message-location)
  * [Message: `Line`](#message-line)
  * [Message: `Mapping`](#message-mapping)
  * [Message: `Function`](#message-function)
  * [Message: `ValueType`](#message-valuetype)
  * [Message: `KeyValueAndUnit`](#message-keyvalueandunit)
- [Relationships with other signals](#relationships-with-other-signals)
  * [From profiles to other signals](#from-profiles-to-other-signals)
  * [From other signals to profiles](#from-other-signals-to-profiles)
- [Example payloads](#example-payloads)
  * [Simple CPU profile](#simple-cpu-profile)
  * [CPU profile with resource attributes and span link](#cpu-profile-with-resource-attributes-and-span-link)
- [References](#references)

<!-- tocstop -->

</details>

## Overview

The OpenTelemetry data format for Profiles consists of a protocol specification
and [semantic conventions](https://opentelemetry.io/docs/specs/semconv/general/profiles/)
for encoding and delivery of aggregated stack traces and associated metadata.

The protocol specification is defined in the
[profiles.proto](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/profiles/v1development/profiles.proto)
protobuf file and is based on the [pprof](https://github.com/google/pprof/tree/main/proto) format.
This means that pprof can be unambiguously mapped to this data format. Lossless reverse mapping from this
data format is also possible to the extent that the target profiling format has equivalent capabilities.

The following diagram shows the relationships between messages. Solid arrows represent
embedded relationships. Dashed arrows represent references by index into a dictionary
table.

```mermaid
graph TD
    ProfilesData -->|"1-n"| ResourceProfiles
    ProfilesData -->|"1"| ProfilesDictionary
    ResourceProfiles -->|"1-n"| ScopeProfiles
    ScopeProfiles -->|"1-n"| Profile
    Profile -->|"1-n"| Sample

    Sample -. "n-1" .-> Stack
    Sample -. "n-n" .-> KeyValueAndUnit
    Sample -. "n-1" .-> Link

    Stack -. "n-n" .-> Location

    Location -->|"1-n"| Line
    Location -. "n-n" .-> KeyValueAndUnit
    Location -. "n-1" .-> Mapping

    Line -. "n-1" .-> Function

    Mapping -. "n-n" .-> KeyValueAndUnit
```

## Notable differences compared to other signals

Profilers generate large amounts of data and users are highly sensitive to
the overhead that profiling introduces. With that in mind, we designed the
Profiles data format departing from other OpenTelemetry signals in several
ways. This was done to keep payload sizes small and processing costs low
while remaining compatible with [pprof](./pprof.md) and the rest of the
OpenTelemetry ecosystem.

### Message embedding

Most OpenTelemetry signals use direct ("by value") embedding: a span in a trace embeds
its events and links. A log record contains its attributes inline.

Profiles use both "by value" and "by reference" embedding schemes:

1. **Direct embedding** is used for the outer hierarchies
   (`ProfilesData` &#x2192; `ResourceProfiles` &#x2192; `ScopeProfiles`
   &#x2192; `Profile` &#x2192; `Sample`) and (`Location`  &#x2192; `Line`).
2. **Index-based referencing** into a shared [dictionary](#message-profilesdictionary)
   is used for all other relationships. Samples reference stacks, attributes and links
   by index rather than embedding them directly.

### Dictionary

The Profiles data format uses a top-level dictionary message
([`ProfilesDictionary`](#message-profilesdictionary)) to deduplicate data
that is shared across the entire [`ProfilesData`](#message-profilesdata)
message. Unlike other OpenTelemetry signals where each record is largely
self-contained, profiles contain a high volume of repetitive data that
benefits from deduplication. By referencing the shared dictionary instead
of inlining this data, producers avoid repeatedly storing and transmitting
the same bytes, which substantially reduces on-the-wire size of profiles
payloads.

The top-level dictionary embeds additional dictionary tables, one for each
type of deduplicated data with each embedded dictionary table encoded as
an array whose elements are referenced by index.

### Attributes

The data format uses two kinds of attributes:

1. **Standard `KeyValue` attributes**: the same
   [`KeyValue`](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/common/v1/common.proto)
   pairs used by other signals. These appear on [`Resource`](../resource/README.md) and
   [`InstrumentationScope`](../common/instrumentation-scope.md) messages
   and follow the usual OpenTelemetry attribute semantics (unique keys, no unit)
   with the profiles-specific extension of string reference fields for keys and values
   (see [next section](#dictionary-use-in-keyvalue)).

2. **[`KeyValueAndUnit`](#message-keyvalueandunit) attributes**:
   a Profiles-specific encoding of an attribute. These are stored in the [`ProfilesDictionary.attribute_table`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Aattribute_table&type=code)
   and referenced by index from [`Profile`](#message-profile),
   [`Sample`](#message-sample), [`Mapping`](#message-mapping) and [`Location`](#message-location)
   messages. In addition to a key and value they carry an optional unit
   field, allowing attributes such as `"allocation_size": 128 By`
   (unit in [UCUM](https://ucum.org/)) to express their unit explicitly
   rather than relying solely on semantic conventions.

### Dictionary use in KeyValue

To minimize payload size, the data format extends the standard
OpenTelemetry [`KeyValue`](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/common/v1/common.proto)
and [`AnyValue`](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/common/v1/common.proto)
messages with string reference fields that point into [`ProfilesDictionary.string_table`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Astring_table&type=code):

This is done because [`Resource`](../resource/README.md) attributes
frequently repeat the same string values across many profiles or samples
in a single [`ProfilesData`](#message-profilesdata) message (e.g. `service.name`, `host.name`).

## Message descriptions

### Message `ProfilesData`

`ProfilesData` is the top-level message and encapsulates data that can be stored
in persistent storage or embedded by other protocols that transfer OTLP Profiles
but do not implement the OTLP protocol.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+ProfilesData+%22&type=code) for more information.

### Message `ProfilesDictionary`

`ProfilesDictionary` contains all the dictionary tables that are shared
across the entire [`ProfilesData`](#message-profilesdata) message.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+ProfilesDictionary+%22&type=code) for more information.

### Message `ResourceProfiles`

A collection of [`ScopeProfiles`](#message-scopeprofiles) from a [Resource](../resource/README.md).

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+ResourceProfiles+%22&type=code) for more information.

### Message `ScopeProfiles`

A collection of [`Profile`](#message-profile) messages produced by an
[InstrumentationScope](../common/instrumentation-scope.md).

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+ScopeProfiles+%22&type=code) for more information.

### Message `Profile`

Represents a complete profile: sample types, samples, mappings to binaries,
stacks, locations, functions and associated metadata.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Profile+%22&type=code) for more information.

### Message `Sample`

Each `Sample` records values encountered in a program context (typically a
stack trace) possibly augmented with auxiliary information such as thread ID
or higher-level request context.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Sample+%22&type=code) for more information.

### Message `Link`

A pointer from a profile [`Sample`](#message-sample) to a trace span, identified
by unique trace and span IDs.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Link+%22&type=code) for more information.

### Message `Stack`

A stack trace encoded as a list of [`Locations`](#message-location) (leaf first).

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Stack+%22&type=code) for more information.

### Message `Location`

Contains function and line table debug information for a single frame.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Location+%22&type=code) for more information.

### Message `Line`

Details a specific line in source code, linked to a function.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Line+%22&type=code) for more information.

### Message `Mapping`

Describes the mapping of a binary in memory, including its address range,
file offset, and metadata like build ID. For required attributes on
`Mapping` messages please see [Mappings](./mappings.md).

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Mapping+%22&type=code) for more information.

### Message `Function`

Describes a function, including its human-readable name, system name, source
file and starting line number.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+Function+%22&type=code) for more information.

### Message `ValueType`

Describes the type and units of a value.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+ValueType+%22&type=code) for more information.

### Message `KeyValueAndUnit`

A custom dictionary-native encoding of attributes which uses the [`ProfilesDictionary.string_table`](#message-profilesdictionary)
for keys and allows encoding optional unit information.

See the protobuf [specification](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+%22message+KeyValueAndUnit+%22&type=code) for more information.

## Relationships with other signals

OpenTelemetry Profiles support bi-directional links with other signals across
two dimensions:

* Correlation by resource context
* Correlation by direct reference

Correlation by resource context is simply linking profile data to the same
[Resource](../resource/README.md) that emitted the associated logs, metrics or
traces, such as the same service instance.

There are two types of direct reference relationships between profiles and other
signals:

* from profiles to other signals
* from other signals to profiles

### From profiles to other signals

[`Link`](#message-link) connects a profile [`Sample`](#message-sample) to a
trace span via [`trace_id`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Atrace_id&type=code) and [`span_id`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Aspan_id&type=code). Because other signals such as logs
and metrics may use the same trace/span identifiers, profiles can be correlated
with those signals through this shared trace context.

### From other signals to profiles

Other signals can reference a profile using the [`profile_id`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Aprofile_id&type=code) field on the
[`Profile`](#message-profile) message. For example, a log record may carry a
`profile_id` attribute to reference the profile that was collected at the time
the log record was generated. Note that the `profile_id` field is currently
optional at the source, but may be populated after collection (e.g. in the
OpenTelemetry Collector processing pipeline).

Moreover, [`trace_id`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Atrace_id&type=code) and [`span_id`](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-proto+path%3Aopentelemetry%2Fproto%2Fprofiles%2Fv1development%2Fprofiles.proto+symbol%3Aspan_id&type=code) can be used to reference groups of
[`Sample`](#message-sample) (but not individual) messages in a profile,
since samples are linked to traces using [`Link`](#message-link) messages.

## Example payloads

### Simple CPU profile

The following example shows an on-CPU profile collected by a sampling profiler
running at 20Hz (one sample every 50ms of actual CPU execution time). Two
unique stack traces were observed: One (seen 3 times) has the call stack
`main -> foo -> bar` and the other (seen 2 times) has the call stack `main -> baz`.

String and dictionary indices are shown inline for clarity.

```
ProfilesData {
  dictionary: ProfilesDictionary {
    string_table: ["", "samples", "count", "cpu", "nanoseconds",
                   "main", "foo", "bar", "baz",
                   "main.go", "foo.go", "bar.go", "baz.go"]
    function_table: [
      Function {},                                          // index 0: null
      Function { name_strindex: 5, filename_strindex: 9 },  // index 1: main
      Function { name_strindex: 6, filename_strindex: 10 }, // index 2: foo
      Function { name_strindex: 7, filename_strindex: 11 }, // index 3: bar
      Function { name_strindex: 8, filename_strindex: 12 }, // index 4: baz
    ]
    location_table: [
      Location {},                                                // index 0: null
      Location { lines: [Line { function_index: 1, line: 10 }] }, // index 1: main
      Location { lines: [Line { function_index: 2, line: 20 }] }, // index 2: foo
      Location { lines: [Line { function_index: 3, line: 30 }] }, // index 3: bar
      Location { lines: [Line { function_index: 4, line: 40 }] }, // index 4: baz
    ]
    stack_table: [
      Stack {},                              // index 0: null
      Stack { location_indices: [3, 2, 1] }, // index 1: bar <- foo <- main
      Stack { location_indices: [4, 1] },    // index 2: baz <- main
    ]
    mapping_table:   [Mapping {}]
    link_table:      [Link {}]
    attribute_table: [KeyValueAndUnit {}]
  }
  resource_profiles: [ResourceProfiles {
    scope_profiles: [ScopeProfiles {
      profiles: [Profile {
        sample_type: ValueType { type_strindex: 1, unit_strindex: 2 } // "samples", "count"
        samples: [
          Sample { stack_index: 1, values: [3] },
          Sample { stack_index: 2, values: [2] },
        ]
        time_unix_nano: 1234567890000000000
        duration_nano:  1000000000
        period_type: ValueType { type_strindex: 3, unit_strindex: 4 } // "cpu", "nanoseconds"
        period: 50000000 // 50ms = 20Hz
      }]
    }]
  }]
}
```

### CPU profile with resource attributes and span link

This example shows a profile with resource attributes (`service.name`, `process.executable.name`)
and a span link on one of the samples, demonstrating correlation with traces.

The resource attributes (which are not profiles-specific
[`KeyValueAndUnit`](#message-keyvalueandunit) attributes, but standard [`KeyValue`](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/common/v1/common.proto)
attributes), are using string references to [`ProfilesDictionary`](#message-profilesdictionary).

```
ProfilesData {
  dictionary: ProfilesDictionary {
    string_table: ["", "samples", "count", "cpu", "nanoseconds",
                   "handleRequest", "db.Query", "server.go", "db.go",
                   "service.name", "process.executable.name",
                   "my-service", "my-service.bin"]
    function_table: [
      Function {},                                         // index 0: null
      Function { name_strindex: 5, filename_strindex: 7 }, // index 1: handleRequest
      Function { name_strindex: 6, filename_strindex: 8 }, // index 2: db.Query
    ]
    location_table: [
      Location {},                                                 // index 0: null
      Location { lines: [Line { function_index: 1, line: 45 }] },  // index 1: handleRequest
      Location { lines: [Line { function_index: 2, line: 112 }] }, // index 2: db.Query
    ]
    stack_table: [
      Stack {},                           // index 0: null
      Stack { location_indices: [2, 1] }, // index 1: db.Query <- handleRequest
      Stack { location_indices: [1] },    // index 2: handleRequest
    ]
    link_table: [
      Link {},                                     // index 0: null
      Link {                                       // index 1
        trace_id: 1122aabbccddeeff0000000000000000
        span_id:  ff01020304050607
      },
    ]
    mapping_table:   [Mapping {}]
    attribute_table: [KeyValueAndUnit {}]
  }
  resource_profiles: [ResourceProfiles {
    resource: Resource {
      attributes: [
        { key_strindex: 9, value: { string_value_strindex: 11 } }, // "service.name", "my-service"
        { key_strindex: 10, value: { string_value_strindex: 12 } }, // "process.executable.name", "my-service.bin"
      ]
    }
    scope_profiles: [ScopeProfiles {
      profiles: [Profile {
        sample_type: ValueType { type_strindex: 1, unit_strindex: 2 } // "samples", "count"
        samples: [
          Sample { stack_index: 1, values: [5], link_index: 1 }, // Linked to trace span
          Sample { stack_index: 2, values: [3] },                // No span link
        ]
        time_unix_nano: 2000000000000000000
        duration_nano:  1000000000
        period_type: ValueType { type_strindex: 3, unit_strindex: 4 } // "cpu", "nanoseconds"
        period: 50000000 // 50ms = 20Hz
      }]
    }]
  }]
}
```

## References

- [Profiles Proto](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/profiles/v1development/profiles.proto): Contains the current version of the data format
- [Profiles Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/general/profiles/)
