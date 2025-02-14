<!--- Hugo front matter used to generate the website version of this page:
linkTitle: TraceState
--->

# TraceState Handling

**Status**: [Development](../document-status.md)

In alignment to the [TraceContext](https://www.w3.org/TR/trace-context/) specification, this section uses the
Augmented Backus-Naur Form (ABNF) notation of [RFC5234](https://www.w3.org/TR/trace-context/#bib-rfc5234),
including the DIGIT rule in that document.

When setting [TraceState](api.md#tracestate) values that are part of the OTel ecosystem,
they MUST all be contained in a single entry using the `ot` key, with the value being
a semicolon separated list of key-value pairs such as:

* `ot=p:8;r:62`
* `ot=foo:bar;k1:13`

The [TraceContext](https://www.w3.org/TR/trace-context/) specification defines support for multiple "tenants" each to use their own `tracestate` entry by prefixing `tenant@` to tenant-specific values in a mixed tracing environment. OpenTelemetry recognizes this syntax but does not specify an interpretation for multi-tenant `tracestate`.
The list can be formally defined as:

```
list        = list-member *( ";" list-member )
list-member = key ":" value
```

The complete list length MUST NOT exceed 256 characters, as defined by the
[TraceState value section](https://www.w3.org/TR/trace-context/#value),
and the used keys MUST be unique.

Instrumentation libraries and clients MUST NOT use this entry, and they MUST
instead use their own entry.

## Key

The key is an identifier that describes an OTel concern.
Simple examples are `p`, `ts`, or `s1`.

The key can be formally defined as:

```
key        = lcalpha *(lcalpha / DIGIT )
lcalpha    = %x61-7A ; a-z
```

Specific keys used by OTel concerns MUST be defined as part of the Specification,
and hence it is forbidden to use any key that has not been defined in
the Specification itself.

## Value

The value is an opaque string. Although it has no maximum allowed length,
it is recommended to use short values, as the **entire** list of key-values
MUST NOT exceed 256 characters.

The value can be formally defined as:

```
value      = *(chr)
chr        = ucalpha / lcalpha / DIGIT / "." / "_" / "-"
ucalpha    = %x41-5A ; A-Z
lcalpha    = %x61-7A ; a-z
```

## Setting values

Set values MUST be either updated or added to the `ot` entry in `TraceState`,
in order to preserve existing values belonging to other OTel concerns. For example,
if a given concern K wants to set `k1:13`:

* `ot=p:8;r:62` will become `ot=p:8;r:62;k1:13`.
* `ot=p:8;k1:7;r:62` will become `ot=p:8;r:62;k1:13`. Preserving the order is not required.

If setting a value ends up making the entire `ot` entry exceed the 256 characters limit,
SDKs are advised to abort the operation and signal the user about the error, e.g.

```go
traceState, ok := SetTraceStateValue(traceState, value)
if ok {
  // Successfully set the specified value, traceState was updated.
} else {
  // traceState was not updated.
}
```

## Pre-defined OpenTelemetry sub-keys

The following values have been defined by OpenTelemetry.

### Explicit randomness value `rv`

The OpenTelemetry TraceState `rv` sub-key defines an alternative source of randomness called the _explicit randomness value_.
Values of `rv` MUST be exactly 14 lower-case hexadecimal digits:

```
hexdigit = DIGIT ; a-f
```

The explicit randomness value is meant to be used instead of extracting randomness from TraceIDs, therefore it contains the same number of bits as W3C Trace Context Level 2 recommends for TraceIDs.

Lowercase hexadecimal digits are specified to enable direct lexicographical comparison between a sampling thresohld and either the TraceID (as it appears in the `traceparent` header) or the explicit randomness value (as it appears in the `tracestate` header).

Explicit randomness values are meant to propagate through [span contexts](../context/README.md) unmodified.
Explicit randomness values SHOULD NOT be erased from the OpenTelemetry TraceState or modified once associated with a new TraceID, so that sampling decisions made using the explicit randomness value are consistent across signals.

For example, here is a W3C TraceState value including an OpenTelemetry explicit randomness value:

```
tracestate: ot=rv:6e6d1a75832a2f
```

This corresponds with the explicit randomness value, an unsigned integer value, of 0x6e6d1a75832a2f. This randomness value is meant to be used instead of the least-significant 56 bits of the TraceID. In this example, the 56-bit fraction (i.e., 0x6e6d1a75832a2f / 0x100000000000000 = 43.1%) supports making a consistent positive sampling decision at probabilities ranging from 56.9% through 100% (i.e., rejection thresohld values 0x6e6d1a75832a2f through 0), the same as for a hexadecimal TraceID ending in 6e6d1a75832a2f without explicit randomness value.
