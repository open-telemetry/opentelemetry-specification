# Baggage API

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
  - [Baggage](#baggage)
  - [Get baggages](#get-all)
  - [Get baggage](#get-baggage)
  - [Set baggage](#set-baggage)
  - [Remove baggage](#remove-baggage)
  - [Clear](#clear)
- [Baggage Propagation](#baggage-propagation)
  - [Serialization](#serialization)
- [Conflict Resolution](#conflict-resolution)

</details>

## Overview

The Baggage API consists of:

- the `Baggage`
- functions to interact with the `Baggage` in a `Context`

### Baggage

`Baggage` is used to annotate telemetry, adding context and information to metrics, traces, and logs.
It is an abstract data type represented by a set of name/value pairs describing user-defined properties.
Each name in `Baggage` MUST be associated with exactly one value.

### Get all

Returns the name/value pairs in the `Baggage`. The order of name/value pairs MUST NOT be
significant. Based on the language specification, the returned value can be
either an immutable collection or an immutable iterator to the collection of
name/value pairs in the `Baggage`.

OPTIONAL parameters:

`Context` the context containing the `Baggage` from which to get the baggages.

### Get baggage

To access the value for a name/value pair by a prior event, the Baggage API
SHALL provide a function that takes a context and a name as input, and returns a
value. Returns the value associated with the given name, or null
if the given name is not present.

REQUIRED parameters:

`Name` the name to return the value for.

OPTIONAL parameters:

`Context` the context containing the `Baggage` from which to get the baggage entry.

### Set baggage

To record the value for a name/value pair, the Baggage API SHALL provide a function which
takes a context, a name, and a value as input. Returns a new `Context` which
contains a `Baggage` with the new value.

REQUIRED parameters:

`Name` the name for which to set the value.

`Value` the value to set.

OPTIONAL parameters:

`Context` the context containing the `Baggage` in which to set the baggage entry.

### Remove baggage

To delete a name/value pair, the Baggage API SHALL provide a function which takes a context
and a name as input. Returns a new `Context` which no longer contains the selected name.

REQUIRED parameters:

`Name` the name to remove.

OPTIONAL parameters:

`Context` the context containing the `Baggage` from which to remove the baggage entry.

### Clear

To avoid sending any name/value pairs to an untrusted process, the Baggage API SHALL provide
a function to remove all baggage entries from a context. Returns a new `Context`
with no `Baggage`.

OPTIONAL parameters:

`Context` the context containing the `Baggage` from which to remove all baggage entries.

## Baggage Propagation

`Baggage` MAY be propagated across process boundaries or across any arbitrary boundaries
(process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various reasons.

### Serialization

Until the [W3C Baggage](https://w3c.github.io/baggage/) specification is recommended for use, OpenTelemetry `Baggage` implementations MUST be serialized according to the [editor's draft of W3C Correlation Context as of March 27, 2020](https://github.com/w3c/correlation-context/blob/c974664b9ab4d33af6355f1f7f03a2d52c89a99e/correlation_context/HTTP_HEADER_FORMAT.md) using a vendor-specific header name to avoid collisions with the W3C Baggage specification should it change in the future.

#### Header Name

`Baggage` implementations MUST use the header name `otcorrelations`.

#### Header Value

`Baggage` MUST be serialized according to the [editor's draft of W3C Correlation Context as of March 27, 2020](https://github.com/w3c/correlation-context/blob/c974664b9ab4d33af6355f1f7f03a2d52c89a99e/correlation_context/HTTP_HEADER_FORMAT.md).

`Baggage` values MUST be serialized as Percent-Encoded UTF-8 strings according to [RFC 3986 Section 2.1](https://tools.ietf.org/html/rfc3986#section-2.1).

#### Example

Baggage:

```json
{
  "user": "foo@example.com",
  "name": "Example Name"
}
```

Header:

```
otbaggages: user=foo%40example.com,name=Example%20Name
```

## Conflict Resolution

If a new name/value pair is added and its name is the same as an existing name, than the new pair MUST take precedence. The value
is replaced with the added value (regardless if it is locally generated or received from a remote peer).
