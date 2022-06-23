## Events and Logs API Interface

For reference, a prototype of the Events and Logs API in Java is [here](https://github.com/scheler/opentelemetry-java/pull/1/files)

Client-side telemetry is one of the initial clients that will use the Events API and so the API will be made available in JavaScript, Java and Swift first to be able to use in the SDKs for Browser, Android and iOS.  It may also be added in Go since there is a Kubernetes events receiver implemented in Collector based on Logs data-model.

The Events and Logs API consist of these main classes:

* LoggerProvider is the entry point of the API. It provides access to Loggers.
* Logger is the class responsible for creating events using Log records.

LoggerProvider/Logger are analogous to TracerProvider/Tracer.

![Events and Logs API classes](img/-events-and-logs-api.png)

### LoggerProvider

Logger can be accessed with an LoggerProvider.

In implementations of the API, the LoggerProvider is expected to be the stateful object that holds any configuration. (Note: The SDK implementation of this is what we currently call the [LogEmitterProvider](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/logging-library-sdk.md#logemitterprovider))

Normally, the LoggerProvider is expected to be accessed from a central place. Thus, the API SHOULD provide a way to set/register and access a global default LoggerProvider.

Notwithstanding any global LoggerProvider, some applications may want to or have to use multiple LoggerProvider instances, e.g. to have different configuration (like LogRecordProcessors) for each (and consequently for the Loggers obtained from them), or because it's easier with dependency injection frameworks. Thus, implementations of LoggerProvider SHOULD allow creating an arbitrary number of instances.

#### LoggerProvider operations

The LoggerProvider MUST provide the following functions:

* Get an Logger

##### Get an Logger

This API MUST accept the following parameters that determine the scope for the `Logger` returned. Most of these are common with the scope parameters for `Tracer` and `Meter`, except for `event_domain` and `include_trace_context` which is specific to `Logger`.

- `name` (required): This name SHOULD uniquely identify the [instrumentation scope](../glossary.md#instrumentation-scope), such as the [instrumentation library](../glossary.md#instrumentation-library) (e.g. `io.opentelemetry.contrib.mongodb`), package, module or class name.  If an application or library has built-in OpenTelemetry instrumentation, both [Instrumented library](../glossary.md#instrumented-library) and [Instrumentation library](../glossary.md#instrumentation-library) may refer to the same library. In that scenario, the `name` denotes a module name or component name within that library or application. In case an invalid name (null or empty string) is specified, a working Logger implementation MUST be returned as a fallback rather than returning null or throwing an exception, its `name` property SHOULD be set to an empty string, and a message reporting that the specified value is invalid SHOULD be logged. A library implementing the OpenTelemetry API may also ignore this name and return a default instance for all calls, if it does not support "named" functionality (e.g. an implementation which is not even observability-related). A LoggerProvider could also return a no-op Logger here if application owners configure the SDK to suppress telemetry produced by this library.

- `version` (optional): Specifies the version of the instrumentation scope if the scope has a version (e.g. a library version). Example value: 1.0.0.
- `schema_url` (optional): Specifies the Schema URL that should be recorded in the emitted telemetry
- `event_domain` (optional): Specifies the domain for the events created, which should be added in the attribute `event.domain` in the instrumentation scope.
- `include_trace_context` (optional): Specifies whether the Trace Context should automatically be passed on to the events and logs created by the Logger. This SHOULD be false by default.
- `attributes` (optional): Specifies the instrumentation scope attributes to associate with emitted telemetry.

Implementations MUST return different `Logger` instances when called repeatedly with different values of parameters. Note that always returning a new `Logger` instance is a valid implementation. The only exception to this rule is the no-op `Logger`: implementations MAY return the same instance regardless of parameter values.

Implementations MUST NOT require users to repeatedly obtain an Logger again with the same name+version+schema_url+event_domain+include_trace_context+attributes to pick up configuration changes. This can be achieved either by allowing to work with an outdated configuration or by ensuring that new configuration applies also to previously returned Loggers.

Note: This could, for example, be implemented by storing any mutable configuration in the LoggerProvider and having Logger implementation objects have a reference to the LoggerProvider from which they were obtained. If configuration must be stored per-Logger (such as disabling a certain Logger), the Logger could, for example, do a look-up with its name+version+schema_url+event_domain+include_trace_context+attributes in a map in the LoggerProvider, or the LoggerProvider could maintain a registry of all returned Loggers and actively update their configuration if it changes.

The effect of associating a Schema URL with a Logger MUST be that the telemetry emitted using the Logger will be associated with the Schema URL, provided that the emitted data format is capable of representing such association.

### Logger

The Logger is responsible for creating Events and Logs.

Note that Loggers should not be responsible for configuration. This should be the responsibility of the LoggerProvider instead.

#### Logger operations

The Logger MUST provide functions to:

- Create an `Event` and emit it to the processing pipeline.
  - The API MUST accept an event name as a parameter. The event name provided should be inserted as an attribute with key `event.name`. Care MUST be taken to not override or delete this attribute while the `Event` is created.  This function MAY be named `logEvent`.
- Create a `Log Record` and emit it to the processing pipeline.
  - This function MAY be named `logRecord`.
  - The intended users of this API is Log Appenders.

### Usage

```java
OpenTelemetry openTelemetry = OpenTelemetry.noop();
Logger logger = openTelemetry.getLogger("my-scope");

// Using the convenience method to log an event directly
logger.logEvent("network-changed", 
                 Attributes.builder().put("type", "wifi").build());

// Using the event builder to log an event
logger.eventBuilder("page-navigated").build().setAttribute("url", "http://foo.com/bar#new").emit();

// Using the logRecord builder to log a record
Logger logger = openTelemetry.getLogger("another-scope");
logger.logRecordBuilder().build().setBody("I am a log message").emit();

```

### Usage in Client-side telemetry

Some Events in a browser application occur when there is no span in progress, for example, errors, user interaction events and web-vitals. They can be recorded as standalone Events as follows.

```java
public void addBrowserEvent(String name, Attributes attributes) {
   Logger logger = openTelemetry.getLogger("my-scope", "1.0", "browser");
   logger.logEvent(name, attributes);
}

public void addMobileEvent(String name, Attributes attributes) {
   Logger logger = openTelemetry.getLogger("my-scope", "1.0", "mobile");
   logger.logEvent(name, attributes);
}
```

## Semantic Convention for event attributes

We introduce the concept of an event domain as a mechanism to avoid conflicts with event names.

**type:** `event`

**Description:** Event attributes.

| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `event.name` | string | Name or type of the event. | `network-change`; `button-click`; `exception` | Yes |
| `event.domain` | string | Domain or scope for the event. | `profiling`; `browser`, `db`, `k8s` | No |

An `event.name` is supposed to be unique only in the context of an `event.domain`, so this allows for two events in different domains to have same `event.name`, yet be unrelated events. No claim is made about the uniqueness of `event.name`s in the absence of `event.domain`.

Note that Scope attributes are equivalent to the attributes at Span and LogRecord level, so recording the attribute `event.domain` on the Scope is equivalent to recording it on Spans and LogRecords within the Scope.

## Causality on Events

It is sometimes desired to indicate one event led to another. Since spans in a trace are better suited to represent causality, we can create wrapper spans to represent causality between events. Note that the events themselves are represented using LogRecords and not as Span Events.

```java

Logger logger = openTelemetry.getLogger("my-scope", "1.0", "mobile", /* include_trace_context */ true);

Span span1 = tracer.spanBuilder(event1).startSpan();
    logger.logEvent(event1, attributes)
    Span span2 = tracer.spanBuilder(event2).startSpan();
        logger.logEvent(event2, attributes)
    span2.end()
span1.end()
```

## Comparing with Span Events

- Span Events are events recorded within spans using Trace API. It is not possible to create standalone Events using Trace API. The Events API must be used instead.
- Span Events were added in the Trace spec when Logs spec was in early stages. Ideally, Events should only be recorded using LogRecords and correlated with Spans by adding Span Context in the LogRecords. However, since Trace API spec is stable Span Events MUST continue to be supported.
- We may add a configuration option to the `TracerProvider` to create LogRecords for the Span Events and associate them with the Span using Span Context in the LogRecords. Note that in this case, if a noop TracerProvider is used it will not produce LogRecords for the Span Events.

