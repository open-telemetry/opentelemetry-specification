# Glossary

Below are a list of some OpenTelemetry specific terms that are used across this
specification.

## (Telemetry) Library

Denotes the actual *OpenTelemetry* library in use.  
See [Library](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/data-resource-semantic-conventions.md#library)

<a name="instrumented_library"></a>

## Instrumented Library

Denotes the library instrumented with OpenTelemetry API calls, thus the library
that is producing telemetry data.

Example: `org.mongodb`.

<a name="instrumenting_library"></a>

## Instrumenting Library

Denotes the library which provides the instrumentation *for* a given library (i.e.
the [Instrumented Library](#instrumented_library)). Hence, *Instrumented Library*
and *Instrumenting Library* can be identical, but they don't necessarily have to.

Example: `io.opentelemetry.contrib.mongodb`.

Synonyms: *Instrumentation Library*, *Integration*.

<a name="name"></a>

## Tracer Name / Meter Name

This refers to the `name` specified when creating a new `Tracer` or `Meter`
(see [Obtaining a Tracer](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-tracing.md#obtaining-a-tracer)/[Obtaining a Meter](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-metrics-user.md#obtaining-a-meter)). It is identical to
[Instrumenting Library](#instrumenting_library).

## Namespace

This term applies to [Metric names](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-metrics-user.md#metric-names) only and is used to disambiguate identical metric
names used in different libraries. The [Name](#name) provided for creating a `Meter`
also serves as its namespace.
