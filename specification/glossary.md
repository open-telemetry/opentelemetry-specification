# Glossary

Below are a list of some OpenTelemetry specific terms that are used across this
specification.

## (Telemetry) Library

Denotes the actual *OpenTelemetry* (or API compatible) library in use.  
See [Library](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/data-resource-semantic-conventions.md#library)

<a name="instrumented_library"></a>

## Instrumented Library

Denotes the library whose "actions" (e.g. called methods/functions, operations, ...)
result in OpenTelemetry signals (traces, metrics, logs).  
The actual OpenTelemetry API calls can happen inside this library but might as well
happen in a different one (the [Instrumenting Library](#instrumenting_library)).

Example: `org.mongodb.client`.

<a name="instrumenting_library"></a>

## Instrumenting Library

Denotes the library which provides the instrumentation *for* a given library (i.e.
the [Instrumented Library](#instrumented_library)). Hence, *Instrumented Library*
and *Instrumenting Library* can be identical if a library has built-in OpenTelemetry
instrumentation or gets auto-instrumented, but they don't necessarily have to.

Example: `io.opentelemetry.contrib.mongodb`.

Synonyms: *Instrumentation Library*, *Integration*.

<a name="name"></a>

## Tracer Name / Meter Name

This refers to the `name` and (optional) `version` arguments specified when
creating a new `Tracer` or `Meter` (see [Obtaining a Tracer](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-tracing.md#obtaining-a-tracer)/[Obtaining a Meter](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-metrics-user.md#obtaining-a-meter)). It is identical to [Instrumenting Library](#instrumenting_library).

## Namespace

This term applies to [Metric names](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-metrics-user.md#metric-names) only and is used to disambiguate identical metric
names used in different instrumenting libraries. The [Name](#name) provided
for creating a `Meter` serves as its namespace in addition to the primary semantics
described [here](#name).

The `version` argument is not relevant here and will not be included in
the resulting namespace string.
