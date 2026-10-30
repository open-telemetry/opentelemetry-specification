<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Data Model
weight: 2
--->

# Entity Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- START doctoc -->

- [Minimally Sufficient Identity](#minimally-sufficient-identity)
- [Repeatable Identity](#repeatable-identity)
- [Identifying Attributes](#identifying-attributes)
- [Resource and Entities](#resource-and-entities)
  * [Attribute Referencing Model](#attribute-referencing-model)
  * [Placement of Shared Descriptive Attributes](#placement-of-shared-descriptive-attributes)
- [Identity Scope](#identity-scope)
  * [Global Identity Composition](#global-identity-composition)
  * [Unresolved Identity](#unresolved-identity)
- [Merging of Entities](#merging-of-entities)
- [Examples of Entities](#examples-of-entities)

<!-- END doctoc -->

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

> [!NOTE]
> Entity relationship modelling will be refined in future specification
> work.

The data model below defines a logical model for an entity (irrespective of the
physical format and encoding of how entity data is recorded).

| Field | Type | Description |
| ----- | ---- | ----------- |
| Type | string | Defines the type of the entity. MUST not change during the lifetime of the entity. For example: "service" or "host". This field is required and MUST not be empty for valid entities. |
| Schema URL | string | Identifies the schema version for the entity's attributes. Used to determine merge compatibility (see [Merging of Entities](#merging-of-entities)). MAY be empty. |
| ID | map<string, attribute value> | Attributes that identify the entity.<p>MUST not change during the lifetime of the entity. The ID must contain at least one attribute.<p>The scope within which the ID is unique is defined by [Identity Scope](#identity-scope).<p>Follows OpenTelemetry [attribute definition](../common/README.md#attribute). SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions) for attributes. |
| Description | map<string, attribute value> | Descriptive (non-identifying) attributes of the entity.<p>MAY change over the lifetime of the entity. MAY be empty. These attributes are not part of entity's identity.<p>Follows OpenTelemetry [attribute definition](../common/README.md#attribute). SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/README.md) for attributes. |
| ID Scope | enum: `unspecified`, `global`, `local` | Whether the entity's ID is unique on its own or only within another entity.<p>MUST not change during the lifetime of the entity. See [Identity Scope](#identity-scope). |
| Scope Entity Type | string | The type of the entity within which this entity's ID is unique.<p>MUST be set when ID Scope is `local`, and MUST be empty otherwise. MUST not change during the lifetime of the entity. See [Identity Scope](#identity-scope). |

## Minimally Sufficient Identity

Commonly, a number of attributes of an entity are readily available for the telemetry
producer to compose an ID from. Of the available attributes the entity ID should
include the minimal set of attributes that is sufficient for uniquely identifying
that entity. For example a Process on a host can be uniquely identified by
(`process.pid`,`process.start_time`) attributes. Adding for example `process.executable.name` attribute to the ID is unnecessary and violates the
Minimally Sufficient Identity rule.

## Repeatable Identity

The identifying attributes for entity SHOULD be values that can be repeatably
obtained by observers of that entity. For example, a `process` entity SHOULD
have the same identity (and be recognized as the same process), regardless of whether
the identity was generated from the process itself, e.g. via SDK, or by an
OpenTelemetry Collector running on the same host, or by some other system
describing the process.

> [!TIP]
> There are many ways to accomplish repeatable identifying attributes
> across multiple observers. While many successful systems rely on pushing down
> identity from a central registry or knowledge store, OpenTelemetry must
> support all possible scenarios.

## Identifying Attributes

OpenTelemetry Semantic Conventions MUST define a set of identifying attribute
keys for every defined entity type.

Names of the identifying attributes SHOULD use the entity type as a prefix to avoid
collisions with other entity types. For example, the `k8s.node` entity uses
`k8s.node.uid` as an identifying attribute.

When an entity can be emitted by multiple observers, the following rules apply:

* Two independent observers that report the same entity MUST be able to
  supply identical values for all identifying attributes.

* If an observer cannot reliably obtain one or more identifying attributes, it
  MUST NOT emit telemetry using that entity type. Instead, it SHOULD:
  1. delegate to the observer that _can_ supply the full set and treat that
     observer as the _source of truth_, or
  2. emit a _different_ entity type with a set of identifying attributes it
     can populate reliably.

This ensures that entity identity is consistent and unambiguous across
observers.

## Resource and Entities

OpenTelemetry signals (metrics, logs, traces, and profiles) support attaching
one or more entities each representing a specific infrastructure or runtime
component such as a `k8s.cluster`, `k8s.node`, `host`, or `container`.

Previously, the Resource data model relied on flattened attributes per signal.
With Entities, telemetry can represent multiple distinct but related components
within the same signal, each with its own identity and extra metadata. Entities
leverage the same pool of attributes as the Resource model. This allows for more
efficient encoding and transmission of the data, as well as backward
compatibility with existing Resource attributes.

### Attribute Referencing Model

Entities can be defined in the `resource` section of a telemetry signal. Their
identifying and descriptive attributes reference shared attributes defined in
the Resource. For example, in OTLP, entities do not carry their own key-value
pairs directly. Instead, they reference keys in `resource.attributes` to remain
backward compatible with OTLP 1.x.

This approach is designed to support attribute flattening, where attributes are
not tied to a specific structure but can be flexibly referenced across different
entities. The model provides:

- A way for entities to be identified and described with shared attributes.
- The ability to avoid data duplication and inconsistencies.
- A more efficient representation for encoding and transmission.

### Placement of Shared Descriptive Attributes

Attribute flattening allows multiple entities to reference the same attribute key,
but with different values across the entities. In such situations, the following
rule applies:

If multiple entities share the same descriptive attribute key with potentially
conflicting values, the attribute MUST logically belong to **only one** of them.
All others SHOULD NOT reference it. The attribute MUST be referenced by the
**most specific** entity, the one closest in the topology graph to the entity
associated with the telemetry signal.

**Example:**  

If a signal includes both `k8s.cluster` and `k8s.node` entities with
the `cloud.availability_zone` descriptive attribute, which may have
different values, then **only** the `k8s.node` entity can reference this key
— as it is the more specific entity.

Other entities (e.g., `k8s.cluster`) can report this attribute in a separate
telemetry channel (e.g., entity events) where full ownership context is known.

## Identity Scope

Identifying attributes are not always enough to identify an entity universally.
Some IDs are unique on their own, others only within another entity. For example
`k8s.pod.uid` is a Kubernetes-generated UUID, while `k8s.container.name` is
unique only within a single Kubernetes Pod.

Every entity therefore records an **ID Scope**, and when that scope is `local`, a
**Scope Entity Type**: the type of the entity its ID is unique within.

| ID Scope | Scope Entity Type | Meaning |
| -------- | ----------------- | ------- |
| `global` | MUST be empty | The ID is unique on its own, because it comes from a scheme that produces globally unique values, such as a UUID. Any two observers of the same entity produce the same ID. |
| `local` | MUST be set | The ID is unique only within an entity of that type, because whatever assigns it only avoids collisions within that entity. |
| `unspecified` | MUST be empty | The producer did not state the scope. The identity is [unresolved](#unresolved-identity). |

Both fields describe the entity's own ID. They say what kind of entity the ID is
unique within, not which particular entity, and that follows from the
identifying attributes the producer populated.

> [!NOTE]
> The scope of an ID follows from how the ID is generated, not from where the
> system that assigns it documents its guarantee. `k8s.pod.uid` is `global`
> because Kubernetes UIDs are UUIDs, even though Kubernetes documents uniqueness
> per cluster. Scoping it to `k8s.cluster` would add nothing, since
> `k8s.cluster.uid` is itself a Kubernetes UID and the chain would rest on the
> same property one step later.

The producer of an entity MUST set the ID Scope, and MUST set the Scope Entity
Type when that scope is `local`. A producer that cannot determine the scope of
an ID it generated MUST use `unspecified` rather than guess, so that consumers
do not treat a scoped ID as globally unique.

A component MUST NOT set or modify either field on an entity it did not produce.
Only the producer of an entity knows how it generated that entity's ID. A
component that detects a scoping entity adds its own entity to the Resource and
leaves the scoped entity unchanged.

> [!NOTE]
> This keeps both fields independent of the order in which entities are added to
> a Resource, and of which other entities happen to be present. Adding a scoping
> entity later completes an entity's Global Identity without modifying that
> entity.

OpenTelemetry Semantic Conventions MUST declare the ID Scope of every defined
entity type, and for a `local` scope the Scope Entity Types it can have. There
MAY be more than one: a `process` is scoped by a `host` in one deployment and by
a `container` in another. The producer records which one applies.

Consumers MUST be able to determine an entity's ID Scope from the entity itself.
A consumer MUST NOT be required to consult Semantic Conventions to interpret an
entity's identity.

### Global Identity Composition

An entity's **Local Identity** is its ID attributes. Its **Global Identity** is
the union of its Local Identity and the Global Identity of the entity that
scopes it.

A scoping entity is found by type. This is unambiguous because a Resource holds
at most one entity of a given type, see
[Merging An Entity into a Resource](../resource/data-model.md#merging-an-entity-into-a-resource).

A consumer computes an entity's Global Identity from the Resource alone:

1. Start with the entity's Local Identity.
2. If the ID Scope is `unspecified`, the identity is
   [unresolved](#unresolved-identity).
3. If the ID Scope is `global`, stop. The accumulated identity is the Global
   Identity.
4. If the Scope Entity Type is empty, the identity is
   [unresolved](#unresolved-identity).
5. Otherwise find the entity on the Resource whose type matches the Scope Entity
   Type. If there is no such entity, the identity is
   [unresolved](#unresolved-identity).
6. Union that entity's Local Identity into the accumulated identity and repeat
   from step 2 for that entity.

If the walk reaches an entity type it has already visited, the chain is cyclic.
The consumer MUST stop and the identity is [unresolved](#unresolved-identity).

### Unresolved Identity

An entity's identity is **unresolved** when its ID Scope is `unspecified`, when
a scoping entity in its chain is missing from the Resource, or when the chain is
cyclic. A `local` ID Scope with an empty Scope Entity Type does not conform to
this specification, and a consumer that receives one MUST also treat the
identity as unresolved.

An unresolved entity is still a valid entity and still describes the object the
telemetry is about. A consumer:

- MAY use the entity to correlate signals that carry the same Resource.
- MUST NOT treat the entity's Local Identity as a Global Identity.
- SHOULD NOT merge the entity with an entity from another Resource that has the
  same type and the same Local Identity, since the two may be different objects
  in different scopes. A consumer MAY merge them if it knows, from outside the
  data, that every Resource it receives is scoped by the same entity, as in a
  pipeline that collects from a single cluster.

An unresolved identity is expected when one component reports an entity and a
different component reports the entity that scopes it. It resolves once that
component adds its entity to the Resource. For example, `k8s.namespace` is
identified by `k8s.namespace.name`, which is unique only within a cluster, and
the Kubernetes API exposes no cluster identity, so a receiver watching
Kubernetes objects can only report the namespace. A resource detector that knows
the cluster completes the chain by adding `k8s.cluster`.

> [!NOTE]
> A producer cannot always tell which kind of entity scopes an ID. A `process`
> identified by `process.pid` is unique within a PID namespace, and a producer
> that did not mount the procfs it reads cannot always tell which namespace that
> is. Leaving the ID Scope `unspecified` is the right outcome: the entity remains
> usable within its Resource, and no consumer is misled into treating a scoped ID
> as globally unique.

## Merging of Entities

Entities MAY be merged if and only if their types are the same, their
identity attributes are exactly the same, their ID scopes and scope entity
types are the same AND their schema_url is the same.
This means both Entities MUST have the same identity attribute keys and
for each key, the values of the key MUST be the same.

Here's an example algorithm that will check compatibility:

```
can_merge(current_entity, new_entity) {
  current_entity.type == new_entity.type &&
  current_entity.schema_url == new_entity.schema_url &&
  current_entity.id_scope == new_entity.id_scope &&
  current_entity.id_scope_entity_type == new_entity.id_scope_entity_type &&
  has_same_attributes(current_entity.identity, new_entity.identity)
}
```

Note: this algorithm merges entities within a single Resource, where an entity
of a given type is the same for both entities, so comparing ID scopes and scope
entity types is sufficient. An operation that merges entities across Resources, which
this specification does not define, MUST compare
[Global Identity](#global-identity-composition) instead, because the same Local
Identity can refer to different objects in different contexts.

When merging entities, all attributes in description are merged together, with
Conflicting descriptive attributes values from the new entity overwrite descriptive
attribute values from the current entity.

Here's an example algorithm that will merge:

```
merge(current_entity, new_entity) {
  if can_merge(current_entity, new_entity) {
    for attribute in new_entity.description {
      // new_entity descriptions take precedence.
      current_entity.description.insert(attribute)
    }
  }
}
```

Note: If Entities have different `schema_url`s, they SHOULD be converted to the
same schema version (if possible) before attempting a merge. The merge algorithm
defined here assumes the entities are already at the same schema version.

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
    <td><strong>ID Scope</strong>
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
    <td>global
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
    <td>global when <code>host.id</code> is a machine ID;<br/>local, within <code>cloud</code>, when it is a cloud instance ID
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
    <td>global
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
    <td>global
    </td>
    <td>k8s.pod.name<br/>
        k8s.pod.label.{key}<br/>
        k8s.pod.annotation.{key}<br/>
    </td>
   </tr>
   <tr>
    <td>Kubernetes Container
    </td>
    <td><pre>k8s.container</pre>
    </td>
    <td>k8s.container.name
    </td>
    <td>local, within <code>k8s.pod</code>
    </td>
    <td>k8s.container.restart_count
    </td>
   </tr>
   <tr>
    <td>Service Instance
    </td>
    <td><pre>service.instance</pre>
    </td>
    <td>service.instance.id
    </td>
    <td>local, within <code>service</code>
    </td>
    <td>service.version
    </td>
   </tr>
</table>

The `service.instance` row shows how Identity Scope replaces composing a
globally unique ID by hand. `service.instance.id` is only required to be unique
within a `service`, so the `service` entity's identity no longer has to be
repeated in the `service.instance` identity to make it globally unique.
