# Kubernetes

**Status**: [Experimental](../../document-status.md)

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

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
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.cluster.name` | string | The name of the cluster. | `opentelemetry-cluster` | Recommended |
| `k8s.cluster.uid` | string | A pseudo-ID for the cluster, set to the UID of the `kube-system` namespace. [1] | `218fc5a9-a5f1-4b54-aa05-46717d0ab26d` | Recommended |

**[1]:** K8s does not have support for obtaining a cluster ID. If this is ever
added, we will recommend collecting the `k8s.cluster.uid` through the
official APIs. In the meantime, we are able to use the `uid` of the
`kube-system` namespace as a proxy for cluster ID. Read on for the
rationale.

Every object created in a K8s cluster is assigned a distinct UID. The
`kube-system` namespace is used by Kubernetes itself and will exist
for the lifetime of the cluster. Using the `uid` of the `kube-system`
namespace is a reasonable proxy for the K8s ClusterID as it will only
change if the cluster is rebuilt. Furthermore, Kubernetes UIDs are
UUIDs as standardized by
[ISO/IEC 9834-8 and ITU-T X.667](https://www.itu.int/ITU-T/studygroups/com17/oid.html).
Which states:

> If generated according to one of the mechanisms defined in Rec.
  ITU-T X.667 | ISO/IEC 9834-8, a UUID is either guaranteed to be
  different from all other UUIDs generated before 3603 A.D., or is
  extremely likely to be different (depending on the mechanism chosen).

Therefore, UIDs between clusters should be extremely unlikely to
conflict.
<!-- endsemconv -->

## Node

**type:** `k8s.node`

**Description:** A Kubernetes Node.

<!-- semconv k8s.node -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.node.name` | string | The name of the Node. | `node-1` | Recommended |
| `k8s.node.uid` | string | The UID of the Node. | `1eb3a0c6-0477-4080-a9cb-0cb7db65c6a2` | Recommended |
<!-- endsemconv -->

## Namespace

Namespaces provide a scope for names. Names of objects need to be unique within
a namespace, but not across namespaces.

**type:** `k8s.namespace`

**Description:** A Kubernetes Namespace.

<!-- semconv k8s.namespace -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.namespace.name` | string | The name of the namespace that the pod is running in. | `default` | Recommended |
<!-- endsemconv -->

## Pod

The smallest and simplest Kubernetes object. A Pod represents a set of running
containers on your cluster.

**type:** `k8s.pod`

**Description:** A Kubernetes Pod object.

<!-- semconv k8s.pod -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.pod.uid` | string | The UID of the Pod. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.pod.name` | string | The name of the Pod. | `opentelemetry-pod-autoconf` | Recommended |
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
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.container.name` | string | The name of the Container from Pod specification, must be unique within a Pod. Container runtime usually uses different globally unique name (`container.name`). | `redis` | Recommended |
| `k8s.container.restart_count` | int | Number of times the container was restarted. This attribute can be used to identify a particular container (running or stopped) within a container spec. | `0`; `2` | Recommended |
<!-- endsemconv -->

## ReplicaSet

A ReplicaSet’s purpose is to maintain a stable set of replica Pods running at
any given time.

**type:** `k8s.replicaset`

**Description:** A Kubernetes ReplicaSet object.

<!-- semconv k8s.replicaset -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.replicaset.uid` | string | The UID of the ReplicaSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.replicaset.name` | string | The name of the ReplicaSet. | `opentelemetry` | Recommended |
<!-- endsemconv -->

## Deployment

An API object that manages a replicated application, typically by running Pods
with no local state. Each replica is represented by a Pod, and the Pods are
distributed among the nodes of a cluster.

**type:** `k8s.deployment`

**Description:** A Kubernetes Deployment object.

<!-- semconv k8s.deployment -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.deployment.uid` | string | The UID of the Deployment. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.deployment.name` | string | The name of the Deployment. | `opentelemetry` | Recommended |
<!-- endsemconv -->

## StatefulSet

Manages the deployment and scaling of a set of Pods, and provides guarantees
about the ordering and uniqueness of these Pods.

**type:** `k8s.statefulset`

**Description:** A Kubernetes StatefulSet object.

<!-- semconv k8s.statefulset -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.statefulset.uid` | string | The UID of the StatefulSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.statefulset.name` | string | The name of the StatefulSet. | `opentelemetry` | Recommended |
<!-- endsemconv -->

## DaemonSet

A DaemonSet ensures that all (or some) Nodes run a copy of a Pod.

**type:** `k8s.daemonset`

**Description:** A Kubernetes DaemonSet object.

<!-- semconv k8s.daemonset -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.daemonset.uid` | string | The UID of the DaemonSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.daemonset.name` | string | The name of the DaemonSet. | `opentelemetry` | Recommended |
<!-- endsemconv -->

## Job

A Job creates one or more Pods and ensures that a specified number of them
successfully terminate.

**type:** `k8s.job`

**Description:** A Kubernetes Job object.

<!-- semconv k8s.job -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.job.uid` | string | The UID of the Job. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.job.name` | string | The name of the Job. | `opentelemetry` | Recommended |
<!-- endsemconv -->

## CronJob

A CronJob creates Jobs on a repeating schedule.

**type:** `k8s.cronjob`

**Description:** A Kubernetes CronJob object.

<!-- semconv k8s.cronjob -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `k8s.cronjob.uid` | string | The UID of the CronJob. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` | Recommended |
| `k8s.cronjob.name` | string | The name of the CronJob. | `opentelemetry` | Recommended |
<!-- endsemconv -->
