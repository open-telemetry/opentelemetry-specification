<!--- Hugo front matter used to generate the website version of this page:
--->

# Propagators

**Status**: [Stable](../document-status.md)

**Concept**: [Propagation](/docs/context-propagation/#propagation)

## Overview

Cross-cutting concerns send their state to the next process using
`Propagator`s, which are defined as objects used to read and write
context data to and from messages exchanged by the applications.
Each concern creates a set of `Propagator`s for every supported
`Propagator` type.

`Propagator`s leverage the `Context` to inject and extract data for each
cross-cutting concern, such as traces and `Baggage`.

Propagation is usually implemented via a cooperation of library-specific request
interceptors and `Propagators`, where the interceptors detect incoming and outgoing requests and use the `Propagator`'s extract and inject operations respectively.

The Propagators API is expected to be leveraged by users writing
instrumentation libraries.

## Propagator Types

A `Propagator` type defines the restrictions imposed by a specific transport
and is bound to a data type, in order to propagate in-band context data across process boundaries.

The Propagators API currently defines one `Propagator` type:

- `TextMapPropagator` is a type that injects values into and extracts values
  from carriers as string key/value pairs.

### Carrier

A carrier is the medium used by `Propagator`s to read values from and write values to.
Each specific `Propagator` type defines its expected carrier type, such as a string map
or a byte array.

Carriers used at [Inject](api.md#inject) are expected to be mutable.
