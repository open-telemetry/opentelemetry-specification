# Semantic Conventions for Exceptions

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for recording exceptions on
[logs](../bridge-api.md#emit-a-logrecord) and [events](../event-api.md#emit-event)
emitted through the [Logger API](../bridge-api.md#logger).

<!-- toc -->

- [Recording an Exception](#recording-an-exception)
- [Attributes](#attributes)
  * [Stacktrace Representation](#stacktrace-representation)

<!-- tocstop -->

## Recording an Exception

Exceptions SHOULD be recorded as attributes on the
[LogRecord](../data-model.md#log-and-event-record-definition) passed to the [Logger](../bridge-api.md#logger) emit
operations. Exceptions MAY be recorded on "logs" or "events" depending on the
context.

To encapsulate proper handling of exceptions API authors MAY provide a
constructor, `RecordException` method/extension, or similar helper mechanism on
the `LogRecord` class/structure or wherever it makes the most sense depending on
the language runtime.

## Attributes

The table below indicates which attributes should be added to the
[LogRecord](../data-model.md#log-and-event-record-definition) and their types.

<!-- semconv log-exception -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `exception.message` | string | The exception message. | `Division by zero`; `Can't convert 'int' object to str implicitly` | See below |
| `exception.stacktrace` | string | A stacktrace as a string in the natural representation for the language runtime. The representation is to be determined and documented by each language SIG. | `Exception in thread "main" java.lang.RuntimeException: Test exception\n at com.example.GenerateTrace.methodB(GenerateTrace.java:13)\n at com.example.GenerateTrace.methodA(GenerateTrace.java:9)\n at com.example.GenerateTrace.main(GenerateTrace.java:5)` | Recommended |
| `exception.type` | string | The type of the exception (its fully-qualified class name, if applicable). The dynamic type of the exception should be preferred over the static type in languages that support it. | `java.net.ConnectException`; `OSError` | See below |

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `exception.type`
* `exception.message`
<!-- endsemconv -->

### Stacktrace Representation

Same as [Trace Semantic Conventions for Exceptions - Stacktrace
Representation](../../trace/semantic_conventions/exceptions.md#stacktrace-representation).
