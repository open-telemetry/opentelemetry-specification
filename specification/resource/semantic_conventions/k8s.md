# Kubernetes

**Status**: [Experimental](../../document-status.md)

Useful resources to understand Kubernetes objects and metadata:

* [Namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
* [Names and UIDs](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/).
* [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
* [Controllers](https://kubernetes.io/docs/concepts/workloads/controllers/)

The "name" of a Kubernetes object is unique for that type of object within a
"namespace" and only at a specific moment of time (names can be reused over
time). The "uid" is unique across your whole cluster, and very likely across
time. Because of this it is recommended to always set the UID for every
Kubernetes object, but "name" is usually more user friendly so can be also set.

## Cluster

**type:** `k8s.cluster`

**Description:** A Kubernetes Cluster.

<!-- semconv k8s.cluster -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.cluster.name` | string | The name of the cluster. | `opentelemetry-cluster` | No |
<!-- endsemconv -->

## Node

**type:** `k8s.node`

**Description:** A Kubernetes Node.

<!-- semconv k8s.node -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.node.name` | string | The name of the Node. | `node-1` | No |
| `k8s.node.uid` | string | The UID of the Node. | `1eb3a0c6-0477-4080-a9cb-0cb7db65c6a2` | No |
<!-- endsemconv -->

## Namespace

Namespaces provide a scope for names. Names of objects need to be unique within
a namespace, but not across namespaces.

**type:** `k8s.namespace`

**Description:** A Kubernetes Namespace.

<!-- semconv k8s.namespace -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.namespace.name` | string | The name of the namespace that the pod is running in. | `default` | No |
| `k8s.namespace.uid` | string | The UID of the Namespace. | `bb219a0e-a465-4a0e-aaec-a3731ecc7fe1` | No |
| `k8s.namespace.start_time` | string | The creation time of the namespace. [1] | `2021-05-13 17:23:11` | No |

**[1]:** This is a string representing an RFC 3339 date of the date and time the namespace object was created. [kubernetes api conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#metadata)
<!-- endsemconv -->

## Pod

The smallest and simplest Kubernetes object. A Pod represents a set of running
containers on your cluster.

**type:** `k8s.pod`

**Description:** A Kubernetes Pod object.

<!-- semconv k8s.pod -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.pod.uid` | string | The UID of the Pod. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.pod.name` | string | The name of the Pod. | `opentelemetry-pod-autoconf` | No |
| `k8s.pod.start_time` | string | The creation time of the Pod. [1] | `2021-05-25 23:36:44` | No |

**[1]:** This is a string representing an RFC 3339 date of the date and time the pod object was created. [kubernetes api conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#metadata)
<!-- endsemconv -->

## Container

A container specification in a Pod template. This type is intended to be used to
capture information such as name of a container in a Pod template which is different
from the name of the running container.

Note: This type is different from [container](./container.md), which corresponds
to a running container.

**type:** `k8s.container`

**Description:** A container in a [PodTemplate](https://kubernetes.io/docs/concepts/workloads/pods/#pod-templates).

<!-- semconv k8s.container -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.container.name` | string | The name of the Container in a Pod template. | `redis` | No |
<!-- endsemconv -->

## ReplicaSet

A ReplicaSet’s purpose is to maintain a stable set of replica Pods running at
any given time.

**type:** `k8s.replicaset`

**Description:** A Kubernetes ReplicaSet object.

<!-- semconv k8s.replicaset -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.replicaset.uid` | string | The UID of the ReplicaSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.replicaset.name` | string | The name of the ReplicaSet. | `opentelemetry` | No |
<!-- endsemconv -->

## Deployment

An API object that manages a replicated application, typically by running Pods
with no local state. Each replica is represented by a Pod, and the Pods are
distributed among the nodes of a cluster.

**type:** `k8s.deployment`

**Description:** A Kubernetes Deployment object.

<!-- semconv k8s.deployment -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.deployment.uid` | string | The UID of the Deployment. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.deployment.name` | string | The name of the Deployment. | `opentelemetry` | No |
<!-- endsemconv -->

## StatefulSet

Manages the deployment and scaling of a set of Pods, and provides guarantees
about the ordering and uniqueness of these Pods.

**type:** `k8s.statefulset`

**Description:** A Kubernetes StatefulSet object.

<!-- semconv k8s.statefulset -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.statefulset.uid` | string | The UID of the StatefulSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.statefulset.name` | string | The name of the StatefulSet. | `opentelemetry` | No |
<!-- endsemconv -->

## DaemonSet

A DaemonSet ensures that all (or some) Nodes run a copy of a Pod.

**type:** `k8s.daemonset`

**Description:** A Kubernetes DaemonSet object.

<!-- semconv k8s.daemonset -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.daemonset.uid` | string | The UID of the DaemonSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.daemonset.name` | string | The name of the DaemonSet. | `opentelemetry` | No |
<!-- endsemconv -->

## Job

A Job creates one or more Pods and ensures that a specified number of them
successfully terminate.

**type:** `k8s.job`

**Description:** A Kubernetes Job object.

<!-- semconv k8s.job -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.job.uid` | string | The UID of the Job. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.job.name` | string | The name of the Job. | `opentelemetry` | No |
<!-- endsemconv -->

## CronJob

A CronJob creates Jobs on a repeating schedule.

**type:** `k8s.cronjob`

**Description:** A Kubernetes CronJob object.

<!-- semconv k8s.cronjob -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `k8s.cronjob.uid` | string | The UID of the CronJob. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | No |
| `k8s.cronjob.name` | string | The name of the CronJob. | `opentelemetry` | No |
<!-- endsemconv -->
