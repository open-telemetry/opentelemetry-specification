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
- [Conflict Resolution](#conflict-resolution)

</details>

## Overview

The Baggage API consists of:

- the `Baggage`
- functions to interact with the `Baggage` in a `Context`

The functions described here are one way to approach interacting with the Baggage
purely via the Context. Depending on language idioms, a language API MAY implement these functions
by providing a struct or immutable object that represents the entire Baggage contents. This
construct could then be added or removed from the Context with a single operation. For example,
the [Clear](#clear) function could be implemented by having the user set an empty Baggage object/struct
into the context. The [Get all](#get-all) function could be implemented by returning the Baggage
object as a whole from the function call. If an idiom like this is implemented, the Baggage object/struct
MUST be immutable, so that the containing Context also remains immutable.

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

`Name` The name for which to set the value, of type string.

`Value` The value to set, of type string.

OPTIONAL parameters:

`Metadata` Optional metadata associated with the name-value pair. This should be an opaque wrapper
for a string with no semantic meaning. Left opaque to allow for future functionality.

`Context` The context containing the `Baggage` in which to set the baggage entry.

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

The API layer MAY include the following `Propagator`s:

* A `TextMapPropagator` implementing the [W3C Baggage Specification](https://w3c.github.io/baggage).

Note: The W3C baggage specification does not currently assign semantic meaning to the optional metadata.

On `extract`, the propagator should store all metadata as a single metadata instance per entry.
On `inject`, the propagator should append the metadata per the W3C specification format.

Notes:

If the propagator is unable to parse the `baggage` header, `extract` MUST return a Context with no baggage entries in it.

If the `baggage` header is present, but contains no entries, `extract` MUST return a Context with
no baggage entries in it.

## Conflict Resolution

If a new name/value pair is added and its name is the same as an existing name, than the new pair MUST take precedence. The value
is replaced with the added value (regardless if it is locally generated or received from a remote peer).
