# Recording exceptions and errors with OpenTelemetry

This OTEP provides guidance on how to record exceptions using OpenTelemetry logs focusing on minimizing duplication and providing context to reduce the noise.

## Motivation

OTel recommends recording exceptions using span events available through Trace API. Outside of OTel world, exceptions are usually recorded by user apps and libraries using logging libraries.

Log-based exception events have the following advantages over span events:
- they can be recorded for operations that don't have any tracing instrumentation
- they can be sampled along with or separately from spans
- they can have different severity levels to reflect how critical the exception is
- they are already reported natively by many frameworks and libraries

Exception events are essential for troubleshooting. Regardless of how they are recorded, they could be noisy:
- distributed applications experience transient errors at the rate proportional to their scale and exceptions in logs could be misleading - individual occurrence of transitive errors are not indicative of any problems.
- exception events can be huge due to stack traces. They can frequently reach several KBs resulting in high costs associated with ingesting and storing exception events. It's also common to log exceptions multiple times while they bubble up leading to duplication and aggravating verbosity problem.

In this OTEP, we'll provide the guidance around recording exceptions that minimizes duplication, allows to reduce noise with configuration and capture exceptions in absence of a recorded span.

This guidance applies to general-purpose instrumentations including native ones. Application developers should consider following it as a starting point, but they are expected to adjust it to their needs.

## Guidance

1. Exceptions should be recorded as [log-based `exception` events](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-logs.md)

   This rule ensures that exception events can be recorded independently from traces and cover cases when no span exists,
   or when the corresponding span is not recorded.

