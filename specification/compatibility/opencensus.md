# OpenCensus Compatibility

**Status**: [Experimental](../document-status.md), Unless otherwise specified.

## Abstract

The OpenTelemetry project aims to provide backwards compatibility with the
[OpenCensus](https://opencensus.io) project in order to ease migration of
instrumented codebases.

This functionality will be provided as a bridge layer implementing the
[OpenCensus API](https://github.com/census-instrumentation/opencensus-specs)
using the OpenTelemetry API. This layer MUST NOT rely on implementation specific
details of the OpenTelemetry SDK.

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

OpenCensus supports two primary types of telemetry: Traces and Stats (Metrics).
Compatibility for these is defined separately.

> The overridding philosophy for compatibility is that OpenCensus instrumented
> libraries and applications need make *no change* to their API usage in order
> to use OpenTelemetry. All changes should be solely configuration / setup.

## Goals

OpenTelemetry<->OpenCensus compatibility has the following goals:

1. OpenCensus has no hard dependency on OpenTelemetry
2. Minimal changes to OpenCensus for implementation
3. Easy for users to use, ideally no change to their code

Additionally, for tracing there are the following goals:

1. Maintain parent-child span relationship between applications and libraries
2. Maintain span link relationships between applications and libraries

## Trace

**Status**: [Experimental, Feature Freeze](../document-status.md)

OpenTelemetry will provide an OpenCensus-Trace-Shim component that can be
added as a dependency to ensure compatibility with OpenCensus.

This component MUST be an optional dependency.

### Creating Spans in OpenCensus

When the shim is in place, all OpenCensus Spans MUST be sent through an
OpenTelemetry `Tracer` as specified for the OpenTelemetry API.

This mechanism SHOULD be seamless to the user in languages that allow discovery
and auto injection of dependencies.

### Methods on Spans

All specified methods in OpenCensus will delegate to the underlying `Span` of
OpenTelemetry.

#### Known Incompatibilities

Below are listed known incompatibilities between OpenTelemetry and OpenCensus
specifications.   Applications leveraging unspecified behavior from OpenCensus
that *is* specified incompatibly within OpenTelemetry are not eligble for
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
   Some OpenCensus APIs support "debug" and "defer" tracing flags in additon to
   "sampled".  In this case, the OpenCensus bridge will do its best to support
   and translate unspecified flags into the closest OpenTelemetry equivalent.

### Context Propagation

The shim will provide an OpenCensus `PropagationComponent` implementation which
maps OpenCenus binary and text propagation to OpenTelemetry context.

#### Text Context

This adapter MUST use an OpenTelemetry `TextMapPropagator` to implement the
OpenCensus `TextFormat`.

This adapter SHOULD use configured OpenTelemetry `TextMapPropagator` on the
OpenTelemetry `TraceProvider` for text format propagation.

This adapter MUST provide a default `W3CTraceContextPropagator`.  If
OpenTelemetry defines a global TextMapPropogator, OpenCensus SHOULD use this
for OpenCensus `traceContextFormat` propagation.

#### B3 Context

This adapter SHOULD use a contributed OpenTelemetry `B3Propagator` for the
B3 text format.

#### OpenCensus Binary Context

This adapter MUST provide an implementation of OpenCensus `BinaryPropogator` to
write OpenCensus binary format using OpenTelemetry's context.  This
implementation may be drawn from OpenCensus if applicable.

### Resources

Note: resources appear not to be usable in the "API" section of OpenCensus.

### Semantic Convention Mappings

Where possible, the tracing shim should provide mappings of labels defined
within the OpenTelemetry semantic convetions.  

> The principle is to ensure OpenTelemetry exporters, which use these semantic
> conventions, are likely to export the correct data.

#### HTTP Attributes

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

## Metrics / Stats

Metric compatibility with OpenCensus remains unspecified as the OpenTelemetry
metrics specification solidifies for GA.   Once GA on metrics is declared,
this section will be filled out.

> Philosophically, this should follow the same principles as Trace.
> Specifically: Labels/Metric names should be converted to OTel semantic
> conventions, All API surface area should map to the closest relevant OTel
> API and no SDK usage of OpenCensus will be compatible.
