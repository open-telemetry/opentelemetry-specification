# Propagators API

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
- [Propagator Types](#propagator-types)
  - [Carrier](#carrier)
  - [Operations](#operations)
    - [Inject](#inject)
    - [Extract](#extract)
- [HTTPText Propagator](#httptext-propagator)
  - [Fields](#fields)
  - [Inject](#inject-1)
    - [Setter argument](#setter-argument)
      - [Set](#set)
  - [Extract](#extract-1)
    - [Getter argument](#getter-argument)
      - [Get](#get)
- [Composite Propagator](#composite-propagator)
- [Global Propagators](#global-propagators)

</details>

## Overview

Cross-cutting concerns send their state to the next process using
`Propagator`s, which are defined as objects used to read and write
context data to and from messages exchanged by the applications.
Each concern creates a set of `Propagator`s for every supported
`Propagator` type.

`Propagator`s leverage the `Context` to inject and extract data for each
cross-cutting concern, such as traces and correlation context.

Propagation is usually implemented via a cooperation of library-specific request
interceptors and `Propagators`, where the interceptors detect incoming and outgoing requests and use the `Propagator`'s extract and inject operations respectively.

The Propagators API is expected to be leveraged by users writing
instrumentation libraries.

## Propagator Types

A `Propagator` type defines the restrictions imposed by a specific transport
and is bound to a data type, in order to propagate in-band context data across process boundaries.

The Propagators API currently defines one `Propagator` type:

- `HTTPTextPropagator` is a type that inject values into and extracts values
  from carriers as string key/value pairs.

A binary `Propagator` type will be added in the future (see [#437](https://github.com/open-telemetry/opentelemetry-specification/issues/437)).

### Carrier

A carrier is the medium used by `Propagator`s to read values from and write values to.
Each specific `Propagator` type defines its expected carrier type, such as a string map
or a byte array.

Carriers used at [Inject](#inject) are expected to be mutable.

### Operations

`Propagator`s MUST define `Inject` and `Extract` operations, in order to write
values to and read values from carriers respectively. Each `Propagator` type MUST define the specific carrier type
and CAN define additional parameters.

#### Inject

Injects the value into a carrier. For example, into the headers of an HTTP request.

Required arguments:

- A `Context`. The Propagator MUST retrieve the appropriate value from the `Context` first, such as
`SpanContext`, `CorrelationContext` or another cross-cutting concern context.
- The carrier that holds the propagation fields. For example, an outgoing message or HTTP request.

#### Extract

Extracts the value from an incoming request. For example, from the headers of an HTTP request.

If a value can not be parsed from the carrier for a cross-cutting concern,
the implementation MUST NOT throw an exception and MUST NOT store a new value in the `Context`,
in order to preserve any previously existing valid value.

Required arguments:

- A `Context`.
- The carrier that holds the propagation fields. For example, an incoming message or http response.

Returns a new `Context` derived from the `Context` passed as argument,
containing the extracted value, which can be a `SpanContext`,
`CorrelationContext` or another cross-cutting concern context.

## HTTPText Propagator

`HTTPTextPropagator` performs the injection and extraction of a cross-cutting concern
value as string key/values pairs into carriers that travel in-band across process boundaries.

The carrier of propagated data on both the client (injector) and server (extractor) side is
usually an HTTP request.

`Getter` and `Setter` are optional helper components used for extraction and injection respectively,
and are defined as separate objects from the carrier to avoid runtime allocations,
by removing the need for additional interface-implementing-objects wrapping the carrier in order
to access its contents.

`Getter` and `Setter` MUST be stateless and allowed to be saved as constants, in order to effectively
avoid runtime allocations.

### Fields

The propagation fields defined. If your carrier is reused, you should delete the fields here
before calling [inject](#inject).

Fields are defined as string keys identifying format-specific components in a carrier.

For example, if the carrier is a single-use or immutable request object, you don't need to
clear fields as they couldn't have been set before. If it is a mutable, retryable object,
successive calls should clear these fields first.

The use cases of this are:

- allow pre-allocation of fields, especially in systems like gRPC Metadata
- allow a single-pass over an iterator

Returns list of fields that will be used by the `HttpTextPropagator`.

### Inject

Injects the value into a carrier. The required arguments are the same as defined by
the base [Inject](#inject) operation.

Optional arguments:

- A `Setter` invoked for each propagation key to add or remove. This is an additional
  argument that languages are free to define to help inject data into the carrier.

#### Setter argument

Setter is an argument in `Inject` that sets values into given fields.

`Setter` allows a `HttpTextPropagator` to set propagated fields into a carrier.

One of the ways to implement it is `Setter` class with `Set` method as described below.

##### Set

Replaces a propagated field with the given value.

Required arguments:

- the carrier holding the propagation fields. For example, an outgoing message or an HTTP request.
- the key of the field.
- the value of the field.

The implementation SHOULD preserve casing (e.g. it should not transform `Content-Type` to `content-type`) if the used protocol is case insensitive, otherwise it MUST preserve casing.

### Extract

Extracts the value from an incoming request. The required arguments are the same as defined by
the base [Extract](#extract) operation.

Optional arguments:

- A `Getter` invoked for each propagation key to get. This is an additional
  argument that languages are free to define to help extract data from the carrier.

Returns a new `Context` derived from the `Context` passed as argument.

#### Getter argument

Getter is an argument in `Extract` that get value from given field

`Getter` allows a `HttpTextPropagator` to read propagated fields from a carrier.

One of the ways to implement it is `Getter` class with `Get` method as described below.

##### Get

The Get function MUST return the first value of the given propagation key or return null if the key doesn't exist.

Required arguments:

- the carrier of propagation fields, such as an HTTP request.
- the key of the field.

The Get function is responsible for handling case sensitivity. If the getter is intended to work with a HTTP request object, the getter MUST be case insensitive.

## Injectors and Extractors as Separate Interfaces

Languages can choose to implement a `Propagator` type as a single object
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

Each composite `Propagator` will implement a specific `Propagator` type, such
as `HttpTextPropagator`, as different `Propagator` types will likely operate on different
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
each supported `Propagator` type.

If offered, the global `Propagator`s should default to a composite `Propagator`
containing the W3C Trace Context Propagator and the Correlation Context `Propagator`
specified in [api-correlationcontext.md](../correlationcontext/api.md#serialization),
in order to provide propagation even in the presence of no-op
OpenTelemetry implementations.

### Get Global Propagator

This method MUST exist for each supported `Propagator` type.

Returns a global `Propagator`. This usually will be composite instance.

### Set Global Propagator

This method MUST exist for each supported `Propagator` type.

Sets the global `Propagator` instance.

Required parameters:

- A `Propagator`. This usually will be a composite instance.
