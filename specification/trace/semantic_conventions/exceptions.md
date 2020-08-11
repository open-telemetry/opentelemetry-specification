# Semantic Conventions for Exceptions

This document defines semantic conventions for recording application
exceptions.

<!-- toc -->

- [Recording an Exception](#recording-an-exception)
- [Attributes](#attributes)
  - [Stacktrace Representation](#stacktrace-representation)

<!-- tocstop -->

## Recording an Exception

An exception that escapes the scope of a span
SHOULD be recorded as an `Event` on that span.
An exception is considered to have escaped the scope if the span is ended
while the exception is still "in flight". Note:

* While it is usually not possible to determine whether some exception thrown
  now *will* escape the scope of a span, it is trivial to know that an exception
  will escape, if one checks for an active exception just before ending the span.
  See the [example below](#exception-end-example).
* Special considerations may apply for Go, where exception semantic conventions
  might be used for non-exceptions.
  See [issue #764](https://github.com/open-telemetry/opentelemetry-specification/issues/764).

The name of the event MUST be `"exception"`.

Note that multiple events (on the same or different Spans)
might be logged for the same exception object instance.
E.g. one event might be logged in an instrumented exception constructor
and another event might be logged when an exception leaves the scope of a span.

<a name="exception-end-example"></a>

A typical template for an auto-instrumentation implementing this semantic convention
could look like this:

```java
Span span = myTracer.startSpan(/*...*/);
try {
  // original code
} catch (Throwable e) {
 span.recordException(e, /*escaped=*/true);
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
| exception.escaped | Bool | SHOULD be set to true if the exception event is recoded at a point where it is known that the exception is escaping the scope of the span (e.g. if there is an exception active just before ending the Span). Note that an exception may still leave the scope of the span even if this was not set or set to false, if the event was recorded at an earlier time. | No |

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
| Ruby       | the result of [Exception.backtrace][ruby-stacktrace] joined by "\n" |

Backends can use the language specified methodology for generating a stacktrace
combined with platform information from the
[telemetry sdk resource][telemetry-sdk-resource] in order to extract more fine
grained information from a stacktrace, if necessary.

[gcp-error-reporting]: https://cloud.google.com/error-reporting/reference/rest/v1beta1/projects.events/report
[java-stacktrace]: https://docs.oracle.com/javase/7/docs/api/java/lang/Throwable.html#printStackTrace%28%29
[python-stacktrace]: https://docs.python.org/3/library/traceback.html#traceback.format_exc
[js-stacktrace]: https://v8.dev/docs/stack-trace-api
[ruby-stacktrace]: https://ruby-doc.org/core-2.7.1/Exception.html#method-i-backtrace
[csharp-stacktrace]: https://docs.microsoft.com/en-us/dotnet/api/system.exception.tostring
[go-stacktrace]: https://golang.org/pkg/runtime/debug/#Stack
[telemetry-sdk-resource]: https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions#telemetry-sdk
