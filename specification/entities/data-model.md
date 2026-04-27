<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Data Model
weight: 2
--->

# Entity Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Minimally Sufficient Identity](#minimally-sufficient-identity)
- [Repeatable Identity](#repeatable-identity)
- [Identifying Attributes](#identifying-attributes)
- [Resource and Entities](#resource-and-entities)
  * [Attribute Referencing Model](#attribute-referencing-model)
  * [Placement of Shared Descriptive Attributes](#placement-of-shared-descriptive-attributes)
- [Identity Scope](#identity-scope)
  * [Local and Global Identity](#local-and-global-identity)
  * [ID Context Type](#id-context-type)
  * [Global Identity Composition](#global-identity-composition)
- [Merging of Entities](#merging-of-entities)
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

> [!NOTE]
> Entity relationship modelling will be refined in future specification
> work.

The data model below defines a logical model for an entity (irrespective of the
physical format and encoding of how entity data is recorded).

| Field | Type | Description |
| ----- | ---- | ----------- |
| Type | string | Defines the type of the entity. MUST not change during the lifetime of the entity. For example: "service" or "host". This field is required and MUST not be empty for valid entities. |
| ID | map<string, attribute value> | Attributes that identify the entity.<p>MUST not change during the lifetime of the entity. The ID must contain at least one attribute.<p>Follows OpenTelemetry [attribute definition](../common/README.md#attribute). SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions) for attributes. |
| Description | map<string, attribute value> | Descriptive (non-identifying) attributes of the entity.<p>MAY change over the lifetime of the entity. MAY be empty. These attributes are not part of entity's identity.<p>Follows OpenTelemetry [attribute definition](../common/README.md#attribute). SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/README.md) for attributes. |
| ID Context Type | string | Type of the entity that establishes the context within which this entity's ID is unique. See [ID Context Type](#id-context-type). |

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

An entity's identity has two distinct aspects:

- **Scope kind** — declared once in semantic conventions for each
  entity type. Says whether the entity's ID is unique on its own
  (`global`) or only within some other entity (`local`).
- **Context entity** — chosen by the emitter at emission time, only
  for entities whose scope kind is `local`. Identifies the specific
  entity that establishes the boundary within which this entity's ID
  is unique. The type of the context entity is recorded in the **ID
  Context Type** field.

Scope kinds:

- **global**: the ID is universally unique. Any two observers anywhere
  that report the same entity will produce the same ID. Examples:
  `k8s.pod.uid` (a Kubernetes-issued UUID), `host.id` when treated as
  globally unique.
- **local**: the ID is unique only within a context entity. Examples:
  `process` is identified by (`process.pid`, `process.creation.time`),
  unique only within a single host (or container, in some setups);
  `k8s.container` is identified by `k8s.container.name`, unique only
  within a single Kubernetes Pod.

The scope kind for each entity type is declared in the OpenTelemetry
[semantic conventions](https://github.com/open-telemetry/semantic-conventions).

### Local and Global Identity

For an entity whose scope kind is `global`, **Local Identity** and
**Global Identity** are the same: the entity's ID attributes.

For an entity whose scope kind is `local`, the entity's ID attributes
form its **Local Identity**, sufficient to distinguish the entity
within its context entity. **Global Identity** is the union of the
entity's Local Identity with the Global Identity of its context
entity.

### ID Context Type

For entities whose scope kind is `local`, the OpenTelemetry semantic
conventions do not prescribe a single context entity type. The same
entity type can potentially have a different context entity in different
deployments. For example:

- A `process` typically has a `host` context, but in a multi-process
  container setup it may have a `container` context instead.

The emitter chooses the context entity at emission time and records
its type in the **ID Context Type** field of the entity. The
referenced context entity MUST be present on the same Resource. This
is unambiguous because at most one entity of a given type may appear
on a Resource.

For `global` entities, the ID Context Type field MUST be empty.

For `local` entities, the emitter SHOULD set the ID Context Type to
the type of the context entity on the Resource. The emitter MAY leave
it empty when the whole system operates in a single context and global
identity is not needed — for example, a single-host agent where every
emitted `process` is implicitly in the same host context. In that case
the entity's identity is meaningful only within the producing
Resource.

### Global Identity Composition

A receiver computes an entity's Global Identity by walking the
context entity chain on the same Resource:

1. Start with the entity's Local Identity (its ID attributes).
2. If the entity's ID Context Type is empty, stop. The accumulated
   identity is the Global Identity.
3. Otherwise, look up the entity on the Resource whose type matches
   the ID Context Type, union its Local Identity into the accumulated
   identity, and repeat from step 2 with that context entity.

A receiver SHOULD treat the entity's identity as valid only within the
producing Resource if any of the following holds:

- The ID Context Type is empty for a `local` entity.
- The referenced context entity is not present on the Resource.

In these cases the receiver MUST NOT merge the entity with same-Local-Identity
entities from other Resources.

> [!NOTE]
> The ID Context Type field captures only the identity-defining
> relationship — the entity within which this entity's ID is unique.
> It is intentionally narrow. Other kinds of relationships between
> entities (membership, deployment, runs-on, etc.) are out of scope
> for this section and may be addressed by a future general entity
> relationship model, which would be additive and would not redefine
> the meaning of ID Context Type.

## Merging of Entities

Entities MAY be merged if and only if their types are the same, their
identity attributes are exactly the same, their ID context types are
the same (including the case where both are empty), AND their
schema_url is the same. This means both Entities MUST have the same
identity attribute keys and for each key, the values of the key MUST
be the same.

Here's an example algorithm that will check compatibility:

```
can_merge(current_entity, new_entity) {
  current_entity.type == new_entity.type &&
  current_entity.schema_url == new_entity.schema_url &&
  current_entity.id_context_type == new_entity.id_context_type &&
  has_same_attributes(current_entity.identity, new_entity.identity)
}
```

When merging entities, all attributes in description are merged together, with
one entity acting as "primary" where any conflicting attribute values will be
chosen from the "primary" entity.

Here's an example algorithm that will merge:

```
merge(current_entity, new_entity) {
  if can_merge(current_entity, new_entity) {
    for attribute in new_entity.description {
      // New entity descriptions take precedence.
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
    <td><strong>Scope Kind</strong>
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
    <td>global
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
    <td>local (typical context: <code>k8s.pod</code>)
    </td>
    <td>k8s.container.restart_count
    </td>
   </tr>
   <tr>
    <td>Process
    </td>
    <td><pre>process</pre>
    </td>
    <td>process.pid<br/>
        process.creation.time
    </td>
    <td>local (typical context: <code>host</code>; may be <code>container</code>)
    </td>
    <td>process.command<br/>
        process.executable.name<br/>
        process.owner
    </td>
   </tr>
   <tr>
    <td>Service Instance
    </td>
    <td><pre>service.instance</pre>
    </td>
    <td>service.instance.id
    </td>
    <td>local (typical context: <code>service</code>)
    </td>
    <td>service.version
    </td>
   </tr>
</table>
