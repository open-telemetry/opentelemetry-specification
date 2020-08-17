# OpenTracing Compatibility

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [OpenTracing Tracer](#opentracing-tracer)
  * [Create a Tracer shim](#create-a-tracer-shim)
  * [Inject](#inject)
  * [Extract](#extract)
* [ScopeManager](#scopemanager)
  * [Activate a Span](#activate-a-span)
  * [Get the active Span](#get-the-active-span)
* [Span](#span)
  * [Get Context](#get-context)
  * [Get Baggage Item](#get-baggage-item)
  * [Set Baggage Item](#set-baggage-item)
  * [Set Tag](#set-tag)
  * [Log](#log)
  * [Finish](#finish)
  * [SpanContext](#spancontext)
    * [Get Baggage Items](#get-baggage-items)

</details>

## Abstract

The OpenTelemetry project aims to provide backwards compatibility with the
[OpenTracing](https://opentracing.io) project in order to ease migration of
instrumented codebases.

This functionality will be provided as a bridge layer implementing the
[OpenTracing API](https://github.com/opentracing/specification) using the
OpenTelemetry API. This layer MUST NOT rely on implementation specific details
of any SDK.

## OpenTracing Tracer

The OpenTracing Tracer operations MUST be implemented using the OpenTelemetry
API:

- An OpenTelemetry `Tracer` MUST be used to create `Span`s.
- A `CorrelationContextManager` MUST be used to create the `CorrelationContext`
  objects used to implement the OpenTracing `Span` baggage.
- A set of `Propagator` MUST be leveraged in order to perform inject and extract operations.

### Create a Tracer Shim

The operation MUST accept the following parameters:

- An OpenTelemetry `Tracer`.
- A `CorrelationContextManager`.
- A set of `Propagator`s of the supported types, usually `Composite Propagator`s.

The API MUST return an OpenTracing `Tracer`.

### Inject

Inject the underlying `SpanContext` using the registered `Propagator`s:

- `TEXT_MAP` and `HTTP_HEADERS` formats MUST use the registered `HTTPTextPropagator`, if any.

Errors MUST NOT be raised if the specified OpenTracing `Format` is `BINARY`.

### Extract

Extract an OpenTelemetry `SpanContext` from a carrier using the registered `Propagator`s:

- `TEXT_MAP` and `HTTP_HEADERS` formats MUST use the registered `HTTPTextPropagator`, if any.

Returns an OpenTracing `SpanContext` with the underlying extracted `SpanContext`, or null if
either the OpenTracing `Format` is `BINARY` or no value could be extracted.

## ScopeManager.

For OpenTracing languages implementing the `ScopeManager` interface,  its operations
MUST be implemented using the OpenTelemetry context propagation API.

### Activate a Span.

Sets the specified `Span` as active for the current `Context`.

### Get the active Span.

Gets the active `Span` for the current `Context`. The API MUST return
null if none exist.

## Span

The `Span` operations MUST be implemented using an underlying OpenTelemetry `Span`
in conjunction with an associated `CorrelationContext` object used to implement its
baggage part.

OpenTracing `SpanContext` shim objects MUST act as objects associating an
underlying `SpanContext` with a `CorrelationContext`. Every invocation to the
`Set Baggage Item` operation will result in a newly associated `SpanContext` shim object
with a new `CorrelationContext` containing the specified name/value pair.

Each underlying `Span` can only be associated with one `SpanContext` shim at a time
for all the execution units.

The `Log` operations MUST be implemented using `Span`'s `Add Events`.

The `Set Tag` operations MUST be implemented using `Span`'s `Set Attributes`.

### Get Context

Gets the currently associated `SpanContext` shim.

### Get Baggage Item

Gets a value for the specified name in the `CorrelationContext` of the associated `SpanContext`
shim or null if none exists.

### Set Baggage Item

Creates a newly associated `SpanContext` shim object with a new `CorrelationContext`
containing the specified name/value pair.

### Set Tag

Calls `Set Attribute` on the underlying `Span` with the specified name/value pair.

If the type of the specified value is not supported, the value MUST be converted
to a string.

### Log

Calls `Add Event` on the underlying `Span`.

If an explicit timestamp is specified, a conversion MUST be done to match the OT and
OTel units.

### Finish

Calls `End` on the underlying `Span`.

If an explicit timestamp is specified, a conversion MUST be done to match the OT and
OTel units.

### SpanContext

The `SpanContext` interface MUST be implemented using a OpenTelemetry `SpanContext`
in conjunction with an associated `CorrelationContext`.

Observe that the assigned `SpanContext` and `CorrelationContext` MUST be read-only
and MUST NOT change after creation.

#### Get Baggage Items

Returns a shim exposing the associated `CorrelationContext` values.
