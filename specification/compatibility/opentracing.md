# OpenTracing Compatibility

**Status**: [Experimental](../document-status.md).

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [Create an OpenTracing Tracer Shim](#create-an-opentracing-tracer-shim)
* [Tracer Shim](#tracer-shim)
  * [Inject](#inject)
  * [Extract](#extract)
* [OpenTelemetry Span and SpanContext Shim relationship](#opentelemetry-span-and-spancontext-shim-relationship)
* [Span Shim](#span-shim)
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
createTracerShim(tracer);

// Create a Tracer Shim using:
// 1) TraceContext propagator for TextMap
// 2) Jaeger propagator for HttPHeaders.
createTracerShim(tracer, OTPropagatorsBuilder()
  .setTextMap(W3CTraceContextPropagator.getInstance())
  .setHttpHeaders(JaegerPropagator.getInstance())
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

Inject the underlying OpenTelemetry `Span` and `Bagagge` using either the explicitly
registered or the global OpenTelemetry `Propagator`s, as configured at construction time.

- `TextMap` and `HttpHeaders` formats MUST use their explicitly specified `TextMapPropagator`,
  if any, or else use the global `TextMapPropagator`.

Errors MAY be raised if the specified `Format` is not recognized, depending
on the specific OpenTracing Language API (e.g. Go and Python do, but Java may not).

### Extract

Parameters:

- A `Format` descriptor.
- A carrier.

Extract the underlying OpenTelemetry `Span` and `Bagagge` using either the explicitly
registered or the global OpenTelemetry `Propagator`s, as configured at construction time.

- `TextMap` and `HttpHeaders` formats MUST use their explicitly specified `TextMapPropagator`,
  if any, or else use the global `TextMapPropagator`.

Returns a `SpanContext` Shim with the underlying extracted OpenTelemetry
`Span` and `Baggage`. Errors MAY be raised if either the `Format` is not recognized
or no value could be extracted, depending on the specific OpenTracing Language API
(e.g. Go and Python do, but Java may not).

## OpenTelemetry Span and SpanContext Shim relationship

OpenTracing `SpanContext`, just as OpenTelemetry `SpanContext`, MUST be
immutable, but it MUST also store `Baggage`. Hence, it MUST be replaced
every time baggage is updated through the OpenTracing
[Span Set Baggage Item](#set-baggage-item) operation. Special handling
MUST be done by the Shim layer in order to retain these invariants.

Because of the previous requirement, a given OpenTelemetry `Span`
MUST be associated with ONE AND ONLY ONE `SpanContext` Shim object at all times
for ALL execution units, in order to keep any linked `Baggage` consistent
at all times. It MUST BE safe to get and set the associated `SpanContext` Shim
object for a specified OpenTelemetry `Span` from different execution units.

An example showing the need for these requirements is having an OpenTracing `Span`
have its [Set Baggage Item](#set-baggage-item) operation called from two different
execution units (e.g. threads, coroutines), and afterwards have its
[Context](#get-context) fetched in order to
[iterate over its baggage values](#get-baggage-items).

```java
// Thread A: New SpanContextShim and Baggage values are created.
openTracingSpan.setBaggageItem("1", "a")

// Thread B: New SpanContextShim and Baggage values are created again.
openTracingSpan.setBaggageItem("2", "b")

// Thread C: Up-to-date SpanContextShim and Bagggage values are retrieved.
for (Map.Entry<String, String> entry : openTracingSpan.context().baggageItems()) {
  ...
}
```

This is a simple graphical representation of the mentioned objects:

```
  Span Shim
  +- OpenTelemetry Span
  +- SpanContext Shim
        +- OpenTelemetry SpanContext
        +- OpenTelemetry Baggage
```

The OpenTelemetry `Span` in the `Span` Shim object is used to get and set
its currently associated `SpanContext` Shim.

Managing this one-to-one relationship between an OpenTelemetry `Span` and
a `SpanContext` Shim object is an implementation detail. It can be implemented,
for example, with the help of a global synchronized dictionary, or with an
additional attribute in each OpenTelemetry `Span` object for dynamic languages.

## Span Shim

The OpenTracing `Span` operations MUST be implemented using underlying OpenTelemetry `Span`
and `Baggage` values with the help of a `SpanContext` Shim object.

The `Log` operations MUST be implemented using the OpenTelemetry
`Span`'s `Add Events` operations.

The `Set Tag` operations MUST be implemented using the OpenTelemetry
`Span`'s `Set Attributes` operations.

### Get Context

Returns the [associated](#opentelemetry-span-and-spancontext-shim-relationship)
`SpanContext` Shim.

### Get Baggage Item

Parameters:

- The baggage key, a string.

Returns a value for the specified key in the OpenTelemetry `Baggage` of the
associated `SpanContext` Shim or null if none exists.

This is accomplished by getting the
[associated](#opentelemetry-span-and-spancontext-shim-relationship)
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
[associated](#opentelemetry-span-and-spancontext-shim-relationship) to the underlying
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

If pair set contains a `event=error` entry, the values MUST be mapped from
[OpenTracing Log Fields](https://github.com/opentracing/specification/blob/master/semantic_conventionsmd#log-fields-table)
to an `Event` with the conventions outlined in the
[Exception semantic conventions](../trace/semantic_conventions/exceptions.md) document:

- If an entry with `error.object` key exists and the value is a language-specific
  error object, a call to `RecordException(e)` is performed along the rest of
  the specified key/value pair set as additional event attributes.
- Else, a call to `AddEvent` is performed with `name` being set to `exception`,
  along the specified key/value pair set as additional event attributes,
  including mapping of the following key/value pairs:
  - `error.kind` maps to `exception.type`.
  - `message` maps to `exception.message`.
  - `stack` maps to `exception.stacktrace`.

If an explicit timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

### Finish

Calls `End` on the underlying OpenTelemetry `Span`.

If an explicit timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

## SpanContext Shim

`SpanContext` Shim MUST be immutable and MUST contain the associated
`SpanContext` and `Baggage` values.

### Get Baggage Items

Returns a dictionary, collection, or iterator (depending on the requirements of
the OpenTracing API for a specific language) backed by the associated OpenTelemetry
`Baggage` values.

## ScopeManager Shim

For OpenTracing languages implementing the `ScopeManager` interface, its operations
MUST be implemented using the OpenTelemetry Context Propagation API in order
to get and set active `Context` instances.

### Activate a Span

Parameters:

- A `Span`.

Gets the [associated](#opentelemetry-span-and-spancontext-shim-relationship)
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
