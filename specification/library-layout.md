# OpenTelemetry Project Package Layout

This documentation serves to document the "look and feel" of a basic layout for OpenTelemetry
projects. This package layout is intentionally generic and it doesn't try to impose a language
specific package structure.

## API Package

Here is a proposed generic package structure for OpenTelemetry API package.

A typical top-level directory layout:

```
api
   ├── context
   │   └── propagation
   ├── metrics
   ├── trace
   │   └── propagation
   ├── correlationcontext
   │   └── propagation
   ├── internal
   └── logs
```

> Use of lowercase, CamelCase or Snake Case (stylized as snake_case) names depends on the language.

### `/context`

This directory describes the API that provides in-process context propagation.

### [/metrics](api-metrics.md)

This directory describes the Metrics API that can be used to record application metrics.

### [/correlationcontext](api-correlationcontext.md)

This directory describes the CorrelationContext API that can be used to manage context propagation
and metrics-related labeling.

### [/trace](api-tracing.md)

This API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](api-tracing.md#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](api-tracing.md#span) section.

### `/internal` (_Optional_)

Private application and library code.

### `/logs` (_In the future_)

> TODO: logs operations

## SDK Package

Here is a proposed generic package structure for OpenTelemetry SDK package.

A typical top-level directory layout:

```
sdk
   ├── context
   ├── metrics
   ├── resource
   ├── trace
   ├── correlationcontext
   ├── internal
   └── logs
```

> Use of lowercase, CamelCase or Snake Case (stylized as snake_case) names depends on the language.

### `/sdk/context`

This directory describes the SDK implementation for api/context.

### `/sdk/metrics`

This directory describes the SDK implementation for api/metrics.

### [/sdk/resource](sdk-resource.md)

The resource directory primarily defines a type [Resource](overview.md#resources) that captures
information about the entity for which stats or traces are recorded. For example, metrics exposed
by a Kubernetes container can be linked to a resource that specifies the cluster, namespace, pod,
and container name.

### `/sdk/correlationcontext`

### [/sdk/trace](sdk-tracing.md)

This directory describes the SDK implementation for api/trace.

### `/sdk/internal` (_Optional_)

Private application and library code.

### `/sdk/logs` (_In the future_)

> TODO: logs operations
