# Error handling in OpenTelemetry

OpenTelemetry generates telemetry data to help users monitor application code.
In most cases, the work that the library performs is not essential from the perspective of application business logic.
We assume that users would prefer to lose telemetry data rather than have the library significantly change the behavior of the instrumented application.

OpenTelemetry may be enabled via platform extensibility mechanisms, or dynamically loaded at runtime.
This makes the use of the library non-obvious for end users, and may even be outside of the application developer's control.
This makes for some unique requirements with respect to error handling.

## Basic error handling principles

OpenTelemetry implementations MUST NOT throw unhandled exceptions at run time.

1. API methods must not throw unhandled exceptions when used incorrectly by end users.
   The API and SDK SHOULD provide safe defaults for missing or invalid arguments.
   For instance, a name like `empty` may be used if the user passes in `null` as the span name argument during `Span` construction.

2. The API or SDK may _fail fast_ and cause the application to fail on initialization, e.g. because of bad user config or a environment, but MUST NOT cause the application to fail at run time, e.g. due to dynamic config settings received from the Agent.

3. The SDK MUST NOT throw unhandled exceptions for errors in their own operations.
   For example, an exporter should not throw an exception when it cannot reach the endpoint to which it sends telemetry data.

## Guidance

1. API methods that accept external callbacks MUST handle all errors.
2. Background tasks (e.g. threads, asynchronous tasks, spawned processes) should run in the context of a global error handler to ensure that exceptions do not affect the end user application.
3. Long-running background tasks should not fail permanently in response to internal errors.
   In general, internal exceptions should only affect the execution context of the request that caused the exception.
4. Internal error handling should follow language-specific conventions.
   In general, developers should minimize the scope of handled errors and add special processing for expected errors.
5. Beware external callbacks and overrideable interfaces: Expect them to throw.

## Self-diagnostics

All OpenTelemetry libraries -- API, SDK, exporters, instrumentation adapters, etc. -- are encouraged to expose self-troubleshooting metrics, spans, and other telemetry that can be easily enabled and filtered out by default.

One good example of such telemetry is a `Span` exporter that indicates how much time exporters spend uploading telemetry. Another example may be a metric exposed by a `SpanProcessor` that describes the current queue size of telemetry data to be uploaded.

## Exceptions from the rule

There are situations when end-user wants to know whether API/SDK are used
correctly. For instance, it may be desirable to not deploy an app with the
malformed monitoring configuration. Or catch an invalid use of OpenTelemetry
API.

SDK authors may supply the setting that will allow to change the default
error handling behavior.
