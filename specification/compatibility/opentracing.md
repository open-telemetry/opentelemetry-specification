# OpenTracing Compatibility

**Status**: [Experimental](../document-status.md).

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [Create an OpenTracing Tracer Shim](#create-an-opentracing-tracer-shim)
* [Tracer Shim](#tracer-shim)
  * [Inject](#inject)
  * [Extract](#extract)
* [Span Shim](#span-shim)
  * [OpenTelemetry Span and SpanContext relationship](#opentelemetry-span-and-spancontext-relationship)
  * [Get Context](#get-context)
  * [Get Baggage Item](#get-baggage-item)
  * [Set Baggage Item](#set-baggage-item)
  * [Set Tag](#set-tag)
  * [Log](#log)
  * [Finish](#finish)
* [SpanContext Shim](#spancontext-shim)
  * [Get Baggage Items](#get-baggage-items)
* [ScopeManager Shim](#scopemanager-shim)
  * [Activate a Span](#activate-a-span)
  * [Get the active Span](#get-the-active-span)

</details>

## Abstract

The OpenTelemetry project aims to provide backwards compatibility with the
[OpenTracing](https://opentracing.io) project in order to ease migration of
instrumented codebases.

This functionality will be provided as a bridge layer implementing the
[OpenTracing API](https://github.com/opentracing/specification) using the
OpenTelemetry API. This layer MUST NOT rely on implementation specific details
of any SDK.

More specifically, the intention is to allow OpenTracing instrumentation to be
recorded using OpenTelemetry. This Shim Layer MUST NOT publicly expose any
upstream OpenTelemetry API.

This functionality MUST be defined in its own OpenTracing Shim Layer, not in the
OpenTracing nor the OpenTelemetry API or SDK.

The OpenTracing Shim and the OpenTelemetry API/SDK are expected to be consumed
simultaneously in a running service, in order to ease migration from the former
to the latter.

## Create an OpenTracing Tracer Shim

This operation is used to create a new OpenTracing `Tracer`:

This operation MUST accept the following parameters:

- An OpenTelemetry `Tracer`, used to create `Span`s.
- OpenTelemetry `Propagator`s to be used to perform injection and extraction
  for the the OpenTracing `TextMap` and `HTTPHeaders` formats.
  If not specified, no `Propagator` values will be stored in the Shim, and
  the global OpenTelemetry `TextMap` propagator will be used for both OpenTracing
  `TextMap` and `HTTPHeaders` formats.

The API MUST return an OpenTracing `Tracer`.

```java
// Create a Tracer Shim relying on the global propagators.
createTracerShim(Tracer tracer);

// Create a Tracer Shim with the specified propagators.
createTracerShim(Tracer tracer, OTPropagatorsBuilder()
  .setTextMap(customTextMapPropagator)
  .setHttpHeaders(anotherCustomTextMapPropagator)
  .build());
```

See OpenTracing Propagation
[Formats](https://github.com/opentracing/specification/blob/master/specification.md#extract-a-spancontext-from-a-carrier).

## Tracer Shim

### Inject

Parameters:

- A `SpanContext`.
- A `Format` descriptor.
- A carrier.

Inject the underlying OpenTelemetry `Span` and `Bagagge` using the registered
OpenTelemetry `Propagator`s:

- `TEXT_MAP` and `HTTP_HEADERS` formats MUST use the registered OpenTelemetry
  `HTTPTextPropagator`, if any.

Errors MUST NOT be raised if the specified `Format` is `BINARY`.

### Extract

Parameters:

- A `Format` descriptor.
- A carrier.

Extract OpenTelemetry `Span` and `Baggage` from a carrier using the registered
OpenTelemetry `Propagator`s:

- `TEXT_MAP` and `HTTP_HEADERS` formats MUST use the registered OpenTelemetry
  `HTTPTextPropagator`, if any.

Returns a `SpanContext` Shim with the underlying extracted OpenTelemetry
`Span` and `Baggage`, or null if either the `Format` is `BINARY` or
no value could be extracted.

## Span Shim

The OpenTracing `Span` operations MUST be implemented using underlying OpenTelemetry `Span`
and `Baggage` values through a `SpanContext` Shim.

In order to satisfy the OpenTracing `Span` requirements:

- The associated `SpanContext` Shim object will contain an OpenTelemetry `SpanContext`
  and a `Baggage`. The `SpanContext` Shim MUST be immutable and MUST be
  replaced every time baggage is updated through [Set Baggage Item](#set-baggage-item).
- An underlying OpenTelemetry `Span` MUST be associated with only one
  `SpanContext` Shim at a time. This is done in order to keep its linked `Baggage`
  consistent across all execution units at all times.

This is a simple graphical representation of the mentioned objects:

```
  Span Shim
  +- OpenTelemetry Span
  +- SpanContext Shim
        +- OpenTelemetry SpanContext
        +- OpenTelemetry Baggage
```

The OpenTelemetry `Span` in `Span` Shim is also used to get and set
its currently associated `SpanContext` Shim. See
[OpenTelemetry Span and SpanContext relationship](#opentelemetry-span-and-spancontext-relationship).

The `Log` operations MUST be implemented using the OpenTelemetry
`Span`'s `Add Events` operations.

The `Set Tag` operations MUST be implemented using the OpenTelemetry
`Span`'s `Set Attributes` operations.

### OpenTelemetry Span and SpanContext relationship

A given OpenTelemetry `Span` MUST be associated with only one
`SpanContext` Shim at all times for all execution units, in order
to keep any linked `Baggage` consistent across all execution
units at all times.

An example of this scenario is having an OpenTracing `Span` have its
[Set Baggage Item](#set-baggage-item) operation called from two different
execution units (e.g. threads), and afterwards have its [Context](#get-context)
fetched in order to [iterate over its baggage values](#get-baggage-items).

Getting and setting the currently associated `SpanContext` for a specified
OpenTelemetry `Span` MUST be safe to call from different execution units.

Managing this relationship is an implementation detail. It can be implemented,
for example, with the help of a global synchronized dictionary, or with an
additional attribute in OpenTelemetry `Span` objects for dynamic languages.

### Get Context

Returns the [associated](#opentelemetry-span-and-spancontext-relationship)
`SpanContext` Shim.

### Get Baggage Item

Parameters:

- The baggage key, a string.

Returns a value for the specified key in the OpenTelemetry `Baggage` of the
associated `SpanContext` Shim or null if none exists.

This is accomplished by getting the
[associated](#opentelemetry-span-and-spancontext-relationship)
`SpanContext` Shim and do a lookup for the specified key in the OpenTelemetry
`Baggage` instance.

```java
String getBaggageItem(String key) {
  getSpanContextShim().getBaggage().getEntryValue(key);
}
```

### Set Baggage Item

Parameters:

- The baggage key, a string.
- The baggage value, a string.

Creates a new `SpanContext` Shim with a new OpenTelemetry `Baggage` containing
the specified `Baggage` key/value pair. The resulting `SpanContext` Shim is then
[associated](#opentelemetry-span-and-spancontext-relationship) to the underlying
OpenTelemetry `Span`.

```java
void setBaggageItem(String key, String value) {
  SpanContextShim spanContextShim = getSpanContextShim();

  // Add value/key to the existing Baggage.
  Baggage newBaggage = spanContextShim.getBaggage().toBuilder()
    .put(key, value)
    .build();

  // Set a new SpanContext Shim object with the updated Baggage.
  setSpanContextShim(spanContextShim.newWithBaggage(newBaggage));
}
```

### Set Tag

Parameters:

- The tag key, a string.
- The tag value, which must be either a string, a boolean value, or a numeric type.

Calls `Set Attribute` on the underlying OpenTelemetry `Span` with the specified
key/value pair.

Certain values MUST be mapped from
[OpenTracing Span Tags](https://github.com/opentracing/specification/blob/master/semantic_conventions.md#standard-span-tags-and-log-fields)
to the respective OpenTelemetry `Attribute`:

- `error` maps to [StatusCode](../trace/api.md##set-status):
  - `true` maps to `Error`.
  - `false` maps to `Ok`.
  - no value being set maps to `Unset`.

If the type of the specified value is not supported by the OTel API, the value
MUST be converted to a string.

### Log

Parameters:

- A set of key/value pairs, where keys must be strings, and the values may have
  any type.

Calls `Add Events` on the underlying OpenTelemetry `Span` with the specified
key/value pair set.

The `Add Event`'s `name` parameter MUST be the value with the `event` key in
the pair set, or else fallback to use the `log` literal string.

If an explicit timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

### Finish

Calls `End` on the underlying OpenTelemetry `Span`.

If an explicit timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

## SpanContext Shim

The `SpanContext` Shim MUST contain the associated `Span` and `Baggage` values.

This object MUST be immutable.

### Get Baggage Items

Returns a dictionary, collection, or iterator (depending on the requirements of the OpenTracing API for a specific language)
backed by the associated OpenTelemetry `Baggage` values.

## ScopeManager Shim

For OpenTracing languages implementing the `ScopeManager` interface, its operations
MUST be implemented using the OpenTelemetry Context Propagation API in order
to get and set active `Context` instances.

### Activate a Span

Parameters:

- A `Span`.

Gets the [associated](#opentelemetry-span-and-spancontext-relationship)
`SpanContext` Shim for the specified `Span` and puts its OpenTelemetry
`Span`, `Baggage` and `Span` Shim objects in a new `Context`,
which is then set as the currently active instance.

```java
Scope activate(Span span) {
  SpanContextShim spanContextShim = getSpanContextShim(span);

  // Put the associated Span and Baggage in the used Context.
  Context context = Context.current()
    .withValue(spanContextShim.getSpan())
    .withValue(spanContextShim.getBaggage())
    .withValue((SpanShim)spanShim);

  // Set context as the current instance.
  return context.makeCurrent();
}
```

### Get the active Span

Returns a `Span` Shim wrapping the currently active OpenTelemetry `Span`.

If there are related OpenTelemetry `Span` and `Span` Shim objects in the
current `Context`, the `Span` Shim MUST be returned. Else, a new `Span` Shim
referencing the OpenTelemetry `Span` MUST be created and returned.

The API MUST return null if no actual OpenTelemetry `Span` is set.

```java
Span active() {
  io.opentelemetry.api.trace.Span span = Span.fromContext(Context.current());
  SpanShim spanShim = SpanShim.fromContext(Context.current());

  // Span was activated through the Shim layer, re-use it.
  if (spanShim != null && spanShim.getSpan() == span) {
    return spanShim;
  }

  // Span was NOT activated through the Shim layer.
  new SpanShim(Span.current());
}
```
