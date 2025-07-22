# Recording exceptions and errors in logs

<!-- toc -->

- [Motivation](#motivation)
- [Guidance](#guidance)
  * [Details](#details)
- [API changes](#api-changes)
- [Examples](#examples)
  * [Logging errors from client library in a user application](#logging-errors-from-client-library-in-a-user-application)
  * [Logging errors inside the natively instrumented library](#logging-errors-inside-the-natively-instrumented-library)
  * [Logging errors in messaging processor](#logging-errors-in-messaging-processor)
    + [Natively instrumented library](#natively-instrumented-library)
    + [Instrumentation library](#instrumentation-library)
- [Prototypes](#prototypes)
- [Prior art and alternatives](#prior-art-and-alternatives)
- [Future possibilities](#future-possibilities)

<!-- tocstop -->

This OTEP continues [Span Event API deprecation plan OTEP](./4430-span-event-api-deprecation-plan.md)
and provides guidance on how to record errors and exceptions using OpenTelemetry Logs,
focusing on minimizing duplication and providing context to reduce noise.

> [!NOTE]
> Throughout this OTEP, the terms exception and error are defined as follows:
>
> - *Error* refers to a general concept describing any non-success condition,
>   which may manifest as an exception, non-successful status code, or an invalid
>   response.
> - *Exception* specifically refers to runtime exceptions and their associated stack traces.

## Motivation

Today, OTel supports recording *exceptions* using span events available through
the Trace API that is [being deprecated](./4430-span-event-api-deprecation-plan.md).
Outside the OTel world, *exceptions* and *errors* are usually recorded by user apps
and libraries using logging libraries, and may be recorded as OTel logs via a logging bridge.

Recording errors is essential for troubleshooting, but they can be noisy:

- Distributed applications experience transient errors at a rate proportional to their scale, and
  errors in logs can be misleading. Individual occurrences of transient errors
  are not necessarily indicative of a problem.
- Exception stack traces can be huge. The corresponding attribute value can frequently reach several KBs, resulting in high costs
  associated with ingesting and storing them. It's also common to log errors multiple times
  as they bubble up, leading to duplication and aggravating the verbosity problem.
- Severity depends on the context and, in the general case, is not known at the time the error
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

When an instrumentation records an exception, it SHOULD provide
the whole exception instance to the OTel SDK so the SDK can record it fully or
partially based on the provided configuration. The default SDK behavior SHOULD
be to record exception stack traces when logging exceptions at `Error` or higher severity.

### Details

1. Errors SHOULD be recorded as [logs](https://github.com/open-telemetry/semantic-conventions/blob/v1.36.0/docs/exceptions/exceptions-logs.md)
   or as [log-based events](https://github.com/open-telemetry/semantic-conventions/blob/v1.36.0/docs/general/events.md).

2. Instrumentations for incoming requests, message processing, background job execution, or others that wrap application code and usually
   create local root spans, SHOULD record logs for unhandled errors with `Error` severity.

   Some runtimes provide a global exception handler that can be used to log exceptions.
   Priority should be given to the instrumentation point where the operation context is available.
   Language SIGs are encouraged to provide runtime-specific guidance. For example, here is the
   [.NET guidance](https://github.com/open-telemetry/opentelemetry-dotnet/blob/610045298873397e55e0df6cd777d4901ace1f63/docs/trace/reporting-exceptions/README.md#unhandled-exception)
   for recording exceptions on traces.

3. Natively instrumented libraries SHOULD record a log describing an error and the context in which it occurred
   as soon as the error is detected (or where the most context is available).

4. It is NOT RECOMMENDED to record the same error as it propagates through the call stack, or
   to attach the same instance of an exception to multiple log records.

5. An error SHOULD be logged with appropriate severity depending on the available context.

   - Errors that don't indicate actual issues SHOULD be recorded with
     severity not higher than `Info`.

     Such errors can be used to control application logic and have a minor impact, if any,
     on application functionality, availability, or performance (beyond the performance hit introduced
     if an exception is used to control application logic).

     Examples:

      - An error is returned when checking for optional dependency or resource existence.
      - An exception is thrown on the server when the client disconnects before reading
        the full response from the server.

   - Errors that are expected to be retried or handled by the caller or another
     layer of the component SHOULD be recorded with severity not higher than `Warn`.

     Such errors represent transient failures that are common and expected in
     distributed applications. They typically increase the latency of individual
     operations and have a minor impact on overall application availability.

     Examples:

      - An attempt to connect to the required remote dependency times out.
      - A remote dependency returns a 401 "Unauthorized" response code.
      - Writing data to a file results in an IO exception.
      - A remote dependency returned a 503 "Service Unavailable" response for 5 consecutive times,
        retry attempts are exhausted, and the corresponding operation has failed.

   - Unhandled (by the application code) errors that don't result in application
     shutdown SHOULD be recorded with severity `Error`.

     These errors are not expected and may indicate a bug in the application logic
     that this application instance was not able to recover from, or a gap in the error
     handling logic.

     Examples:

      - A background job terminates with an exception.
      - An HTTP framework error handler catches an exception thrown by the application code.

        Note: Some frameworks use exceptions as a communication mechanism when a request fails. For example,
        Spring users can throw a [ResponseStatusException](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/server/ResponseStatusException.html)
        exception to return an unsuccessful status code. Such exceptions represent errors already handled by the application code.
        Application code, in this case, is expected to log this at the appropriate severity.
        General-purpose instrumentation MAY record such errors, but at a severity not higher than `Warn`.

   - Errors that result in application shutdown SHOULD be recorded with severity `Fatal`.

     Examples:

      - The application detects an invalid configuration at startup and shuts down.
      - The application encounters a (presumably) terminal error, such as an out-of-memory condition.

6. When recording exceptions/errors in logs, applications and instrumentations are encouraged to add additional attributes
   to describe the context in which the exception/error has happened.
   They are also encouraged to define their own events and enrich them with exception/error details.

7. The OTel SDK SHOULD record exception stack traces on logs with severity `Error` or higher and drop
   then on logs with lower severity. It SHOULD allow users to change the threshold.

   See [logback exception config](https://logback.qos.ch/manual/layouts.html#ex) for an example of configuration that
   records stack traces conditionally.

8. Instrumentation libraries that record exceptions using span events SHOULD gracefully migrate
   to log-based exceptions following the migration path outlined in the [Span Event API deprecation plan OTEP](./4430-span-event-api-deprecation-plan.md).

## API changes

> [!NOTE]
>
> It should not be an instrumentation concern to decide whether an exception stack trace
> should be recorded or not.
>
> A natively instrumented library may write logs providing an exception instance
> through a log bridge and not be aware of this guidance.
>
> It also may be desirable for some vendors/apps to record all exception details at all levels.

The OTel Logs API SHOULD provide methods that enrich log records with exception details such as
`setException(exception)` and similar to the [RecordException](../specification/trace/api.md#record-exception) method on span.

The OTel SDK, based on the log severity and configuration, SHOULD record exception details fully or partially.

The signature of the method is to be determined by each language and can be overloaded
as appropriate.

It MUST be possible to efficiently set exception and error information on a log record based on configuration
and without using the `setException` method.

## SDK changes

TODO: we should consider if exception instances should reach log processing pipeline
where their processing can be customized or we'd rather do it via a separate concept like exception
customizer.

## Examples

### Logging errors from client library in a user application

```java
StorageClient client = createClient(endpoint, credential);
...
try {
    BinaryData content = client.download(contentId);

    return response(content, HttpStatus.OK);
} catch (ContentNotFoundException ex) {
    // we don't record exception here, but may record a log record without exception info
    logger.logRecordBuilder()
        .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
        // let's assume it's expected that some content can disappear
        .severityNumber(Severity.INFO)
        // by default SDK will only populate `exception.type` and `exception.message`
        // since severity is `INFO`, but it should not be an instrumentation library
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

### Logging errors inside the natively instrumented library

It's a common practice to record errors using logging libraries. Client libraries that are natively instrumented with OpenTelemetry should
leverage the OTel Events/Logs API for their exception logging purposes.

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
              // we'll retry it, so it's info or lower.
              // we'll write a warn for the overall operation if retries are exhausted.
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

### Logging errors in messaging processor

#### Natively instrumented library

In this example, application code provides the callback to the messaging processor to
execute for each message.

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
  // This natively instrumented library may use the OTel log API or another logging library such as slf4j.
  // Here we use Error severity since this exception was not handled by the application code.
  logger.atError()
    .addKeyValuePair("messaging.message.id", context.getMessageId())
    ...
    .setException(t)
    .log("Message processing failed");
  // error handling logic ...
}
```

If this instrumentation supports tracing, it should capture the error in the scope of the processing
span.

#### Instrumentation library

In this example, we leverage the Spring Kafka `RecordInterceptor` extensibility point that allows us to
listen to exceptions that remained unhandled.

```java
import org.springframework.kafka.listener.RecordInterceptor;
final class InstrumentedRecordInterceptor<K, V> implements RecordInterceptor<K, V> {
  ...

  @Override
  public void failure(ConsumerRecord<K, V> record, Exception exception, Consumer<K, V> consumer) {
    // we should capture this error in the scope of the processing span (or pass its context explicitly).
    logger.logRecordBuilder()
      .setSeverity(Severity.ERROR)
      .addAttribute("messaging.message.id", record.getId())
      ...
      .addException(ex)
      .setBody("Consumer error")
      .emit();
    // ..
  }
}
```

See the [corresponding Java (tracing) instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation/spring/spring-kafka-2.7/library/src/main/java/io/opentelemetry/instrumentation/spring/kafka/v2_7/InstrumentedRecordInterceptor.java) for details.

## Prototypes

TODO (at least prototype in the language that does not have exceptions).

## Prior art and alternatives

Alternatives:

1. Deduplicate exception info by marking exception instances as logged.
   This can potentially mitigate the problem for existing applications when they log exceptions extensively.
   We should still provide optimal guidance for greenfield applications and libraries,
   covering the wider problem of recording errors.

## Future possibilities

Exception stack traces can be recorded in structured form instead of their
string representation. It may be easier to process and consume them in this form.
This is out of scope for this OTEP.