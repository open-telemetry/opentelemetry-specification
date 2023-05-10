# Exceptions

**Status**: [Experimental](../document-status.md)

This document defines how to record exceptions and
their required attributes.

<!-- toc -->

- [Recording an Exception](#recording-an-exception)
- [Attributes](#attributes)

<!-- tocstop -->

## Recording an Exception

An exception SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"exception"`.

A typical template for an auto-instrumentation implementing this semantic convention
using an [API-provided `recordException` method](api.md#record-exception)
could look like this (pseudo-Java):

```java
Span span = myTracer.startSpan(/*...*/);
try {
  // Code that does the actual work which the Span represents
} catch (Throwable e) {
  span.recordException(e, Attributes.of("exception.escaped", true));
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

- `exception.escaped`
- `exception.message`
- `exception.stacktrace`
- `exception.type`

The format and semantics of these attributes are
defined in [semantic conventions](semantic_conventions/exceptions.md).
