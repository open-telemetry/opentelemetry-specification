# OpenCensus Compatibility


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

OpenCensus supports two primary types of telemetry: Traces and Stats (Metrics).
Compatibility for these is defined separately.

> The overridding philosophy for compatibility is that OpenCensus instrumented
> libraries and applications need make *no change* to their API usage in order
> to use OpenTelemetry.   All changes should be solely configuration / setup.


## Goals 

OpenTelemetry<->OpenCensus tracing compatibility has the following goals:

1. OpenCensus has no hard dependency on OpenTelemetry
2. Minimal changes to OpenCensus for implementation
3. Easy for users to use, ideally no change to their code

Additionally, for tracing there are the following goals:

1. Maintain parent-child span relationship from applications and libraries
2. Maintain unscoped span relationships from applications and libraries





# Trace




## Creating Spans in OpenCensus

When the shim is in place, all OpenCensus Spans should be sent through an
OpenTelemetry `Tracer` as specified for the OpenTelemetry API.



TODO - more.


## Context Propogation

The shim will provide an OpenCensus `PropogationComponent` implementation which
maps OpenCenus binary and text progation to OpenTelemetry context.

### Text Context

This adapter MUST use an OpenTelemetry `TextMapPropogator` to implement the
OpenCensus `TextFormat`.

This adapter SHOULD use configured OpenTelemetry `TextMapPropogator` on the
OpenTelemetry `TraceProvider` for text format propogation.

This adapter MUST provide a default `W3CTraceContextPropogator` in lieu of a
propogator defined against the `TraceProvider`.

### B3 Context

This adapter SHOULD use an contributed OpenTelemetry `B3Propogator` for the
B3 text format.

### OpenCensus Binary Context

This adapter MUST implement OpenCensus `BinaryPropogator` to write OpenCensus
binary format using OpenTelemetry's context.

## Resources

Note: resources appear not to be usable in the "API" section of OpenCensus.

## Semantic Convention Mappings

Where possible, the tracing shim should provide mappings of labels defined
within the OpenTelemetry semantic convetions.  

TODO - Define

> The principle is to ensure OpenTelemetry exporters, which use these semantic
> conventions, are likely to export the correct data.


# Metrics / Stats

Metric compatibility with OpenCensus remains unspecified as the OpenTelemetry
metrics specification solidifies for GA.   Once GA on metrics is declared,
this section will be filled out.

> Philosophically, this should follow the same principles as Trace.
> Specifically: Labels/Metric names should be converted to OTel semantic
> conventions, All API surface area should map to the closest relevant OTel
> API and no SDK usage of OpenCensus will be compatible.