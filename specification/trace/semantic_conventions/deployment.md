# Semantic conventions for Application Deployment

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for recording application delivery as span events.
To record an evaluation outside a transaction context, consider
[recording it as a log record](../../logs/semantic_conventions/deployment.md).

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Overview](#overview)
- [Definitions](#definitions)
  * [Application](#application)
  * [Workload](#workload)
  * [Task](#task)

<!-- tocstop -->

## Overview

Deployments of cloud-native applications are automated and done at a fast phase.
In most cases, deployments are complex, require multiple steps, could spawn across multiple environments,
and are delivered mostly via either Operators or GitOps practices and tools.
Hence, the delivery process is modeled as an event stream of OpenTelemetry [`Event`s](../api.md#add-events).
This document defines semantic conventions to collect telemetry signals about events that occur during the
deployment of an application.

## Definitions

### Application

Each stage of the lifecycle of a cloud-native application deployment SHOULD be recorded as an Event on the span during 
which it occurred.

<!-- semconv deployment.application -->
The event name MUST be `deployment.application`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `deployment.application.name` | string | The name of the application under deployment. | `podtato-head` | Required |
| `deployment.application.version` | string | The version of the application under deployment. | `0.1.0` | Recommended |
| `deployment.application.status` | string | The status of the application deployment. | `Pending` | Recommended |

`deployment.application.status` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `Pending` | The deployment has been accepted and is being set up |
| `Progressing` | The deployment is currently taking place |
| `Succeeded` | The deployment was completed correctly |
| `Failed` | The deployment was **not** completed correctly |
| `Unknown` | The deployment was unsuccessful and the reason is unknown |
<!-- endsemconv -->

### Workload 

Cloud-native applications are composed of one or several components that are usually called [workloads](https://kubernetes.io/docs/concepts/workloads/).
Similarly to applications, each stage of the lifecycle of a workload deployment SHOULD be recorded as an Event on the span during
which it occurred.

<!-- semconv deployment.workload -->
The event name MUST be `deployment.workload`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `deployment.workload.name` | string | The name of the single workload under deployment. | `podtato-head-hat`; `podtato-head-left-leg` | Required |
| `deployment.workload.namespace` | string | The namespace in which the workload will be deployed. | `podtatohead` | Recommended |
| `deployment.workload.version` | string | The version of the workload under deployment. | `v0.1.0` | Recommended |
| `deployment.workload.status` | string | The status of the workload deployment. | `Pending` | Recommended |
| `deployment.application.name` | string | The name of the application under deployment. | `podtato-head` | Required |

`deployment.workload.status` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `Pending` | The deployment has been accepted and is being set up |
| `Progressing` | The deployment is currently taking place |
| `Succeeded` | The deployment was completed correctly |
| `Failed` | The deployment was **not** completed correctly |
| `Unknown` | The deployment wass unsuccessful and the reason is unknown |
<!-- endsemconv -->

### Task

The deployment of the new version of an application usually requires several external tasks.
Their execution SHOULD be recorded as an Event on the span during which it occurred.

<!-- semconv deployment.task -->
The event name MUST be `deployment.task`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `deployment.task.name` | string | The name that identifies the executed task. | `database-migration`; `report-metric`; `provision-infrastructure` | Required |
| `deployment.task.status` | string | The status of the task execution. | `Pending` | Recommended |
| `deployment.application.name` | string | The name of the application under deployment. | `podtato-head` | Required |
| `deployment.workload.name` | string | The name of the single workload under deployment. | `podtato-head-hat`; `podtato-head-left-leg` | Recommended |

`deployment.task.status` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `Pending` | The deployment has been accepted and is being set up |
| `Progressing` | The deployment is currently taking place |
| `Succeeded` | The deployment was completed correctly |
| `Failed` | The deployment was **not** completed correctly |
| `Unknown` | The deployment was unsuccessful and the reason is unknown |
<!-- endsemconv -->
