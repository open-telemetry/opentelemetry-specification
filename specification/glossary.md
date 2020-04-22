# Glossary

Below are a list of some OpenTelemetry specific terms that are used across this
specification.

## Common

### Telemetry SDK

Denotes the library that implements the *OpenTelemetry API*.

See [Library Guidelines](library-guidelines.md#sdk-implementation) and
[Library resource semantic conventions](resource/semantic_conventions/README.md#telemetry-sdk)

<a name="instrumented_library"></a>

### Instrumented Library

Denotes the library for which the telemetry signals (traces, metrics, logs) are gathered.

The calls to the OpenTelemetry API can be done either by the Instrumented Library itself,
or by another [Instrumenting Library](#instrumenting_library).

Example: `org.mongodb.client`.

<a name="instrumenting_library"></a>

### Instrumenting Library

Denotes the library that provides the instrumentation for a given [Instrumented Library](#instrumented_library).
*Instrumented Library* and *Instrumenting Library* may be the same library
if it has built-in OpenTelemetry instrumentation.

Example: `io.opentelemetry.contrib.mongodb`.

Synonyms: *Instrumentation Library*, *Integration*.

<a name="name"></a>

### Tracer Name / Meter Name

This refers to the `name` and (optional) `version` arguments specified when
creating a new `Tracer` or `Meter` (see [Obtaining a Tracer](trace/api.md#obtaining-a-tracer)/[Obtaining a Meter](metrics/api-user.md#obtaining-a-meter)). It identifies the [Instrumenting Library](#instrumenting_library).

### Namespace

This term applies to [Metric names](metrics/api-user.md#metric-names) only. The namespace is used to disambiguate identical metric
names used in different [instrumenting libraries](#instrumenting_library). The [Name](#name) provided
for creating a `Meter` serves as its namespace in addition to the primary semantics
described [here](#name).

The `version` argument is not relevant here and will not be included in
the resulting namespace string.

## Logs

### Log Record

A recording of an event. Typically the record includes a timestamp indicating
when the event happened as well as other data that describes what happened,
where it happened, etc.

Also known as Log Entry.

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
