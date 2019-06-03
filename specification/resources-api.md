# Resources API

[Resource](../terminology.md#resources) represents the entity producing
telemetry. The primary purpose of resources as a first-class concept in the API
is decoupling of discovery of resource information from exporters. This allows
for independent development and easy customization for users that need to
integrate with closed source environments. API MUST allow creation of
`Resources` and associating them with telemetry.

When used with distributed tracing resource can be associated with the
[Tracer](tracing-api.md#tracer) or individual
[SpanData](tracing-api.md#spandata). When associated with `Tracer`, all `Span`s
produced by this `Tracer` will automatically be associated with this `Resource`.
When associated with the `SpanData` explicitly for out-of-band spans -
`Resource` that is set on `Tracer` MUST be ignored.

**TODO**: explain how resource is associated with metrics.

## Resources SDK

TODO: notes how Resources API is extended when using `SDK`. https://github.com/open-telemetry/opentelemetry-specification/issues/61 

## Resource creation

API defines two ways to instantiate an instance of `Resource`. First, by
providing a collection of labels - method [Create](#create). The typical use of
this method is by creating resource from the list of labels taken from
environment variables, metadata API call response, or other sources.

Second, by merging two `Resource`s into a new one. The method [Merge](#merge) is
used when a `Resource` is constructed from multiple sources - metadata API call
for the host and environment variables for the container. So a single `Resource`
will contain labels for both.

Lastly, it is a good practice for API to allow easy creation of a default or
empty `Resource`.

Note that the OpenTelemetry project documents certain ["standard
labels"](../semantic-conventions.md) that have prescribed semantic meanings.

### Create

Creates a new `Resource` out of the collection of labels. This is a static
method.

Required parameter:

Collection of name/value labels where both name and value are strings.

### Merge

Creates a new `Resource` that is a combination of labels of two `Resource`s. For
example, from two `Resource`s - one representing the host and one representing a
container, resulting `Resource` will describe both.

Already set labels MUST NOT be overwritten unless they are empty string. Label
key namespacing SHOULD be used to prevent collisions across different resource
detection steps.


Required parameter:

`Resource` to merge into the one, on which the method was called.

## Resource operations

API defines a resource class with a single getter for the list of labels
associated with this resource. `Resource` object should be assumed immutable.

### GetLabels

Returns the read only collection of labels associated with this resource. Each
label is a string to string name value pair. The order of labels in collection
is not significant. The typical use of labels collection is enumeration so the
fast access to the label value by it's key is not a requirement.
