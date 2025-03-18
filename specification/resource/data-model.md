# Resource Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Identity](#identity)
  * [Navigation](#navigation)
  * [Telescoping](#telescoping)

<!-- tocstop -->

</details>

A Resource is an immutable representation of the entity producing telemetry as Attributes. For example, a process producing telemetry that is running in a container on Kubernetes has a Pod name, it is in a namespace and possibly is part of a Deployment which also has a name. All three of these attributes can be included in the Resource. Note that there are certain "standard attributes" that have prescribed meanings.

A resource is composed of 0 or more [`Entities`](../entities/README.md) and 0 or more attributes not associated with any entity.

Resource provides two important aspects for observability:

- It MUST *identify* an entity that is producing telemetry.
- It SHOULD allow users to determine *where* that entity resides within their infrastructure.

## Identity

Most resources are a composition of `Entity`. `Entity` is described [here](../entities/data-model.md), and includes its own notion of identity. The identity of a resource is the set
of entities contained within it. Two resources are considered different if one
contains an entity not found in the other.

Some resources include raw attributes in additon to Entities. Raw attributes are
considered identifying on a resource. That is, if the key-value pairs of
raw attributes are different, then you can assume the resource is different.

### Navigation

Implicit in the design of Resource and attributes is ensuring users are able to navigate their infrastructure, tools, UIs, etc. to find the *same* entity that telemetry is reporting against.  For example, in the definition above, we see a few components listed for one entity:

- A process
- A container
- A kubernetes pod name
- A namespace
- A deployment

By including identifying attributes of each of these, we can help users navigate through their `kubectl` or Kubernetes UIs to find the specific process generating telemetry.   This is as important as being able to uniquely identify one process from another.

> Aside: Observability signals SHOULD be actionable.  Knowing a process is struggling is not as useful as being able to scale up a deployment to take load off the struggling process.

If the only thing important to Resource was identity, we could simply use UUIDs.

### Telescoping

Within OpenTelemetry, we want to give users the flexibility to decide what information needs to be sent *with* observability signals and what information can be later joined.  We call this "telescoping identity" where users can decide how *small* or *large* the size of an OpenTelemetry resource will be on the wire (and correspondingly, how large data points are when stored, depending on storage solution).

For example, in the extreme, OpenTelemery could synthesize a UUID for every system which produces telemetry.  All identifying attributes for Resource and Entity could be sent via a side channel with known relationships to this UUID. While this would optimise the runtime generation and sending of telemetry, it comes at the cost of downstream storage systems needing to join data back together either at ingestion time or query time. For high performance use cases, e.g. alerting, these joins can be expensive.

In practice, users control Resource identity via the configuration of Resource Detection within SDKs and the collector. Users wishing for minimal identity will limit their resource detection just to a `service.instance.id`, for example. Some users highly customize resource detection with many concepts being appended.
