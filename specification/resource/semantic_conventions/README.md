# Resource Semantic Conventions

This document defines standard attributes for resources. These attributes are typically used in the [Resource](../sdk.md) and are also recommended to be used anywhere else where there is a need to describe a resource in a consistent manner. The majority of these attributes are inherited from
[OpenCensus Resource standard](https://github.com/census-instrumentation/opencensus-specs/blob/master/resource/StandardResources.md).

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [TODOs](#todos)
- [Document Conventions](#document-conventions)
- [Service](#service)
- [Telemetry SDK](#telemetry-sdk)
- [Compute Unit](#compute-unit)
- [Compute Instance](#compute-instance)
- [Environment](#environment)
- [Version attributes](#version-attributes)

<!-- tocstop -->

## TODOs

* Add more compute units: AppEngine unit, etc.
* Add Device (mobile) and Web Browser.
* Decide if lower case strings only.
* Consider to add optional/required for each attribute and combination of attributes
  (e.g when supplying a k8s resource all k8s may be required).

## Document Conventions

Attributes are grouped logically by the type of the concept that they described. Attributes in the same group have a common prefix that ends with a dot. For example all attributes that describe Kubernetes properties start with "k8s."

Certain attribute groups in this document have a **Required** column. For these groups if any attribute from the particular group is present in the Resource then all attributes that are marked as Required MUST be also present in the Resource. However it is also valid if the entire attribute group is omitted (i.e. none of the attributes from the particular group are present even though some of them are marked as Required in this document).

## Service

**type:** `service`

**Description:** A service instance.

| Attribute  | Description  | Example  | Required? |
|---|---|---|---|
| service.name | Logical name of the service. <br/> MUST be the same for all instances of horizontally scaled services. | `shoppingcart` | Yes |
| service.namespace | A namespace for `service.name`.<br/>A string value having a meaning that helps to distinguish a group of services, for example the team name that owns a group of services. `service.name` is expected to be unique within the same namespace. The field is optional. If `service.namespace` is not specified in the Resource then `service.name` is expected to be unique for all services that have no explicit namespace defined (so the empty/unspecified namespace is simply one more valid namespace). Zero-length namespace string is assumed equal to unspecified namespace. | `Shop` | No |
| service.instance.id | The string ID of the service instance. <br/>MUST be unique for each instance of the same `service.namespace,service.name` pair (in other words `service.namespace,service.name,service.instance.id` triplet MUST be globally unique). The ID helps to distinguish instances of the same service that exist at the same time (e.g. instances of a horizontally scaled service). It is preferable for the ID to be persistent and stay the same for the lifetime of the service instance, however it is acceptable that the ID is ephemeral and changes during important lifetime events for the service (e.g. service restarts). If the service has no inherent unique ID that can be used as the value of this attribute it is recommended to generate a random Version 1 or Version 4 RFC 4122 UUID (services aiming for reproducible UUIDs may also use Version 5, see RFC 4122 for more recommendations). | `627cc493-f310-47de-96bd-71410b7dec09` | Yes |
| service.version | The version string of the service API or implementation. | `2.0.0` | No |

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
| telemetry.sdk.version | The version string of the telemetry SDK. | `1.2.3` | No |
| telemetry.auto.version | The version string of the auto instrumentation agent, if used. | `1.2.3` | No |

## Compute Unit

Attributes defining a compute unit (e.g. Container, Process, Function as a Service):

- [Container](./container.md)
- [Function as a Service](./faas.md)
- [Process](./process.md)

## Compute Instance

Attributes defining a computing instance (e.g. host):

- [Host](./host.md)

## Environment

Attributes defining a running environment (e.g. Operating System, Cloud, Data Center, Deployment Service):

- [Operating System](./os.md)
- [Cloud](./cloud.md)
- Deployment:
  - [Deployment Environment](./deployment_environment.md)
  - [Kubernetes](./k8s.md)

## Version attributes

Version attributes, such as `service.version`, are values of type `string`. They are
the exact version used to identify an artifact. This may be a semantic version, e.g., `1.2.3`, git hash, e.g.,
`8ae73a`, or an arbitrary version string, e.g., `0.1.2.20210101`, whatever was used when building the artifact.
