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
   ├── baggage
   │   └── propagation
   ├── internal
   └── logs
```

> Use of lowercase, CamelCase or Snake Case (stylized as snake_case) names depends on the language.

### `/context`

This directory describes the API that provides in-process context propagation.

### [/metrics](./metrics/api.md)

This directory describes the Metrics API that can be used to record application metrics.

### [/baggage](baggage/api.md)

This directory describes the Baggage API that can be used to manage context propagation
and metrics-related labeling.

### [/trace](trace/api.md)

This API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](trace/api.md#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](trace/api.md#span) section.

### `/internal` (_Optional_)

Library components and implementations that shouldn't be exposed to the users.
If a language has an idiomatic layout for internal compoents, please follow
the language idiomatic style.

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
   ├── baggage
   ├── internal
   └── logs
```

> Use of lowercase, CamelCase or Snake Case (stylized as snake_case) names depends on the language.

### `/sdk/context`

This directory describes the SDK implementation for api/context.

### `/sdk/metrics`

This directory describes the SDK implementation for api/metrics.

### [/sdk/resource](resource/sdk.md)

The resource directory primarily defines a type [Resource](overview.md#resources) that captures
information about the entity for which stats or traces are recorded. For example, metrics exposed
by a Kubernetes container can be linked to a resource that specifies the cluster, namespace, pod,
and container name.

### `/sdk/baggage`

### [/sdk/trace](trace/sdk.md)

This directory describes the SDK implementation for api/trace.

### `/sdk/internal` (_Optional_)

Library components and implementations that shouldn't be exposed to the users.
If a language has an idiomatic layout for internal compoents, please follow
the language idiomatic style.

### `/sdk/logs` (_In the future_)

> TODO: logs operations
