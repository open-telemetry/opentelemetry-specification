# Exceptions

**Status**: [Deprecated](../document-status.md), follow the
[semantic conventions for recording exceptions](https://opentelemetry.io/docs/specs/semconv/general/recording-errors/#recording-exceptions)
instead.

This document defines how to record exceptions and their attributes.

<!-- toc -->

- [Recording an Exception](#recording-an-exception)
- [Attributes](#attributes)

<!-- tocstop -->

## Recording an Exception

An exception SHOULD be recorded as an `Event` on the span during which it occurred
if and only if it remains unhandled when the span ends and causes the span status
to be set to ERROR.

The name of the event MUST be `"exception"`.

**Status**: [Development](../document-status.md) - Refer to the [Recording Errors](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/recording-errors.md) document for the details on how to report errors across signals.

A typical template for an auto-instrumentation implementing this semantic convention
using an [API-provided `recordException` method](api.md#record-exception)
could look like this (pseudo-Java):

```java
Span span = myTracer.startSpan(/*...*/);
try {
  // Code that does the actual work which the Span represents
} catch (Throwable e) {
  span.recordException(e);
  span.setAttribute(AttributeKey.stringKey("error.type"), e.getClass().getCanonicalName())
  span.setStatus(StatusCode.ERROR, e.getMessage());
  throw e;
} finally {
  span.end();
}
```

## Attributes

An event representing an exception MUST have an
event name `exception`.

Additionally, the following attributes SHOULD be
filled out:

- `exception.message`
- `exception.stacktrace`
- `exception.type`

The format and semantics of these attributes are
defined in [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-spans.md).
