# TraceState Handling

**Status**: [Experimental](../document-status.md)

In alignment to the [TraceContext](https://www.w3.org/TR/trace-context/) specification, this section uses the
Augmented Backus-Naur Form (ABNF) notation of [RFC5234](https://www.w3.org/TR/trace-context/#bib-rfc5234),
including the DIGIT rule in that document.

When setting [TraceState](api.md#tracestate) values that are part of the OTel ecosystem,
they MUST all be contained in a single entry using the `ot` key, with the value being
a semicolon separated list of key-value pairs such as:

* `ot=p:8;r:64`
* `ot=foo:bar;k1:13`

The list can be formally defined as:

```
list        = list-member *( ";" list-member )
list-member = key ":" value
```

The complete list length MUST NOT exceed 256 characters, as defined by the
[TraceState value section](https://www.w3.org/TR/trace-context/#value),
and the used keys MUST be unique.

## Key

The key is an identifier that describes an OTel concern.
Simple examples are `p`, `ts`, or `s1`.

The key can be formally defined as:

```
key        = lcalpha *(lcalpha / DIGIT )
lcalpha    = %x61-7A ; a-z
```

Specific keys used by OTel concerns MUST be defined as part as the Specification.

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

* `ot=p:8;r:64` will become `ot=p:8;r:64;k1:13`.
* `ot=p:8,r:64;k1:7` will become `ot:p8;r:64;k1:13`.

If setting a value ends up making the entire `ot` entry exceed the 256 characters limit,
SDKs are advised to abort the operation and signal the user about the error, e.g.

```go
traceState, err := SetTraceStateValue(traceState, value)
if err != nil {
  // Could not set the specified value, traceState was not updated.
}
```

