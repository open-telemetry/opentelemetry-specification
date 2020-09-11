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

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

<!-- semconv exception -->
| Attribute  | Type | Description  | Example  | Required |
|---|---|---|---|---|
| `exception.type` | string | The type of the exception (its fully-qualified class name, if applicable). The dynamic type of the exception should be preferred over the static type in languages that support it. | `java.net.ConnectException`<br>`OSError` | See below |
| `exception.message` | string | The exception message. | `Division by zero`<br>`Can't convert 'int' object to str implicitly` | See below |
| `exception.stacktrace` | string | A stacktrace as a string in the natural representation for the language runtime. The representation is to be determined and documented by each language SIG. | `Exception in thread "main" java.lang.RuntimeException: Test exception\n at com.example.GenerateTrace.methodB(GenerateTrace.java:13)\n at com.example.GenerateTrace.methodA(GenerateTrace.java:9)\n at com.example.GenerateTrace.main(GenerateTrace.java:5)` | No |
| `exception.escaped` | boolean | SHOULD be set to true if the exception event is recorded at a point where it is known that the exception is escaping the scope of the span (e.g. if there is an exception active just before ending the span). [1] |  | No |

**[1]:** Note that an exception may still leave the scope of the span even if this was not set or set to false, if the event was recorded at an earlier time.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `exception.type`
* `exception.message`
<!-- endsemconv -->

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
