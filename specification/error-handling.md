# Error handling in OpenTelemetry

OpenTelemetry is a library that will in many cases run in a context of customer
app performing non-essential from app business logic perspective operations.
OpenTelemetry SDK also can be enabled via platform extensibility mechanisms and
potentially only enabled in runtime. Which makes the use of SDK non-obvious for
the end user and sometimes even outside of the application developer control.

This makes some unique requirements for OpenTelemetry error handling practices.

## Basic error handling principles

OpenTelemetry SDK must not throw or leak unhandled or user unhandled exceptions.

1. APIs must not throw unhandled exceptions when the API is used incorrectly by
   the end user. Smart defaults should be used so that the SDK generally works.
   For instance, name like `empty` MUST be used when `null` value was passed as
   a span name. Instead of throwing `NullReferenceException`.
2. SDK must not throw unhandled exceptions for configuration errors. Wrong
   configuration file, environment variables or config settings received from
   Agent MUST NOT bring the entire process down.
3. SDK must not throw unhandled exceptions for errors in their own operations.
   For examples, SDK MUST NOT crash process by throwing exception or causing
   `OutOfMemoryException` when telemetry receiving endpoint cannot be reached.

## Guidance

1. Every API call that may call external callback MUST handle all errors.
2. Every background operation callback, Task or Thread method should have a
   global error handling set up (like `try{}catch` statement) to ensure
   that exception from this asynchronous operation will not affect end-user app.
3. Error handling in other cases MUST follow standard language practice. Which
   is typically - reduce the scope of the error handler and add special
   processing for the expected errors.
4. Beware of any call to external callbacks or override-able interface. Expect
   them to throw.

## SDK self-diagnostics

All OpenTelemetry libraries - API, SDK, exporters, instrumentation adapters,
etc. are encouraged to expose self-troubleshooting metrics, spans and other
telemetry that can be easily enabled and filtered out by default.

Good example of such telemetry is a `Span` Zipkin exporter that indicates how
much time exporter spent on uploading telemetry. Another example may be a metric
exposed by SpanProcessor exposing the current queue size of telemetry to be
uploaded.

## Exceptions from the rule

There are situations when end-user wants to know whether API/SDK are used
correctly. For instance, it may be desirable to not deploy an app with the
malformed monitoring configuration. Or catch an invalid use of OpenTelemetry
API.

SDK authors may supply the setting that will allow to change the default
error handling behavior.
