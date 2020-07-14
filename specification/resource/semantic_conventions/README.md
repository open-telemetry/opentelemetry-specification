# Resource Semantic Conventions

This document defines standard attributes for resources. These attributes are typically used in the [Resource](../sdk.md) and are also recommended to be used anywhere else where there is a need to describe a resource in a consistent manner. The majority of these attributes are inherited from
[OpenCensus Resource standard](https://github.com/census-instrumentation/opencensus-specs/blob/master/resource/StandardResources.md).

- [Service](#service)
- [Telemetry SDK](#telemetry-sdk)
- [Compute Unit](#compute-unit)
  * [Container](#container)
  * [Function as a Service](#function-as-a-service)
  * [Process](#process)
- [Deployment Service](#deployment-service)
  * [Kubernetes](#kubernetes)
- [Compute Instance](#compute-instance)
  * [Host](#host)
- [Environment](#environment)
  * [Cloud](#cloud)

<!-- tocstop -->

## TODOs

* Add more compute units: AppEngine unit, etc.
* Add Device (mobile) and Web Browser.
* Decide if lower case strings only.
* Consider to add optional/required for each attribute and combination of attributes
  (e.g when supplying a k8s resource all k8s may be required).

### Document Conventions

Attributes are grouped logically by the type of the concept that they described. Attributes in the same group have a common prefix that ends with a dot. For example all attributes that describe Kubernetes properties start with "k8s."

Certain attribute groups in this document have a **Required** column. For these groups if any attribute from the particular group is present in the Resource then all attributes that are marked as Required MUST be also present in the Resource. However it is also valid if the entire attribute group is omitted (i.e. none of the attributes from the particular group are present even though some of them are marked as Required in this document).

## Service

**type:** `service`

**Description:** A service instance.

| Attribute  | Description  | Example  | Required? |
|---|---|---|---|
| service.name | Logical name of the service. <br/> MUST be the same for all instances of horizontally scaled services. | `shoppingcart` | Yes |
| service.namespace | A namespace for `service.name`.<br/>A string value having a meaning that helps to distinguish a group of services, for example the team name that owns a group of services. `service.name` is expected to be unique within the same namespace. The field is optional. If `service.namespace` is not specified in the Resource then `service.name` is expected to be unique for all services that have no explicit namespace defined (so the empty/unspecified namespace is simply one more valid namespace). Zero-length namespace string is assumed equal to unspecified namespace. | `Shop` | No |
| service.instance.id | The string ID of the service instance. <br/>MUST be unique for each instance of the same `service.namespace,service.name` pair (in other words `service.namespace,service.name,service.id` triplet MUST be globally unique). The ID helps to distinguish instances of the same service that exist at the same time (e.g. instances of a horizontally scaled service). It is preferable for the ID to be persistent and stay the same for the lifetime of the service instance, however it is acceptable that the ID is ephemeral and changes during important lifetime events for the service (e.g. service restarts). If the service has no inherent unique ID that can be used as the value of this attribute it is recommended to generate a random Version 1 or Version 4 RFC 4122 UUID (services aiming for reproducible UUIDs may also use Version 5, see RFC 4122 for more recommendations). | `627cc493-f310-47de-96bd-71410b7dec09` | Yes |
| service.version | The version string of the service API or implementation as defined in [Version Attributes](#version-attributes). | `semver:2.0.0` | No |

Note: `service.namespace` and `service.name` are not intended to be concatenated for the purpose of forming a single globally unique name for the service. For example the following 2 sets of attributes actually describe 2 different services (despite the fact that the concatenation would result in the same string):

```
# Resource attributes that describes a service.
namespace = Company.Shop
service.name = shoppingcart
```

```
# Another set of resource attributes that describe a different service.
namespace = Company
service.name = Shop.shoppingcart
```

## Telemetry SDK

**type:** `telemetry.sdk`

**Description:** The telemetry SDK used to capture data recorded by the instrumentation libraries.

The default OpenTelemetry SDK provided by the OpenTelemetry project MUST set `telemetry.sdk.name`
to the value `opentelemetry`.

If another SDK, like a fork or a vendor-provided implementation, is used, this SDK MUST set the attribute
`telemetry.sdk.name` to the fully-qualified class or module name of this SDK's main entry point
or another suitable identifier depending on the language.
The identifier `opentelemetry` is reserved and MUST NOT be used in this case.
The identifier SHOULD be stable across different versions of an implementation.

| Attribute  | Description  | Example  | Required? |
|---|---|---|---|
| telemetry.sdk.name | The name of the telemetry SDK as defined above. | `opentelemetry` | No |
| telemetry.sdk.language | The language of the telemetry SDK.<br/> One of the following values MUST be used, if one applies: "cpp", "dotnet", "erlang", "go", "java", "nodejs", "php", "python", "ruby", "webjs" | `java` | No |
| telemetry.sdk.version | The version string of the telemetry SDK as defined in [Version Attributes](#version-attributes). | `semver:1.2.3` | No |

## Compute Unit

Attributes defining a compute unit (e.g. Container, Process, Function as a Service).

### Container

**type:** `container`

**Description:** A container instance.

| Attribute  | Description  | Example  |
|---|---|---|
| container.name | Container name. | `opentelemetry-autoconf` |
| container.id | Container id. Usually a UUID, as for example used to [identify Docker containers][]. The UUID might be abbreviated. | `a3bf90e006b2` |
| container.image.name | Name of the image the container was built on. | `gcr.io/opentelemetry/operator` |
| container.image.tag | Container image tag. | `0.1` |

[identify Docker containers]: https://docs.docker.com/engine/reference/run/#container-identification
### Function as a Service

**type:** `faas`

**Description:** A serverless instance.

| Label  | Description  | Example  | Required |
|---|---|---|--|
| faas.name | The name of the function being executed. | `my-function` | Yes |
| faas.id | The unique name of the function being executed. <br /> For example, in AWS Lambda this field corresponds to the [ARN] value, in GCP to the URI of the resource, and in Azure to the [FunctionDirectory] field. | `arn:aws:lambda:us-west-2:123456789012:function:my-function` | Yes |
| faas.version | The version string of the function being executed as defined in [Version Attributes](#version-attributes). | `semver:2.0.0` | No |
| faas.instance | The execution environment ID as a string. | `my-function:instance-0001` | No |

Note: The resource attribute `faas.instance` differs from the span attribute `faas.execution`. For more information see the [Semantic conventions for FaaS spans](../../trace/semantic_conventions/faas.md#difference-between-execution-and-instance).

[ARN]:https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
[FunctionDirectory]: https://github.com/Azure/azure-functions-host/wiki/Retrieving-information-about-the-currently-running-function

### Process

**type:** `process`

**Description:** An operating system process.

| Attribute  | Description  | Example  | Required |
|---|---|---|--|
| process.pid | Process identifier (PID). | `1234` | Yes |
| process.executable.name | The name of the process executable. On Linux based systems, can be set to the `Name` in `proc/[pid]/status`. On Windows, can be set to the base name of `GetProcessImageFileNameW`. | `otelcol` | See below |
| process.executable.path | The full path to the process executable. On Linux based systems, can be set to the target of `proc/[pid]/exe`. On Windows, can be set to the result of `GetProcessImageFileNameW`. | `/usr/bin/cmd/otelcol` | See below |
| process.command | The command used to launch the process (i.e. the command name). On Linux based systems, can be set to the zeroth string in `proc/[pid]/cmdline`. On Windows, can be set to the first parameter extracted from `GetCommandLineW`. | `cmd/otelcol` | See below |
| process.command_line | The full command used to launch the process. The value can be either a list of strings representing the ordered list of arguments, or a single string representing the full command. On Linux based systems, can be set to the list of null-delimited strings extracted from `proc/[pid]/cmdline`. On Windows, can be set to the result of `GetCommandLineW`. | Linux: `[ cmd/otecol, --config=config.yaml ]`, Windows: `cmd/otecol --config=config.yaml` | See below |
| process.owner | The username of the user that owns the process. | `root` | No |

At least one of `process.executable.name`, `process.executable.path`, `process.command`, or `process.command_line` is required.

## Deployment Service

Attributes defining a deployment service (e.g. Kubernetes).

### Kubernetes

**type:** `k8s`

**Description:** A Kubernetes resource.

| Attribute  | Description  | Example  |
|---|---|---|
| k8s.cluster.name | The name of the cluster that the pod is running in. | `opentelemetry-cluster` |
| k8s.namespace.name | The name of the namespace that the pod is running in. | `default` |
| k8s.pod.name | The name of the pod. | `opentelemetry-pod-autoconf` |
| k8s.deployment.name | The name of the deployment. | `opentelemetry` |

## Compute Instance

Attributes defining a computing instance (e.g. host).

### Host

**type:** `host`

**Description:** A host is defined as a general computing instance.

| Attribute  | Description  | Example  |
|---|---|---|
| host.hostname | Hostname of the host.<br/> It contains what the `hostname` command returns on the host machine. | `opentelemetry-test` |
| host.id | Unique host id.<br/> For Cloud this must be the instance_id assigned by the cloud provider | `opentelemetry-test` |
| host.name | Name of the host.<br/> It may contain what `hostname` returns on Unix systems, the fully qualified, or a name specified by the user. | `opentelemetry-test` |
| host.type | Type of host.<br/> For Cloud this must be the machine type.| `n1-standard-1` |
| host.image.name | Name of the VM image or OS install the host was instantiated from. | `infra-ami-eks-worker-node-7d4ec78312`, `CentOS-8-x86_64-1905` |
| host.image.id | VM image id. For Cloud, this value is from the provider. | `ami-07b06b442921831e5` |
| host.image.version | The version string of the VM image as defined in [Version Attributes](#version-attributes). | `0.1` |

## Environment

Attributes defining a running environment (e.g. Cloud, Data Center).

### Cloud

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

| Attribute  | Description  | Example  |
|---|---|---|
| cloud.provider | Name of the cloud provider.<br/> Example values are aws, azure, gcp. | `gcp` |
| cloud.account.id | The cloud account id used to identify different entities. | `opentelemetry` |
| cloud.region | A specific geographical location where different entities can run | `us-central1` |
| cloud.zone | Zones are a sub set of the region connected through low-latency links.<br/> In aws it is called availability-zone. | `us-central1-a` |

## Version Attributes

Version attributes such as `service.version` and `library.version` are values of type `string`,
with naming schemas hinting at the type of a version, such as the following:

- `semver:1.2.3` (a semantic version)
- `git:8ae73a` (a git sha hash)
- `0.0.4.2.20190921` (a untyped version)

The type and version value MUST be separated by a colon character `:`.
