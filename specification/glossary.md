# Glossary

Below are a list of some OpenTelemetry specific terms that are used across this
specification.

## Common

<a name="in-band"></a>
<a name="out-of-band"></a>
### In-band and Out-of-band Data

> In telecommunications, **in-band signaling** is the sending of control information within the same band or channel used for data such as voice or video. This is in contrast to **out-of-band signaling** which is sent over a different channel, or even over a separate network ([Wikipedia](https://en.wikipedia.org/wiki/In-band_signaling)).

In OpenTelemetry we refer to **in-band data** as data that is passed
between components of a distributed system as part of business messages,
for example, when trace or correlation contexts are included
in the HTTP requests in the form of HTTP headers.
Such data usually does not contain the telemetry,
but is used to correlate and join the telemetry produced by various components.
The telemetry itself is referred to as **out-of-band data**:
it is transmitted from applications via dedicated messages,
usually asynchronously by background routines
rather than from the critical path of the business logic.
Metrics, logs, and traces exported to telemetry backends are examples of out-of-band data.

<a name="telemetry_sdk"></a>
### Telemetry SDK

Denotes the library that implements the *OpenTelemetry API*.

See [Library Guidelines](library-guidelines.md#sdk-implementation) and
[Library resource semantic conventions](resource/semantic_conventions/README.md#telemetry-sdk).

<a name="exporter_library"></a>
### Exporter Library

Libraries which are compatible with the [Telemetry SDK](#telemetry-sdk) and provide functionality to emit telemetry to consumers.

### Instrumented Library

Denotes the library for which the telemetry signals (traces, metrics, logs) are gathered.

The calls to the OpenTelemetry API can be done either by the Instrumented Library itself,
or by another [Instrumentation Library](#instrumentation-library).

Example: `org.mongodb.client`.

<a name="instrumenting_library"></a>
<a name="instrumentation_library"></a>
### Instrumentation Library

Denotes the library that provides the instrumentation for a given [Instrumented Library](#instrumented-library).
*Instrumented Library* and *Instrumentation Library* may be the same library
if it has built-in OpenTelemetry instrumentation.

See [Overview](overview.md#instrumentation-libraries) for a more detailed definition and naming guidelines.

Example: `io.opentelemetry.contrib.mongodb`.

Synonyms: *Instrumenting Library*.

<a name="tracer-name"></a>
<a name="meter-name"></a>
### Tracer Name / Meter Name

This refers to the `name` and (optional) `version` arguments specified when
creating a new `Tracer` or `Meter` (see [Obtaining a Tracer](trace/api.md#tracerprovider)/[Obtaining a Meter](metrics/api.md#meter-interface)).
The name/version pair identifies the [Instrumentation Library](#instrumentation-library).

## Logs

### Log Record

A recording of an event. Typically the record includes a timestamp indicating
when the event happened as well as other data that describes what happened,
where it happened, etc.

Synonyms: *Log Entry*.

### Log

Sometimes used to refer to a collection of Log Records. May be ambiguous, since
people also sometimes use `Log` to refer to a single `Log Record`, thus this
term should be used carefully and in the context where ambiguity is possible
additional qualifiers should be used (e.g. `Log Record`).

### Embedded Log

`Log Records` embedded inside a [Span](trace/api.md#span)
object, in the [Events](trace/api.md#add-events) list.

### Standalone Log

`Log Records` that are not embedded inside a `Span` and are recorded elsewhere.

### Log Attributes

Key/value pairs contained in a `Log Record`.

### Structured Logs

Logs that are recorded in a format which has a well-defined structure that allows
to differentiate between different elements of a Log Record (e.g. the Timestamp,
the Attributes, etc). The _Syslog protocol_ ([RFC 5425](https://tools.ietf.org/html/rfc5424)),
for example, defines a `structured-data` format.

### Flat File Logs

Logs recorded in text files, often one line per log record (although multiline
records are possible too). There is no common industry agreement whether
logs written to text files in more structured formats (e.g. JSON files)
are considered Flat File Logs or not. Where such distinction is important it is
recommended to call it out specifically.
