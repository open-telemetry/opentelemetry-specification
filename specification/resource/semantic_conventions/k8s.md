# Kubernetes

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

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.cluster.name | The name of the cluster. | `opentelemetry-cluster` |

## Namespace

Namespaces provide a scope for names. Names of objects need to be unique within
a namespace, but not across namespaces.

**type:** `k8s.namespace`

**Description:** A Kubernetes Namespace.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.namespace.name | The name of the namespace that the pod is running in. | `default` |

## Pod

The smallest and simplest Kubernetes object. A Pod represents a set of running
containers on your cluster.

**type:** `k8s.pod`

**Description:** A Kubernetes Pod object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.pod.uid | The uid of the Pod. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.pod.name | The name of the Pod. | `opentelemetry-pod-autoconf` |

## Container

A container specification in a Pod template. This type is intended to be used to
capture information such as name of a container in a Pod template which is different
from the name of the running container.

Note: This type is different from [container](./container.md), which corresponds
to a running container.

**type:** `k8s.container`

**Description:** A container in a [PodTemplate](https://kubernetes.io/docs/concepts/workloads/pods/#pod-templates).

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.container.name | The name of the Container in a Pod template. | `redis` |

## ReplicaSet

A ReplicaSet’s purpose is to maintain a stable set of replica Pods running at
any given time.

**type:** `k8s.replicaset`

**Description:** A Kubernetes ReplicaSet object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.replicaset.uid | The uid of the ReplicaSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.replicaset.name | The name of the ReplicaSet. | `opentelemetry` |

## Deployment

An API object that manages a replicated application, typically by running Pods
with no local state. Each replica is represented by a Pod, and the Pods are
distributed among the nodes of a cluster.

**type:** `k8s.deployment`

**Description:** A Kubernetes Deployment object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.deployment.uid | The uid of the Deployment. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.deployment.name | The name of the Deployment. | `opentelemetry` |

## StatefulSet

Manages the deployment and scaling of a set of Pods, and provides guarantees
about the ordering and uniqueness of these Pods.

**type:** `k8s.statefulset`

**Description:** A Kubernetes StatefulSet object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.statefulset.uid | The uid of the StatefulSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.statefulset.name | The name of the StatefulSet. | `opentelemetry` |

## DaemonSet

A DaemonSet ensures that all (or some) Nodes run a copy of a Pod.

**type:** `k8s.daemonset`

**Description:** A Kubernetes DaemonSet object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.daemonset.uid | The uid of the DaemonSet. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.daemonset.name | The name of the DaemonSet. | `opentelemetry` |

## Job

A Job creates one or more Pods and ensures that a specified number of them
successfully terminate.

**type:** `k8s.job`

**Description:** A Kubernetes Job object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.job.uid | The uid of the Job. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.job.name | The name of the Job. | `opentelemetry` |

## CronJob

A CronJob creates Jobs on a repeating schedule.

**type:** `k8s.cronjob`

**Description:** A Kubernetes CronJob object.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.cronjob.uid | The uid of the CronJob. | `275ecb36-5aa8-4c2a-9c47-d8bb681b9aff` |
| k8s.cronjob.name | The name of the CronJob. | `opentelemetry` |
