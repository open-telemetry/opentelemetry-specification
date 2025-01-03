# Recording exceptions and errors on logs

<!-- toc -->

- [Motivation](#motivation)
- [Guidance](#guidance)
  * [Details](#details)
- [API changes](#api-changes)
- [Examples](#examples)
  * [Logging exception from client library in a user application](#logging-exception-from-client-library-in-a-user-application)
  * [Logging error inside the library (native instrumentation)](#logging-error-inside-the-library-native-instrumentation)
  * [Logging errors in messaging processor](#logging-errors-in-messaging-processor)
    + [Native instrumentation](#native-instrumentation)
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

In this OTEP, we'll provide guidance around recording exceptions that minimizes duplication, allows to reduce noise with configuration and
allows to capture exceptions in absence of a recorded span.

This guidance applies to general-purpose instrumentations including native ones. Application developers should consider following it as a
starting point, but they are encouraged to adjust it to their needs.

## Guidance

This guidance boils down to the following:

Instrumentations should record exception information (along with other context) on the log record and
use appropriate severity - only unhandled exceptions should be recorded as `Error` or higher. Instrumentations
should strive to report each exception once.

Instrumentations should provide the whole exception instance to the OTel SDK (instead of individual attributes)
and the SDK should, based on configuration, decide which information to record. As a default,
this OTEP proposes to record exception stack traces on logs with `Error` or higher severity.

### Details

1. Exceptions should be recorded on [logs](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-logs.md)
   or [log-based events](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md)

2. Instrumentations for incoming requests, message processing, background job execution, or others that wrap user code and usually create local root spans, should record logs
   for unhandled exceptions with `Error` severity.

    > [!NOTE]
    >
    > Only top-level instrumentations (native and non-native) should record exceptions at `Error` (or higher) severity.

   Some runtimes provide global exception handler that can be used to log exceptions.
   Priority should be given to the instrumentation point where the operation context is available.
   Language SIGs are encouraged to give runtime-specific guidance. For example, here is the
   [.NET guidance](https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/docs/trace/reporting-exceptions#unhandled-exception)
   for recording exceptions on traces.

3. Native instrumentations should record log describing an error and the context it happened in
   when this error is detected (or where the most context is available).

4. It's not recommended to record the same error as it propagates through the stack trace or
   attach the same instance of exception to multiple log records.

5. An error should be logged with appropriate severity depending on the available context.

   - Errors that don't indicate any issue should be recorded with severity not higher than `Info`.
   - Transient errors (even if it's the last try) should be recorded with severity not higher than `Warning`.
   - Unhandled exceptions that don't result in application shutdown should be recorded with severity `Error`
   - Errors that result in application shutdown should be recorded with severity `Fatal`.

6. When recording exception on logs, user applications and instrumentations are encouraged to put additional attributes
   to describe the context that the exception was thrown in.
   They are also encouraged to define their own error events and enrich them with exception details.

7. OTel SDK should record stack traces on exceptions with severity `Error` or higher and should allow users to
   change the threshold.

   See [logback exception config](https://logback.qos.ch/manual/layouts.html#ex) for an example of configuration that
   records stack trace conditionally.

## API changes

> [!IMPORTANT]
>
> OTel should provide API like `setException` when creating log record that will record only necessary information depending
> on the configuration and log severity.

It should not be an instrumentation library concern to decide whether exception stack trace should be recorded or not.
Library may write logs providing exception instance through a log bridge and not be aware of this guidance.

It also maybe desirable by some vendors/apps to record all exception details at all levels.

OTel Logs API should provide methods that enrich log record with exception details such as
`setException(exception)` similar to [RecordException](../specification/trace/api.md?plain=1#L682)
method on span.

OTel SDK should implement such methods and set exception attributes based on configuration
and in the optimal way. This would also provide a more scalable way to evolve this guidance
and extend configuration options if necessary.

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

### Logging error inside the instrumented Library (native instrumentation)

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

#### Native instrumentation

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
  // This native instrumentation may use OTel log API or another logging library such as slf4j.
  // Here we use Error severity since this exception was not handled by the application code.
  logger.atError()
    .addKeyValuePair("messaging.message.id", context.getMessageId())
    ...
    .setException(t)
    .log();
  // error handling logic ...
}
```

If native instrumentation supports tracing, it should capture the error in the scope of the processing
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

1. Breaking change for any component following existing [exception guidance](https://github.com/open-telemetry/opentelemetry-specification/blob/a265ae0628177be25dc477ea8fe200f1c825b871/specification/trace/exceptions.md) which recommends recording exceptions as span events in every instrumentation that detects them.

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
