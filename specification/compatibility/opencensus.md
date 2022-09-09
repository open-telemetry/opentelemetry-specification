# OpenCensus Compatibility

**Status**: [Experimental](../document-status.md), Unless otherwise specified.

The OpenTelemetry project aims to provide backwards compatibility with the
[OpenCensus](https://opencensus.io) project in order to ease migration of
instrumented codebases.

## Migration Path

### Breaking Changes when migrating to OpenTelemetry

Migrating from OpenCensus to OpenTelemetry may require breaking changes to the telemetry produced
because of:

* Different or new semantic conventions for names and attributes (e.g. [`grpc.test.EchoService/Echo`](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/gRPC.md#grpc-trace) vs [`rpc.server.duration`](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.12.0/semantic_conventions/trace/rpc.yaml#L64))
* Data model differences (e.g. OpenCensus supports [SumOfSquaredDeviations](https://github.com/census-instrumentation/opencensus-proto/blob/v0.3.0/src/opencensus/proto/metrics/v1/metrics.proto#L195), OTLP does not)
* Instrumentation API feature differences (e.g. OpenCensus supports [context-based attributes](https://github.com/census-instrumentation/opencensus-specs/blob/master/stats/Record.md#recording-stats)), OTel does not)
* Differences between equivalent OC and OTel exporters (e.g. the OpenTelemetry Prometheus exporter [adds type and unit suffixes](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/data-model.md#metric-metadata-1); OpenCensus [does not](https://github.com/census-ecosystem/opencensus-go-exporter-prometheus/blob/v0.4.1/prometheus.go#L227))

This migration path groups most breaking changes into the installation of bridges. This gives
users control over introducing the initial breaking change, and makes subsequent migrations of
instrumentation (including in third-party libraries) non-breaking.

### Migration Plans

#### Migrating from the OpenCensus Agent and Protocol

Starting with a deployment of the OC agent, using the OC protocol, migrate by:

1. Deploy the OpenTelemetry collector with OpenCensus and OTLP receivers and equivalent processors and exporters.
2. **breaking**: For each workload sending the OC protocol, change to sending to the OpenTelemetry collector's OpenCensus receiver.
3. Remove the deployment of the OC Agent
4. For each workload, migrate the application from OpenCensus to OpenTelemetry, following the guidance below, and use the OTLP exporter

#### Migrating an Application using Bridges

Starting with an application using entirely OpenCensus instrumention for traces and metrics, it can be migrated by:

1. Migrate the exporters (SDK)
    1. Install the OpenTelemetry SDK, with an equivalent exporter
        1. If using an OpenCensus exporter, switch to using an OTLP exporter
    2. Install equivalent OpenTelemetry resource detectors
    3. Install OpenTelemetry propagators for OpenCensus' `TextFormat` and `BinaryPropagator` formats.
    4. **breaking**: Install the metrics and trace bridges
    5. Remove initialization of OpenCensus exporters
2. Migrate the instrumentation (API)
    1. **breaking**: For OpenCensus instrumentation packages, migrate to the OpenTelemetry equivalent.
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

**Status**: [Experimental, Feature Freeze](../document-status.md)

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

### Span Attributes

Span attributes SHOULD be mapped following
[semantic convention mappings](#semantic-convention-mappings) described below.

### Resources

Note: resources appear not to be usable in the "API" section of OpenCensus.

#### Known Incompatibilities

Below are listed known incompatibilities between OpenTelemetry and OpenCensus
specifications.   Applications leveraging unspecified behavior from OpenCensus
that *is* specified incompatibly within OpenTelemetry are not eligible for
using the OpenCensus <-> OpenTelemetry bridge.

1. In OpenCensus, there is [no specification](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/Span.md#span-creation)
   when parent spans can be specified on a child span.   OpenTelemetry specifies
   that [parent spans must be specified during span creation](../trace/api.md#span-creation).
   This leads to some issues with OpenCensus APIs that allowed flexible
   specification of parent spans post-initialization.
2. Links added to spans after the spans are created. This is [not supported in
   OpenTelemetry](../trace/api.md#specifying-links), therefore OpenCensus spans
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

## OpenCensus Context Propagation

The shim will provide an OpenCensus `PropagationComponent` implementation which
maps OpenCenus binary and text propagation to OpenTelemetry context.

### Text Context

This adapter MUST use an OpenTelemetry `TextMapPropagator` to implement the
OpenCensus `TextFormat`.

This adapter SHOULD use configured OpenTelemetry `TextMapPropagator` on the
OpenTelemetry `TraceProvider` for text format propagation.

This adapter MUST provide a default `W3CTraceContextPropagator`.  If
OpenTelemetry defines a global TextMapPropogator, OpenCensus SHOULD use this
for OpenCensus `traceContextFormat` propagation.

### B3 Context

This adapter SHOULD use a contributed OpenTelemetry `B3Propagator` for the
B3 text format.

### OpenCensus Binary Context

This adapter MUST provide an implementation of OpenCensus `BinaryPropogator` to
write OpenCensus binary format using OpenTelemetry's context.  This
implementation may be drawn from OpenCensus if applicable.

## Metrics / Stats

Metric compatibility with OpenCensus remains unspecified as the OpenTelemetry
metrics specification solidifies for GA.   Once GA on metrics is declared,
this section will be filled out.

> Philosophically, this should follow the same principles as Trace.
> Specifically: Metric names/attributes should be converted to OTel semantic
> conventions, All API surface area should map to the closest relevant OTel
> API and no SDK usage of OpenCensus will be compatible.

## Semantic Convention Mappings

Where possible, the tracing and metrics shims SHOULD provide mappings of labels
to attributes defined within the OpenTelemetry semantic convetions.

> The principle is to ensure OpenTelemetry exporters, which use these semantic
> conventions, are likely to export the correct data.

### HTTP Attributes

OpenCensus specifies the following [HTTP Attributes](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/HTTP.md#attributes):

| OpenCensus Name    | OpenTelemetry Name | Comments             |
| ------------------ | ------------------ |----------------------|
| `http.host`        | `http.host`        |                      |
| `http.method`      | `http.method`      |                      |
| `http.user_agent`  | `http.user_agent`  |                      |
| `http.status_code` | `http.status_code` |                      |
| `http.url`         | `http.url`         |                      |
| `http.path`        | `http.target`      | key-name change only |
| `http.route`       | N/A                | Pass through ok      |
