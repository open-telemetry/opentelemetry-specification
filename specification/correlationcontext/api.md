# Correlations API

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
  - [CorrelationContext](#correlationcontext)
  - [Get correlations](#get-correlations)
  - [Get correlation](#get-correlation)
  - [Set correlation](#set-correlation)
  - [Remove correlation](#remove-correlation)
  - [Clear correlations](#clear-correlations)
- [CorrelationContext Propagation](#correlationcontext-propagation)
  - [Serialization](#serialization)
- [Conflict Resolution](#conflict-resolution)

</details>

## Overview

The Correlations API consists of:

- the `CorrelationContext`
- functions to interact with the `CorrelationContext` in a `Context`

### CorrelationContext

`CorrelationContext` is used to annotate telemetry, adding context and information to metrics, traces, and logs.
It is an abstract data type represented by a set of name/value pairs describing user-defined properties.
Each name in `CorrelationContext` MUST be associated with exactly one value.

### Get correlations

Returns the name/value pairs in the `CorrelationContext`. The order of name/value pairs MUST NOT be
significant. Based on the language specification, the returned value can be
either an immutable collection or an immutable iterator to the collection of
name/value pairs in the `CorrelationContext`.

OPTIONAL parameters:

`Context` the context containing the `CorrelationContext` from which to get the correlations.

### Get correlation

To access the value for a name/value pair by a prior event, the Correlations API
SHALL provide a function that takes a context and a name as input, and returns a
value. Returns the value associated with the given name, or null
if the given name is not present.

REQUIRED parameters:

`Name` the name to return the value for.

OPTIONAL parameters:

`Context` the context containing the `CorrelationContext` from which to get the correlation.

### Set correlation

To record the value for a name/value pair, the Correlations API SHALL provide a function which
takes a context, a name, and a value as input. Returns a new `Context` which
contains a `CorrelationContext` with the new value.

REQUIRED parameters:

`Name` the name for which to set the value.

`Value` the value to set.

OPTIONAL parameters:

`Context` the context containing the `CorrelationContext` in which to set the correlation.

### Remove correlation

To delete a name/value pair, the Correlations API SHALL provide a function which takes a context
and a name as input. Returns a new `Context` which no longer contains the selected name.

REQUIRED parameters:

`Name` the name to remove.

OPTIONAL parameters:

`Context` the context containing the `CorrelationContext` from which to remove the correlation.

### Clear correlations

To avoid sending any name/value pairs to an untrusted process, the Correlations API SHALL provide
a function to remove all Correlations from a context. Returns a new `Context`
with no correlations.

OPTIONAL parameters:

`Context` the context containing the `CorrelationContext` from which to remove all correlations.

## CorrelationContext Propagation

`CorrelationContext` MAY be propagated across process boundaries or across any arbitrary boundaries
(process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various reasons.

### Serialization

Until the [W3C Correlation Context](https://w3c.github.io/correlation-context/) specification is recommended for use, OpenTelemetry `CorrelationContext` implementations MUST be serialized according to the [editor's draft of W3C Correlation Context as of March 27, 2020](https://github.com/w3c/correlation-context/blob/c974664b9ab4d33af6355f1f7f03a2d52c89a99e/correlation_context/HTTP_HEADER_FORMAT.md) using a vendor-specific header name to avoid collisions with the W3C Correlation Context specification should it change in the future.

#### Header Name

`CorrelationContext` implementations MUST use the header name `otcorrelations`.

#### Header Value

`CorrelationContext` MUST be serialized according to the [editor's draft of W3C Correlation Context as of March 27, 2020](https://github.com/w3c/correlation-context/blob/c974664b9ab4d33af6355f1f7f03a2d52c89a99e/correlation_context/HTTP_HEADER_FORMAT.md).

`CorrelationContext` values MUST be serialized as Percent-Encoded UTF-8 strings according to [RFC 3986 Section 2.1](https://tools.ietf.org/html/rfc3986#section-2.1).

#### Example

Correlation Context:

```json
{
  "user": "foo@example.com",
  "name": "Example Name"
}
```

Header:

```
otcorrelations: user=foo%40example.com,name=Example%20Name
```

## Conflict Resolution

If a new name/value pair is added and its name is the same as an existing name, than the new pair MUST take precedence. The value
is replaced with the added value (regardless if it is locally generated or received from a remote peer).
