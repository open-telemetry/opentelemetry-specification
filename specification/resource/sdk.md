# Resource SDK

A [Resource](../overview.md#resources) is an immutable representation of the entity producing
telemetry. For example, a process producing telemetry that is running in a
container on Kubernetes has a Pod name, it is in a namespace and possibly is
part of a Deployment which also has a name. All three of these attributes can be
included in the `Resource`.

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
When associated with a [`MeterProvider`](../metrics/api.md#meter-interface),
all metrics produced by any `Meter` from the provider will be
associated with this `Resource`.

## Resource creation

The SDK must support two ways to instantiate new resources. Those are:

### Create

The interface MUST provide a way to create a new resource, from [`Attributes`](../common/common.md#attributes).
Examples include a factory method or a constructor for a resource
object. A factory method is recommended to enable support for cached objects.

Note that certain **required** `Resource` attributes MUST be set to a default value if they were not specified.
See [Attributes with Default Value](semantic_conventions/README.md#attributes-with-default-value).

Required parameters:

- [`Attributes`](../common/common.md#attributes)

### Merge

The interface MUST provide a way for a primary resource and a
secondary resource to be merged into a new resource.

Note: This is intended to be utilized for merging of resources whose attributes
come from different sources,
such as environment variables, or metadata extracted from the host or container.

The resulting resource MUST have all attributes that are on any of the two input resources.
Conflicts (i.e. a key for which attributes exist on both the primary and secondary resource)
MUST be handled as follows:

* If the value on the primary resource is an empty string, the result has the value of the secondary resource.
* Otherwise, the value of the primary resource is used.

Attribute key namespacing SHOULD be used to prevent collisions across different
resource detection steps.

Required parameters:

- the primary resource whose attributes take precedence.
- the secondary resource whose attributes will be merged in.

### The empty resource

It is recommended, but not required, to provide a way to quickly create an empty
resource.

Note that the OpenTelemetry project documents certain ["standard
attributes"](semantic_conventions/README.md) that have prescribed semantic meanings.

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

### Specifying resource information via an environment variable

The SDK MUST extract information from the `OTEL_RESOURCE_ATTRIBUTES` environment
variable and [merge](#merge) this, as the secondary resource, with any resource
information provided by the user, i.e. the user provided resource information
has higher priority.

The `OTEL_RESOURCE_ATTRIBUTES` environment variable will contain of a list of
key value pairs, and these are expected to be represented in a format matching
to the [W3C Baggage](https://github.com/w3c/baggage/blob/fdc7a5c4f4a31ba2a36717541055e551c2b032e4/baggage/HTTP_HEADER_FORMAT.md#header-content),
except that additional semi-colon delimited metadata is not supported, i.e.:
`key1=value1,key2=value2`. All attribute values MUST be considered strings.

## Resource operations

Resources are immutable. Thus, in addition to resource creation,
only the following operations should be provided:

### Retrieve attributes

The SDK should provide a way to retrieve a read only collection of attributes
associated with a resource. The attributes should consist of the name and values,
both of which should be strings.

There is no need to guarantee the order of the attributes.

The most common operation when retrieving attributes is to enumerate over them. As
such, it is recommended to optimize the resulting collection for fast
enumeration over other considerations such as a way to quickly retrieve a value
for a attribute with a specific key.
