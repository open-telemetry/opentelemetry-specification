# Resource SDK

A [Resource](overview.md#resources) represents the entity producing telemetry.
The primary purpose of resources as a first-class concept in the API is
decoupling of discovery of resource information from exporters. This allows for
independent development and easy customization for users that need to integrate
with closed source environments. API MUST allow for creation of `Resources` and
for associating them with telemetry.

When used with distributed tracing, a resource can be associated with the
[TracerSdk](sdk-tracing.md#tracer-sdk). When associated with `TracerSdk`, all
`Span`s produced by the `Tracer`, that is implemented by this `TracerSdk`, will
automatically be associated with this `Resource`.

When used with metrics, a resource can be associated with the
[MeterSdk](sdk-metrics.md#meter-sdk). When associated with `MeterSdk`, all
`Metrics` produced by this `Meter`, that is implemented by this `MeterSdk`, will
automatically be associated with this `Resource`.

## Resource creation

The API interface must support two ways to instantiate new resources. Those are:

### Create

The interface MUST provide a way to create a new resource, from a collection of
labels. Examples include a factory method or a constructor for a resource
object. A factory method is recommended to enable support for cached objects.

Required parameters:

- a collection of name/value labels, where name and value are both strings.

### Merge

The interface MUST provide a way for a primary resource to merge with a
secondary resource, resulting in the creation of a brand new resource. The
original resources should be unmodified.

This is utilized for merging of resources whose labels come from different
sources, such as environment variables, or metadata extracted from the host or
container.

Already set labels MUST NOT be overwritten unless they are the empty string.

Label key namespacing SHOULD be used to prevent collisions across different
resource detection steps.

Required parameters:

- the primary resource whose labels takes precedence.
- the secondary resource whose labels will be merged.

### The empty resource

It is recommended, but not required, to provide a way to quickly create an empty
resource.

Note that the OpenTelemetry project documents certain ["standard
labels"](data-semantic-conventions.md) that have prescribed semantic meanings.

## Resource operations

In addition to resource creation, the following operations should be provided:

### Retrieve labels

The API should provide a way to retrieve a read only collection of labels
associated with a resource. The labels should consist of the name and values,
both of which should be strings.

There is no need to guarantee the order of the labels.

The most common operation when retrieving labels is to enumerate over them. As
such, it is recommended to optimize the resulting collection for fast
enumeration over other considerations such as a way to quickly retrieve a value
for a label with a specific key.
