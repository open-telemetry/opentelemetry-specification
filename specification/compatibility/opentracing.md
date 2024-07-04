---
# Hugo front matter used to generate the website version of this page:
linkTitle: OpenTracing
---

# OpenTracing Compatibility

**Status**: [Stable](../document-status.md).

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [Language version support](#language-version-support)
* [Create an OpenTracing Tracer Shim](#create-an-opentracing-tracer-shim)
* [Tracer Shim](#tracer-shim)
  * [Start a new Span](#start-a-new-span)
  * [Inject](#inject)
  * [Extract](#extract)
  * [Close](#close)
* [Span Shim and SpanContext Shim relationship](#span-shim-and-spancontext-shim-relationship)
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
* [Span References](#span-references)
* [In-process propagation exceptions](#in-process-propagation-exceptions)
  * [Implicit and Explicit support mismatch](#implicit-and-explicit-support-mismatch)

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

Semantic convention mapping SHOULD NOT be performed, with the
exception of error mapping, as described in the [Set Tag](#set-tag) and
[Log](#log) sections.

Consuming both the OpenTracing Shim and the OpenTelemetry API in the same codebase
is not recommended for the following scenarios:

* If the OpenTracing-instrumented code consumes baggage, as the
 `Baggage` itself may not be properly propagated.
  See [Span Shim and SpanContext Shim relationship](#span-shim-and-spancontext-shim-relationship).
* For languages with **implicit** in-process propagation support in OpenTelemetry
  and none in OpenTracing (e.g. Javascript), as it breaks the expected propagation
  semantics and may lead to incorrect `Context` usage and incorrect traces.
  See [Implicit and Explicit support mismatch](#implicit-and-explicit-support-mismatch).

## Language version support

Users are encouraged to check and update their language and runtime
components before using the Shim layer, as the OpenTelemetry APIs and SDKs
may have higher version requirements than their OpenTracing counterparts.

For details, see the [Language version support][] section of [Migrating from
OpenTracing][].

[Language version support]: https://opentelemetry.io/docs/migration/opentracing/#language-version-support
[Migrating from OpenTracing]: https://opentelemetry.io/docs/migration/opentracing/

## Create an OpenTracing Tracer Shim

This operation is used to create a new OpenTracing `Tracer`:

This operation MUST accept the following parameters:

- An OpenTelemetry `TracerProvider`. This operation MUST use this `TracerProvider`
  to obtain a `Tracer` with the name `opentracing-shim` along with the current
  shim library version.
- OpenTelemetry `Propagator`s to be used to perform injection and extraction
  for the the OpenTracing `TextMap` and `HTTPHeaders` formats.
  If not specified, no `Propagator` values will be stored in the Shim, and
  the global OpenTelemetry `TextMap` propagator will be used for both OpenTracing
  `TextMap` and `HTTPHeaders` formats.

The API MUST return an OpenTracing `Tracer`.

```java
// Create a Tracer Shim relying on the global propagators.
createTracerShim(tracerProvider);

// Create a Tracer Shim using:
// 1) TraceContext propagator for TextMap
// 2) Jaeger propagator for HttPHeaders.
createTracerShim(tracerProvider, OTPropagatorsBuilder()
  .setTextMap(W3CTraceContextPropagator.getInstance())
  .setHttpHeaders(JaegerPropagator.getInstance())
  .build());
```

See OpenTracing Propagation
[Formats](https://github.com/opentracing/specification/blob/master/specification.md#extract-a-spancontext-from-a-carrier).

## Tracer Shim

### Start a new Span

Parameters:

- The operation name, a string.
- An optional list of [Span references](#span-references).
- An optional list of [tags](#set-tag).
- An optional explicit start timestamp, a numeric value.

For OpenTracing languages implementing the [ScopeManager](#scopemanager-shim)
interface, the following parameters are defined as well:

- An optional boolean specifying whether the current `Span`
  should be ignored as automatic parent.

If a list of `Span` references is specified, the first `SpanContext`
with **Child Of** type in the entire list is used as parent, else the
the first `SpanContext` is used as parent. All values in the list
MUST be added as [Link](../trace/api.md)s with the reference type value
as a `Link` attribute, i.e.
[opentracing.ref_type](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/trace-compatibility.md#opentracing)
set to `follows_from` or `child_of`.

If a list of `Span` references is specified, the union of their
`Baggage` values MUST be used as the initial `Baggage` of the newly created
`Span`. It is unspecified which `Baggage` value is used in the case of
repeated keys. If no such lisf of references is specified, the current
`Baggage` MUST be used as the initial value of the newly created `Span`.

If an initial set of tags is specified, the values MUST be set at
the creation time of the OpenTelemetry `Span`, as opposed to setting them
after the `Span` is already created. This is done in order to make
those values available to any pre-`Span`-creation hook, e.g. the reference
SDK performs a [sampling](../trace/sdk.md#sampling) step that consults
`Span` information, including the initial tags/attributes, to decide whether
to sample or not.

If an initial set of tags is specified and the OpenTracing `error` tag is
included, after the OpenTelemetry `Span` was created the Shim layer MUST
perform the same error handling as described in the [Set Tag](#set-tag) operation.

If an explicit start timestamp is specified, a conversion MUST be done to match the
OpenTracing and OpenTelemetry units.

The API MUST return an OpenTracing `Span`.

### Inject

Parameters:

- A `SpanContext`.
- A `Format` descriptor.
- A carrier.

Inject the underlying OpenTelemetry `Span` and `Baggage` using either the explicitly
registered or the global OpenTelemetry `Propagator`s, as configured at construction time.

- `TextMap` and `HttpHeaders` formats MUST use their explicitly specified `TextMapPropagator`,
  if any, or else use the global `TextMapPropagator`.

It MUST inject any non-empty `Baggage` even amidst no valid `SpanContext`.

Errors MAY be raised if the specified `Format` is not recognized, depending
on the specific OpenTracing Language API (e.g. Go and Python do, but Java may not).

### Extract

Parameters:

- A `Format` descriptor.
- A carrier.

Extract the underlying OpenTelemetry `Span` and `Baggage` using either the explicitly
registered or the global OpenTelemetry `Propagator`s, as configured at construction time.

- `TextMap` and `HttpHeaders` formats MUST use their explicitly specified `TextMapPropagator`,
  if any, or else use the global `TextMapPropagator`.

The operation MUST return a `SpanContext` Shim instance with the extracted values if any of these conditions are met:

* `SpanContext` is valid.
* `SpanContext` is sampled.
* `SpanContext` contains non-empty extracted `Baggage`.

Otherwise, the operation MUST return null or empty value.

```java
if (!extractedSpanContext.isValid()
    && !extractedSpanContext.isSampled()
    && extractedBaggage.isEmpty()) {
  return null;
}

return SpanContextShim(extractedSpanContext, extractedBaggage);
```

Errors MAY be raised if either the `Format` is not recognized
or no value could be extracted, depending on the specific OpenTracing Language API
(e.g. Go and Python do, but Java may not).

Note: Invalid but sampled `SpanContext` instances are returned as a way to support
`jaeger-debug-id` [headers](https://github.com/jaegertracing/jaeger-client-java#via-http-headers),
which are used to force propagation of debug information.

## Close

OPTIONAL operation. If this operation is implemented for a specific OpenTracing language,
it MUST close the underlying `TracerProvider` if it implements a "closeable" interface or method;
otherwise it MUST be defined as a no-op operation.

The Shim layer MUST protect against errors or exceptions raised while closing the
underlying `TracerProvider`.

Note: Users are advised against calling this operation more than once per `TracerProvider`
as it may have unexpected side effects, limitations or race conditions, e.g.
a single Shim `Tracer` being closed multiple times or multiple Shim `Tracer`
having their close operation being called.

## Span Shim and SpanContext Shim relationship

As per the OpenTracing Specification, the OpenTracing `SpanContext` Shim
MUST contain `Baggage` data and it MUST be immutable.

In turn, the OpenTracing `Span` Shim MUST contain a `SpanContext` Shim.
When updating its associated baggage, the OpenTracing `Span` MUST set its
OpenTracing `SpanContext` Shim to a new instance containing the updated
`Baggage`.

This is a simple graphical representation of the mentioned objects:

```
  Span Shim
  +- OpenTelemetry Span (read-only)
  +- SpanContext Shim
        +- OpenTelemetry SpanContext (read-only)
        +- OpenTelemetry Baggage (read-only)
```

The OpenTracing Shim properly performs in-process and inter-process
propagation of the OpenTelemetry `Span` along its associated `Baggage`
leveraging the hierarchy of objects shown above.

As OpenTelemetry is not aware of this association, the related `Baggage`
may not be properly propagated if the OpenTelemetry API is consumed
along the OpenTracing Shim in the same codebase, as shown in the example
below:

```java
// methodOne consumes the OpenTelemetry API.
void methodOne(Span span) {
  try (Scope scope = span.makeCurrent()) {
    methodTwo();
  }
}

// methodTwo consumes the OpenTracing Shim.
void methodTwo() {
  io.opentracing.Span span = io.opentracing.util.GlobalTracer.get()
    .activeSpan();

  // Correctly set in the underlying io.opentelemetry.api.trace.Span
  span.setTag("tag", "value");

  // Value is set in the Shim layer -- it may not be later propagated
  // as OpenTelemetry is not aware of the Baggage associated
  // to this Span.
  span.setBaggageItem("baggage", "item");
}
```

Operations accessing the associated `Baggage` MUST be safe to be called concurrently.

## Span Shim

The OpenTracing `Span` operations MUST be implemented using the underlying OpenTelemetry `Span`
and `Baggage` values with the help of a `SpanContext` Shim object.

The `Log` operations MUST be implemented using the OpenTelemetry
`Span`'s `Add Events` operations.

The `Set Tag` operations MUST be implemented using the OpenTelemetry
`Span`'s `Set Attributes` operations.

### Get Context

Returns the current `SpanContext` Shim.

This operation MUST be safe to be called concurrently.

### Get Baggage Item

Parameters:

- The baggage key, a string.

Returns the value for the specified key in the OpenTelemetry `Baggage` of the
current `SpanContext` Shim, or null if none exists.

This operation MUST be safe to be called concurrently.

```java
String getBaggageItem(String key) {
  synchronized(this) {
    // Get the current SpanContext's Baggage.
    io.opentelemetry.baggage.Baggage baggage = this.spanContextShim.getBaggage();

    // Return the value for key.
    return baggage.getEntryValue(key);
  }
}
```

### Set Baggage Item

Parameters:

- The baggage key, a string.
- The baggage value, a string.

Creates a new `SpanContext` Shim with a new OpenTelemetry `Baggage` containing
the specified `Baggage` key/value pair, and sets it as the current instance for
this `Span` Shim.

This operation MUST be safe to be called concurrently.

```java
void setBaggageItem(String key, String value) {
  synchronized(this) {
    // Add value/key to the existing Baggage.
    Baggage newBaggage = this.spanContextShim.getBaggage().toBuilder()
      .put(key, value)
      .build();

    // Create a new SpanContext with the updated Baggage.
    SpanContextShim newSpanContextShim = this.spanContextShim
      .newWithBaggage(newBaggage);

    // Update our SpanContext instance.
    this.spanContextShim = newSpanContextShim;
  }
}
```

### Set Tag

Parameters:

- The tag key, a string.
- The tag value, which must be either a string, a boolean value, or a numeric type.

Calls `Set Attribute` on the underlying OpenTelemetry `Span` with the specified
key/value pair.

The `error` tag MUST be
[mapped](https://github.com/opentracing/specification/blob/master/semantic_conventions.md#standard-span-tags-and-log-fields)
to [StatusCode](../trace/api.md#set-status):

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

If pair set contains an `event=error` entry, the values MUST be
[mapped](https://github.com/opentracing/specification/blob/master/semantic_conventions.md#log-fields-table)
to an `Event` with the conventions outlined in the
[Exception semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-spans.md) document:

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

Stores the `Span` Shim and its underlying `Span` and `Baggage`
in a new `Context`, which is then set as the currently active instance.

If the specified `Span` is null, it MUST be set to a
[NonRecordableSpan](../trace/api.md#wrapping-a-spancontext-in-a-span)
wrapping an invalid `SpanContext`, to signal there is no active
`Span` nor `Baggage`.

```java
Scope activate(Span span) {
  if (span == null) {
    span = new SpanShim(io.opentelemetry.api.trace.Span.getInvalid());
  }

  SpanShim spanShim = (SpanShim)span;

  // Put the associated Span and Baggage in a new Context.
  Context context = Context.current()
    .withValue(spanShim)
    .withValue(spanShim.getSpan())
    .withValue(spanShim.getBaggage());

  // Set context as the current instance.
  return context.makeCurrent();
}
```

Unsampled OpenTelemetry `Span`s can be perfectly activated,
as they have valid `SpanContext`s (albeit with the
`sampled` flag set to `false`):

```java
// The underlying OpenTelemetry TracerProvider's Sampler
// decided to NOT sample this Span, hence
// io.opentelemetry.api.trace.Span.getSpanContext().isSampled() == false.
Span span = tracer.buildSpan("operationName").start();

try (Scope scope = tracer.scopeManager().activate(span)) {
  // tracer.scopeManager().activeSpan() == span
}
```

### Get the active Span

Returns a `Span` Shim wrapping the currently active OpenTelemetry `Span`.

This operation MUST immediately return null if the current OpenTelemetry
`Span`'s `SpanContext` is invalid and the current `Baggage` is empty,
to signal there is no active `Span` nor `Baggage`.

If the current OpenTelemetry `Span`'s `SpanContext` is invalid but
the current `Baggage` is not empty, this operation MUST return a new
`Span` Shim containing a no-op OpenTelemetry `Span` and the non-empty `Baggage`.

If there are **matching** OpenTelemetry `Span` and `Span` Shim objects in the
current `Context`, the `Span` Shim MUST be returned. Else, a new `Span` Shim
containing the current OpenTelemetry `Span` and `Baggage` MUST be returned.

```java
Span active() {
  io.opentelemetry.api.trace.Span span = Span.fromContext(Context.current());
  io.opentelemetry.api.baggage.Baggage baggage = Baggage.fromContext(Context.current());
  SpanShim spanShim = SpanShim.fromContext(Context.current());

  // There is no actual currently active Span.
  if (!span.getSpanContext().isValid()) {
    // Immediately return null if there is no Baggage.
    if (baggage.isEmpty()) {
      return null;
    }

    // Else return a no-op Span with the Baggage.
    return SpanShim(baggage);
  }

  // Span was activated through the Shim layer, re-use it.
  if (spanShim != null && spanShim.getSpan() == span) {
    return spanShim;
  }

  // Span was NOT activated through the Shim layer,
  // do a best effort with the current values.
  new SpanShim(span, baggage);
}
```

## Span References

As defined in the
[OpenTracing Specification](https://github.com/opentracing/specification/blob/master/specification.md#references-between-spans),
a `Span` may reference zero or more other `SpanContext`s that are
causally related. The reference information itself consists of a
`SpanContext` and the reference type.

OpenTracing defines two types of references:

* **Child Of**: The parent `Span` depends on the child `Span`
  in some capacity.
* **Follows From**: The parent `Span` does not depend in any
  way on the result of their child `Span`s.

OpenTelemetry does not define strict equivalent semantics for these
references. These reference types must not be confused with the
[Link](../trace/api.md#link) functionality. This information
is however preserved as the `opentracing.ref_type` attribute.

## In process Propagation exceptions

### Implicit and Explicit support mismatch

For languages with **implicit** in-process propagation support in
OpenTelemetry and none in OpenTracing (i.e. no [ScopeManager](#scopemanager-shim) support),
the Shim MUST only use **explicit** context propagation in its operations
(e.g. when starting a new `Span`). This is done to easily comply with the
explicit-only propagation semantics of the OpenTracing API:

```ts
// Tracer Shim
startSpan(name: string, options: SpanOptions = {}): Span {
  const otelSpanOptions = ...;

  if (!options.childOf && !options.references) {
    // Do NOT get nor set the current Context/Span,
    // as it is part of the implicit propagation support.
    otelSpanOptions.root = true;
  }
  ...
}
```

Using both the OpenTracing Shim and the OpenTelemetry API in the same codebase
may result in traces using the incorrect parent `Span`, given the different
implicit/explicit propagation expectations. For this case, the Shim MAY offer
**in-Development** integration with the OpenTelemetry implicit in-process
propagation via an **explicit** setting, warning the user incorrect parent
values may be consumed:

```ts
// Tracer Shim
startSpan(name: string, options: SpanOptions = {}): Span {
  const otelSpanOptions = ...;

  if (!options.childOf && !options.references) {
    if (otShimOptions.supportImplicitPropagation) {
      // Allow OpenTelemetry to consume the current Context
      // to fetch the parent Span.
      otelSpanOptions.root = false;
    }
    ...
  }
  ...
}
```
