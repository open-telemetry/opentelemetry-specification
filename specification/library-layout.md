# OpenTelemetry Project Package Layout
This documentation serves to document the "look and feel" of a basic layout for OpenTelemetry projects. This package layout is intentionally generic and it doesn't try to impose a language specific package structure.

## API Package
Here is a proposed generic package structure for OpenTelemetry API package.

### `/context`

This directory describes the API that provides in-process context propagation.

### `/metrics`

This directory describes the Metrics API that can be used to record application metrics.

### `/resources`

This API for resource information population.

The resource directory primarily defines a type [Resource](../terminology.md#resources) that captures information about the entity for which stats or traces are recorded. For example, metrics exposed by a Kubernetes container can be linked to a resource that specifies the cluster, namespace, pod, and container name.

### `/distributedcontext`

This directory describes the DistributedContext API that can be used to manage context propagation and metrics-related labeling.

This API consists of a few main classes:

- `Entry` is used to label anything that is associated with a specific operation, such as an HTTP request.
- An `Entry` consists of `EntryMetadata`, `EntryKey`, and `EntryValue`.

### `/trace`

This API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](./tracing-api.md#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](./tracing-api.md#span) section.
- `SpanData` is an immutable object that is used to report out-of-band completed
  spans. See [SpanData](./tracing-api.md#spandata) section.

### `/internal` (_Optional_)
Private application and library code.

### `/logs` (_In the future_)
> TODO: logs operations


A typical top-level directory layout:
```
api
   ├── context
   │   └── propagation
   ├── metrics
   ├── resources
   ├── trace
   ├── distributedcontext
   │   └── propagation
   ├── internal
   └── logs
```
> Use of lowercase, CamelCase or Snake Case (stylized as snake_case) names depends on the language.
