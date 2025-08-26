<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
weight: 3
--->

# Resource SDK

**Status**: [Stable](../document-status.md) except where otherwise specified

A [Resource](../overview.md#resources) is an immutable representation of the entity producing
telemetry as [Attributes](../common/README.md#attribute).
For example, a process producing telemetry that is running in a
container on Kubernetes has a Pod name, it is in a namespace and possibly is
part of a Deployment which also has a name. All three of these attributes can be
included in the `Resource`. Note that there are certain
[attributes](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md)
that have prescribed meanings.

The primary purpose of resources as a first-class concept in the SDK is
decoupling of discovery of resource information from exporters. This allows for
independent development and easy customization for users that need to integrate
with closed source environments. The SDK MUST allow for creation of `Resources` and
for associating them with telemetry.

When used with distributed tracing, a resource can be associated with the
[TracerProvider](../trace/api.md#tracerprovider) when the TracerProvider is created.
That association cannot be changed later.
When associated with a `TracerProvider`,
all `Span`s produced by any `Tracer` from the provider MUST be associated with this `Resource`.

Analogous to distributed tracing, when used with metrics,
a resource can be associated with a `MeterProvider`.
When associated with a [`MeterProvider`](../metrics/api.md#meterprovider),
all metrics produced by any `Meter` from the provider will be
associated with this `Resource`.

## SDK-provided resource attributes

The SDK MUST provide access to a Resource with at least the attributes listed at
[Semantic Attributes with SDK-provided Default Value](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#semantic-attributes-with-sdk-provided-default-value).
This resource MUST be associated with a `TracerProvider` or `MeterProvider`
if another resource was not explicitly specified.

Note: This means that it is possible to create and associate a resource that
does not have all or any of the SDK-provided attributes present. However, that
does not happen by default. If a user wants to combine custom attributes with
the default resource, they can use [`Merge`](#merge) with their custom resource
or specify their attributes by implementing
[Custom resource detectors](#detecting-resource-information-from-the-environment)
instead of explicitly associating a resource.

## Resource creation

The SDK must support two ways to instantiate new resources. Those are:

### Create

The interface MUST provide a way to create a new resource, from [`Attributes`](../common/README.md#attribute).
Examples include a factory method or a constructor for a resource
object. A factory method is recommended to enable support for cached objects.

Required parameters:

- [`Attributes`](../common/README.md#attribute)
- [since 1.4.0] `schema_url` (optional): Specifies the Schema URL that should be
  recorded in the emitted resource. If the `schema_url` parameter is unspecified
  then the created resource will have an empty Schema URL.

### Merge

The interface MUST provide a way for an old resource and an
updating resource to be merged into a new resource.

Note: This is intended to be utilized for merging of resources whose attributes
come from different sources,
such as environment variables, or metadata extracted from the host or container.

The resulting resource MUST have all attributes that are on any of the two input resources.
If a key exists on both the old and updating resource, the value of the updating
resource MUST be picked (even if the updated value is empty).

The resulting resource will have the Schema URL calculated as follows:

- If the old resource's Schema URL is empty then the resulting resource's Schema
  URL will be set to the Schema URL of the updating resource,
- Else if the updating resource's Schema URL is empty then the resulting
  resource's Schema URL will be set to the Schema URL of the old resource,
- Else if the Schema URLs of the old and updating resources are the same then
  that will be the Schema URL of the resulting resource,
- Else this is a merging error (this is the case when the Schema URL of the old
  and updating resources are not empty and are different). The resulting resource is
  undefined, and its contents are implementation-specific.

Required parameters:

- the old resource
- the updating resource whose attributes take precedence

### The empty resource

It is recommended, but not required, to provide a way to quickly create an empty
resource.

### Detecting resource information from the environment

Custom resource detectors related to generic platforms (e.g. Docker, Kubernetes)
or vendor specific environments (e.g. EKS, AKS, GKE) MUST be implemented as
packages separate from the SDK.

Resource detector packages MUST provide a method that returns a resource. This
can then be associated with `TracerProvider` or `MeterProvider` instances as
described above.

Resource detector packages MAY detect resource information from multiple
possible sources and merge the result using the `Merge` operation described
above.

Resource detection logic is expected to complete quickly since this code will be
run during application initialization. Errors should be handled as specified in
the [Error Handling
principles](../error-handling.md#basic-error-handling-principles). Note the
failure to detect any resource information MUST NOT be considered an error,
whereas an error that occurs during an attempt to detect resource information
SHOULD be considered an error.

Resource detectors that populate resource attributes according to OpenTelemetry
semantic conventions MUST ensure that the resource has a Schema URL set to a
value that matches the semantic conventions. Empty Schema URL SHOULD be used if
the detector does not populate the resource with any known attributes that have
a semantic convention or if the detector does not know what attributes it will
populate (e.g. the detector that reads the attributes from environment values
will not know what Schema URL to use). If multiple detectors are combined and
the detectors use different non-empty Schema URL it MUST be an error since it is
impossible to merge such resources. The resulting resource is undefined, and its
contents are implementation specific.

#### Resource detector name

**Status**: [Development](../document-status.md)

Resource detectors SHOULD have a unique name for reference in configuration. For
example, users list and configure individual resource detectors by name
in [declarative configuration](../configuration/README.md#declarative-configuration).
Names SHOULD be [snake case](https://en.wikipedia.org/wiki/Snake_case) and
consist of lowercase alphanumeric and `_` characters, which ensures they conform
to declarative
configuration [property name requirements](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/CONTRIBUTING.md#property-name-case).

Resource detector names SHOULD reflect
the [root namespace](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/naming.md#general-naming-considerations)
of attributes they populate. For example, a resource detector named `os`
populates `os.*` attributes. Resource detectors which populate attributes from
multiple root namespaces SHOULD choose a name which appropriately conveys their
purpose.

An SDK which identifies multiple resource detectors with the same name SHOULD
report an error. In order to limit collisions, resource detectors SHOULD
document their name in a manner which is easily discoverable. Authors of
resource detectors should check existing resource detectors to ensure their
target name isn't already in use. Additionally, the following detector names are
reserved for built-in resource detectors published with language SDKs:

* `container`:
  Populates [container.*](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/container.md)
  attributes.
* `host`:
  Populates [host.*](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/host.md) and [os.*](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/os.md)
  attributes.
* `process`:
  Populates [process.*](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/process.md)
  attributes.
* `service`: Populates `service.name` based
  on [OTEL_SERVICE_NAME](../configuration/sdk-environment-variables.md#general-sdk-configuration)
  environment variable; populates `service.instance.id`
  as [defined here](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/registry/attributes/service.md#service-attributes).

### Specifying resource information via an environment variable

The SDK MUST extract information from the `OTEL_RESOURCE_ATTRIBUTES` environment
variable and [merge](#merge) this, as the secondary resource, with any resource
information provided by the user, i.e. the user provided resource information
has higher priority.

The `OTEL_RESOURCE_ATTRIBUTES` environment variable will contain of a list of
key value pairs, and these are expected to be represented in a format matching
to the [W3C Baggage](https://www.w3.org/TR/baggage/#header-content), except that additional
semi-colon delimited metadata is not supported, i.e.: `key1=value1,key2=value2`.
All attribute values MUST be considered strings and characters outside the
`baggage-octet` range MUST be percent-encoded.

## Resource operations

Resources are immutable. Thus, in addition to resource creation,
only the following operations should be provided:

### Retrieve attributes

The SDK should provide a way to retrieve a read only collection of attributes
associated with a resource.

There is no need to guarantee the order of the attributes.

The most common operation when retrieving attributes is to enumerate over them. As
such, it is recommended to optimize the resulting collection for fast
enumeration over other considerations such as a way to quickly retrieve a value
for a attribute with a specific key.
