# Error handling in OpenTelemetry

OpenTelemetry generates telemetry data to help users monitor application code.
In most cases, the work that the library performs is not essential from the perspective of application business logic.
We assume that users would prefer to lose telemetry data rather than have the library significantly change the behavior of the instrumented application.

OpenTelemetry may be enabled via platform extensibility mechanisms, or dynamically loaded at runtime.
This makes the use of the library non-obvious for end users, and may even be outside of the application developer's control.
This makes for some unique requirements with respect to error handling.

## Basic error handling principles

OpenTelemetry implementations MUST NOT throw unhandled exceptions at runtime.

1. API methods MUST NOT throw unhandled exceptions when used incorrectly by end users.
   The API and SDK SHOULD provide safe defaults for missing or invalid arguments.
   For instance, a name like `empty` may be used if the user passes in `null` as the span name argument during `Span` construction.
2. The API or SDK MAY _fail fast_ and cause the application to fail on initialization, e.g. because of a bad user config or environment, but MUST NOT cause the application to fail later at runtime, e.g. due to dynamic config settings received from the Collector.
3. The SDK MUST NOT throw unhandled exceptions for errors in their own operations.
   For example, an exporter should not throw an exception when it cannot reach the endpoint to which it sends telemetry data.

## Guidance

1. API methods that accept external callbacks MUST handle all errors.
2. Background tasks (e.g. threads, asynchronous tasks, and spawned processes) should run in the context of a global error handler to ensure that exceptions do not affect the end user application.
3. Long-running background tasks should not fail permanently in response to internal errors.
   In general, internal exceptions should only affect the execution context of the request that caused the exception.
4. Internal error handling should follow language-specific conventions.
   In general, developers should minimize the scope of error handlers and add special processing for expected exceptions.
5. Beware external callbacks and overridable interfaces: Expect them to throw.
6. Beware to call any methods that wasn't explicitly provided by API and SDK users as a callbacks.
   Method `ToString` that SDK may decide to call on user object may be badly implemented and lead to stack overflow.
   It is common that the application never calls this method and this bad implementation would never be caught by an application owner.
7. Whenever API call returns values that is expected to be non-`null` value - in case of error in processing logic - SDK MUST return a "no-op" or any other "default" object that was (_ideally_) pre-allocated and readily available.
   This way API call sites will not crash on attempts to access methods and properties of a `null` objects.

## Error handling and performance

Error handling and extensive input validation may cause performance degradation, especially on dynamic languages where the input object types are not guaranteed in compile time.
Runtime type checks will impact performance and are error-prone, exceptions may occur despite the best effort.

It is recommended to have a global exception handling logic that will guarantee that exceptions are not leaking to the user code.
And make a reasonable trade-off of the SDK performance and fullness of type checks that will provide a better on-error behavior and SDK errors troubleshooting.

## Self-diagnostics

All OpenTelemetry libraries -- the API, SDK, exporters, instrumentations, etc. -- are encouraged to expose self-troubleshooting metrics, spans, and other telemetry that can be easily enabled and filtered out by default.

One good example of such telemetry is a `Span` exporter that indicates how much time exporters spend uploading telemetry.
Another example may be a metric exposed by a `SpanProcessor` that describes the current queue size of telemetry data to be uploaded.

Whenever the library suppresses an error that would otherwise have been exposed to the user, the library SHOULD log the error using language-specific conventions.
SDKs MAY expose callbacks to allow end users to handle self-diagnostics separately from application code.

## Configuring Error Handlers

SDK implementations MUST allow end users to change the library's default error handling behavior for relevant errors.
Application developers may want to run with strict error handling in a staging environment to catch invalid uses of the API, or malformed config.
Note that configuring a custom error handler in this way is the only exception to the basic error handling principles outlined above.
The mechanism by which end users set or register a custom error handler should follow language-specific conventions.

### Examples

These are examples of how end users might register custom error handlers.
Examples are for illustration purposes only. OpenTelemetry client authors
are free to deviate from these provided that their design matches the requirements outlined above.

#### Go

```go
// The basic Error Handler interface
type ErrorHandler interface {
  Handle(err error)
}

func Handler() ErrorHandler
func SetHandler(handler ErrorHandler)
```

```go
// Registering a custom Error Handler
type IgnoreExporterErrorsHandler struct{}

func (IgnoreExporterErrorsHandler) Handle(err error) {
    switch err.(type) {
    case *SpanExporterError:
    default:
        fmt.Println(err)
    }
}

func main() {
    // Other setup ...
    opentelemetrysdk.SetHandler(IgnoreExporterErrorsHandler{})
}
```

#### Java

OpenTelemetry Java uses [java.util.logging](https://docs.oracle.com/javase/7/docs/api/java/util/logging/package-summary.html)
to output and handle all logs, including errors. Custom handlers and filters can be registered both in code and using the Java logging configuration file.  

```properties
## Turn off all error logging
io.opentelemetry.level = OFF
```

```java
// Creating a custom filter which does not log errors that come from the exporter
public class IgnoreExportErrorsFilter implements Filter {

 public boolean isLoggable(LogRecord record) {
    return !record.getMessage().contains("Exception thrown by the export");
 }
}
```

```properties
## Registering the custom filter on the BatchSpanProcessor
io.opentelemetry.sdk.trace.export.BatchSpanProcessor = io.opentelemetry.extensions.logging.IgnoreExportErrorsFilter
```
