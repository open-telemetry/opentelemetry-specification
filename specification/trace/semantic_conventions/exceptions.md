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

| Attribute name       | Type   | Notes and examples                                                                                                                                                                                                                                                                                                                                                                                                                  | Required?                                                  |
| :------------------- | :----- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
| exception.type       | String | The type of the exception (its fully-qualified class name, if applicable). The dynamic type of the exception should be preferred over the static type in languages that support it. E.g. "java.net.ConnectException", "OSError"                                                                                                                                                                                                     | One of `exception.type` or `exception.message` is required |
| exception.message    | String | The exception message. E.g. `"Division by zero"`, `"Can't convert 'int' object to str implicitly"`                                                                                                                                                                                                                                                                                                                                  | One of `exception.type` or `exception.message` is required |
| exception.stacktrace | String | A stacktrace as a string in the natural representation for the language runtime. The representation is to be determined and documented by each language SIG. E.g. `"Exception in thread \"main\" java.lang.RuntimeException: Test exception\n at com.example.GenerateTrace.methodB(GenerateTrace.java:13)\n at com.example.GenerateTrace.methodA(GenerateTrace.java:9)\n at com.example.GenerateTrace.main(GenerateTrace.java:5)"`. | No                                                         |
| exception.event      | String | An enum-like string describing the event that happened with the exception. [See below.](#exception.event) | Yes                                                         |

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

<a name="exception.event"></a>

### exception.event

This string describes what event occurred. It MUST be one of the following strings:

* `handled`: The exception was caught.
* `translated`: A special case of `handled`:
  If the exception was translated into some non-exception error indicator
  (e.g. a `KeyNotFoundException` was caught and translated into an HTTP 404 status code).
  If possible, instrumentations SHOULD NOT record a `handled` for the same exception immediately preceding this.
* `thrown`: The exception was thrown.
  Typical code that should set this: `throw new RuntimeException("Error!")`.
* `rethrown`: The exception was caught and then re-thrown as-is.
  Typical code that should set this: `throw;` in C++,
  `raise` (without argument) in Python, `catch (... e) { ...; throw e}` in Java.
  If a new exception object is thrown (even if a previous exception is the cause),
  `thrown` MUST be used instead.
  Instrumentations may not be able distinguish this from `thrown` and SHOULD use `thrown` if in doubt.

Note that instrumentations are not expected to record all exception events.
Typically, `thrown` is the most important event.
`rethrown` may also be useful especially if the original `thrown` event was not instrumented.
Instrumentations should use good judgment of when to record `translated` and especially `handled` events.
They may often not be that interesting and exception events can be relatively heavyweight.

In particular, there is one typical case where multiple closely-related exception events occur:
If an exception is handled by throwing a new exception,
logically both a `handled` and a `thrown` event occur.
As information about the original exception is usually found in the cause-chain
encoded in the `exception.stacktrace` of the `thrown` exception,
instrumentations SHOULD NOT record the the `handled` exception in this case.

The following example (Java) shows several possible events:

```java
public class Example {
  public static void main(String[] args) {
    try {
      someMethodThatMayThrow();
    } catch (Exception e) {
      // e is *handled*
      // (if instrumentation can detect the translation below,
      // e should not be recorded here).
      e.printStackTrace();
      System.exit(1); // e is *translated* (to exit code 1).
    }
  }

  static void someMethodThatMayThrow() {
    someMethodWithCleanup();
  } // Instrumentation may record a *rethrown* exception here
  // if a span is recorded within this method.
  // E.g. if someMethodThatMayThrow was instrumented with a span that is both
  // started and ended within the method (typically using some kind of Scope API)-

  static void someMethodThatMayThrow() {
    try {
      someOptionalMethod();
    } catch (IOException e) { // e is *handled* here
      // OK, we don't care. Or we call an alternative method.
    }
    try {
      someFailingMethod();
    } (catch Exception e) {
      // e is *handled* (should not be recorded because of rethrow below)

      // ...Some cleanup...
      throw e; // e is *rethrown*
    }
  }

  static void someOptionalMethod() throws IOException {
    try {
      // Something that throws an IOException
    } catch (IOException e) {
      // Even though we throw an exception that has e as a cause,
      // we do not rethrow it, but throw a new exception object,
      // so this is a *thrown* exception.
      throw new IOException("some optional operation failed", e);
    }
  }

  static void someFailingMethod() {
    throw new RuntimeException("Whoops"); // e is *thrown*
  }
}
```
