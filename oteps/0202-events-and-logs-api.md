# Introducing Events and Logs API

We introduce an Events and Logs API that is based on the OpenTelemetry Log signal, backed by LogRecord data model and LogEmitter SDK.

## Motivation

In OpenTelemetry's perspective Log Records and Events are different names for the same concept - however, there is a subtle difference in how they are represented using the underlying data model that is described below. We will describe why the existing Logging APIs are not sufficient for the purpose of creating events.  It will then be evident that we will need an API in OpenTelementry for creating events. Note that the Events here refer to standalone Events and not to be confused with Span Events which occur only in the context of a span.

The Logs part of the API introduced here is supposed to be used only by the Log Appenders and end-users should continue to use the logging APIs available in the languages.

### Subtle differences between Logs and Events

Logs have a mandatory severity level as a first-class parameter that events do not have, and events have a mandatory name that logs do not have. Further, logs typically have messages in string form and events have data in the form of key-value pairs. It is due to this that their API interface requirements are slightly different.

### Who requires Events API

Here are a few situations that require recording of Events, there will be more.  Note that the Trace API provides capability to record Events but that is only when a span is in progress. We need a separate API for recording standalone Events.

- RUM events (Client-side instrumentation)
  - Standalone events that occur when there is no span in progress, such as errors, user interaction events and web vitals.
- Recording kubernetes events
- Collector Entity events [link](https://docs.google.com/document/d/1Tg18sIck3Nakxtd3TFFcIjrmRO_0GLMdHXylVqBQmJA/edit)
- Few other event systems described in [example mappings](../specification/logs/data-model-appendix.md#appendix-a-example-mappings) in the data model.

### Can the current Log API interfaces be used for events?

- The log level is fundamental to the Log APIs in almost all the languages; all the methods in the Log interface are named after the log level, and there is usually no generic method to submit a log entry without log level.
  - In JavaScript for Web, the standard method of logging is to use console.log. Events can be created using [Event/CustomEvent](https://developer.mozilla.org/en-US/docs/Web/Events/Creating_and_triggering_events) interfaces. However, there is no option to define custom destination for these logs and events. Logs go only to console and event listeners are attached to the DOM element that dispatches it.
  - In Android, android.util.Log has methods  Log.v(), Log.d(), Log.i(), Log.w(), and Log.e() to write logs. These methods correspond to the severity level.
  - Swift on iOS has Logger interface that has methods corresponding to severity level too.
- The current Log APIs do not have a standard way to pass event attributes.
  - It may be possible to use the interpolation string args as the parameter to pass event attributes. However, the logging spec seems to map the human readable message (which is obtained after replacing the args in the interpolated string) to the Body field of LogRecord.
  - Log4j has an EventLogger interface that can be used to create structured messages with arbitrary key-value pairs, but log4j is not commonly used in Android apps as it is not officially supported on Android as per this [Stack Overflow thread](https://stackoverflow.com/questions/60398799/disable-log4j-jmx-on-android/60407849#60407849) by one of log4j’s maintainers.
  - In Python, logging.LogRecord's extra field is mapped to Otel LogRecord's attributes but this field is a hidden field and not part of the public interface.
- The current Log APIs have a message parameter which could map to the Body field of LogRecord. However, this is restricted to String messages and does not allow for structured logs.

For the above reasons we can conclude that we will need an API for creating Events.

## Explanation

We propose a structure for Events for the purpose of distinguishing them from Logs and also propose having an API to ensure the structure is followed when creating Events using `LogRecord` data model.

### Events structure

All Events will have a name and a domain. The name is MANDATORY. The domain will serve as a mechanism to avoid conflicts with event names and is OPTIONAL. With this structure, an event name will be unique only in the context of a domain. It allows for two events in different domains to have same name, yet be unrelated events. When the domain is not present in an Event no claim is made about the uniqueness of event name.

### Events and Logs API

We also propose having an API interface for creating Events and Logs. Currently, there is only an SDK called [LoggerProvider](../specification/logs/sdk.md#loggerprovider) for creating `LogRecord`s.

However, there is a question of whether OTel should have an API for logs. A part of the OTel community thinks that we should not have a full-fledged logging API unless there is a language that doesn't already have a plethora of logging libraries and APIs to choose from where it might make sense to define one. Further, we will not be able to have the [rich set of configuration options](https://logging.apache.org/log4j/2.x/manual/configuration.html) that some popular logging frameworks provide so the logging API in OTel will only become yet another API. However, it was noted that the Log Appender API is very similar to the API for Events and so instead of having API for Events and API for Log Appenders separately it was agreed to have one API for Events and Logs, and that the API for Logs is targeted only to Log Appenders. This will also keep it consistent with Traces and Metrics in having one API for each signal.

## Internal Details

The event name and domain will be attributes in the `LogRecord` defined using semantic conventions.

For the Events and Logs API, it will be very similar to the Trace API. There will be LoggerProvider and Logger interfaces analogous to TracerProvider and Tracer. The Logger interface will then be used to create Events and Logs using the LogRecord data model.

## Trade-offs and mitigations

There could be confusion on whether the Logs part of the API is end-user callable. While it can eventually be used in the languages that do not have a popular logging library, it is not recommended to be used in the languages where there are other popular logging libraries and APIs and this fact must emphasized in different forums.

## Prior art and alternatives

For client-side instrumentation, it was suggested initially that we use 0-duration spans to represent Events to get the benefit of Spans providing causality. For example, Splunk's RUM sdk for Android implements Events using [0-duration span](https://github.com/signalfx/splunk-otel-android/blob/3ca8584632f334671fdb6eaa09199ce01961787f/splunk-otel-android/src/main/java/com/splunk/rum/SplunkRum.java#L213). However, 0-duration spans are confusing and not consistent with standalone Events in other domains which are represented using `LogRecord`s.  Hence, for consistency reasons it will be good to use `LogRecord`s for standalone Events everywhere. To address the requirement of modeling causality between Events, we can create wrapper spans linked to the `LogRecord`s.

## Open questions

None.

## Future possibilities

1. As noted in the `Trade-offs and mitigation` section, we could allow the API to be used by end-users in the languages that do not have a popular logging library.
2. There is a possibility that we may want to record the Span Events using `LogRecord`s in future. In this case, they will be correlated wth the Spans using the `TraceId` and `SpanId` fields of the `LogRecord`. If this is desired, we may add a configuration option to the `TracerProvider` to create LogRecords for the Span Events.
