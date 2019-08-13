# Remove SpanData

**Status:** `proposed`

Remove and replace SpanData by adding span start and end options.

## Motivation

SpanData represents an immutable span object, creating a fairly large API for all of the fields (12 to be exact). It exposes what feels like an SDK concern and implementation detail to the API surface. As a user, this is another API I need to learn how to use, and ID generation might also need to be exposed. As an implementer, it is a new data type that needs to be supported. The primary motivation for removing SpanData revolves around the desire to reduce the size of the tracing API.

## Explanation

SpanData has a couple of use cases.

The first use case revolves around creating a span synchronously but needing to change the start time to a more accurate timestamp. For example, in an HTTP server, you might record the time the first byte was received, parse the headers, determine the span name, and then create the span. The moment the span was created isn't representative of when the request actually began, so the time the first byte was received would become the span's start time. Since the current API doesn't allow start timestamps, you'd need to create a SpanData object. The big downside is that you don't end up with an active span object.

The second use case comes from the need to construct and report out of band spans, meaning that you're creating "custom" spans for an operation you don't own. One good example of this is a span sink that takes in structured logs that contain correlation IDs and a duration (e.g. from splunk) and [converts them](https://github.com/lightstep/splunktospan/blob/58ef9bca81933a47605a51047b12742e2d13aa8f/splunktospan/span.py#L43) to spans for your tracing system. [Another example](https://github.com/lightstep/haproxy_log2span/blob/761da5bf3e4b6cce56039d65439ae7db57f48603/lib/lib.go#L292) is running a sidecar on an HAProxy machine, tailing the request logs, and creating spans. SpanData allows you to report the out of band reporting case, whereas you can’t with the current Span API as you cannot set the start and end timestamp.

I'd like to propose getting rid of SpanData and `tracer.recordSpanData()` and replacing it by allowing `tracer.startSpan()` to accept a start timestamp option and `span.end()` to accept end timestamp option. This reduces the API surface, consolidating on a single span type. Options would meet the requirements for out of band reporting.

## Internal details

`startSpan()` would change so you can include an optional start timestamp, span ID, and resource. When you have a span sink, out of band spans may have different resources than the tracer they are being reported to, so you want to pass an explicit resource. For `span.end()` you would have an optional end timestamp. The exact implementation would be language specific, so some would use an options pattern with function overloading or variadic parameters, or add these options to the span builder.

## Trade-offs and mitigations

From https://github.com/open-telemetry/opentelemetry-specification/issues/71: If the underlying SDK automatically adds tags to spans such as thread-id, stacktrace, and cpu-usage when a span is started, they would be incorrect for out of band spans as the tracer would not know the difference between in and out of band spans. This can be mitigated by indicating that the span is out of band to prevent attaching incorrect information, possibly with an `isOutOfBand()` option on `startSpan()`.

## Prior art and alternatives

The OpenTracing specification for `tracer.startSpan()` includes an optional start timestamp and zero or more tags. It also calls out an optional end timestamp and bulk logging for `span.end()`.

## Open questions

There also seems to be some hidden dependency between SpanData and the sampler API. For example, given a complete SpanData object with a start and end timestamp, I imagine there's a use case where the sampler can look at the that and decide "this took a long time" and sample it. Is this a real use case? Is there a requirement to be able to provide complete span objects to the sampler?

## Future Work

We might want to include attributes as a start option to give the underlying sampler more information to sample with. We also might want to include optional events, which would be for bulk adding events with explicit timestamps.

We will also want to ensure, assuming the span or subtrace is being created in the same process, that the timestamps use the same precision and are monotonic. 

## Related Issues

Removing SpanData would resolve [open-telemetry/opentelemetry-specification#71](https://github.com/open-telemetry/opentelemetry-specification/issues/71).

Options would solve [open-telemetry/opentelemetry-specification#139](https://github.com/open-telemetry/opentelemetry-specification/issues/139).

By removing SpanData, [open-telemetry/opentelemetry-specification#92](https://github.com/open-telemetry/opentelemetry-specification/issues/92) can be resolved and closed.

[open-telemetry/opentelemetry-specification#68](https://github.com/open-telemetry/opentelemetry-specification/issues/68) can be closed. An optional resource can provide a different resource for out of band spans, otherwise the tracer can provide the default resource.

[open-telemetry/opentelemetry-specification#60](https://github.com/open-telemetry/opentelemetry-specification/issues/60) can be closed due to removal of SpanData.
