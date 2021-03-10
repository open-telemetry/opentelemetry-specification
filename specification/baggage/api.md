# Baggage API

**Status**: [Stable, Feature-freeze](../document-status.md)

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
- [Operations](#operations)
  - [Get Value](#get-value)
  - [Get All Values](#get-all-values)
  - [Set Value](#set-value)
  - [Remove Value](#remove-value)
- [Context Interaction](#context-interaction)
  - [Clear Baggage in the Context](#clear-baggage-in-the-context)
- [Propagation](#propagation)
- [Conflict Resolution](#conflict-resolution)

</details>

## Overview

`Baggage` is used to annotate telemetry, adding context and information to
metrics, traces, and logs. It is a set of name/value pairs describing
user-defined properties. Each name in `Baggage` MUST be associated with
exactly one value.

The Baggage API consists of:

- the `Baggage`
- functions to interact with the `Baggage` in a `Context`

The functions described here are one way to approach interacting with the
`Baggage` via having struct/object that represents the entire Baggage content.
Depending on language idioms, a language API MAY implement these functions by
interacting with the baggage via the `Context` directly.

The Baggage API MUST be fully functional in the absence of an installed SDK.
This is required in order to enable transparent cross-process Baggage
propagation. If a Baggage propagator is installed into the API, it will work
with or without an installed SDK.

The `Baggage` container MUST be immutable, so that the containing `Context`
also remains immutable.

## Operations

### Get Value

To access the value for a name/value pair set by a prior event, the Baggage API
MUST provide a function that takes the name as input, and returns a value
associated with the given name, or null if the given name is not present.

REQUIRED parameters:

`Name` the name to return the value for.

### Get All Values

Returns the name/value pairs in the `Baggage`. The order of name/value pairs
MUST NOT be significant. Based on the language specifics, the returned
value can be either an immutable collection or an iterator on the immutable
collection of name/value pairs in the `Baggage`.

### Set Value

To record the value for a name/value pair, the Baggage API MUST provide a
function which takes a name, and a value as input. Returns a new `Baggage`
that contains the new value. Depending on language idioms, a language API MAY
implement these functions by using a `Builder` pattern and exposing a way to
construct a `Builder` from a `Baggage`.

REQUIRED parameters:

`Name` The name for which to set the value, of type string.

`Value` The value to set, of type string.

OPTIONAL parameters:

`Metadata` Optional metadata associated with the name-value pair. This should be
an opaque wrapper for a string with no semantic meaning. Left opaque to allow
for future functionality.

### Remove Value

To delete a name/value pair, the Baggage API MUST provide a function which
takes a name as input. Returns a new `Baggage` which no longer contains the
selected name. Depending on language idioms, a language API MAY
implement these functions by using a `Builder` pattern and exposing a way to
construct a `Builder` from a `Baggage`.

REQUIRED parameters:

`Name` the name to remove.

## Context Interaction

This section defines all operations within the Baggage API that interact with
the [`Context`](../context/context.md).

If an implementation of this API does not operate directly on the `Context`, it
MUST provide the following functionality to interact with a `Context` instance:

- Extract the `Baggage` from a `Context` instance
- Insert the `Baggage` to a `Context` instance

The functionality listed above is necessary because API users SHOULD NOT have
access to the [Context Key](../context/context.md#create-a-key) used by the
Baggage API implementation.

If the language has support for implicitly propagated `Context` (see
[here](../context/context.md#optional-global-operations)), the API SHOULD also
provide the following functionality:

- Get the currently active `Baggage` from the implicit context. This is
equivalent to getting the implicit context, then extracting the `Baggage` from
the context.
- Set the currently active `Baggage` to the implicit context. This is equivalent
to getting the implicit context, then inserting the `Baggage` to the context.

All the above functionalities operate solely on the context API, and they MAY be
exposed as static methods on the baggage module, as static methods on a class
inside the baggage module (it MAY be named `BaggageUtilities`), or on the
`Baggage` class. This functionality SHOULD be fully implemented in the API when
possible.

### Clear Baggage in the Context

To avoid sending any name/value pairs to an untrusted process, the Baggage API
MUST provide a way to remove all baggage entries from a context.

This functionality can be implemented by having the user set an empty `Baggage`
object/struct into the context, or by providing an API that takes a `Context` as
input, and returns a new `Context` with no `Baggage` associated.

## Propagation

`Baggage` MAY be propagated across process boundaries or across any arbitrary
boundaries (process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various
reasons.

The API layer or an extension package MUST include the following `Propagator`s:

* A `TextMapPropagator` implementing the [W3C Baggage Specification](https://w3c.github.io/baggage).

See [Propagators Distribution](../context/api-propagators.md#propagators-distribution)
for how propagators are to be distributed.

Note: The W3C baggage specification does not currently assign semantic meaning
to the optional metadata.

On `extract`, the propagator should store all metadata as a single metadata instance per entry.
On `inject`, the propagator should append the metadata per the W3C specification format.

Notes:

If the propagator is unable to parse the incoming `baggage`, `extract` MUST return
a `Context` with no baggage entries in it.

If the incoming `baggage` is present, but contains no entries, `extract` MUST
return a `Context` with no baggage entries in it.

## Conflict Resolution

If a new name/value pair is added and its name is the same as an existing name,
than the new pair MUST take precedence. The value is replaced with the added
value (regardless if it is locally generated or received from a remote peer).
