# Recording exceptions and errors on logs

This OTEP provides guidance on how to record exceptions using OpenTelemetry logs focusing on minimizing duplication and providing context to reduce the noise.

## Motivation

Today OTel supports recording exceptions using span events available through Trace API. Outside of OTel world, exceptions are usually recorded by user apps and libraries using logging libraries and may be recorded as OTel logs via logging bridge.

Exceptions recorded on logs have the following advantages over span events:
- they can be recorded for operations that don't have any tracing instrumentation
- they can be sampled along with or separately from spans
- they can have different severity levels to reflect how critical the exception is
- they are already reported natively by many frameworks and libraries

Recording exception on logs is essential for troubleshooting. But regardless of how they are recorded, they could be noisy:
- distributed applications experience transient errors at the rate proportional to their scale and exceptions in logs could be misleading -
  individual occurrence of transient errors are not necessarily indicative of a problem.
- exception stack traces can be huge. Corresponding attribute value can frequently reach several KBs resulting in high costs
  associated with ingesting and storing such logs. It's also common to log exceptions multiple times while they bubble up
  leading to duplication and aggravating the verbosity problem.

In this OTEP, we'll provide guidance around recording exceptions that minimizes duplication, allows to reduce noise with configuration and
allows to capture exceptions in absence of a recorded span.

This guidance applies to general-purpose instrumentations including native ones. Application developers should consider following it as a starting point, but they are expected to adjust it to their needs.

## Guidance

This guidance boils down to the following:

- we should record full exception details including stack traces only for unhandled exceptions (by default).
- we should log error details and context when the error happens. These records don't need need to include exception stack traces unless this exception is unhandled.
- we should avoid logging the same error as it propagates up through the stack.
- we should log errors with appropriate severity ranging from `Trace` to `Fatal`.

