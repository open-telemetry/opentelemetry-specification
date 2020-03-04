# Glossary

Below are a list of some OpenTelemetry specific terms that are used across this
specification.

## Telemetry SDK

Denotes the library that implements the *OpenTelemetry API*.

See [Library Guidelines](library-guidelines.md#sdk-implementation) and
[Library resource semantic conventions](data-resource-semantic-conventions.md#telemetry-sdk)

<a name="instrumented_library"></a>

## Instrumented Library

Denotes the library for which the telemetry signals (traces, metrics, logs) are gathered.

The calls to the OpenTelemetry API can be done either by the Instrumented Library itself,
or by another [Instrumenting Library](#instrumenting_library).

Example: `org.mongodb.client`.

<a name="instrumenting_library"></a>

## Instrumenting Library

Denotes the library that provides the instrumentation for a given [Instrumented Library](#instrumented_library).
*Instrumented Library* and *Instrumenting Library* may be the same library
if it has built-in OpenTelemetry instrumentation.

Example: `io.opentelemetry.contrib.mongodb`.

Synonyms: *Instrumentation Library*, *Integration*.

<a name="name"></a>

## Tracer Name / Meter Name

This refers to the `name` and (optional) `version` arguments specified when
creating a new `Tracer` or `Meter` (see [Obtaining a Tracer](api-tracing.md#obtaining-a-tracer)/[Obtaining a Meter](api-metrics-user.md#obtaining-a-meter)). It identifies the [Instrumenting Library](#instrumenting_library).

## Namespace

This term applies to [Metric names](api-metrics-user.md#metric-names) only. The namespace is used to disambiguate identical metric
names used in different [instrumenting libraries](#instrumenting_library). The [Name](#name) provided
for creating a `Meter` serves as its namespace in addition to the primary semantics
described [here](#name).

The `version` argument is not relevant here and will not be included in
the resulting namespace string.
