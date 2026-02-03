# Entities Data Model, Part 1

This is a proposal of a data model to represent entities. The purpose of the data model
is to have a common understanding of what an entity is, what data needs to be recorded,
transferred, stored and interpreted by an entity observability system.

<!-- toc -->

- [Motivation](#motivation)
- [Design Principles](#design-principles)
- [Data Model](#data-model)
  * [Minimally Sufficient ID](#minimally-sufficient-id)
  * [Examples of Entities](#examples-of-entities)
- [Entity Events](#entity-events)
  * [EntityState Event](#entitystate-event)
  * [EntityDelete Event](#entitydelete-event)
- [Entity Identification](#entity-identification)
  * [LID, GID and IDCONTEXT](#lid-gid-and-idcontext)
  * [Semantic Conventions](#semantic-conventions)
  * [Examples](#examples)
    + [Process in a Host](#process-in-a-host)
    + [Process in Kubernetes](#process-in-kubernetes)
    + [Host in Cloud Account](#host-in-cloud-account)
- [Prototypes](#prototypes)
- [Prior Art](#prior-art)
- [Alternatives](#alternatives)
  * [Different ID Structure](#different-id-structure)
  * [No Entity Events](#no-entity-events)
  * [Merge Entity Events data into Resource](#merge-entity-events-data-into-resource)
  * [Hierarchical ID Field](#hierarchical-id-field)
- [Open questions](#open-questions)
  * [Attribute Data Type](#attribute-data-type)
  * [Classes of Entity Types](#classes-of-entity-types)
  * [Multiple Observers](#multiple-observers)
  * [Is Type part of Entity's identity?](#is-type-part-of-entitys-identity)
  * [Choosing from Multiple IDs](#choosing-from-multiple-ids)
- [Future Work](#future-work)
- [References](#references)

<!-- tocstop -->

## Motivation

This data model sets the foundation for adding entities to OpenTelemetry. The data model
is largely borrowed from
[the initial proposal](https://docs.google.com/document/d/1VUdBRInLEhO_0ABAoiLEssB1CQO_IcD5zDnaMEha42w/edit)
that was accepted for entities SIG formation.

This OTEP is step 1 in introducing the entities data model. Follow up OTEPs will add
further data model definitions, including the linking of Resource information
to entities.

## Design Principles

- Consistency with the rest of OpenTelemetry is important. We heavily favor solutions
  that look and feel like other OpenTelemetry data models.

- Meaningful (especially human-readable) IDs are more valuable than random-generated IDs.
  Long-lived IDs that survive state changes (e.g. entity restarts) are more valuable than
  short-lived, ephemeral IDs.
  See [the need for navigation](https://docs.google.com/document/d/1Xd1JP7eNhRpdz1RIBLeA1_4UYPRJaouloAYqldCeNSc/edit#heading=h.fut2c2pec5wa).

- We cannot make an assumption that the entirety of information that is necessary for
  global identification of an entity is available at once, in one place. This knowledge
  may be distributed across multiple participants and needs to be combined to form an
  identifier that is globally unique.

- Semantic conventions must bring as much order as possible to telemetry, however they
  cannot be too rigid and prevent real-world use cases.

## Data Model

We propose a new concept of Entity.

Entity represents an object of interest associated with produced telemetry:
traces, metrics or logs.

For example, telemetry produced using OpenTelemetry SDK is normally associated with
a Service entity. Similarly, OpenTelemetry defines system metrics for a host. The Host is the
entity we want to associate metrics with in this case.

Entities may be also associated with produced telemetry indirectly.
For example a service that produces
telemetry is also related with a process in which the service runs, so we say that
the Service entity is related to the Process entity. The process normally also runs
on a host, so we say that the Process entity is related to the Host entity.

Note: subsequent OTEPs will define how the entities are associated with
traces, metrics and logs and how relations between entities will be specified.
See [Future Work](#future-work).

The data model below defines a logical model for an entity (irrespective of the physical
format and encoding of how entity data is recorded).

<table>
   <tr>
    <td><strong>Field</strong>
    </td>
    <td><strong>Type</strong>
    </td>
    <td><strong>Description</strong>
    </td>
   </tr>
   <tr>
    <td>Type
    </td>
    <td>string
    </td>
    <td>Defines the type of the entity. MUST not change during the
lifetime of the entity. For example: "service" or "host". This field is
required and MUST not be empty for valid entities.
    </td>
   </tr>
   <tr>
    <td>Id
    </td>
    <td>map&lt;string, attribute&gt;
    </td>
    <td>Attributes that identify the entity.
<p>
MUST not change during the lifetime of the entity. The Id must contain
at least one attribute.
<p>
Follows OpenTelemetry <a
href="../../specification/common/README.md#attribute">common
attribute definition</a>. SHOULD follow OpenTelemetry <a
href="https://github.com/open-telemetry/semantic-conventions">semantic
conventions</a> for attributes.
    </td>
   </tr>
   <tr>
    <td>Attributes
    </td>
    <td>map&lt;string, any&gt;
    </td>
    <td>Descriptive (non-identifying) attributes of the entity.
<p>
MAY change over the lifetime of the entity. MAY be empty. These
attributes are not part of entity's identity.
<p>
Follows <a
href="https://github.com/open-telemetry/opentelemetry-specification/blob/v1.44.0/specification/logs/data-model.md#type-any">any</a>
value definition in the OpenTelemetry spec - it can be a scalar value,
byte array, an array or map of values. Arbitrary deep nesting of values
for arrays and maps is allowed.
<p>
SHOULD follow OpenTelemetry <a
href="https://github.com/open-telemetry/semantic-conventions">semantic
conventions</a> for attributes.
    </td>
   </tr>
</table>

### Minimally Sufficient ID

Commonly, a number of attributes of an entity are readily available for the telemetry
producer to compose an ID from. Of the available attributes the entity ID should
include the minimal set of attributes that is sufficient for uniquely identifying
that entity. For example
a Process on a host can be uniquely identified by (`process.pid`,`process.start_time`)
attributes. Adding for example `process.executable.name` attribute to the ID is
unnecessary and violates the Minimally Sufficient ID rule.

### Examples of Entities

_This section is non-normative and is present only for the purposes of demonstrating
the data model._

Here are examples of entities, the typical identifying attributes they
have and some examples of non-identifying attributes that may be
associated with the entity.

<table>
   <tr>
    <td><strong>Entity</strong>
    </td>
    <td><strong>Entity Type</strong>
    </td>
    <td><strong>Identifying Attributes</strong>
    </td>
    <td><strong>Non-identifying Attributes</strong>
    </td>
   </tr>
   <tr>
    <td>Service
    </td>
    <td>"service"
    </td>
    <td>service.name (required)
<p>
service.instance.id
<p>
service.namespace
    </td>
    <td>service.version
    </td>
   </tr>
   <tr>
    <td>Host
    </td>
    <td>"host"
    </td>
    <td>host.id
    </td>
    <td>host.name
<p>
host.type
<p>
host.image.id
<p>
host.image.name
    </td>
   </tr>
   <tr>
    <td>K8s Pod
    </td>
    <td>"k8s.pod"
    </td>
    <td>k8s.pod.uid (required)
<p>
k8s.cluster.name
    </td>
    <td>Any pod labels
    </td>
   </tr>
   <tr>
    <td>K8s Pod Container
    </td>
    <td>"container"
    </td>
    <td>k8s.pod.uid (required)
<p>
k8s.cluster.name
<p>
container.name
    </td>
    <td>Any container labels
    </td>
   </tr>
</table>

See more examples showing nuances of ID field composition in the
[Entity Identification](#entity-identification) section.

## Entity Events

Information about Entities can be produced and communicated using 2
types of entity events: EntityState and EntityDelete.

### EntityState Event

The EntityState event stores information about the _state_ of the entity
at a particular moment of time. The data model of the EntityState event
is the same as the entity data model with some extra fields:

<table>
   <tr>
    <td><strong>Field</strong>
    </td>
    <td><strong>Type</strong>
    </td>
    <td><strong>Description</strong>
    </td>
   </tr>
   <tr>
    <td>Timestamp
    </td>
    <td>nanoseconds
    </td>
    <td>The time since when the entity state is described by this event.
The time is measured by the origin clock. The field is required.
    </td>
   </tr>
   <tr>
    <td>Interval
    </td>
    <td>milliseconds
    </td>
    <td>Defines the reporting period, i.e. how frequently the
information about this entity is reported via EntityState events even if
the entity does not change. The next expected EntityEvent for this
entity is expected at (Timestamp+Interval) time. Can be used by
receivers to infer that a no longer reported entity is gone, even if the
EntityDelete event was not observed. Optional, if missing the interval
is unknown.
    </td>
   </tr>
   <tr>
    <td>Type
    </td>
    <td>
    </td>
    <td>See data model.

</td>
   </tr>
   <tr>
    <td>Id
    </td>
    <td>
    </td>
    <td>See data model
</td>
   </tr>
   <tr>
    <td>Attributes
    </td>
    <td>
    </td>
    <td>See data model
</td>
   </tr>
</table>

We say that an entity mutates (changes) when one or more of its
descriptive attributes changes. A new descriptive attribute may be
added, an existing descriptive attribute may be deleted or a value of an
existing descriptive attribute may be changed. All these changes
represent valid mutations of an entity over time. When these mutations
happen the identity of the entity does not change.

When the entity's state is changed it is expected that the source will
emit a new EntityState event with a fresh timestamp and full list of
values of all other fields.

Entity event producers SHOULD periodically emit events even
if the entity does not change. In this case the Type, ID and Attribute
fields will remain the same, but a fresh Timestamp will be recorded in
the event. Producing such events allows the system to be resilient to
event losses. Even if some events are lost eventually the correct state
of the entity is more likely to be delivered to the final destination.
Periodic sending of EntityState events also serves as a liveliness
indicator (see below how it can be used in lieu of EntityDelete event).

### EntityDelete Event

EntityDelete event indicates that a particular entity is gone:

<table>
   <tr>
    <td><strong>Field</strong>
    </td>
    <td><strong>Type</strong>
    </td>
    <td><strong>Description</strong>
    </td>
   </tr>
   <tr>
    <td>Timestamp
    </td>
    <td>nanoseconds
    </td>
    <td>The time when the entity was deleted. The time is measured by
the origin clock. The field is required.
    </td>
   </tr>
   <tr>
    <td>Type
    </td>
    <td>
    </td>
    <td>See data model
</td>
   </tr>
   <tr>
    <td>Id
    </td>
    <td>
    </td>
    <td>See data model
</td>
   </tr>
</table>

Note that transmitting EntityDelete is not guaranteed
when the entity is gone. Recipients of entity signals need to be prepared to
handle this situation by expiring entities that are no longer seeing
EntityState events reported (i.e. treat the presence of EntityState
events as a liveliness indicator).

The expiration mechanism is based on the previously reported `Interval` field of
EntityState event. The recipient can use this value to compute when to expect the next
EntityState event and if the event does not arrive in a timely manner (plus some Slack)
it can consider the entity to be gone even if the EntityDelete event was not observed.

## Entity Identification

The data model defines the structure of the entity ID field. This section explains
how the ID field is computed.

### LID, GID and IDCONTEXT

All entities have a local ID (LID) and a global ID (GID).

The LID is unique in a particular identification context, but is not necessarily globally
unique. For example a process entity's LID is its PID number and process start time.
The (PID,StartTime) pair is unique only in the context of a host where the process runs
(and the host in this case is the identification context).

The GID of an entity is globally unique, in the sense that for the entire set of entities
in a particular telemetry store no 2 entities exist that have the same GID value.

The GID of an entity E is defined as:

`GID(E) = UNION( LID(E), GID(IDCONTEXT(E)) )`

Where `IDCONTEXT(E)` is the identification context in which the LID of entity E is unique.
The value of `IDCONTEXT(E)` is an entity itself, and thus we can compute the GID value of it too.

In other words, the GID of an entity is a union of its LID and the GID of its
identification context. Note: GID(E) is a map of key-value attributes.

The enrichment process often is responsible for determining the value of `IDCONTEXT(E)`
and for computing the GID according to the formula defined above, although the GID may
also be produced at once by the telemetry source (e.g. by OTel SDK) without requiring
any additional enrichment.

### Semantic Conventions

OpenTelemetry semantic conventions will be enhanced to include entity definitions for
well-known entities such as Service, Process, Host, etc.

For well-known entity types LID(E) is defined in OTel semantic conventions per
entity type. The value of LID is a map of key-value attributes. For example,
for entity of type "process" the semantic conventions define LID as 2 attributes:

```json5
{
  "process.pid": $pid,
  "process.start_time": $starttime
}
```

For custom entity types (not defined in OTel semantic conventions) the end user is
responsible for defining their custom semantic conventions in a similar way.

The entity information producer is responsible for determining the identification
context of each entity it is producing information about.

In certain cases, where only one possible IDCONTEXT definition is meaningful, the
IDCONTEXT may be defined in the semantic conventions. For example Kubernetes nodes
always exist in the identifying context of a Kubernetes cluster. The semantic convention
for "k8s.node" and "k8s.cluster" can prescribe that the IDCONTEXT of entity of type
"k8s.node" is always an entity of type "k8s.cluster".

Important: semantic conventions are not expected to (and normally won't) prescribe
the complete GID composition.
Semantic conventions should prescribe LID and may prescribe IDCONTEXT, but GID
composition, generally speaking, cannot be known statically.

For example: a host's LID should be a `host.id` attribute. A host running on a cloud
should have an IDCONTEXT of "cloud.account" and the LID of "cloud.account" entity
is (`cloud.provider`, `cloud.account.id`). However semantic conventions cannot prescribe
that the GID of a host is (`host.id`, `cloud.provider`, `cloud.account.id`) because not all
hosts run on cloud. A host that runs on prem in a single data center may have a GID
of just (`host.id`) or if a customer has multiple on prem data centers they may use
data.center.id as its identifier and use (`host.id`, `data.center.id`) as GID of the host.

### Examples

_This section is a supplementary guideline and is not part of logical data model._

#### Process in a Host

A locally running host agent (e.g. an OTel Collector) that produces
information about "process" entities has the knowledge that the
processes run in the particular host and thus the "host" is the
identification context for the processes that the agent observes. The
LID of a process can look like this:

```json5
{
  "process.pid": 12345,
  "process.start_time": 1714491491
}
```

and Collector will use "host" as the IDCONTEXT and add host's LID to it:

```json5
{
  // Process LID, unique per host.
  "process.pid": 12345,
  "process.start_time": 1714491491,


  // Host LID
  "host.id": "fdbf79e8af94cb7f9e8df36789187052"
}
```

If we assume that we have only one data center and host IDs are globally
unique then the above ID is globally unique and is the GID of the
process. If this assumption is not valid in our situation we would
continue applying additional IDCONTEXT's until the GID is globally
unique. See for example the
[Host in Cloud Account](#host-in-cloud-account) example below.

#### Process in Kubernetes

An OTel Collector (running in Kubernetes) that produces information about process entities
has the knowledge that the processes run in the particular containers in
the particular pod and thus the container is the identification context
for the process, and the pod is the identification context for the
container. If we begin with the same process LID:

```json5
{
  "process.pid": 12345,
  "process.start_time": 1714491491
}
```

the Collector will then add the IDCONTEXT of container and
pod to this, resulting in:

```json5
{
  // Process LID, unique per container.
  "process.pid": 12345,
  "process.start_time": 1714491491,

  // Container LID, unique per pod.
  "k8s.container.name": "redis",


  // Pod LID has 2 attributes.
  "k8s.pod.uid": "0c4cbbf8-d4b4-4e84-bc8b-b95f0d537fc7",
  "k8s.cluster.name": "dev"
}
```

Note that we used 3 different LIDs above to compose the GID. The
attributes that are part of each LID are defined in OTel semantic
conventions.

In this example we assume this to be a valid GID because Pod is the root
IDCONTEXT, since Pod's LID includes the cluster name, which is expected
to be globally unique. If this assumption about global uniqueness of
cluster names is wrong then another containing IDCONTEXT within which
cluster names are unique will need to be applied and so forth.

Note also how we used a pair (`k8s.pod.uid`, `k8s.cluster.name`).
Alternatively, we could say that Kubernetes Cluster is a separate entity
we care about. This would mean the Pod's IDCONTEXT is the cluster. The
net result for process's GID would be exactly the same, but we would
arrive to it in a different way:

```json5
{
  // Process LID, unique per container.
  "process.pid": 12345,
  "process.start_time": 1714491491,

  // Container LID, unique per pod.
  "k8s.container.name": "redis",


  // Pod LID, unique per cluster.
  "k8s.pod.uid": "0c4cbbf8-d4b4-4e84-bc8b-b95f0d537fc7",

  // Cluster LID, also globally unique since cluster is root entity.
  "k8s.cluster.name": "dev"
}
```

#### Host in Cloud Account

A host running in a cloud account (e.g. AWS) will have a LID that uses
the host instance ID, unique within a single cloud account, e.g.:

```json5
{
  // Host LID, unique per cloud account.
  "host.id": "fdbf79e8af94cb7f9e8df36789187052"
}
```

OTel Collector with
[resourcedetection](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/resourcedetectionprocessor)
processor with "AWS" detector enabled will add the IDCONTEXT of the
cloud account like this:

```json5
{
  // Host LID, unique per cloud account.
  "host.id": "fdbf79e8af94cb7f9e8df36789187052"

  // Cloud account LID has 2 attributes:
  "cloud.provider": "aws",
  "cloud.account.id": "1234567890"
}
```

## Prototypes

A set of prototypes that demonstrate this data model has been implemented:

- [Go SDK Prototype](https://github.com/tigrannajaryan/opentelemetry-go/pull/244)
- [Collector Prototype](https://github.com/tigrannajaryan/opentelemetry-collector/pull/4)
- [Collector Contrib Prototype](https://github.com/tigrannajaryan/opentelemetry-collector-contrib/pull/1/files)
- [OTLP Protocol Buffer changes](https://github.com/tigrannajaryan/opentelemetry-proto/pull/2/files)

## Prior Art

An experimental entity data model was implemented in OpenTelemetry Collector as described
in [this document](https://docs.google.com/document/d/1Tg18sIck3Nakxtd3TFFcIjrmRO_0GLMdHXylVqBQmJA/edit).
The Collector's design uses LogRecord as the carrier of entity events, with logical structure
virtually identical to what this OTEP proposes.

There is also an implementation of this design in the Collector, see
[completed issue to add entity events](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/23565)
and [the PR](https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/24419)
that implements entity event emitting for `k8scluster` receiver in the Collector.

## Alternatives

### Different ID Structure

Alternative proposals were made [here](https://docs.google.com/document/d/1PLPSAnWvFWCsm6meAj6OIVDBvxsk983V51WugF0NgVo/edit) and  
[here](https://docs.google.com/document/d/1bLmkQSv35Fi6Wbe4bAqQ-_JS7XWIXWbvuirVmAkz4a4/edit)
to use a different structure for entity ID field.

We rejected these proposals in favour of the ID field proposed in this OTEP for the
following reasons:

- The map of key-value attributes is widely used elsewhere in OpenTelemetry as
  Resource attributes, as Scope attributes, as Metric datapoint attributes, etc. so
  it is conceptually consistent with the rest of OTel.

- We already have a lot of machinery that works well with this definition of attributes,
  for example OTTL language has syntax for working with attributes, or Collector's pdata
  API or Attribute value types in SDKs. All this code will no longer work as is if we
  have a different data structure and needs to be re-implemented in a different way.

### No Entity Events

Entity signal allows recording the state of the entities. As the entity's state changes
events are emitted that describe the new state. In this proposal the entity's state is
(type,id,attributes) tuple, but we envision that in the future we may also want to add
more information to the entity signal, particularly to record the relationships between
entities (i.e the fact that a Process runs on a Host).

### Merge Entity Events data into Resource

If we eliminate the entity signal as a concept and put the entire entity's state into
the Resource then every time the entity's state changes we must emit one of
ResourceLogs/ResourceSpans/ResourceMetrics messages that includes the Resource that
represents the entity's state.

However, what do we do if there are no logs or spans or metrics data points to
report? Do we emit a ResourceLogs/ResourceSpans/ResourceMetrics OTLP message with empty logs
or spans or metrics data points? Which one do we emit: ResourceLogs, ResourceSpans
or ResourceMetrics?

What do we do when we want to add support for recording entity relationships in the
future? Do we add all that information to the Resource and bloat the Resource size?

How do we report the EntityDelete event?

All these questions don't have good answers. Attempting to shoehorn the entity
information into the Resource where it does not naturally fit is likely to result
in ugly and inefficient solutions.

### Hierarchical ID Field

We had an alternate proposal to retain the information about how the ID was
[composed from LID and IDCONTEXT](#entity-identification), essentially to record the
hierarchy of identification contexts in the ID data structure instead of flattening it
and losing the information about the composition process that resulted in the particular ID.

There are a couple of reasons:

- The flat ID structure is simpler.

- There are no known use cases that require a hierarchical ID structure. The use case
  of "record parental relationship between entities" will be handled explicitly via
  separate relationship data structures (see [Future Work](#future-work)).

## Open questions

### Attribute Data Type

The data model requires the Attributes field to use the extended
[any](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.44.0/specification/logs/data-model.md#type-any)
attribute values, that allows more complex data types. This is different from the data
type used by the ID field, which is more restricted in the shape.

Are we happy with this discrepancy?

Here is corresponding
[TODO item](https://github.com/orgs/open-telemetry/projects/85/views/1?pane=issue&itemId=62411493).

### Classes of Entity Types

Do we need to differentiate between infrastructure entities (e.g. Pod, Host, Process)
and non-infrastructure entities (logical entities) such as Service? Is this distinction
important?

Here is corresponding
[TODO item](https://github.com/orgs/open-telemetry/projects/85/views/1?pane=issue&itemId=62411407).

### Multiple Observers

The same entity may be observed by different observers simultaneously. For example the
information about a Host may be reported by the agent that runs on the host. At the same
time more information about that same host may be obtained via cloud provider's API.

The information obtained by different observers can be complementary, they don't
necessarily have access exactly to the same data. It can be very useful to combine this
information in the backend and make it all available to the user.

However, it is not possible for multiple observers to simultaneously use EntityState
events as they are defined earlier in this document, since the information in the event
will overwrite information in the previously received event about that same entity.

A possible way to allow multiple observers to report portions of information about the
same entity simultaneously is to indicate the observer in the EntityState event by adding
an "ObserverId" field. EntityState event will then look like this:

|Field|Type|
|---|---|
|Timestamp|nanoseconds|
|Interval|milliseconds|
|Type||
|ID||
|Attributes||
|ObserverId|string or bytes|

ObserverId field can be optional. Attributes from EntityState events that contain
different ObserverId values will be merged in the backend. Attributes from EntityState
events that contain the same ObserverId value will overwrite attributes from the previous
reporting of the EntityState event from that observer.

Here is corresponding
[TODO item](https://github.com/orgs/open-telemetry/projects/85/views/1?pane=issue&itemId=62411289).

### Is Type part of Entity's identity?

Is the Type field part of the entity's identity together with the ID field?

For example let's assume we have a Host and an OTel Collector running on the Host.
The Host's ID will contain one attribute: `host.id`, and the Type of the entity will be
"host". The Collector technically speaking can be also identified by one attribute
`host.id` and the Type of the entity will be "otel.collector". This only works if we
consider the Type field to be part of the entity's identity.

If the Type field is not part of identity then in the above example we require that the
entity that describes the Collector has some other attribute in its ID (for example
`agent.type` attribute [if it gets accepted](https://github.com/open-telemetry/semantic-conventions/pull/950)).

Here is corresponding
[TODO item](https://github.com/orgs/open-telemetry/projects/85?pane=issue&itemId=57053320).

### Choosing from Multiple IDs

Sometimes the same entity may be identified in more than one way. For example a Pod can
be identified by its `k8s.pod.uid` but it can be also identified by a pair of
`k8s.namespace.name`, `k8s.pod.name` attributes.

We need to provide a recommendation for the cases when more than one valid identifier
exists about how to make a choice between the identifiers.

Here is corresponding
[TODO item](https://github.com/orgs/open-telemetry/projects/85?pane=issue&itemId=57053415).

## Future Work

This OTEP is step 1 of defining the Entities data model. It will be followed by other
OTEPs that cover the following topics:

- How the existing Resource concept will be modified to link existing
  signals to entities.

- How relationships between entities are modeled.

- Representation of entity data over the wire and the transmission
  protocol for entities.

- Add transformations that describe entity semantic convention changes in
  OpenTelemetry Schema Files.

We will possibly also submit additional OTEPs that address the Open Questions.

## References

- [OpenTelemetry Proposal: Resources and Entities](https://docs.google.com/document/d/1VUdBRInLEhO_0ABAoiLEssB1CQO_IcD5zDnaMEha42w/edit)
- [OpenTelemetry Entity Data Model](https://docs.google.com/document/d/1FdhTOvB1xhx7Ks7dFW6Ht1Vfw2myU6vyKtEfr_pqZPw/edit)
- [OpenTelemetry Entity Identification](https://docs.google.com/document/d/1hJIAIMsRCgZs-poRsw3lnirP14d3sMfn1LB08C4LCDw/edit)
- [OpenTelemetry Resources - Principles and Characteristics](https://docs.google.com/document/d/1Xd1JP7eNhRpdz1RIBLeA1_4UYPRJaouloAYqldCeNSc/edit)
