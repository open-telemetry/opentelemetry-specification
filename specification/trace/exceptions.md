# Exceptions

**Status**: [Stable](../document-status.md), Unless otherwise specified.

This document defines how to record exceptions and their attributes.

<!-- toc -->

- [Recording an Exception](#recording-an-exception)
- [Attributes](#attributes)

<!-- tocstop -->

## Recording an Exception

An exception SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"exception"`.

<!-- TODO: update to semconv tag once merged and released  -->
**Status**: [Development](../document-status.md) - Refer to the [Recording Errors](https://github.com/open-telemetry/semantic-conventions/blob/c77c7d7866c943b357d1d26ffa2fa89b092f2b9f/docs/general/recording-errors.md) document for the details on how to report errors across signals.

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

- [Deprecated](../document-status.md) `exception.escaped`
- `exception.message`
- `exception.stacktrace`
- `exception.type`

The format and semantics of these attributes are
defined in [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-spans.md).
