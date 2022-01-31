# Kubernetes

**Status**: [Experimental](../../document-status.md)

## Event

The Event is created when other Kubernetes resources have state changes,
errors, or other messages that should be broadcast to the system.

**type:** `k8s.event`

**Description:** A Kubernetes Event object.

<!-- semconv k8s.event -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.event.uid` | string | The UID of the Event. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.event.name` | string | The name of the Event. | `opentelemetry-depl-5c8bf76b5b-tn9h5.16a678548ba4963c` | No |
| `k8s.event.start_time` | string | The start time of the [Event](https://docs.openshift.com/container-platform/4.8/rest_api/objects/index.html#objectmeta-meta-v1)  as the native [Timestamp](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model.md#field-timestamp) can be used for the Timestamp of the [related object](https://docs.openshift.com/container-platform/4.8/rest_api/metadata_apis/event-core-v1.html) of the Event. | `2021-09-20T07:50:19Z` | No |
| `k8s.event.action` | string | The action was taken/failed regarding the related object of the Event. | `Binding` | No |
| `k8s.event.count` | int | The number of times the Event has occurred. | `1`; `2` | No |
| `k8s.event.reason` | string | The reason for the status transition of the Event causing object. | `ScalingReplicaSet` | No |
<!-- endsemconv -->
