# OpenTelemetry tracer construction and resolution

This document describes tracer object construction and how it is provided to the user application.

User code should not directly instantiate the tracer and it MUST use `OpenTelemetry.getTracer()`
to access the tracer. Behind the scenes `OpenTelemetry` uses `TracerProvider` which returns
a configured tracer instance. `TracerProvider` is part of the trace implementation (or runtime) and 
it is registered to `OpenTelemetry`.

The tracer object construction depends on the implementation. The implementation might require
specifying various configuration properties at creation time. Therefore to make it work with
parameterless `OpenTelemetry` the configuration should be done via external configuration files.

## Tracer provider

Tracer provider is an internal class used by `OpenTelemetry` to get a tracer instance.
Implementations MUST provide an implementation `TracerProvider` which is used by API package to get
a tracer instance. The tracer provider is registered to API usually via language-specific mechanism.
For instance in Java `ServiceLoader` is used.

### Runtime with multiple deployments/applications

An application runtime might provide its own implementation of `TracerProvider` with higher
loading priority than the provider packaged inside the implementation. This provider can return
a different tracer instance per deployment/application.
