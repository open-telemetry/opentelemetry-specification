# Supplementary Guidelines

Note: this document is NOT a spec, it is provided to support the Logs
[API](./bridge-api.md) and [SDK](./sdk.md) specifications, it does NOT add any
extra requirements to the existing specifications.

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Usage](#usage)
  * [How to Create a Log4J Log Appender](#how-to-create-a-log4j-log-appender)
  * [Logger Name](#logger-name)
  * [Context](#context)
    + [Implicit Context Injection](#implicit-context-injection)
    + [Explicit Context Injection](#explicit-context-injection)

<!-- tocstop -->

</details>

## Usage

### How to Create a Log4J Log Appender

A [log appender](../glossary.md#log-appender--bridge) implementation can be used
to bridge logs into the [Log SDK](./sdk.md)
OpenTelemetry [LogRecordExporters](sdk.md#logrecordexporter). This approach is
typically used for applications which are fine with changing the log transport
and is [one of the supported](README.md#direct-to-collector) log collection
approaches.

The log appender implementation will typically acquire a
[Logger](./bridge-api.md#logger), then
call [Emit LogRecord](./bridge-api.md#emit-a-logrecord) for `LogRecord`s
received from the application.

[Implicit Context Injection](#implicit-context-injection)
and [Explicit Context Injection](#explicit-context-injection) describe how an
Appender injects `TraceContext` into `LogRecord`s.

![Appender](img/appender.png)

This same approach can be also used for example for:

- Python logging library by creating a Handler.
- Go zap logging library by implementing the Core interface. Note that since
  there is no implicit Context in Go it is not possible to get and use the
  active Span.

Log appenders can be created in OpenTelemetry language libraries by OpenTelemetry
maintainers, or by 3rd parties for any logging library that supports a similar
extension mechanism. This specification recommends each OpenTelemetry language
library to include out-of-the-box Appender implementation for at least one
popular logging library.

### Logger Name

If the logging library has a concept that is similar to OpenTelemetry's
definition of the [Instrumentation Scope's](../glossary.md#instrumentation-scope)
name, then the appender's implementation should use that value as the
name parameter when [obtaining the Logger](./bridge-api.md#get-a-logger).

This is for example applicable to:

- Logger name in [Log4J](https://javadoc.io/doc/org.apache.logging.log4j/log4j-api/latest/org.apache.logging.log4j/org/apache/logging/log4j/Logger.html)
- Channel name in [Monolog](https://github.com/Seldaek/monolog/blob/3.4.0/doc/01-usage.md#leveraging-channels)

Appenders should avoid setting any attributes of the Instrumentation Scope.
Doing so may result in different appenders setting different attributes on the
same Instrumentation Scope, obtained with the same identity of the
[Logger](./bridge-api.md#get-a-logger), which, according to the specification,
is an error.

### Context

#### Implicit Context Injection

When Context is implicitly available (e.g. in Java) the Appender can rely on
automatic context propagation by NOT explicitly setting `Context` when
calling [emit a LogRecord](./bridge-api.md#emit-a-logrecord).

Some log libraries have mechanisms specifically tailored for injecting
contextual information into logs, such as MDC in Log4j. When available, it may
be preferable to use these mechanisms to set the Context. A log appender can
then fetch the Context and explicitly set it when
calling [emit a LogRecord](./bridge-api.md#emit-a-logrecord). This allows the correct Context
to be included even when log records are emitted asynchronously, which can
otherwise lead the Context to be incorrect.

TODO: clarify how works or doesn't work when the log statement call site and the
log appender are executed on different threads.

#### Explicit Context Injection

In order for `TraceContext` to be recorded in `LogRecord`s in languages where
the Context must be provided explicitly (e.g. Go), the end user must capture the
Context and explicitly pass it to the logging subsystem. The log appender must
take this Context and explicitly set it when
calling [emit a LogRecord](./bridge-api.md#emit-a-logrecord).

Support for OpenTelemetry for logging libraries in these languages typically can
be implemented in the form of logger wrappers that can capture the context once,
when the span is created and then use the wrapped logger to execute log
statements in a normal way. The wrapper will be responsible for injecting the
captured context in the logs.

This specification does not define how exactly it is achieved since the actual
mechanism depends on the language and the particular logging library used. In
any case the wrappers are expected to make use of the Trace Context API to get
the current active span.

See
[an example](https://docs.google.com/document/d/15vR7D1x2tKd7u3zaTF0yH1WaHkUr2T4hhr7OyiZgmBg/edit#heading=h.4xuru5ljcups)
of how it can be done for zap logging library for Go.
