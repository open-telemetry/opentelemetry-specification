# Propagators API

**Status**: [Stable, Feature-Freeze](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Propagator Types](#propagator-types)
  * [Carrier](#carrier)
  * [Operations](#operations)
    + [Inject](#inject)
    + [Extract](#extract)
- [TextMap Propagator](#textmap-propagator)
  * [Fields](#fields)
  * [TextMap Inject](#textmap-inject)
    + [Setter argument](#setter-argument)
      - [Set](#set)
  * [TextMap Extract](#textmap-extract)
    + [Getter argument](#getter-argument)
      - [Keys](#keys)
      - [Get](#get)
- [Injectors and Extractors as Separate Interfaces](#injectors-and-extractors-as-separate-interfaces)
- [Composite Propagator](#composite-propagator)
  * [Create a Composite Propagator](#create-a-composite-propagator)
  * [Composite Extract](#composite-extract)
  * [Composite Inject](#composite-inject)
- [Global Propagators](#global-propagators)
  * [Get Global Propagator](#get-global-propagator)
  * [Set Global Propagator](#set-global-propagator)
- [Propagators Distribution](#propagators-distribution)
  * [B3 Requirements](#b3-requirements)
    + [B3 Extract](#b3-extract)
    + [B3 Inject](#b3-inject)
    + [Fields](#fields-1)
    + [Configuration](#configuration)

<!-- tocstop -->

</details>

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

A binary `Propagator` type will be added in the future (see [#437](https://github.com/open-telemetry/opentelemetry-specification/issues/437)).

### Carrier

A carrier is the medium used by `Propagator`s to read values from and write values to.
Each specific `Propagator` type defines its expected carrier type, such as a string map
or a byte array.

Carriers used at [Inject](#inject) are expected to be mutable.

### Operations

`Propagator`s MUST define `Inject` and `Extract` operations, in order to write
values to and read values from carriers respectively. Each `Propagator` type MUST define the specific carrier type
and MAY define additional parameters.

#### Inject

Injects the value into a carrier. For example, into the headers of an HTTP request.

Required arguments:

- A `Context`. The Propagator MUST retrieve the appropriate value from the `Context` first, such as
`SpanContext`, `Baggage` or another cross-cutting concern context.
- The carrier that holds the propagation fields. For example, an outgoing message or HTTP request.

#### Extract

Extracts the value from an incoming request. For example, from the headers of an HTTP request.

If a value can not be parsed from the carrier, for a cross-cutting concern,
the implementation MUST NOT throw an exception and MUST NOT store a new value in the `Context`,
in order to preserve any previously existing valid value.

Required arguments:

- A `Context`.
- The carrier that holds the propagation fields. For example, an incoming message or HTTP request.

Returns a new `Context` derived from the `Context` passed as argument,
containing the extracted value, which can be a `SpanContext`,
`Baggage` or another cross-cutting concern context.

## TextMap Propagator

`TextMapPropagator` performs the injection and extraction of a cross-cutting concern
value as string key/values pairs into carriers that travel in-band across process boundaries.

The carrier of propagated data on both the client (injector) and server (extractor) side is
usually an HTTP request.

In order to increase compatibility, the key/value pairs MUST only consist of US-ASCII characters
that make up valid HTTP header fields as per [RFC 9110](https://tools.ietf.org/html/rfc9110/#name-fields).

`Getter` and `Setter` are optional helper components used for extraction and injection respectively,
and are defined as separate objects from the carrier to avoid runtime allocations,
by removing the need for additional interface-implementing-objects wrapping the carrier in order
to access its contents.

`Getter` and `Setter` MUST be stateless and allowed to be saved as constants, in order to effectively
avoid runtime allocations.

### Fields

The predefined propagation fields. If your carrier is reused, you should delete the fields here
before calling [Inject](#inject).

Fields are defined as string keys identifying format-specific components in a carrier.

For example, if the carrier is a single-use or immutable request object, you don't need to
clear fields as they couldn't have been set before. If it is a mutable, retryable object,
successive calls should clear these fields first.

The use cases of this are:

- allow pre-allocation of fields, especially in systems like gRPC Metadata
- allow a single-pass over an iterator

Returns list of fields that will be used by the `TextMapPropagator`.

Observe that some `Propagator`s may define, besides the returned values, additional fields with
variable names. To get a full list of fields for a specific carrier object, use the
[Keys](#keys) operation.

### TextMap Inject

Injects the value into a carrier. The required arguments are the same as defined by
the base [Inject](#inject) operation.

Optional arguments:

- A `Setter` to set a propagation key/value pair. Propagators MAY invoke it multiple times in order to set multiple pairs.
  This is an additional argument that languages are free to define to help inject data into the carrier.

#### Setter argument

Setter is an argument in `Inject` that sets values into given fields.

`Setter` allows a `TextMapPropagator` to set propagated fields into a carrier.

One of the ways to implement it is `Setter` class with `Set` method as described below.

##### Set

Replaces a propagated field with the given value.

Required arguments:

- the carrier holding the propagation fields. For example, an outgoing message or an HTTP request.
- the key of the field.
- the value of the field.

The implementation SHOULD preserve casing (e.g. it should not transform `Content-Type` to `content-type`) if the used protocol is case insensitive, otherwise it MUST preserve casing.

### TextMap Extract

Extracts the value from an incoming request. The required arguments are the same as defined by
the base [Extract](#extract) operation.

Optional arguments:

- A `Getter` invoked for each propagation key to get. This is an additional
  argument that languages are free to define to help extract data from the carrier.

Returns a new `Context` derived from the `Context` passed as argument.

#### Getter argument

Getter is an argument in `Extract` that get value from given field

`Getter` allows a `TextMapPropagator` to read propagated fields from a carrier.

One of the ways to implement it is `Getter` class with `Get` and `Keys` methods
as described below. Languages may decide on alternative implementations and
expose corresponding methods as delegates or other ways.

##### Keys

The `Keys` function MUST return the list of all the keys in the carrier.

Required arguments:

- The carrier of the propagation fields, such as an HTTP request.

The `Keys` function can be called by `Propagator`s which are using variable key names in order to
iterate over all the keys in the specified carrier.

For example, it can be used to detect all keys following the `uberctx-{user-defined-key}` pattern, as defined by the
[Jaeger Propagation Format](https://www.jaegertracing.io/docs/1.18/client-libraries/#baggage).

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
as `TextMapPropagator`, as different `Propagator` types will likely operate on different
data types.

There MUST be functions to accomplish the following operations.

- Create a composite propagator
- Extract from a composite propagator
- Inject into a composite propagator

### Create a Composite Propagator

Required arguments:

- A list of `Propagator`s or a list of `Injector`s and `Extractor`s.

Returns a new composite `Propagator` with the specified `Propagator`s.

### Composite Extract

Required arguments:

- A `Context`.
- The carrier that holds propagation fields.

If the `TextMapPropagator`'s `Extract` implementation accepts the optional `Getter` argument, the following arguments are REQUIRED, otherwise they are OPTIONAL:

- The instance of `Getter` invoked for each propagation key to get.

### Composite Inject

Required arguments:

- A `Context`.
- The carrier that holds propagation fields.

If the `TextMapPropagator`'s `Inject` implementation accepts the optional `Setter` argument, the following arguments are REQUIRED, otherwise they are OPTIONAL:

- The `Setter` to set a propagation key/value pair. Propagators MAY invoke it multiple times in order to set multiple pairs.

## Global Propagators

The OpenTelemetry API MUST provide a way to obtain a propagator for each
supported `Propagator` type. Instrumentation libraries SHOULD call propagators
to extract and inject the context on all remote calls. Propagators, depending on
the language, MAY be set up using various dependency injection techniques or
available as global accessors.

**Note:** It is a discouraged practice, but certain instrumentation libraries
might use proprietary context propagation protocols or be hardcoded to use a
specific one. In such cases, instrumentation libraries MAY choose not to use the
API-provided propagators and instead hardcode the context extraction and injection
logic.

The OpenTelemetry API MUST use no-op propagators unless explicitly configured
otherwise. Context propagation may be used for various telemetry signals -
traces, metrics, logging and more. Therefore, context propagation MAY be enabled
for any of them independently. For instance, a span exporter may be left
unconfigured, although the trace context propagation was configured to enrich logs or metrics.

Platforms such as ASP.NET may pre-configure out-of-the-box
propagators. If pre-configured, `Propagator`s SHOULD default to a composite
`Propagator` containing the W3C Trace Context Propagator and the Baggage
`Propagator` specified in the [Baggage API](../baggage/api.md#propagation).
These platforms MUST also allow pre-configured propagators to be disabled or overridden.

### Get Global Propagator

This method MUST exist for each supported `Propagator` type.

Returns a global `Propagator`. This usually will be composite instance.

### Set Global Propagator

This method MUST exist for each supported `Propagator` type.

Sets the global `Propagator` instance.

Required parameters:

- A `Propagator`. This usually will be a composite instance.

## Propagators Distribution

The official list of propagators that MUST be maintained by the OpenTelemetry
organization and MUST be distributed as OpenTelemetry extension packages:

* [W3C TraceContext](https://www.w3.org/TR/trace-context). MAY alternatively
  be distributed as part of the OpenTelemetry API.
* [W3C Baggage](https://www.w3.org/TR/baggage). MAY alternatively
  be distributed as part of the OpenTelemetry API.
* [B3](https://github.com/openzipkin/b3-propagation).
* [Jaeger](https://www.jaegertracing.io/docs/latest/client-libraries/#propagation-format).

This is a list of additional propagators that MAY be maintained and distributed
as OpenTelemetry extension packages:

* [OT Trace](https://github.com/opentracing?q=basic&type=&language=). Propagation format
  used by the OpenTracing Basic Tracers. It MUST NOT use `OpenTracing` in the resulting
  propagator name as it is not widely adopted format in the OpenTracing ecosystem.
* [OpenCensus BinaryFormat](https://github.com/census-instrumentation/opencensus-specs/blob/master/encodings/BinaryEncoding.md#trace-context).
  Propagation format used by OpenCensus, which describes how to format the span context
  into the binary format, and does not prescribe a key. It is commonly used with
  OpenCensus gRPC using the `grpc-trace-bin` propagation key.

Additional `Propagator`s implementing vendor-specific protocols such as AWS
X-Ray trace header protocol MUST NOT be maintained or distributed as part of
the Core OpenTelemetry repositories.

### B3 Requirements

B3 has both single and multi-header encodings. It also has semantics that do not
map directly to OpenTelemetry such as a debug trace flag, and allowing spans
from both sides of request to share the same id. To maximize compatibility
between OpenTelemetry and Zipkin implementations, the following guidelines have
been established for B3 context propagation.

#### B3 Extract

When extracting B3, propagators:

* MUST attempt to extract B3 encoded using single and multi-header
  formats. The single-header variant takes precedence over
  the multi-header version.
* MUST preserve a debug trace flag, if received, and propagate
  it with subsequent requests. Additionally, an OpenTelemetry implementation
  MUST set the sampled trace flag when the debug flag is set.
* MUST NOT reuse `X-B3-SpanId` as the id for the server-side span.

#### B3 Inject

When injecting B3, propagators:

* MUST default to injecting B3 using the single-header format
* MUST provide configuration to change the default injection format to B3
  multi-header
* MUST NOT propagate `X-B3-ParentSpanId` as OpenTelemetry does not support
  reusing the same id for both sides of a request.

#### Fields

Fields MUST return the header names that correspond to the configured format,
i.e., the headers used for the inject operation.

#### Configuration

| Option    | Extract Order | Inject Format | Specification     |
|-----------|---------------|---------------| ------------------|
| B3 Single | Single, Multi | Single        | [Link][b3-single] |
| B3 Multi  | Single, Multi | Multi         | [Link][b3-multi]  |

[b3-single]: https://github.com/openzipkin/b3-propagation#single-header
[b3-multi]: https://github.com/openzipkin/b3-propagation#multiple-headers
