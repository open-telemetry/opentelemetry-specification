# Entity Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Minimally Sufficient Identity](#minimally-sufficient-identity)
- [Repeatable Identity](#repeatable-identity)
- [Resource and Entities](#resource-and-entities)
  * [Attribute Referencing Model](#attribute-referencing-model)
  * [Placement of Shared Descriptive Attributes](#placement-of-shared-descriptive-attributes)
- [Examples of Entities](#examples-of-entities)

<!-- tocstop -->

</details>

Entity represents an object of interest associated with produced telemetry:
traces, metrics, profiles, or logs.

For example, telemetry produced using an OpenTelemetry SDK is normally
associated with a `service` entity. Similarly, OpenTelemetry defines system
metrics for a `host`. The `host` is the entity we want to associate metrics with
in this case.

Entities may be also associated with produced telemetry indirectly.
For example a service that produces
telemetry is also related to a process in which the service runs, so we say that
the `service` entity is related to the `process` entity. The process normally
also runs on a host, so we say that the `process` entity is related to the
`host` entity.

> Note: Entity relationship modelling will be refined in future specification
> work.

The data model below defines a logical model for an entity (irrespective of the
physical format and encoding of how entity data is recorded).

| Field        | Type                                   | Description     |
|--------------|----------------------------------------|-----------------|
| Type         | string                                 | Defines the type of the entity. MUST not change during the lifetime of the entity. For example: "service" or "host". This field is required and MUST not be empty for valid entities. |
| Id           | map<string, standard attribute value>  | Attributes that identify the entity.<p>MUST not change during the lifetime of the entity. The Id must contain at least one attribute.<p>Follows OpenTelemetry [Standard attribute definition](../common/README.md#standard-attribute). SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions) for attributes. |
| Description  | map<string, any>                       | Descriptive (non-identifying) attributes of the entity.<p>MAY change over the lifetime of the entity. MAY be empty. These attributes are not part of entity's identity.<p>Follows [any](../logs/data-model.md#type-any) value definition in the OpenTelemetry spec. Arbitrary deep nesting of values for arrays and maps is allowed.<p>SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/README.md) for attributes. |

## Minimally Sufficient Identity

Commonly, a number of attributes of an entity are readily available for the telemetry
producer to compose an Id from. Of the available attributes the entity Id should
include the minimal set of attributes that is sufficient for uniquely identifying
that entity. For example a Process on a host can be uniquely identified by
(`process.pid`,`process.start_time`) attributes. Adding for example `process.executable.name` attribute to the Id is unnecessary and violates the
Minimally Sufficient Identity rule.

## Repeatable Identity

The identifying attributes for entity SHOULD be values that can be repeatably
obtained by observers of that entity. For example, a `process` entity SHOULD
have the same identity (and be recognized as the same process), regardless of whether
the identity was generated from the process itself, e.g. via SDK, or by an
OpenTelemetry Collector running on the same host, or by some other system
describing the process.

> Aside: There are many ways to accomplish repeatable identifying attributes
> across multiple observers. While many successful systems rely on pushing down
> identity from a central registry or knowledge store, OpenTelemetry must
> support all possible scenarios.

## Resource and Entities

OpenTelemetry signals (metrics, logs, traces) support attaching one or more
entities each representing a specific infrastructure or runtime component such as
a `k8s.cluster`, `k8s.node`, `host`, or `container`.

This model improves upon the previous Resource concept, which allowed only a single
flat set of attributes per signal. With entities, telemetry can represent multiple
distinct but related components within the same signal, each with its own identity
and context.

### Attribute Referencing Model

Entities are defined in the `resource` section of a telemetry signal. However,
they do not carry their own key-value pairs directly. Instead, they reference keys
defined in `resource.attributes`.

Each entity reference includes:

- a `type` (e.g., `k8s.node`, `host`)

- a list of attribute keys that identify the entity

- a list of attribute keys that describe the entity

Each key listed in an entity MUST match a corresponding key in the
`resource.attributes` section.

This indirection:

- provides backward compatibility with existing Resource attributes,

- avoids data duplication and potential data inconsistencies,

- allows more efficient encoding and transmission.

### Placement of Shared Descriptive Attributes

Because all attribute values reside in the shared `resource.attributes` block and
entities reference those keys, a single attribute (e.g., `cloud.availability_zone`)
may potentially be referenced by multiple entities. To avoid confusion, the following
rule applies:

If multiple entities share the same descriptive attribute key, the attribute
MUST logically belong to **only one** of them. All others MUST NOT reference it.
The attribute MUST be referenced by the **most specific** (or **lowest-level**)
entity among those present.

**Example:**  

If a signal includes both `k8s.cluster` and `k8s.node` entities and the `resource`
contains `cloud.availability_zone`, then **only** the `k8s.node` entity may reference
this key — as it is the more specific entity.

Other entities (e.g., `k8s.cluster`) may report this attribute in a separate
telemetry channel (e.g., entity events) where full ownership context is known.

## Examples of Entities

_This section is non-normative and is present only for the purposes of
demonstrating the data model._

Here are examples of entities, the typical identifying attributes they
have and some examples of descriptive attributes that may be
associated with the entity.

_Note: These examples MAY diverge from semantic conventions._

<table>
   <tr>
    <td><strong>Entity</strong>
    </td>
    <td><strong>Entity Type</strong>
    </td>
    <td><strong>Identifying Attributes</strong>
    </td>
    <td><strong>Descriptive Attributes</strong>
    </td>
   </tr>
   <tr>
    <td>Container
    </td>
    <td><pre>container</pre>
    </td>
    <td>container.id
    </td>
    <td>container.image.id<br/>
        container.image.name<br/>
        container.image.tag.{key}<br/>
        container.label.{key}<br/>
        container.name<br/>
        container.runtime<br/>
        oci.manifest.digest<br/>
        container.command<br/>
    </td>
   </tr>
   <tr>
    <td>Host
    </td>
    <td><pre>host</pre>
    </td>
    <td>host.id
    </td>
    <td>host.arch<br/>
        host.name<br/>
        host.type<br/>
        host.image.id<br/>
        host.image.name<br/>
        host.image.version<br/>
        host.type
    </td>
   </tr>
   <tr>
    <td>Kubernetes Node
    </td>
    <td><pre>k8s.node</pre>
    </td>
    <td>k8s.node.uid
    </td>
    <td>k8s.node.name
    </td>
   </tr>
   <tr>
    <td>Kubernetes Pod
    </td>
    <td><pre>k8s.pod</pre>
    </td>
    <td>k8s.pod.uid
    </td>
    <td>k8s.pod.name<br/>
        k8s.pod.label.{key}<br/>
        k8s.pod.annotation.{key}<br/>
    </td>
   </tr>
   <tr>
    <td>Service Instance
    </td>
    <td><pre>service.instance</pre>
    </td>
    <td>service.instance.id<br/>
        service.name<br/>
        service.namesapce
    </td>
    <td>service.version
    </td>
   </tr>
</table>
