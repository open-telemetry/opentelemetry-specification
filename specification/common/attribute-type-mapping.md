<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Mapping to AnyValue
--->

# Mapping Arbitrary Data to OTLP AnyValue

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Converting to AnyValue](#converting-to-anyvalue)
  * [Primitive Values](#primitive-values)
    + [Integer Values](#integer-values)
    + [Enumerations](#enumerations)
    + [Floating Point Values](#floating-point-values)
    + [String Values](#string-values)
    + [Byte Sequences](#byte-sequences)
  * [Composite Values](#composite-values)
    + [Array Values](#array-values)
    + [Associative Arrays With Unique Keys](#associative-arrays-with-unique-keys)
    + [Associative Arrays With Non-Unique Keys](#associative-arrays-with-non-unique-keys)
    + [Sets](#sets)
  * [Other Values](#other-values)
  * [Empty Values](#empty-values)

<!-- tocstop -->

</details>

This document defines how to map (convert) arbitrary data (e.g. in-memory
objects) to OTLP's [AnyValue](https://github.com/open-telemetry/opentelemetry-proto/blob/cc4ed55c082cb75e084d40b4ddf3805eda099f97/opentelemetry/proto/common/v1/common.proto#L27).

The mapping is needed when OpenTelemetry needs to convert a value produced outside
OpenTelemetry into a value that can be exported using an OTLP exporter, or otherwise be
converted to be used inside OpenTelemetry boundaries. Example use cases are the following:

- In the [Logging SDK](../logs/sdk.md)s, to convert values received
  from logging libraries into OpenTelemetry representation.
- In the Collector, to convert values received from various data sources into
  [pdata](https://github.com/open-telemetry/opentelemetry-collector/blob/4998703dadd19fa91a88eabf7ccc68d728bee3fd/model/pdata/common.go#L84)
  internal representation.

## Converting to AnyValue

[AnyValue](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L27)
is capable of representing primitive and structured data of certain types.

Implementations that have source data in any form, such as in-memory objects
or data coming from other formats that needs to be converted to AnyValue SHOULD
follow the rules described below.

### Primitive Values

#### Integer Values

Integer values which are within the range of 64 bit signed numbers
[-2^63..2^63-1] SHOULD be converted to AnyValue's
[int_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L33)
field.

Integer values which are outside the range of 64 bit signed numbers SHOULD be
converted to AnyValue's
[string_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L31)
field using decimal representation.

#### Enumerations

Values, which belong to a limited enumerated set (e.g. a Java
[enum](https://docs.oracle.com/javase/tutorial/java/javaOO/enum.html)), SHOULD be
converted to AnyValue's
[string_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L31)
field with the value of the string set to the symbolic name of the enumeration.

If it is not possible to obtain the symbolic name of the enumeration, the
implementation SHOULD map enumeration values to AnyValue's
[int_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L33)
field set to the enum's ordinal value, when such an ordinal number is naturally
obtainable.

If it is also not possible to obtain the ordinal value, the enumeration SHOULD be
converted to AnyValue's
[bytes_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L37)
field in any manner that the implementation deems reasonable.

#### Floating Point Values

Floating point values which are within the range and precision of IEEE 754
64-bit floating point numbers (including IEEE 32-bit floating point values)
SHOULD be converted to AnyValue's
[double_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L34)
field.

Floating point values which are outside the range or precision of IEEE 754
64-bit floating point numbers (e.g. IEEE 128-bit floating bit values) SHOULD be
converted to AnyValue's
[string_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L31)
field using decimal floating point representation.

#### String Values

String values which are valid UTF-8 sequences SHOULD be converted to
AnyValue's
[string_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L31)
field.

String values which are not valid Unicode sequences SHOULD be dropped.

#### Byte Sequences

Byte sequences (e.g. Go's `[]byte` slice or raw byte content of a file) SHOULD
be converted to AnyValue's
[bytes_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L37)
field.

### Composite Values

#### Array Values

Values that represent ordered sequences of other values (such as
[arrays](https://docs.oracle.com/javase/specs/jls/se7/html/jls-10.html),
[vectors](https://en.cppreference.com/w/cpp/container/vector), ordered
[lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists),
[slices](https://golang.org/ref/spec#Slice_types)) SHOULD be converted to
AnyValue's
[array_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L35)
field. String values and byte sequences are an exception from this rule (see
above).

The rules described in this document should be applied recursively to each element
of the array.

#### Associative Arrays With Unique Keys

Values that represent associative arrays with unique keys (also often known
as maps, dictionaries or key-value stores) SHOULD be converted to AnyValue's
[kvlist_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L36)
field.

If the keys of the source array are not strings, they MUST be converted to
strings by any means available, often via a toString() or stringify functions
available in programming languages. The conversion function MUST be chosen in a
way that ensures that the resulting string keys are unique in the target array.

The value part of each element of the source array SHOULD be converted to
AnyValue recursively.

For example a JSON object `{"a": 123, "b": "def"}` SHOULD be converted to

```
AnyValue{
    kvlist_value:KeyValueList{
        values:[
            KeyValue{key:"a",value:AnyValue{int_value:123}},
            KeyValue{key:"b",value:AnyValue{string_value:"def"}},
        ]
    }
}
```

The rules described in this document should be applied recursively to each value
of the associative array.

#### Associative Arrays With Non-Unique Keys

Values that represent an associative arrays with non-unique keys where multiple values may be associated with the same key (also sometimes known
as multimaps, multidicts) SHOULD be converted to AnyValue's
[kvlist_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L36)
field.

The resulting
[kvlist_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L36)
field MUST list each key only once and the value of each element of
[kvlist_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L36)
field MUST be an array represented using AnyValue's
[array_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L35)
field, each element of the
[array_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L35)
representing one value of source array associated with the given key.

For example an associative array shown in the following table:

|Key|Value|
|---|---|
|"abc"|123|
|"def"|"foo"|
|"def"|"bar"|

SHOULD be converted to:

```
AnyValue{
    kvlist_value:KeyValueList{
        values:[
            KeyValue{
                key:"abc",
                value:AnyValue{array_value:ArrayValue{values[
                    AnyValue{int_value:123}
                ]}}
            },
            KeyValue{
                key:"def",
                value:AnyValue{array_value:ArrayValue{values[
                    AnyValue{string_value:"foo"},
                    AnyValue{string_value:"bar"}
                ]}}
            },
        ]
    }
}
```

The rules described in this document should be applied recursively to each value
of the associative array.

#### Sets

Unordered collections of unique values (such as
[Java Sets](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/Set.html),
[C++ sets](https://en.cppreference.com/w/cpp/container/set),
[Python Sets](https://docs.python.org/3/tutorial/datastructures.html#sets)) SHOULD be
converted to AnyValue's
[array_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L35)
field, where each element of the set becomes an element of the array.

The rules described in this document should be applied recursively to each value
of the set.

### Other Values

Any other values not listed above SHOULD be converted to AnyValue's
[string_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L31)
field if the source data can be serialized to a string (can be stringified)
using toString() or stringify functions available in programming languages.

If the source data cannot be serialized to a string then the value SHOULD be
converted AnyValue's
[bytes_value](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L37)
field by serializing it into a byte sequence by any means available.

If the source data cannot be serialized neither to a string nor to a byte
sequence then it SHOULD by converted to an empty AnyValue.

### Empty Values

If the source data has no type associated with it and is empty, null, nil or
otherwise indicates absence of data it SHOULD be converted to an
[empty](https://github.com/open-telemetry/opentelemetry-proto/blob/38b5b9b6e5257c6500a843f7fdacf89dd95833e8/opentelemetry/proto/common/v1/common.proto#L29)
AnyValue, where all the fields are unset.

Empty values which has a type associated with them (e.g. empty associative
array) SHOULD be converted using the corresponding rules defined for the types
above.
