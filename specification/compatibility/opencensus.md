<!--- Hugo front matter used to generate the website version of this page:
linkTitle: OpenCensus
--->

# OpenCensus Compatibility

**Status**: [Stable](../document-status.md), Unless otherwise specified.

The OpenTelemetry project aims to provide backwards compatibility with the
[OpenCensus](https://opencensus.io) project in order to ease migration of
instrumented codebases.

## Migration Path

### Breaking Changes when migrating to OpenTelemetry

Migrating from OpenCensus to OpenTelemetry may require breaking changes to the telemetry produced
because of:

* Different or new semantic conventions for names and attributes (e.g. [`grpc.io/server/server_latency`](https://github.com/census-instrumentation/opencensus-specs/blob/master/stats/gRPC.md#server) vs [`rpc.server.call.duration`](https://opentelemetry.io/docs/specs/semconv/rpc/rpc-metrics/#metric-rpcservercallduration))
* Data model differences (e.g. OpenCensus supports [SumOfSquaredDeviations](https://github.com/census-instrumentation/opencensus-proto/blob/v0.3.0/src/opencensus/proto/metrics/v1/metrics.proto#L195), OTLP does not)
* Instrumentation API feature differences (e.g. OpenCensus supports [context-based attributes](https://github.com/census-instrumentation/opencensus-specs/blob/master/stats/Record.md#recording-stats)), OTel does not)
* Differences between equivalent OC and OTel exporters (e.g. the OpenTelemetry Prometheus exporter [adds type and unit suffixes](prometheus_and_openmetrics.md#metric-metadata-1); OpenCensus [does not](https://github.com/census-ecosystem/opencensus-go-exporter-prometheus/blob/v0.4.1/prometheus.go#L227))

This migration path groups most breaking changes into the installation of bridges. This gives
users control over introducing the initial breaking change, and makes subsequent migrations of
instrumentation (including in third-party libraries) non-breaking.

### Migration Plans

#### Migrating from the OpenCensus Agent and Protocol

Starting with a deployment of the OC agent, using the OC protocol, migrate by:

1. Deploy the OpenTelemetry collector with OpenCensus and OTLP receivers and equivalent processors and exporters.
2. **breaking**: For each workload sending the OC protocol, change to sending to the OpenTelemetry collector's OpenCensus receiver.
3. Remove the deployment of the OC Agent.
4. For each workload, migrate the application from OpenCensus to OpenTelemetry, following the guidance below, and use the OTLP exporter.

#### Migrating an Application using Bridges

Starting with an application using entirely OpenCensus instrumention for traces and metrics, it can be migrated by:

1. Migrate the exporters (SDK)
    1. Install the OpenTelemetry SDK, with an equivalent exporter
        1. If using an OpenCensus exporter, switch to using an OTLP exporter
    2. Install equivalent OpenTelemetry resource detectors
    3. Install OpenTelemetry [`W3c TraceContext`](../context/api-propagators.md#propagators-distribution) propagator, which is the equivalent of the OpenCensus' `TextFormat` propagator.
    4. **breaking**: Install the metrics and trace bridges
    5. Remove initialization of OpenCensus exporters
2. Migrate the instrumentation (API)
    1. **breaking**: For OpenCensus instrumentation packages, migrate to the OpenTelemetry equivalent.
        1. If migrating gRPC, enable the [`BinaryPropagation`](../context/api-propagators.md#propagators-distribution) propagator if the language supports it. Otherwise, enable OpenCensus `BinaryPropagation` on the OpenTelemetry gRPC instrumentation.
    2. For external dependencies, wait for it to migrate to OpenTelemetry, and update the dependency.
    3. For instrumentation which is part of the application, migrate it following the "library" guidance below.
3. Clean up: Remove the metrics and trace bridges

#### Migrating Libraries using OC Instrumentation

##### In-place Migration

Libraries which want a simple migration can choose to replace instrumentation in-place.

Starting with a library using OpenCensus Instrumentation:

1. Annouce to users the library's transition from OpenCensus to OpenTelemetry, and recommend users adopt OC bridges.
2. Change unit tests to use the OC bridges, and use OpenTelemetry unit testing frameworks.
3. After a notification period, migrate instrumentation line-by-line to OpenTelemetry. The notification period should be long for popular libraries.
4. Remove the OC bridge from unit tests.

##### Migration via Config

Libraries which are eager to add native OpenTelemetry instrumentation sooner, and/or want to
provide extended support for OpenCensus may choose to provide users the option to use OpenCensus
instrumentation _or_ OpenTelemetry instrumentation.

Starting with a library using OpenCensus Instrumentation:

1. Change unit tests to use the OC bridges, and use OpenTelemetry unit testing frameworks.
2. Add configuration allowing users to enable OpenTelemetry instrumentation and disable OpenCensus instrumentation.
3. Add OpenTelemetry instrumentation gated by the configuration, and tested using the same sets of unit tests.
4. After a notification period, switch to using OpenTelemetry instrumentation by default.
5. After a deprecation period, remove the option to use OpenCensus instrumentation.

## Trace Bridge

The trace bridge is provided as a shim layer implementing the
[OpenCensus Trace API](https://github.com/census-instrumentation/opencensus-specs)
using the OpenTelemetry Trace API. This layer MUST NOT rely on implementation
specific details of the OpenTelemetry SDK.

More specifically, the intention is to allow OpenCensus instrumentation to be
recorded using OpenTelemetry. This Shim Layer MUST NOT publicly expose any
upstream OpenTelemetry API.

The OpenCensus Shim and the OpenTelemetry API/SDK are expected to be consumed
simultaneously in a running service, in order to ease migration from the former
to the latter.  It is expected that application owners will begin the migration
process towards OpenTelemetry via the shim and adding new telemetry information
via OpenTelemetry.  Slowly, libraries and integrations will also migrate
towards opentelemetry until the shim is no longer necessary.

For example, an application may have traces today of the following variety:

```
|-- Application - Configured OpenCensus --------------------------------- |
    |--  gRPC -> Using OpenCensus to generate Trace A  --------- |
      |--  Application -> Using OpenCensus to generate a sub Trace B-- |
```

In this case, the application should be able to update its outer layer to
OpenTelemetry, without having to wait for all downstream dependencies to
have updated to OpenTelemetry (or deal with incompatibilities therein). The
Application also doesn't need to rewrite any of its own instrumentation.

```
|-- Application - Configured Otel w/ OpenCensus Shim ------------------- |
    |--  gRPC -> Using OpenCensus to generate Trace A  --------- |
      |--  Application -> Using OpenCensus to generate a sub Trace B-- |
```

Next, the application can update its own instrumentation in a piecemeal fashion:

```
|-- Application - Configured Otel w/ OpenCensus Shim ---------------------- |
    |--  gRPC -> Using OpenCensus to generate Trace A  --------- |
      |--  Application -> Using OpenTelemetry to generate a sub Trace B-- |
```

> This layer of Otel -> OpenCensus -> Otel tracing can be thought of as the
> "OpenTelemetry sandwich" problem, and is the key motivating factor for
> this specification.

Finally, the Application would update all usages of OpenCensus to OpenTelemetry.

```
|-- Application - Configured Otel standalone ----------------------------- |
    |--  gRPC -> Using Otel to generate Trace A  --------- |
      |--  Application -> Using OpenTelemetry to generate a sub Trace B-- |
```

### Requirements

The OpenTelemetry<->OpenCensus trace bridge has the following requirements:

* OpenCensus has no hard dependency on OpenTelemetry
* Minimal changes to OpenCensus for implementation
* Easy for users to use, ideally no change to their code
* Maintain parent-child span relationship between applications and libraries
* Maintain span link relationships between applications and libraries
* This component MUST be an optional dependency.

### Creating Spans in OpenCensus

When the shim is in place, all OpenCensus Spans MUST be sent through an
OpenTelemetry `Tracer` as specified for the OpenTelemetry API.

This mechanism SHOULD be seamless to the user in languages that allow discovery
and auto injection of dependencies.

### Methods on Spans

All specified methods in OpenCensus will delegate to the underlying `Span` of
OpenTelemetry.

### Resources

Note: resources appear not to be usable in the "API" section of OpenCensus.

#### Known Incompatibilities

Below are listed known incompatibilities between OpenTelemetry and OpenCensus
specifications. Applications leveraging unspecified behavior from OpenCensus
that _is_ specified incompatibly within OpenTelemetry are not eligible for
using the OpenCensus <-> OpenTelemetry bridge.

1. In OpenCensus, there is [no specification](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/Span.md#span-creation)
   when parent spans can be specified on a child span.   OpenTelemetry specifies
   that [parent spans must be specified during span creation](../trace/api.md#span-creation).
   This leads to some issues with OpenCensus APIs that allowed flexible
   specification of parent spans post-initialization.
2. Links added to spans after the spans are created. This is [not supported in
   OpenTelemetry](../trace/api.md#link), therefore OpenCensus spans
   that have links added to them after creation will be mapped to OpenTelemetry
   spans without the links.
3. OpenTelemetry specifies that samplers are
   [attached to an entire Trace provider](../trace/sdk.md#sampling)
   while [OpenCensus allows custom samplers per span](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/Sampling.md#how-can-users-control-the-sampler-that-is-used-for-sampling).
4. TraceFlags in both OpenCensus and OpenTelemetry only specify the single
   `sampled` flag ([OpenTelemetry](../trace/api.md#spancontext),
   [OpenCensus](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/TraceConfig.md#traceparams)).
   Some OpenCensus APIs support "debug" and "defer" tracing flags in addition to
   "sampled".  In this case, the OpenCensus bridge will do its best to support
   and translate unspecified flags into the closest OpenTelemetry equivalent.

## OpenCensus Binary Context Propagation

The shim will provide an OpenCensus `BinaryPropogator` implementation which
maps [OpenCenus binary trace context format](https://github.com/census-instrumentation/opencensus-specs/blob/master/encodings/BinaryEncoding.md#trace-context) to an OpenTelemetry
[SpanContext](../overview.md#spancontext).

This adapter MUST provide an implementation of OpenCensus `BinaryPropogator` to
write OpenCensus binary format using OpenTelemetry's context.  This
implementation may be drawn from OpenCensus if applicable.

The `BinaryPropagator` MUST be a [TextMapPropagator](../context/api-propagators.md#textmap-propagator)
if possible in the language. Otherwise, the `BinaryPropagator` MUST be a library,
which is expected to be used by OpenTelemetry gRPC instrumentation. gRPC
instrumentation in those languages SHOULD NOT enable the `BinaryPropagator` by
default, but SHOULD provide configuration to allow users to enable it.

## Metrics / Stats

OpenTelemetry will provide an OpenCensus-Metrics-Shim component which
implements the OpenTelemetry [MetricProducer](../metrics/sdk.md#metricproducer)
interface. When Produce() is invoked, the shim collects metrics from the
OpenCensus global state, converts the metrics to an OpenTelemetry metrics
batch, and returns.

### Requirements

* This component MUST be an optional dependency
* MUST NOT require OpenTelemetry to be included in OpenCensus API distributions
* SHOULD NOT require OpenCensus to depend on OpenTelemetry at runtime
* MUST require few or no changes to OpenCensus
* MUST be compatible with push and pull exporters
* MUST support Gauges, Counters, Cumulative Histograms, and Summaries
* Is NOT REQUIRED to support Gauge Histograms
* MUST support exemplar span context in language that provide utilities for recording span context in exemplars

### Resource

The shim MUST discard the resource attached to OpenCensus metrics, and insert
the resource provided during initialization, or fall back to the the default
OpenTelemetry resource.

### Instrumentation Scope

The shim MUST add an instrumentation scope name and version which identifies
the shim.

### Usage

The shim can be passed as an option to an OpenTelemetry
[MetricReader](../metrics/sdk.md#metricreader) when configuring the
OpenTelemetry SDK. This enables the bridge to work with both push and pull
metric exporters.

#### Known Incompatibilities

* OpenTelemetry does not support OpenCensus' GaugeHistogram type; these metrics
  MUST be dropped when using the bridge.
* OpenTelemetry does not currently support context-based attributes (tags).
* OpenTelemetry does not support OpenCensus' SumOfSquaredDeviation field; this
  is dropped when using the bridge.
