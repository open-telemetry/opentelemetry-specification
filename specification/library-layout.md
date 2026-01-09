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

> Use of lowercase, camelCase or snake_case (stylized as snake_case) names depends on the language.

### `/api/context`

This directory describes the API that provides in-process context propagation.

### `/api/metrics`

This directory describes the [Metrics API](./metrics/api.md) that can be used to
record application metrics.

### `/api/baggage`

This directory describes the [Baggage API](baggage/api.md) that can be used to
manage context propagation and metric event attributes.

### `/api/trace`

The [Trace API](trace/api.md) consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](trace/api.md#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](trace/api.md#span) section.

### `/api/internal` (_Optional_)

Library components and implementations that shouldn't be exposed to the users.
If a language has an idiomatic layout for internal components, please follow
the language idiomatic style.

### `/api/logs` (_In the future_)

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

> Use of lowercase, camelCase or snake_case (stylized as snake_case) names depends on the language.

### `/sdk/context`

This directory describes the SDK implementation for api/context.

### `/sdk/metrics`

This directory describes the SDK implementation for api/metrics.

### `/sdk/resource`

The [resource directory](resource/sdk.md) primarily defines a type
[Resource](overview.md#resources) that captures information about the entity for
which stats or traces are recorded. For example, metrics exposed by a Kubernetes
container can be linked to a resource that specifies the cluster, namespace,
pod, and container name.

### `/sdk/baggage`

> TODO

### `/sdk/trace`

This directory describes the [Tracing SDK](trace/sdk.md) implementation.

### `/sdk/internal` (_Optional_)

Library components and implementations that shouldn't be exposed to the users.
If a language has an idiomatic layout for internal components, please follow
the language idiomatic style.

### `/sdk/logs` (_In the future_)

> TODO: logs operations