> [!NOTE]
>
> Based on this guidance non-native instrumentations should record exceptions in top-level instrumentations only (#2 above)

### Details

1. Exceptions should be recorded as [logs](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-logs.md)
   or [log-based events](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md)

2. Instrumentations for incoming requests, message processing, background job execution, or others that wrap user code and usually create local root spans, should record logs
   for unhandled exceptions with `Error` severity and [`exception.escaped`](https://github.com/open-telemetry/semantic-conventions/blob/v1.29.0/docs/attributes-registry/exception.md) flag set to `true`.

    <!-- TODO: do we need an `exception.unhandled` attribute instead of `exception.escaped`? -->
   Some runtimes and frameworks provide global exception handler that can be used to record exception logs. Priority should be given to the instrumentation point where the operation context is available.

3. It's recommended to record exception stack traces only for unhandled exceptions in cases outlined in #2 above.

4. Native instrumentations should record log describing an error and the context it happened in
   when this error is detected. Corresponding log record should not contain exception stack
   traces (if an exception was thrown/caught) unless such exceptions usually remain unhandled.

5. An error should be logged with appropriate severity depending on the available context.

   - Error that don't indicate any issue should be recorded with severity not higher than `Info`.
   - Transient errors (even if it's the last try) should be recorded with severity not higher than `Warning`.
   - Unhandled exceptions that don't result in application shutdown should be recorded with severity `Error`
   - Errors that result in application shutdown should be recorded with severity `Fatal`

6. Instrumentations should not log errors or exceptions that are handled or
   are propagated as is, except ones handled in global exception handlers (see #2 below)

   If a new exception is created based on the original one or a new details about the error become available,
   instrumentation may record another error (without stack trace)

7. When recording exception on logs, user applications and instrumentations are encouraged to put additional attributes
   to describe the context that the exception was thrown in.
   They are also encouraged to define their own error events and enrich them with `exception.*` attributes.

## API changes

It should not be an instrumentation library concern to decide whether exception stack trace should be recorded or not.
Library may write logs providing exception instance through a log bridge and not be aware of this guidance.

It also maybe desirable by some vendors/apps to record all the exception details.

OTel Logs API should provide additional methods that enrich log record with exception details such as
`addException(exception)` (`addUnhandledException`, etc), similar to [RecordException](../specification/trace/api.md?plain=1#L682)
method on span.

OTel SDK should implement such methods and set exception attributes based on configuration
and in the optimal way. This would also provide a more scalable way to evolve this guidance
and extend configuration options if necessary.

### Examples

#### Catching exception from client library in a user application

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
        .severityNumber(Severity.INFO)
        // let's assume it's expected that some content can disappear
        .addAttribute(AttributeKey.stringKey("exception.type"), ex.getClass().getCanonicalName())
        .addAttribute(AttributeKey.stringKey("exception.message"), ex.getMessage())
         // ideally we should provide the following method for convenience, optimization,
         // and to support different behavior behind config options
         //.addException(ex)
        .emit();

    return response(HttpStatus.NOT_FOUND);
} catch (NotAuthorizedException ex) {
    // let's assume it's really unexpected - service lost access to the underlying storage
    // since we're returning error response without an exception, we
    logger.logRecordBuilder()
        .severityNumber(Severity.ERROR)
        .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
         // ideally we should provide the following method for convenience, optimization,
         // and to support different behavior behind config options
         //.addException(ex)
        .addAttribute(AttributeKey.stringKey("exception.type"), ex.getClass().getCanonicalName())
        .addAttribute(AttributeKey.stringKey("exception.message"), ex.getMessage())
        .emit();

    return response(HttpStatus.INTERNAL_SERVER_ERROR);
}
```

#### Recording error inside the library (native instrumentation)

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
            // we may set different levels depending on the status code, but in general
            // we expect caller to handle the error, so this is at most warning
            .setSeverity(Severity.WARN)
            .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
            .addAttribute(AttributeKey.stringKey("http.response.status_code"), response.statusCode())
            // ideally we should provide the following method for convenience, optimization,
            // and to support different behavior behind config options
            //.addException(ex)
            .addAttribute(AttributeKey.stringKey("exception.type"), ex.getClass().getCanonicalName())
            .addAttribute(AttributeKey.stringKey("exception.message"), ex.getMessage())
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
public class Connection {

    private final Logger logger;
    ...
    public long send(ByteBuffer content) {
        try {
            return socketChannel.write(content);
        } catch (Throwable ex) {
            logger.logRecordBuilder()
              // we'll retry it, so it's Info or lower
              .setSeverity(Severity.INFO)
              .addAttribute("connection.id", this.getId())
              .addAttribute(AttributeKey.stringKey("exception.type"), ex.getClass().getCanonicalName())
              .addAttribute(AttributeKey.stringKey("exception.message"), ex.getMessage())
              .emit();

            throw ex;
        }
    }
}
```

#### HTTP server instrumentation/global exception handler

TODO

## Trade-offs and mitigations

1. Breaking change for any component following existing [exception guidance](https://github.com/open-telemetry/opentelemetry-specification/blob/a265ae0628177be25dc477ea8fe200f1c825b871/specification/trace/exceptions.md) which recommends recording exceptions as span events in every instrumentation that detects them.

   **Mitigation:**
   - OpenTelemetry API and/or SDK in the future may provide opt-in span events -> log-based events conversion,
     but that's not enough - instrumentations will have to change their behavior to report exception logs
     with appropriate severity (or stop reporting them).
   - TODO: document opt-in mechanism similar to `OTEL_SEMCONV_STABILITY_OPT_IN`

1. Recording exceptions as log-based events would result in UX degradation for users
   leveraging trace-only backends such as Jaeger.

   **Mitigation:**
   - OpenTelemetry API and/or SDK may provide span events -> log events conversion.
     See also [Event vision OTEP](./0265-event-vision.md#relationship-to-span-events).

## Prior art and alternatives

Alternatives:

1. Deduplicate exception info on logs. We can mark exception instances as logged
   (augment exception instance or keep a small cache of recently logged exceptions).
   This can potentially mitigate the problem for existing application when it logs exceptions extensively.
   We should still provide optimal guidance for the greenfield applications and libraries.

2. Log full exception info only when exception is thrown for the first time
   (including new exceptions wrapping original ones). This results in at-most-once
   logging, but even this is known to be problematic since absolute majority of exceptions
   are handled.
   It also relies on the assumption that most libraries will follow this guidance.

## Open questions

TBD

## Future possibilities

1. OpenTelemetry should provide configuration options and APIs allowing (but not limited) to:

   - Record unhandled exceptions only (the default documented in this guidance)
   - Record exception info based on the log severity
   - Record exception logs, but omit the stack trace based on (at least) the log level.
     See [logback exception config](https://logback.qos.ch/manual/layouts.html#ex) for an example of configuration that records stack trace conditionally.
   - Record all available exceptions with all the details

   It should be possible to optimize instrumentation and avoid collecting exception information
   (such as stack trace) when the corresponding exception log is not going to be recorded.

2. Exception stack traces can be recorded in structured form instead of their
   string representation. It may be easier to process and consume them in this form.
