# Semantic Conventions for Application Deployment

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for recording an application delivery as
a [log record](../api.md#logrecord) emitted through the [Logger API](../api.md#emit-logrecord).

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Recording an Application Delivery](#recording-an-application-delivery)
  * [Attributes](#attributes)
- [Recording a Workload Delivery](#recording-a-workload-delivery)
  * [Attributes](#attributes-1)
- [Recording a Task execution](#recording-a-task-execution)
  * [Attributes](#attributes-2)

<!-- tocstop -->

## Recording an Application Delivery

Application deployments SHOULD be recorded as attributes on the
[LogRecord](../api.md#logrecord) passed to the [Logger](../api.md#logger) emit
operations. Application deployments MAY be recorded on "logs" or "events" depending on the
context.

### Attributes

The table below indicates which attributes should be added to the
[LogRecord](../api.md#logrecord) and their types.

<!-- semconv log-deployment-application -->
The event name MUST be `deployment.application`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`deployment.application.name`](../../trace/semantic_conventions/deployment.md) | string | The name of the application under deployment. | `podtato-head` | Required |
| [`deployment.application.status`](../../trace/semantic_conventions/deployment.md) | string | The status of the application deployment. | `Pending` | Recommended |
| [`deployment.application.version`](../../trace/semantic_conventions/deployment.md) | string | The version of the application under deployment. | `0.1.0` | Recommended |
<!-- endsemconv -->

## Recording a Workload Delivery

Workload deployments SHOULD be recorded as attributes on the
[LogRecord](../api.md#logrecord) passed to the [Logger](../api.md#logger) emit
operations. Workload deployments MAY be recorded on "logs" or "events" depending on the
context.

### Attributes

<!-- semconv log-deployment-workload -->
The event name MUST be `deployment.workload`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`deployment.application.name`](../../trace/semantic_conventions/deployment.md) | string | The name of the application under deployment. | `podtato-head` | Required |
| [`deployment.workload.name`](../../trace/semantic_conventions/deployment.md) | string | The name of the single workload under deployment. | `podtato-head-hat`; `podtato-head-left-leg` | Required |
| [`deployment.workload.status`](../../trace/semantic_conventions/deployment.md) | string | The status of the workload deployment. | `Pending` | Recommended |
| [`deployment.workload.version`](../../trace/semantic_conventions/deployment.md) | string | The version of the workload under deployment. | `v0.1.0` | Recommended |
<!-- endsemconv -->

## Recording a Task execution

Task executions that support deployments SHOULD be recorded as attributes on the
[LogRecord](../api.md#logrecord) passed to the [Logger](../api.md#logger) emit
operations. Task executions MAY be recorded on "logs" or "events" depending on the
context.


### Attributes

<!-- semconv log-deployment-task -->
The event name MUST be `deployment.task`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`deployment.application.name`](../../trace/semantic_conventions/deployment.md) | string | The name of the application under deployment. | `podtato-head` | Required |
| [`deployment.task.name`](../../trace/semantic_conventions/deployment.md) | string | The name that identifies the executed task. | `database-migration`; `report-metric`; `provision-infrastructure` | Required |
| [`deployment.task.status`](../../trace/semantic_conventions/deployment.md) | string | The status of the task execution. | `Pending` | Recommended |
| [`deployment.workload.name`](../../trace/semantic_conventions/deployment.md) | string | The name of the single workload under deployment. | `podtato-head-hat`; `podtato-head-left-leg` | Recommended |
<!-- endsemconv -->