2. Exception event should be logged with appropriate severity depending on the available context.

   - Exceptions that don't indicate any issue should be recorded with severity not higher than `Info`.
   - Transient errors (even if it's the last try) should be recorded with severity not higher than `Warning`.

   This rule enables typical log level mechanisms to control exception event volume.

3. Exception event should be recorded when the exception instance is created and thrown for the first time.
   This includes new exception instances that wrap other exception(s).

   This rule ensures that exception event is recorded at least once for each exception thrown.

4. Exception events should not be recorded when exception is handled or rethrown as is, except the following cases:
   - exceptions handled in global exception handlers (see p5 below)
   - exceptions from the code that doesn't record exception events in the compatible with OTel way.

   This rule ensures that exception event is recorded at most once for each *handled* exception.

5. Instrumentations for incoming requests, message processing, background job execution, or others that wrap user code and usually create local root spans, should record exception events for unhandled exceptions with `Error` severity and [`exception.escaped`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/attributes-registry/exception.md#exception-escaped) flag set to `true`.

   Some runtimes and frameworks provide global exception handler which could be used to record exception events. The priority should be given to the instrumentation point where the operation context is available.

    <!-- TODO: do we need an `unhandled` attribute instead of `exception.escaped`? -->

   This allows to record unhandled exception with proper severity and distinguish them from handled ones.

6. User applications and instrumentations are encouraged to put additional attributes on exception events to describe the context exception was thrown in. They are also encouraged to define their own error events and enrich them with `exception.*` attributes.

### Log configuration scenarios

OpenTelemetry SDK should provide configuration options allowing (but not limited to):

- Record unhandled exceptions only
- Record exceptions based on the log severity
- Record exception events, but omit the stack trace based on (at least) the log level. It should be possible to optimize instrumentation and avoid collecting the attribute. See [logback exception config](https://logback.qos.ch/manual/layouts.html#ex) for an example of configuration that records stack trace conditionally.
- Record all available exceptions with all the details

### Examples

#### Catching exception from client library call

If underlying client library is already recording exceptions using OTel-compatible logger facade, the caller should not record exception event.

```java
StorageClient client = createClient(endpoint, credential);
...
try {
    // let's assume that the underlying client library is already
    // recording exceptions using OTel-compatible logger facade.
    BinaryData content = client.download(contentId);

    return response(content, HttpStatus.OK);
} catch (ContentNotFoundException ex) {
    // we don't record exception here, but may record a log record without exception info
    logger.logRecordBuilder()
        // let's assume it's expected that some content can disappear
        .severityNumber(Severity.INFO)
        .addAttribute(AttributeKey.stringKey("error.type"), ex.getClass().getCanonicalName())
        .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
        .emit();

    return response(HttpStatus.NOT_FOUND);
} catch (NotAuthorizedException ex) {
    // let's assume it's really unexpected - service lost access to the underlying storage
    logger.logRecordBuilder()
        .severityNumber(Severity.ERROR)
        .addAttribute(AttributeKey.stringKey("error.type"), ex.getClass().getCanonicalName())
        .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
        .emit();

    return response(HttpStatus.INTERNAL_SERVER_ERROR);
}
```

#### Recording exceptions inside the library (native instrumentation)

It's a common practice to record exceptions using logging libraries. Client libraries that are natively instrumented with OpenTelemetry should
leverage OTel Events/Logs API for their logging purposes.

```java
public class MyClient {

    private final Logger logger;
    ...
    public BinaryData getContent(String contentId) {

        // let's assume as have logging interceptor in our
        // http client pipeline and exception are logged there
        // or HTTP client already records exceptions using logger
        // supported by OTel
        HttpResponse response = client.get(contentId);
        if (response.statusCode == 200) {
            return readContent(response);
        }

        MyClientException ex = new MyClientException(response.statusCode(), readErrorInfo(response));

        logger.eventBuilder("exception")
            .setSeverity(Severity.INFO)
            .addAttribute(AttributeKey.stringKey("com.example.content.id"), contentId)
            .addAttribute(AttributeKey.stringKey("exception.type"), ex.getClass().getCanonicalName())
            .addAttribute(AttributeKey.stringKey("exception.name"), ex.getMessage())
            .addAttribute(AttributeKey.stringKey("exception.stacktrace"), getStackTrace(ex))
            .emit();
    }
}
```

Some libraries or runtimes don't record exception logs or record them in ways that are not compatible with OpenTelemetry. In this case, it's recommended to
record exception event when the exception is rethrown.

```java
public class Connection {

    private final Logger logger;
    ...
    public long send(ByteBuffer content) {
        try {
            return socketChannel.write(content);
        } catch (Throwable ex) {
            // we're rethrowing an exception here since the underlying
            // platform code may or may not record exception logs depending on JRE,
            // configuration, and other implementation details
            logger.eventBuilder("exception")
              .setSeverity(Severity.INFO)
              .addAttribute("connection.id", this.getId())
              .addAttribute(AttributeKey.stringKey("exception.type"), ex.getClass().getCanonicalName())
              .addAttribute(AttributeKey.stringKey("exception.name"), ex.getMessage())
              .addAttribute(AttributeKey.stringKey("exception.stacktrace"), getStackTrace(ex))
              .emit();

            throw ex;
        }
    }
}
```

#### HTTP server instrumentation

TODO

## Trade-offs and mitigations

1. Breaking change to existing [exception guidance](https://github.com/open-telemetry/opentelemetry-specification/blob/a265ae0628177be25dc477ea8fe200f1c825b871/specification/trace/exceptions.md) which recommends recording exceptions as span events in every instrumentation that detects them.

   **Mitigation:**
   - OpenTelemetry API and/or SDK in the future may provide opt-in span events -> log events conversion, but that's not enough - instrumentations will have to change their behavior to report exception events with appropriate severity (or stop reporting exceptions).
   - TODO: document opt-in mechanism similar to `OTEL_SEMCONV_STABILITY_OPT_IN`

2. Recording exceptions as log-based events would result in UX degradation for users leveraging trace-only backends such as Jaeger.

   **Mitigation:**
   - OpenTelemetry API and/or SDK in the future may provide span events -> log events conversion. See also [Event vision OTEP](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0265-event-vision.md#relationship-to-span-events).

## Prior art and alternatives

Alternatives:

1. Record exceptions only when exception is handled (or remains unhandled). This relies on the user applications to log them correctly and consistently, it also makes it impossible to add context available deep in the stack when exception happens.
2. Record exception events whenever exception is detected (even if exception is handled or rethrown), use additional attributes and/or severity so that it can be filtered out by the processing pipeline. This OTEP does not prevent evolution in this direction.
3. (Variation of 2) Exception stack traces are the most problematic in terms of volume. We can record exception type and message whenever caller feels like recording exception event. This OTEP does not prevent evolution in this direction.
4. OTel may deduplicate exception events and mark exception instances as logged (augment exception instance or keep a small cache of recently logged exceptions). This can potentially mitigate the problem for existing application when it and its dependencies log exceptions extensively. It does not though help with guidance for the greenfield applications and libraries.

## Open questions

1. This OTEP assumes that client libraries (in general) are already instrumented with logs natively. It's valid for some environments (e.g. .NET, Java, Python, ?) which have standard or widely used structured logging libraries. Are there environments where it's not the case?
   - E.g. in JS it's not common to depend on the logging lib.

## Future possibilities

1. OpenTelemetry API should be extended to provide convenience methods to
   - record log-based event from exception instance
   - attach exception information to any event or log

2. Log-based events allow to capture exception stack trace as structured event body instead of a string attribute. It can be easier to process and consume exception events with structured stack traces.
