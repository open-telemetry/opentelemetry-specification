# Propagators API

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
- [HTTP Text Format](#http-text-format)
  - [Fields](#fields)
  - [Inject](#inject)
    - [Setter argument](#setter)
      - [Set](#set)
  - [Extract](#extract)
    - [Getter argument](#getter)
      - [Get](#get)
- [Composite Propagator](#composite-propagator)
- [Global Propagators](#global-propagators)

</details>

## Overview

Cross-cutting concerns send their state to the next process using
`Propagator`s, which are defined as objects used to read and write
context data to and from messages exchanged by the applications.
Each concern creates a set of `Propagator`s for every supported `Format`.

Propagators leverage the `Context` to inject and extract data for each
cross-cutting concern, such as traces and correlation context.

The Propagators API is expected to be leveraged by users writing
instrumentation libraries.

The Propagators API currently consists of one `Format`:

- `HTTPTextFormat` is used to inject values into and extract values from carriers as text that travel
  in-band across process boundaries.

A binary `Format` will be added in the future.

## HTTP Text Format

`HTTPTextFormat` is a formatter that injects and extracts a cross-cutting concern
value as text into carriers that travel in-band across process boundaries.

Encoding is expected to conform to the HTTP Header Field semantics. Values are often encoded as
RPC/HTTP request headers.

The carrier of propagated data on both the client (injector) and server (extractor) side is
usually an http request. Propagation is usually implemented via library-specific request
interceptors, where the client-side injects values and the server-side extracts them.

`HTTPTextFormat` MUST expose the APIs that injects values into carriers,
and extracts values from carriers.

### Fields

The propagation fields defined. If your carrier is reused, you should delete the fields here
before calling [inject](#inject).

For example, if the carrier is a single-use or immutable request object, you don't need to
clear fields as they couldn't have been set before. If it is a mutable, retryable object,
successive calls should clear these fields first.

The use cases of this are:

- allow pre-allocation of fields, especially in systems like gRPC Metadata
- allow a single-pass over an iterator

Returns list of fields that will be used by this formatter.

### Inject

Injects the value downstream. For example, as http headers.

Required arguments:

- A `Context`. The Propagator MUST retrieve the appropriate value from the `Context` first, such as `SpanContext`, `CorrelationContext` or another cross-cutting concern context. For languages supporting current `Context` state, this argument is OPTIONAL, defaulting to the current `Context` instance.
- the carrier that holds propagation fields. For example, an outgoing message or http request.
- the `Setter` invoked for each propagation key to add or remove.

#### Setter argument

Setter is an argument in `Inject` that sets value into given field.

`Setter` allows a `HTTPTextFormat` to set propagated fields into a carrier.

`Setter` MUST be stateless and allowed to be saved as a constant to avoid runtime allocations. One of the ways to implement it is `Setter` class with `Set` method as described below.

##### Set

Replaces a propagated field with the given value.

Required arguments:

- the carrier holds propagation fields. For example, an outgoing message or http request.
- the key of the field.
- the value of the field.

The implemenation SHOULD preserve casing (e.g. it should not transform `Content-Type` to `content-type`) if the used protocol is case insensitive, otherwise it MUST preserve casing.

### Extract

Extracts the value from an incoming request. For example, from the headers of an HTTP request.

If a value can not be parsed from the carrier for a cross-cutting concern,
the implementation MUST NOT throw an exception and MUST NOT store a new value in the `Context`,
in order to preserve any previously existing valid value.

Required arguments:

- A `Context`. For languages supporting current `Context` state this argument is OPTIONAL, defaulting to the current `Context` instance.
- the carrier holds propagation fields. For example, an outgoing message or http request.
- the instance of `Getter` invoked for each propagation key to get.

Returns a new `Context` derived from the `Context` passed as argument,
containing the extracted value, which can be a `SpanContext`,
`CorrelationContext` or another cross-cutting concern context.

If the extracted value is a `SpanContext`, its `IsRemote` property MUST be set to true.

#### Getter argument

Getter is an argument in `Extract` that get value from given field

`Getter` allows a `HttpTextFormat` to read propagated fields from a carrier.

`Getter` MUST be stateless and allowed to be saved as a constant to avoid runtime allocations. One of the ways to implement it is `Getter` class with `Get` method as described below.

##### Get

The Get function MUST return the first value of the given propagation key or return null if the key doesn't exist.

Required arguments:

- the carrier of propagation fields, such as an HTTP request.
- the key of the field.

The Get function is responsible for handling case sensitivity. If the getter is intended to work with a HTTP request object, the getter MUST be case insensitive. To improve compatibility with other text-based protocols, text `Format` implementions MUST ensure to always use the canonical casing for their attributes. NOTE: Canonical casing for HTTP headers is usually title case (e.g. `Content-Type` instead of `content-type`).

## Injectors and Extractors as Separate Interfaces

Languages can choose to implement a `Propagator` for a format as a single object
exposing `Inject` and `Extract` methods, or they can opt to divide the
responsibilities further into individual `Injector`s and `Extractor`s. A
`Propagator` can be implemented by composing individual `Injector`s and
`Extractors`.

## Composite Propagator

Implementations MUST offer a facility to group multiple `Propagator`s
from different cross-cutting concerns in order to leverage them as a
single entity.

A composite propagator can be built from a list of propagators, or a list of
injectors and extractors. The resulting composite `Propagator` will invoke the `Propagator`s, `Injector`s, or `Extractor`s, in the order they were specified.

Each composite `Propagator` will be bound to a specific `Format`, such
as `HttpTextFormat`, as different `Format`s will likely operate on different
data types.
There MUST be functions to accomplish the following operations.

- Create a composite propagator
- Extract from a composite propagator
- Inject into a composite propagator

### Create a Composite Propagator

Required arguments:

- A list of `Propagator`s or a list of `Injector`s and `Extractor`s.

Returns a new composite `Propagator` with the specified `Propagator`s.

### Extract

Required arguments:

- A `Context`.
- The carrier that holds propagation fields.
- The instance of `Getter` invoked for each propagation key to get.

### Inject

Required arguments:

- A `Context`.
- The carrier that holds propagation fields.
- The `Setter` invoked for each propagation key to add or remove.

## Global Propagators

Implementations MAY provide global `Propagator`s for
each supported `Format`.

If offered, the global `Propagator`s should default to a composite `Propagator`
containing the W3C Trace Context Propagator and the Correlation Context `Propagator`
specified in [api-correlationcontext.md](../correlationcontext/api.md#serialization),
in order to provide propagation even in the presence of no-op
OpenTelemetry implementations.

### Get Global Propagator

This method MUST exist for each supported `Format`.

Returns a global `Propagator`. This usually will be composite instance.

### Set Global Propagator

This method MUST exist for each supported `Format`.

Sets the global `Propagator` instance.

Required parameters:

- A `Propagator`. This usually will be a composite instance.
