# Semantic Conventions for Exceptions

This document defines semantic conventions for recording application
exceptions.

<!-- toc -->

- [Recording an Exception](#recording-an-exception)
- [Attributes](#attributes)
  - [Stacktrace Representation](#stacktrace-representation)

<!-- tocstop -->

## Recording an Exception

An exception SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"exception"`.

<a name="exception-end-example"></a>

A typical template for an auto-instrumentation implementing this semantic convention
using an [API-provided `recordException` method](../api.md#record-exception)
could look like this (pseudo-Java):

```java
Span span = myTracer.startSpan(/*...*/);
try {
  // original code
} catch (Throwable e) {
 span.recordException(e, Attributes.of("exception.escaped", true));
 throw e;
} finally {
 span.end();
}
```

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

| Attribute name       | Type   | Notes and examples                                                                                                                                                                                                                                                                                                                                                                                                                  | Required?                                                  |
| :------------------- | :----- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
| exception.type       | String | The type of the exception (its fully-qualified class name, if applicable). The dynamic type of the exception should be preferred over the static type in languages that support it. E.g. "java.net.ConnectException", "OSError"                                                                                                                                                                                                     | One of `exception.type` or `exception.message` is required |
| exception.message    | String | The exception message. E.g. `"Division by zero"`, `"Can't convert 'int' object to str implicitly"`                                                                                                                                                                                                                                                                                                                                  | One of `exception.type` or `exception.message` is required |
| exception.stacktrace | String | A stacktrace as a string in the natural representation for the language runtime. The representation is to be determined and documented by each language SIG. E.g. `"Exception in thread \"main\" java.lang.RuntimeException: Test exception\n at com.example.GenerateTrace.methodB(GenerateTrace.java:13)\n at com.example.GenerateTrace.methodA(GenerateTrace.java:9)\n at com.example.GenerateTrace.main(GenerateTrace.java:5)"`. | No                                                         |
| exception.escaped | Bool | SHOULD be set to true if the exception event is recorded at a point where it is known that the exception is escaping the scope of the span. See [explanation below](#escaped-exceptions). | No |

### Stacktrace Representation

The table below, adapted from [Google Cloud][gcp-error-reporting], includes
possible representations of stacktraces in various languages. The table is not
meant to be a recommendation for any particular language, although SIGs are free
to adopt them if they see fit.

| Language   | Format                                                              |
| ---------- | ------------------------------------------------------------------- |
| C#         | the return value of [Exception.ToString()][csharp-stacktrace]       |
| Go         | the return value of [runtime.Stack][go-stacktrace]                  |
| Java       | the contents of [Throwable.printStackTrace()][java-stacktrace]      |
| Javascript | the return value of [error.stack][js-stacktrace] as returned by V8  |
| Python     | the return value of [traceback.format_exc()][python-stacktrace]     |
| Ruby       | the return value of [Exception.full_message][ruby-full-message]     |

Backends can use the language specified methodology for generating a stacktrace
combined with platform information from the
[telemetry sdk resource][telemetry-sdk-resource] in order to extract more fine
grained information from a stacktrace, if necessary.

[gcp-error-reporting]: https://cloud.google.com/error-reporting/reference/rest/v1beta1/projects.events/report
[java-stacktrace]: https://docs.oracle.com/javase/7/docs/api/java/lang/Throwable.html#printStackTrace%28%29
[python-stacktrace]: https://docs.python.org/3/library/traceback.html#traceback.format_exc
[js-stacktrace]: https://v8.dev/docs/stack-trace-api
[ruby-full-message]: https://ruby-doc.org/core-2.7.1/Exception.html#method-i-full_message
[csharp-stacktrace]: https://docs.microsoft.com/en-us/dotnet/api/system.exception.tostring
[go-stacktrace]: https://golang.org/pkg/runtime/debug/#Stack
[telemetry-sdk-resource]: https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions#telemetry-sdk

### Escaped exceptions

An exception is considered to have escaped (aka left) the scope of a span,
if that span is ended while the exception is still "in flight".

While it is usually not possible to determine whether some exception thrown
now *will* escape the scope of a span, it is trivial to know that an exception
will escape, if one checks for an active exception just before ending the span.
See the [example above](#exception-end-example). It follows that an exception
may still escape the scope of the span even if the `exception.escaped` attribute
was not set or set to false, since that event might have been recorded at a time
where it was not clear whether the exception will escape.
