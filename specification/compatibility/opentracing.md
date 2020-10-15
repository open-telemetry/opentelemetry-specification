# OpenTracing Compatibility

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [Create an OpenTracing Tracer Shim](#create-an-opentracing-tracer-shim)
* [OpenTracing Tracer Shim](#opentracing-tracer-shim)
  * [Inject](#inject)
  * [Extract](#extract)
* [ScopeManager Shim](#scopemanager-shim)
  * [Activate a Span](#activate-a-span)
  * [Get the active Span](#get-the-active-span)
* [Span Shim](#span-shim)
  * [Get Context](#get-context)
  * [Get Baggage Item](#get-baggage-item)
  * [Set Baggage Item](#set-baggage-item)
  * [Set Tag](#set-tag)
  * [Log](#log)
  * [Finish](#finish)
  * [SpanContext Shim](#spancontext-shim)
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

This functionality MUST defined in its own OpenTracing Shim Layer, not in the
OpenTracing nor the OpenTelemetry API or SDK.

## Create an OpenTracing Tracer Shim

This operation is used to create a new OpenTracing `Tracer` Shim using the
OpenTelemetry API.

This operation MUST accept the following parameters:

- An OpenTelemetry `Tracer`, used to create `Span`s.
- An OpenTelemetry `BaggageManager`, used to create OpenTelemetry `Baggage` objects,
  required to implement the OpenTracing `Span` baggage notion.
- A set of OpenTelemetry `Propagator`s of the supported types, used to perform
  context injection and extraction. Usually these are the global
  `Composite Propagator`s.

The API MUST return an OpenTracing `Tracer`.

## OpenTracing Tracer Shim

### Inject

Parameters:

- A `SpanContext` instance.
- A `Format` descriptor.
- A carrier.

Inject the underlying OpenTelemetry `SpanReference` and `Bagagge` using the
registered OpenTelemetry `Propagator`s:

- `TEXT_MAP` and `HTTP_HEADERS` formats MUST use the registered OpenTelemetry
  `HTTPTextPropagator`, if any.

Errors MUST NOT be raised if the specified `Format` is `BINARY`.

### Extract

Parameters:

- A `Format` descriptor.
- A carrier.

Extract OpenTelemetry `SpanReference` and `Baggage` from a carrier using the
registered OpenTelemetry `Propagator`s:

- `TEXT_MAP` and `HTTP_HEADERS` formats MUST use the registered OpenTelemetry
  `HTTPTextPropagator`, if any.

Returns a `SpanContext` with the underlying extracted OpenTelemetry
`SpanReference` and `Baggage`, or null if either the `Format` is `BINARY` or
no value could be extracted.

## ScopeManager Shim

For OpenTracing languages implementing the `ScopeManager` interface,  its operations
MUST be implemented using the OpenTelemetry Context Propagation API.

### Activate a Span

Parameters:

- A `Span`.

Sets the specified `Span` as active for the current OpenTelemetry `Context`.

### Get the active Span

Gets the active `Span` for the current OpenTelemetry `Context`. The API MUST return
null if none exist.

## Span Shim

The `Span` operations MUST be implemented using an underlying OpenTelemetry `Span`
in conjunction with an associated `Baggage` object used to implement its
baggage part.

OpenTracing `SpanContext` Shim objects MUST act as objects associating the
underlying OpenTelemetry `SpanReference` with the OpenTelemetry `Baggage` instance.
Every invocation to the `Set Baggage Item` operation will result in a newly associated
`SpanContext` Shim object with a new OpenTelemetry `Baggage` containing the specified key/value pair.

Each underlying OpenTelemetry `Span` can only be associated with one `SpanContext` Shim at a time
for all the execution units.

The `Log` operations MUST be implemented using the OpenTelemetry
`Span`'s `Add Events` operations.

The `Set Tag` operations MUST be implemented using the OpenTelemetry
`Span`'s `Set Attributes` operations.

### Get Context

Gets the currently associated `SpanContext` Shim.

### Get Baggage Item

Parameters:

- The baggage key, a string.

Gets a value for the specified key in the OpenTelemetry `Baggage` of the
associated `SpanContext` Shim or null if none exists.

### Set Baggage Item

Parameters:

- The baggage key, a string.
- The baggage value, a string.

Creates a newly associated `SpanContext` Shim object with a new OpenTelemetry
`Baggage` containing the specified key/value pair.

### Set Tag

Parameters:

- The tag key, a string.
- The tag value, which must be either a string, a boolean value, or a numeric type.

Calls `Set Attribute` on the underlying OpenTelemetry `Span` with the specified
key/value pair.

The value MUST be mapped to the respective OpenTelemetry `Attribute`,
or converted to a string if the value type is not supported.

If the type of the specified value is not supported, the value MUST be converted
to a string.

### Log

Parameters:

- A set of key/value pairs, where keys must be strings, and the values may have
  any type.

Calls `Add Event` on the underlying OpenTelemetry `Span` with the specified
key/value pair set.

The `Add Event`'s `name` parameter MUST be the value with the `event` key in
the pair set, or else fallback to use the `log` literal string.

The set of values MUST be mapped to the respective OpenTelemetry `Attribute`,
or converted to a string if the value type is not supported.

If an explicit timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

### Finish

Calls `End` on the underlying OpenTelemetry `Span`.

If an explicit timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

### SpanContext Shim

The `SpanContext` interface MUST be implemented through a Shim object using an
OpenTelemetry `SpanReference` in conjunction with an associated OpenTelemetry
`Baggage`.

#### Get Baggage Items

Returns a Shim object exposing the associated OpenTelemetry `Baggage` values.
