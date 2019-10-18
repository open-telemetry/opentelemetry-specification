# Resource Conventions

This section defines standard labels for [Resources](sdk-resource.md). The
majority of these labels are inherited from
[OpenCensus Resource standard](https://github.com/census-instrumentation/opencensus-specs/blob/master/resource/StandardResources.md).

* [Service](#service)
* [Compute Unit](#compute-unit)
  * [Container](#container)
* [Deployment Service](#deployment-service)
  * [Kubernetes](#kubernetes)
* [Compute Instance](#compute-instance)
  * [Host](#host)
* [Environment](#environment)
  * [Cloud](#cloud)
  * [Cluster](#cluster)

## TODOs

* Add more compute units: Process, Lambda Function, AppEngine unit, etc.
* Add Device (mobile) and Web Browser.
* Decide if lower case strings only.
* Consider to add optional/required for each label and combination of labels
  (e.g when supplying a k8s resource all k8s may be required).

## Service

**type:** `service`

**Description:** A service instance.

| Label  | Description  | Example  | Required? |
|---|---|---|---|
| service.name | Logical name of the service. <br/> MUST be the same for all instances of horizontally scaled services. | `shoppingcart` | Yes |
| service.namespace | A namespace for `service.name`.<br/>A string value having a meaning that helps to distinguish a group of services, for example the team name that owns a group of services. `service.name` is expected to be unique within the same namespace. The field is optional. If `service.namespace` is not specified in the Resource then `service.name` is expected to be unique for all services that have no explicit namespace defined (so the empty/unspecified namespace is simply one more valid namespace). Zero-length namespace string is assumed equal to unspecified namespace. | `Shop` | No |
| service.instance.uuid | UUID of the service instance (RFC 4122, string representation). <br/>MUST be unique for each instance of the same `service.name/service.namespace` pair and SHOULD be globally unique. Helps to distinguish instances of the same service that exist at the same time (e.g. instances of a horizontally scaled service). | `627cc493-f310-47de-96bd-71410b7dec09` | Yes |

## Compute Unit

Labels defining a compute unit (e.g. Container, Process, Lambda Function).

### Container

**type:** `container`

**Description:** A container instance.

| Label  | Description  | Example  |
|---|---|---|
| container.name | Container name. | `opentelemetry-autoconf` |
| container.image.name | Name of the image the container was built on. | `gcr.io/opentelemetry/operator` |
| container.image.tag | Container image tag. | `0.1` |

## Deployment Service

Labels defining a deployment service (e.g. Kubernetes).

### Kubernetes

**type:** `k8s`

**Description:** A Kubernetes resource.

| Label  | Description  | Example  |
|---|---|---|
| k8s.cluster.name | The name of the cluster that the pod is running in. | `opentelemetry-cluster` |
| k8s.namespace.name | The name of the namespace that the pod is running in. | `default` |
| k8s.pod.name | The name of the pod. | `opentelemetry-pod-autoconf` |
| k8s.deployment.name | The name of the deployment. | `opentelemetry` |

## Compute Instance

Labels defining a computing instance (e.g. host).

### Host

**type:** `host`

**Description:** A host is defined as a general computing instance.

| Label  | Description  | Example  |
|---|---|---|
| host.hostname | Hostname of the host.<br/> It contains what the `hostname` command returns on the host machine. | `opentelemetry-test` |
| host.id | Unique host id.<br/> For Cloud this must be the instance_id assigned by the cloud provider | `opentelemetry-test` |
| host.name | Name of the host.<br/> It may contain what `hostname` returns on Unix systems, the fully qualified, or a name specified by the user. | `opentelemetry-test` |
| host.type | Type of host.<br/> For Cloud this must be the machine type.| `n1-standard-1` |

## Environment

Labels defining a running environment (e.g. Cloud, Data Center).

### Cloud

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

| Label  | Description  | Example  |
|---|---|---|
| cloud.provider | Name of the cloud provider.<br/> Example values are aws, azure, gcp. | `gcp` |
| cloud.account.id | The cloud account id used to identify different entities. | `opentelemetry` |
| cloud.region | A specific geographical location where different entities can run | `us-central1` |
| cloud.zone | Zones are a sub set of the region connected through low-latency links.<br/> In aws it is called availability-zone. | `us-central1-a` |
