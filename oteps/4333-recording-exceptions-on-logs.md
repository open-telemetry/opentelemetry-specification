# Recording exceptions and errors on logs

<!-- toc -->

- [Motivation](#motivation)
- [Guidance](#guidance)
  * [Details](#details)
- [API changes](#api-changes)
- [Examples](#examples)
  * [Logging exception from client library in a user application](#logging-exception-from-client-library-in-a-user-application)
  * [Logging error inside the natively instrumented Library](#logging-error-inside-the-natively-instrumented-library)
  * [Logging errors in messaging processor](#logging-errors-in-messaging-processor)
    + [Natively instrumented library](#natively-instrumented-library)
    + [Instrumentation library](#instrumentation-library)
- [Trade-offs and mitigations](#trade-offs-and-mitigations)
- [Prior art and alternatives](#prior-art-and-alternatives)
- [Open questions](#open-questions)
- [Future possibilities](#future-possibilities)

<!-- tocstop -->

This OTEP provides guidance on how to record exceptions using OpenTelemetry logs focusing on minimizing duplication and providing context to reduce the noise.

## Motivation

Today OTel supports recording exceptions using span events available through Trace API. Outside of OTel world, exceptions are usually recorded by user apps and libraries using logging libraries and may be recorded as OTel logs via logging bridge.

Exceptions recorded on logs have the following advantages over span events:

- they can be recorded for operations that don't have any tracing instrumentation
- they can be sampled along with or separately from spans
- they can have different severity levels to reflect how critical the exception is
- they are already reported natively by many frameworks and libraries

Recording exceptions is essential for troubleshooting, but regardless of how exceptions are recorded, they could be noisy:

- distributed applications experience transient errors at the rate proportional to their scale and exceptions in logs could be misleading -
  individual occurrence of transient errors are not necessarily indicative of a problem.
- exception stack traces can be huge. Corresponding attribute value can frequently reach several KBs resulting in high costs
  associated with ingesting and storing them. It's also common to log exceptions multiple times while they bubble up
  leading to duplication and aggravating the verbosity problem.

In this OTEP, we'll provide guidance around recording exceptions that minimizes duplication, allows reducing noise with configuration, and
allows capturing exceptions in the absence of a recorded span.

This guidance applies to general-purpose instrumentations including native ones. Application developers should consider following it as a
starting point, but they are encouraged to adjust it to their needs.

## Guidance

This guidance boils down to the following:

Instrumentations SHOULD record exception information (along with other context) as a log record with appropriate severity.
Only unhandled exceptions SHOULD be recorded as `Error` or higher. Instrumentations SHOULD do the best effort to report
each exception once.

Instrumentations SHOULD provide the whole exception instance to the OTel SDK so it can
record it fully or partially based on provided configuration. The default SDK behavior SHOULD
be to record exception stack traces when logging exceptions at `Error` or higher severity.

In the long term, exceptions recorded on logs will replace span events (according to [Event vision OTEP](./0265-event-vision.md)).

### Details

1. Exceptions SHOULD be recorded as [logs](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-logs.md)
   or [log-based events](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md)

2. Instrumentations for incoming requests, message processing, background job execution, or others that wrap user code and usually
   create local root spans, SHOULD record logs for unhandled exceptions with `Error` severity.

   Some runtimes provide global exception handler that can be used to log exceptions.
   Priority should be given to the instrumentation point where the operation context is available.
   Language SIGs are encouraged to give runtime-specific guidance. For example, here is the
   [.NET guidance](https://github.com/open-telemetry/opentelemetry-dotnet/blob/610045298873397e55e0df6cd777d4901ace1f63/docs/trace/reporting-exceptions/README.md#unhandled-exception)
   for recording exceptions on traces.

3. Natively instrumented libraries SHOULD record a log describing an exception and the context it happened in
   as soon as the exception is detected (or where the most context is available).

4. It's NOT RECOMMENDED to record the same exception as it propagates through the stack frames, or
   to attach the same instance of an exception to multiple log records.

5. An exception (or error) SHOULD be logged with appropriate severity depending on the available context.

   - Exceptions or errors that don't indicate actual issues SHOULD be recorded with
     severity not higher than `Info`.

     Such exceptions can be used to control application logic and have a minor impact, if any,
     on application functionality, availability, or performance.

     Examples:

      - exception is thrown when checking optional dependency or resource existence.
      - exception thrown when client disconnects before reading full response from the server

   - Exceptions or errors that are expected to be retried or handled by the caller or another
     layer of the component SHOULD be recorded with severity not higher than `Warning`.

     Such exceptions represent transient failures that are common and expected in
     distributed applications. They typically increase the latency of individual
     operations and have a minor impact on overall application availability.

     Examples:

      - attempt to connect to the required remote dependency times out
      - remote dependency returns 401 "Unauthorized" response code
      - writing data to a file results in IO exception
      - remote dependency returned 503 "Service Unavailable" response for 5 times in a row,
        retry attempts are exhausted and the corresponding operation has failed.

   - Unhandled (by the user code) exceptions that don't result in application shutdown SHOULD
     be recorded with severity `Error`

     These exceptions are not expected and may indicate a bug in the application logic
     that this application instance was not able to recover from or a gap in the error
     handling logic.

     Examples:

      - Background job terminates with an exception
      - HTTP framework error handler catches exception thrown by the user code.

        Note: some frameworks use exceptions as a communication mechanism when request fails. For example,
        Spring users can throw [ResponseStatusException](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/server/ResponseStatusException.html)
        exception to return unsuccessful status code. Such exceptions represent errors already handled by the application code.
        Application code, in this case, is expected to logs error at appropriate severity and
        general-purpose instrumentation SHOULD NOT record such exceptions.

   - Exceptions or errors that result in application shutdown SHOULD be recorded with severity `Fatal`.

      - The application detects an invalid configuration at startup and shuts down.
      - The application encounters a (presumably) terminal error, such as an out-of-memory condition.

1. When recording exception on logs, user applications and instrumentations are encouraged to add additional attributes
   to describe the context that the exception was thrown in.
   They are also encouraged to define their own error events and enrich them with exception details.

2. OTel SDK SHOULD record stack traces on exceptions with severity `Error` or higher and SHOULD allow users to
   change the threshold.

   See [logback exception config](https://logback.qos.ch/manual/layouts.html#ex) for an example of configuration that
   records stack trace conditionally.

3. Instrumentation libraries that record exceptions using span events SHOULD gracefully migrate
   to log-based exceptions offering it as an opt-in feature first and then switching to log-based exceptions
   in the next major version update.

## API changes

> [!NOTE]
>
> It should not be an instrumentation concern to decide whether exception stack trace
> should be recorded or not.
>
> A natively instrumented library may write logs providing exception instance
> through a log bridge and not be aware of this guidance.
>
> It also may be desirable by some vendors/apps to record all exception details at all levels.

OTel Logs API SHOULD provide methods that enrich log record with exception details such as
`setException(exception)` and similar to [RecordException](../specification/trace/api.md#L682) method on span.

OTel SDK, based on the log severity and configuration, SHOULD record exception details fully or partially.

The signature of the method is to be determined by each language
and can be overloaded as appropriate including ability to collect and customize stack trace
collection.

It MUST be possible to efficiently set exception information on a log record without
using the `setException` method.

## Examples

### Logging exception from client library in a user application

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

### Logging error inside the natively instrumented Library

It's a common practice to record exceptions using logging libraries. Client libraries that are natively instrumented with OpenTelemetry should
leverage OTel Events/Logs API for their exception logging purposes.

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
            // In general we don't know if it's certainly an error - we expect caller
            // to handle the exception and decide. So this is warning (at most).
            // If it remains unhandled, it'd be logged by the global handler.
            .setSeverity(Severity.WARN)
            .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
            .addAttribute(AttributeKey.stringKey("http.response.status_code"), response.statusCode())
            .addException(ex)
            .emit();

        if (response.statusCode() == 404) {
            throw new ContentNotFoundException(readErrorInfo(response));
        }

        ...
    }
}
```

Network level errors are part of normal life, we should consider using low severity for them

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
              // we'll write a warn for overall operation if retries are exhausted.
              .setSeverity(Severity.INFO)
              .addAttribute("connection.id", this.getId())
              .addException(ex)
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

The `MessagingProcessorClient` implementation should catch exceptions thrown by the  `processMessage` callback and log them similarly to
this example:

```java
MessageContext context = retrieveNext();
try {
  processMessage.accept(context)
} catch (Throwable t) {
  // This natively instrumented library may use OTel log API or another logging library such as slf4j.
  // Here we use Error severity since this exception was not handled by the application code.
  logger.atError()
    .addKeyValuePair("messaging.message.id", context.getMessageId())
    ...
    .setException(t)
    .log();
  // error handling logic ...
}
```

If this instrumentation supports tracing, it should capture the error in the scope of the processing
span.

#### Instrumentation library

In this example we leverage Spring Kafka `RecordInterceptor` extensibility point that allows to
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
      .emit();
    // ..
  }
}
```

See [corresponding Java (tracing) instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation/spring/spring-kafka-2.7/library/src/main/java/io/opentelemetry/instrumentation/spring/kafka/v2_7/InstrumentedRecordInterceptor.java) for the details.

## Trade-offs and mitigations

1. Breaking change for any component following existing [exception guidance](/specification/trace/exceptions.md) which recommends recording exceptions as span events in every instrumentation that detects them.

   **Mitigation:**
   - OpenTelemetry API and/or SDK in the future may provide opt-in span events -> log-based events conversion,
     but that's not enough - instrumentations will have to change their behavior to report exception logs
     with appropriate severity (or stop reporting them).
   - We should provide opt-in mechanism for existing instrumentations to switch to logs.

2. Recording exceptions as log-based events would result in UX degradation for users
   leveraging trace-only backends such as Jaeger.

   **Mitigation:**
   - OpenTelemetry API and/or SDK may provide span events -> log events conversion.
     See also [Event vision OTEP](./0265-event-vision.md#relationship-to-span-events).

## Prior art and alternatives

Alternatives:

1. Deduplicate exception info by marking exception instances as logged.
   This can potentially mitigate the problem for existing application when it logs exceptions extensively.
   We should still provide optimal guidance for the greenfield applications and libraries.

2. Log full exception info only when exception is thrown for the first time.
   This results in at-most-once logging, but even this is known to be problematic since absolute
   majority of exceptions are handled.
   It also relies on the assumption that most libraries will follow this guidance.

## Open questions

- Do we need to have log-related limits similar to [span event limits](/specification/trace/sdk.md#span-limits)
  on the SDK level?

## Future possibilities

Exception stack traces can be recorded in structured form instead of their
string representation. It may be easier to process and consume them in this form.
This is out of scope of this OTEP.
