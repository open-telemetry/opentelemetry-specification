<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
weight: 3
--->

# Resource SDK

**Status**: [Stable](../document-status.md) except where otherwise specified

A [Resource](../overview.md#resources) is an immutable representation of the
observed entity for which telemetry is being produced. A Resource is composed of
a collection of [Entities](#entities) and a set of
[Attributes](../common/README.md#attribute).
For example, a process running in a container on Kubernetes has a Pod name, it
is in a namespace and possibly is part of a Deployment which also has a name.
Each of these may be represented as an `Entity` within the `Resource`, and all of
their attributes are included in the `Resource`. Note that there are certain
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

Similarly, when used with logs,
a resource can be associated with a `LoggerProvider`.
When associated with a [`LoggerProvider`](../logs/api.md#loggerprovider),
all log records produced by any `Logger` from the provider will be
associated with this `Resource`.
## Entities

**Status**: [Development](../document-status.md)

An Entity represents an object of interest associated with produced telemetry.
For example, a service, a host, a container, or a Kubernetes pod are all
entities. An Entity has:

- **Type**: A string that defines the type of the entity (e.g. `"service"`,
  `"host"`). MUST NOT change during the lifetime of the entity.
- **Identifying attributes**: Attributes that uniquely identify the entity.
  MUST NOT change during the lifetime of the entity. MUST contain at least one
  attribute. MUST be detected synchronously during
  SDK initialization.
- **Descriptive attributes**: Non-identifying attributes of the entity. MAY
  change over the lifetime of the entity. MAY be empty.

A Resource MAY contain zero or more entities. The identifying and descriptive
attributes of all entities in a Resource MUST be included in the Resource's
attributes. When entities are present, Resource identity is determined by the
collection of all attributes whose keys are NOT found in any entity's
descriptive attribute keys. When no entities are present, Resource identity is
the collection of all attributes (both keys and values), preserving backwards
compatibility.

See [Entity Data Model](../entities/data-model.md) and
[OTEP 264: Resource and Entities](../../oteps/entities/0264-resource-and-entities.md)
for more details.

## SDK-provided resource attributes

The SDK MUST provide access to a Resource with at least the attributes listed at
[Semantic Attributes with SDK-provided Default Value](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#semantic-attributes-with-sdk-provided-default-value).
This resource MUST be associated with a `TracerProvider`, `MeterProvider`,
or `LoggerProvider` if another resource was not explicitly specified.

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
can then be associated with `TracerProvider`, `MeterProvider`, or
`LoggerProvider` instances as described above.

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

### Detecting entity information from the environment

**Status**: [Development](../document-status.md)

Entity detectors are responsible for detecting entities that are associated with
the current instance of the SDK. For example, an entity detector may detect a
service entity for the current SDK, or the process or host it is running on.

An entity detector MUST implement a `Detect` method. `Detect` accepts no
arguments and returns a single [Entity](#entities).

Entity detectors MUST detect identifying attributes synchronously. Entity
detectors MAY detect descriptive attributes asynchronously (e.g. via a future
or promise that resolves after initialization). When descriptive attributes are
detected asynchronously, the entity MUST be returned with its identifying
attributes immediately, and the descriptive attributes MUST be merged into the
Resource when they become available.

Entity detectors SHOULD follow the same naming conventions as
[resource detectors](#resource-detector-name).

Entity detection logic is expected to complete quickly since this code will be
run during application initialization. Errors should be handled as specified in
the [Error Handling
principles](../error-handling.md#basic-error-handling-principles). The failure
to detect any entity information MUST NOT be considered an error, whereas an
error that occurs during an attempt to detect entity information SHOULD be
considered an error.

### Resource Provider

**Status**: [Development](../document-status.md)

The Resource Provider is a component responsible for running all configured
resource detectors and entity detectors and constructing a `Resource` for the
SDK.

The Resource Provider MUST:

- Run all configured resource detectors and entity detectors.
- Resolve conflicts when multiple entity detectors detect entities of the same
  type, using a user-controlled priority order.
- Construct a `Resource` from the detected entities and resource attributes.

When using entity detectors and resource detectors together, entity merging MUST
occur first, followed by resource detector merging using existing merge
semantics. The entity merging algorithm is as follows:

- Construct a set of detected entities, `E`.
- All entity detectors are sorted by priority (highest first).
- For each entity detector, detect entities.
  - For each detected entity:
    - If an entity with the same type already exists in `E`:
      - If the identity and `schema_url` are the same, merge the descriptive
        attributes (existing values take precedence).
      - Otherwise, drop the new entity.
    - Otherwise, add the entity to `E`.
- Construct a `Resource` from the set `E`.
  - If all entities within `E` have the same `schema_url`, set the Resource's
    `schema_url` to match.
  - Otherwise, leave the Resource `schema_url` empty.

When descriptive attributes are detected asynchronously, the priority for
merging MUST be determined by the configured order of the entity detectors, not
by the order in which asynchronous results resolve. If a higher-priority
detector's descriptive attributes resolve after a lower-priority detector's,
the higher-priority detector's values MUST still take precedence.

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
key value pairs, represented as `key1=value1,key2=value2`.
All attribute values MUST be considered strings. The `,` and `=` characters
in keys and values MUST be percent encoded. Other characters MAY be
[percent-encoded](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1),
e.g. values outside the ANSI characters set.

In case of any error, e.g. failure during the decoding process, the entire environment
variable value SHOULD be discarded and an error SHOULD be reported following the
[Error Handling principles](../error-handling.md#basic-error-handling-principles).

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
