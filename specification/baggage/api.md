# API

**Status**: [Stable, Feature-freeze](../document-status.md)

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
- [Functions](#functions)
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

`Baggage` is used to annotate telemetry, adding context and information to metrics,
traces and logs. It is a set of name/value pairs that describe user-defined properties.

The API consists of

- The `Baggage`
- Functions to interact with the `Baggage` in a `Context`
  - `setValue`
  - `getValue`
  - `getAllValues`
  - `removeValue`

The functions described here are one way to approach interacting with the `Baggage` via
having a struct/object that represents the entire Baggage content.

##### Requirement 1

> Each name in `Baggage` **MUST** be associated with exactly one value.

##### Requirement 2

> The order of name/value pairs in the `Baggage` **MUST NOT** be significant.

##### Requirement 3

> The API **MAY** implement these functions by interacting with the baggage via the
> `Context` directly.

##### Requirement 4

> The API **MUST** be fully functional in the absence of an installed SDK.

[This](#requirement-2) is required to enable transparent cross-process Baggage
propagation. If a Baggage propagator is installed into the API, it will work with or
without an installed SDK.

##### Requirement 5

> The `Baggage` container **MUST** be immutable.

[This](#requirement-3) is required so that the containing `Context` also remains
immutable.

## Functions

### Get Value

This function gives access to the value of a name/value pair set by a prior event.

##### Requirement 6

> The API **MUST** provide a `getValue` function that takes a required name parameter
> and returns a value associated with the given name, or null if the given name is not
> present.

### Get All Values

This function gives access to all the name/value pairs in the `Baggage`.

##### Requirement 7

> The API **MUST** provide a `getAllValues` function that returns either an immutable
> collection of name/value pairs on the `Baggage` or an iterator on such collection.

### Set Value

This operation makes it possible to record the value for a name/value pair.

##### Requirement 8

> The API **MUST** provide a `setValue` function which takes a required name, a required
> value and optional metadata and returns a new `Baggage` that contains the new value.

##### Requirement 9

> The API **MAY** implement the `setValue` function by using a `Builder` pattern and
> exposing a way to construct a `Builder` from a `Baggage`.

The optional `setValue` metadata is associated with the name-value pair that is being
set.

##### Requirement 10

> The optional `setValue` metadata parameter **SHOULD** be an opaque wrapper for a
> string with no semantic meaning.

This metadata is left opaque to allow for future functionality.

### Remove Value

##### Requirement 11

> To delete a name/value pair, the API **MUST** provide a `removeValue` function which
> takes a required name and returns a new `Baggage` which no longer contains the
> selected name.

##### Requirement 12

> The API **MAY** implement the `removeValue` function by using a `Builder` pattern and
> exposing a way to construct a `Builder` from a `Baggage`.

## Context Interaction

This section defines all functions within the API that interact with the
[`Context`](../context/context.md).

##### Condition 1

> The API does not operate directly on the `Context`.
>
> ##### Conditional Requirement 1.1
>
> > The API **MUST** provide an `extract` function to extract the `Baggage` from a
> > `Context` instance.
>
> ##### Conditional Requirement 1.2
>
> > The API **MUST** provide an `inject` function to inject the `Baggage` in a
> > `Context` instance.

The functionality listed above is necessary because if the API does not operate directly
on the `Context`, then users should not have access to the
[Context Key](../context/context.md#create-a-key) used by the API.

##### Requirement 13

> The API SHOULD NOT provide access to the its
[Context Key](../context/context.md#create-a-key).

##### Condition 2

> The language has support for implicitly propagated `Context`
> (see [here](../context/context.md#optional-global-operations)).
>
> ##### Conditional Requirement 2.1
>
> > The API **SHOULD** provide a get `Baggage` functionality to get the currently active
> > `Baggage` from the implicit context and a set `Baggage` functionality to set the
> > currently active `Baggage` into the implicit context.
> >
> > ##### Condition 2.1
> >
> > > The API provides a functionality to get the currently active `Baggage` from the
> > > implicit context and a functionality to set the currently active `Baggage` into
> > > the implicit context.
> > >
> > > ##### Conditional Requirement 2.1.1
> > >
> > > > The get `Baggage` functionality behavior **MUST** be equivalent to getting the
> > > > implicit context, then extracting the `Baggage` from the context.
> > >
> > > ##### Conditional Requirement 2.1.2
> > >
> > > > The set `Baggage` functionality behavior **MUST** be equivalent to getting the
> > > > implicit context, then inserting the `Baggage` into the context.
> > >
> > > ##### Conditional Requirement 2.1.3
> > >
> > > > The get and set `Baggage` functionalities **MUST** operate solely on the context
> > > > API.
> > >
> > > ##### Conditional Requirement 2.1.4
> > >
> > > > The get and set `Baggage` functionalities **MAY** be exposed
> > > > - as static methods on the baggage module or
> > > > - as static methods on a class inside the baggage module or
> > > > - on the `Baggage` class
> > >
> > > ##### Conditional Requirement 2.1.5
> > >
> > > > The get and set `Baggage` functionalities **SHOULD** be fully implemented in
> > > > the API.

### Clear Baggage in the Context

To avoid sending any name/value pairs to an untrusted process, the API must provide a
way to remove all baggage entries from a context.

##### Requirement 14

> The API **MUST** provide a way to remove all baggage entries from a context.

This functionality can be implemented by having the user set an empty `Baggage`
object/struct into the context, or by providing an API that takes a `Context` as
input, and returns a new `Context` with no `Baggage` associated.

## Propagation

`Baggage` may be propagated across process boundaries or across any arbitrary boundaries
(process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various reasons.

##### Requirement 15

> The API or an extension package **MUST** include a `TextMapPropagator` which
> implements the [W3C Baggage Specification](https://w3c.github.io/baggage)[^1].

[^1]: The W3C baggage specification does not currently assign semantic meaning to the
optional metadata.

See [Propagators Distribution](../context/api-propagators.md#propagators-distribution)
for how propagators are to be distributed.

##### Requirement 16

> On `extract`, a propagator **SHOULD** store all metadata as a single metadata instance
> per entry.

##### Requirement 17

> On `inject`, a propagator **SHOULD** append the metadata per the W3C specification
> format.

Refer to the API Propagators [Operation](../context/api-propagators.md#operations)
section for the additional requirements these operations need to follow.

## Conflict Resolution

##### Requirement 18

> If a new name/value pair is added and its name is the same as an existing name, then
> the new pair **MUST** take precedence, the existing value being replaced with the
> added value (regardless if it is locally generated or received from a remote peer).
