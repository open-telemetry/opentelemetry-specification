# Recording exceptions and errors on logs

<!-- toc -->

- [Motivation](#motivation)
- [Guidance](#guidance)
  * [Details](#details)
- [Spec changes](#spec-changes)
  * [API](#api)
  * [Configuration](#configuration)
- [Migrating instrumentations](#migrating-instrumentations)
  * [Migrating from span events](#migrating-from-span-events)
  * [Migrating log bridges](#migrating-log-bridges)
- [Examples](#examples)
  * [Logging errors from a client library in a user application](#logging-errors-from-a-client-library-in-a-user-application)
  * [Logging errors inside a natively instrumented Library](#logging-errors-inside-a-natively-instrumented-library)
  * [Logging errors in a messaging processor](#logging-errors-in-a-messaging-processor)
    + [Natively instrumented library](#natively-instrumented-library)
    + [Instrumentation library](#instrumentation-library)
- [Trade-offs and mitigations](#trade-offs-and-mitigations)
- [Prior art and alternatives](#prior-art-and-alternatives)
- [Open questions](#open-questions)
- [Future possibilities](#future-possibilities)

<!-- tocstop -->

This OTEP provides guidance on how to record errors using OpenTelemetry Logs,
focusing on minimizing duplication and providing context to reduce the noise.

In the long term, errors recorded on logs **will replace span events**
(according to [Event vision OTEP](./0265-event-vision.md)).

> [!NOTE]
> Throughout this OTEP, the terms error and exception are defined as follows:
>
> - *Error* refers to a general concept describing any non-success condition,
>   which may manifest as an exception, non-successful status code, or an invalid
>   response.
> - *Exception* specifically refers to runtime exceptions and their associated stack traces.

## Motivation

Today, OTel supports recording *exceptions* using span events available through the Trace API. Outside the OTel world,
*errors* are usually recorded by user apps and libraries using logging libraries,
and may be recorded as OTel logs via a logging bridge. As a result, we have two
different ways to record exceptions resulting in inconsistent user experience.

Using logs to record errors has the following advantages over using span events:

- they can be recorded for operations that don't have any tracing instrumentation
- they can be sampled along with or separately from spans
- they can have different severity levels to reflect how critical the error is
- they are already reported natively by many frameworks and libraries

Recording errors is essential for troubleshooting, but regardless of how they are recorded, they could be noisy:

- distributed applications experience transient errors at a rate proportional to their scale, and
  errors in logs could be misleading. Individual occurrences of transient errors
  are not necessarily indicative of a problem.
- exception stack traces can be huge. The corresponding attribute value can frequently reach several KBs, resulting in high costs
  associated with ingesting and storing them. It's also common to log errors multiple times
  as they bubble up, leading to duplication and aggravating the verbosity problem.
- severity depends on the context and, in the general case, is not known at the time the error
  occurs since errors are frequently handled (suppressed, retried, ignored) by the caller.

In this OTEP, we'll provide guidance around recording errors that minimizes duplication,
allows reducing noise with configuration, and allows capturing errors in the
absence of a recorded span.

This guidance applies to general-purpose instrumentations, including natively
instrumented libraries.

Application developers should consider following it as a starting point, but
they are encouraged to adjust it to their needs.

## Guidance

This guidance boils down to the following:

Instrumentations SHOULD record error information along with relevant context as
a log record with appropriate severity.

Instrumentations SHOULD set severity to `Error` or higher only when the log describes a
problem affecting application functionality, availability, performance, security, or
another aspect that is important for the given type of application.

When instrumentation records an exception, it SHOULD, when possible, provide
the whole exception instance to the logging facade or OTel API so the OTel SDK
can record it fully or partially based on provided configuration. The default OTel SDK
behavior SHOULD be to record exception stack traces when logging exceptions at `Error`
or higher severity.

### Details

1. Errors SHOULD be recorded as [logs](https://github.com/open-telemetry/semantic-conventions/blob/v1.29.0/docs/exceptions/exceptions-logs.md)
   or as [log-based events](https://github.com/open-telemetry/semantic-conventions/blob/v1.29.0/docs/general/events.md)

2. Instrumentations for incoming requests, message processing, background job execution, or others that wrap application code and usually
   create local root spans, SHOULD record logs for unhandled errors with `Error` severity.

   Some runtimes provide a global exception handler that can be used to log exceptions.
   Priority should be given to the instrumentation point where the operation context is available.
   Language SIGs are encouraged to give runtime-specific guidance. For example, here is the
   [.NET guidance](https://github.com/open-telemetry/opentelemetry-dotnet/blob/610045298873397e55e0df6cd777d4901ace1f63/docs/trace/reporting-exceptions/README.md#unhandled-exception)
   for recording exceptions on traces.

3. Natively instrumented libraries SHOULD record a log describing an error and the context it happened in
   as soon as the error is detected (or where the most context is available).

4. It's NOT RECOMMENDED to record the same error as it propagates through the call stack, or
   to attach the same instance of an exception to multiple log records.

5. An error SHOULD be logged with appropriate severity depending on the available context.

   - Errors that don't indicate actual issues SHOULD be recorded with
     severity not higher than `Info`.

     Such errors have a minor impact, if any,
     on application functionality, availability, or performance (beyond the performance hit introduced
     if an exception is used to control application logic).

     Examples:

      - an error is returned when checking the existence of an optional service or resource.
      - an exception is thrown on the server when the client disconnects before reading
        the full response from the server.

   - Errors that are expected to be retried or handled by the caller or another
     layer of the component SHOULD be recorded with severity not higher than `Warn`.

     Such errors represent transient failures that are common and expected in
     distributed applications. They typically increase the latency of individual
     operations and have a minor impact on overall application availability.

     Examples:

      - an attempt to connect to a remote service times out.
      - a remote service returns a 401 "Unauthorized" response code.
      - writing data to a file results in an IO exception.
      - a remote service returns a 503 "Service Unavailable" response for 5 times in a row,
        retry attempts are exhausted, and the corresponding operation fails.

   - Unhandled (by the application code) errors that don't result in application
     shutdown SHOULD be recorded with severity `Error`

     These errors are not expected and may indicate a bug in the application logic
     that the application instance was not able to recover from, or a gap in the error
     handling logic.

     Examples:

      - A background job terminates with an exception
      - An HTTP framework error handler catches an exception thrown by the application code.

        Note: some frameworks use exceptions as a communication mechanism when a request fails. For example,
        Spring users can throw a [ResponseStatusException](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/server/ResponseStatusException.html)
        exception to return an unsuccessful status code. Such exceptions represent errors already handled by the application code.
        Application code, in this case, is expected to log this at the appropriate severity.
        General-purpose instrumentation MAY record such errors, but at a severity not higher than `Warn`.

   - Errors that result in application shutdown SHOULD be recorded with severity `Fatal`.

     Examples:

      - The application detects an invalid configuration at startup and shuts down.
      - The application encounters a (presumably) terminal error, such as an out-of-memory condition.

    Note: While fatal errors SHOULD be recorded, the issues causing them may often
    prevent the application from shutting down gracefully and exporting telemetry.

6. When recording exceptions on logs, applications and instrumentations are encouraged to add additional attributes
   to describe the context that the exception was thrown in.
   They are also encouraged to define their own error events and enrich them with exception details.

7. The OTel SDK SHOULD record stack traces on exceptions with severity `Error` or higher and SHOULD allow users to
   change the threshold.

   See [logback exception config](https://logback.qos.ch/manual/layouts.html#ex) for an example of configuration that
   records stack traces conditionally.

## Spec changes

> [!NOTE]
>
> It should not be an instrumentation concern to decide whether an exception stack trace
> should be recorded or not.
>
> A natively instrumented library may write logs providing an exception instance
> through a log bridge and not be aware of this guidance.
>
> It also may be desirable by some vendors/apps to record all exception details at all levels.

### API

The OTel Logs API SHOULD provide methods that enrich log records with exception details such as
`setException(exception)` and similar to the [RecordException](../specification/trace/api.md#record-exception) method on span.

The OTel SDK, based on the log severity and configuration, SHOULD record exception details fully,
partially, or not at all.

The signature of the method is to be determined by each language
and can be overloaded as appropriate, for example to provide custom stack traces
collection when the language does not provide a built-in mechanism for it.

It MUST be possible to efficiently set `exception.*` attributes on a log record
based on configuration and without using the `setException` method.

### Configuration

OTel SHOULD provide a configuration option allowing to specify the severity threshold
at which exception stack traces are to be collected.

It SHOULD be possible to distinguish between the absence of configuration and an
explicit configuration for the default value to support [backward-compatibility in log bridges](#migrating-log-bridges).

The exact configuration option name and semantics will be defined at the OTEP implementation stage.
For the scope of this document, let's use 'exception stack traces collection severity threshold'.

## Migrating instrumentations

### Migrating from span events

> [!NOTE]
>
> The migration begins once the specification for recording exceptions on logs is stabilized,
> and once there is stable support for it in the relevant SDK.
>
> When this happens, new instrumentations (or existing ones that do not record exceptions on
> span events) SHOULD NOT start recording exceptions on span events.
>
> Users will still be able to opt-in to sending their events to span events using
> [log -> span events conversion](https://github.com/open-telemetry/opentelemetry-specification/issues/4393)
> at any stage of the migration process.

We will define a configuration option to let users choose if they want **existing** instrumentations that already emit
span events to record exceptions on span events or logs.

Such instrumentations SHOULD default to recording exceptions on span events in their current major version
and record them on logs only when the user opts-in.

In the next major version, such instrumentations SHOULD stop recording exceptions on span events.

This is a simplified version of [stability opt-in migration](https://github.com/open-telemetry/semantic-conventions/blob/727700406f9e6cc3f4e4680a81c4c28f2eb71569/docs/http/README.md?plain=1#L13-L37) used in semantic conventions.

### Migrating log bridges

Today log bridges translate exception instances into attributes on OTel log records.

Log bridges that capture stack traces regardless of log record severity,
in their current major version, SHOULD preserve their current behavior when the
user has not provided an explicit [exception stack traces collection severity threshold](#configuration).

If the user has provided an explicit exception stack traces collection severity threshold,
log bridges SHOULD record stack traces accordingly and MAY use `setException` convenience
method described in the [API changes](#api-changes) section.

In their next major version, log bridges SHOULD start using `setException` method or
follow defaults documented for OTel SDK when explicitly recording `exception.*`
attributes.

## Examples

### Logging errors from a client library in a user application

```java
StorageClient client = createClient(endpoint, credential);
...
try {
    BinaryData content = client.download(contentId);

    return response(content, HttpStatus.OK);
} catch (ContentNotFoundException ex) {
    logger.logRecordBuilder()
        .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
        // let's assume it's expected that some content can disappear
        .severityNumber(Severity.INFO)
        // by default SDK will only populate `exception.type` and `exception.message`
        // since severity is `INFO`, but it should not be instrumentation library
        // concern
        .setException(ex)
        .emit();

    return response(HttpStatus.NOT_FOUND);
} catch (ForbiddenException ex) {
    logger.logRecordBuilder()
        // let's assume it's really unexpected for this application - service does not have access to the underlying storage.
        .severityNumber(Severity.ERROR)
        .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
        // by default SDK will record stack trace for this exception since the severity is ERROR
        .setException(ex)
        .emit();

    return response(HttpStatus.INTERNAL_SERVER_ERROR);
}
```

### Logging errors inside a natively instrumented Library

It's a common practice to record errors using logging libraries. Client libraries that are natively instrumented with OpenTelemetry
MAY leverage the OTel Events/Logs API for their exception logging purposes.

```java
public class StorageClient {

    private final Logger logger;
    ...
    public BinaryData getContent(String contentId) {
         HttpResponse response = client.get(contentId);
         if (response.statusCode() == 200) {
             return readContent(response);
         }

         logger.logRecordBuilder()
            // In general we don't know if it's an error - we expect the caller
            // to handle it and decide. So this is a warning (at most).
            // If the exception thrown below remains unhandled, it'd be logged by the global handler.
            .setSeverity(Severity.WARN)
            .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
            .addAttribute(AttributeKey.stringKey("http.response.status_code"), response.statusCode())
            .setBody("Unexpected HTTP response")
            .emit();

        if (response.statusCode() == 404) {
            throw new ContentNotFoundException(readErrorInfo(response));
        }

        ...
    }
}
```

Network-level errors are part of normal life; we should consider using low severity for them.

```java
public class NetworkClient {

    private final Logger logger;
    ...
    public long send(ByteBuffer content) {
        try {
            return socketChannel.write(content);
        } catch (SocketException ex) {
            logger.logRecordBuilder()
              // We'll write a warn for the overall operation if retries are exhausted.
              .setSeverity(Severity.INFO)
              .addAttribute("connection.id", this.getId())
              .addException(ex)
              .setBody("Failed to send content")
              .emit();

            throw ex;
        }
    }
}
```

### Logging errors in a messaging processor

#### Natively instrumented library

In this example, application code provides the callback to the messaging processor for
processing each message.

```java
MessagingProcessorClient processorClient = new MessagingClientBuilder()
  .endpoint(endpoint)
  .queueName(queueName)
  .processor()
  .processMessage(messageContext -> processMessage(messageContext))
  .buildProcessorClient();

processorClient.start();
```

The `MessagingProcessorClient` implementation should catch exceptions thrown by the `processMessage` callback and log them similarly to
this example:

```java
MessageContext context = retrieveNext();
try {
  processMessage.accept(context);
} catch (Throwable t) {
  // This natively instrumented library may use the OTel Logs API or another logging library such as slf4j.
  // Here we use Error severity since this exception was not handled by the application code.
  logger.atError()
    .addKeyValuePair("messaging.message.id", context.getMessageId())
    ...
    .setException(t)
    .log("Message processing failed");
  // error handling logic ...
}
```

If this instrumentation captures message processing as a span, it should pass that span's context
(either implicitly or explicitly) when emitting the log record to preserve correlation.

#### Instrumentation library

In this example, we leverage the Spring Kafka `RecordInterceptor` extensibility point that allows us to
listen to exceptions that were never handled.

```java
import org.springframework.kafka.listener.RecordInterceptor;
final class InstrumentedRecordInterceptor<K, V> implements RecordInterceptor<K, V> {
  ...

  @Override
  public void failure(ConsumerRecord<K, V> record, Exception exception, Consumer<K, V> consumer) {
    // We should capture this error in the scope of the processing span (or pass its context explicitly).
    logger.logRecordBuilder()
      .setSeverity(Severity.ERROR)
      .addAttribute("messaging.message.id", record.getId())
      ...
      .addException(exception)
      .setBody("Consumer error")
      .emit();
    // ..
  }
}
```

See [corresponding Java (tracing) instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation/spring/spring-kafka-2.7/library/src/main/java/io/opentelemetry/instrumentation/spring/kafka/v2_7/InstrumentedRecordInterceptor.java) for the details.

## Trade-offs and mitigations

1. Switching from recording exceptions as span events to log records is a breaking change
   for any component following the existing [exception guidance](/specification/trace/exceptions.md).

2. Recording exceptions as logs will result in UX degradation for users
   leveraging trace-only backends such as Jaeger.

3. Having exceptions exported and stored along with span is beneficial for some backends.

**Mitigation:**

In addition to the plan outlined in the [Migration](#migrating-instrumentations) section, we
should provide opt-in [log <-> span events conversion](https://github.com/open-telemetry/opentelemetry-specification/issues/4393)
following [Event vision OTEP](./0265-event-vision.md#relationship-to-span-events).

## Prior art and alternatives

Alternatives:

1. Deduplicate exception info by marking exception instances as logged.
   This can potentially mitigate the problem for existing applications when they log exceptions extensively.
   We should still provide optimal guidance for greenfield applications and libraries,
   covering the wider problem of recording errors.

## Open questions

-

## Future possibilities

-
