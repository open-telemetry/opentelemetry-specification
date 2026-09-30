<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Data Model
weight: 2
--->

# Resource Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- START doctoc -->

- [Identity](#identity)
- [Merging Resources](#merging-resources)
  * [Merging An Entity into a Resource](#merging-an-entity-into-a-resource)
  * [Merging Resource Attributes into a Resource](#merging-resource-attributes-into-a-resource)
    + [Examples](#examples)
      - [Example 1: Entity replaces loose attribute](#example-1-entity-replaces-loose-attribute)
      - [Example 2: Loose attribute replaces entity attribute](#example-2-loose-attribute-replaces-entity-attribute)
      - [Example 3: Identity & Attribute Conflicts](#example-3-identity--attribute-conflicts)

<!-- END doctoc -->

</details>

A Resource represents the observed entity for which telemetry is produced.
It is defined by a set of Attributes that identify the source of the telemetry,
rather than the component that technically produces it (like an
auto-instrumentation agent).
For example, a process running in a container on Kubernetes is associated to a
Pod running on a Node that is a VM, in a namespace, and possibly part of a
Deployment. Resource could have attributes to denote information about the
Container, the Pod, the Node, the VM or the Deployment. All of these help
identify the observed entity. Note that there are certain attributes
that have prescribed meanings.

A resource is composed of 0 or more [`Entities`](../entities/README.md) and 0
or more attributes not associated with any entity.

The data model below defines a logical model for an Resource (irrespective of the physical format and encoding of how resource data is recorded).

| Field | Type | Description |
| ----- | ---- | ----------- |
| Entities | set\<Entity\> | Defines the set of Entities associated with this resource.<p>[Entity is defined here](../entities/data-model.md) |
| Attributes | map\<string, attribute value\> | Additional Attributes that identify the resource.<p>MUST not change during the lifetime of the resource.<p>Follows OpenTelemetry [attribute definition](../common/README.md#attribute). |

## Identity

Most resources are a composition of [`Entity`](../entities/data-model.md).
Entity includes its own notion of identity. The identity of a resource is
the set of entities contained within it. Two resources are considered
different if one contains an entity not found in the other.

Some resources include raw attributes in addition to Entities. Raw attributes are
considered identifying on a resource. That is, if the key-value pairs of
raw attributes are different, then you can assume the resource is different.

## Merging Resources

Note: The current SDK specification outlines a [merge algorithm](sdk.md#merge).
This specification updates the algorithm to be compliant with entities. This
section will replace that section upon stabilization of entities. SDKs SHOULD
NOT update their merge algorithm until full Entity SDK support is provided.

Merging resources is an action of joining together the context of observation.
That is, we can look at the resource context for a signal and *expand* that
context to include more details (see
[telescoping identity](README.md#telescoping)). As such, a merge SHOULD preserve
any identity that already existed on a Resource while adding in new identifying
information or descriptive attributes.

### Merging An Entity into a Resource

We define the following algorithm for merging an Entity into an existing Resource where `e` is the incoming entity and `E` is the set of entities in the resource:

* If `E` contains an entity `e'` that can be merged (equal `type`, `identity`, and `schema_url`) with `e`, apply the [`entity merge algorithm`](../entities/data-model.md#merging-of-entities).
* Else if `E` contains an entity `e'` with equal `type` that cannot be merged (unequal `identity` or `schema_url`), drop `e'` from `E` including all of its attributes and replace it with incoming entity `e`
* Else insert incoming entity `e` into `E`, overwriting any existing attributes.
* If, at any time, an entity being inserted or merged overwrites any attribute, identifying or descriptive, from a pre-existing Entity `e'`, drop `e'`'s `EntityRef`, retaining its other attributes as unassociated attributes.

### Merging Resource Attributes into a Resource

When merging a set of attributes into a Resource, the incoming attributes overwrite existing attributes. If any attribute being overwritten is a part of an Entity, the Entity is removed and all non-conflicting attributes of that entity are added to the Resource as unassociated attributes.

#### Examples

*These examples demonstrate how conflicts are resolved during a merge.*

##### Example 1: Entity replaces loose attribute

The conflict between loose attributes and those belonging to an entity. Here when entity is added it removes previous attributes.

**Initial Resource:**

- Entities: *None*
- Attributes:
  - `host.name`: `"old-name"`
  - `env`: `"prod"`

**Entities to Merge (by priority):**

1. `host`
   - type: `"host"`
   - identity:
     - `host.id`: `"H1"`
   - description:
     - `host.name`: `"new-name"`
2. `service`
   - type: `"service"`
   - identity:
     - `service.name`: `"my-svc"`

**Resulting Resource:**

- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H1"`
    - description:
      - `host.name`: `"new-name"`
  - `service`
    - type: `"service"`
    - identity:
      - `service.name`: `"my-svc"`
- Attributes:
  - `env`: `"prod"`

##### Example 2: Loose attribute replaces entity attribute

The conflict between loose attributes and those belonging to an entity. Here when the loose attribute is added, the entity must be removed due to conflict. The removed entity's other attributes are preserved as raw attributes.

**Initial Resource:**

- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H1"`
    - description:
      - `host.name`: `"detected-name"`
  - `process`
    - type: `"process"`
    - identity:
      - `process.pid`: `12345`
- Attributes: *None*

**Resource to Merge:**

- Entities: *None*
- Attributes:
  - `host.id`: `"h2"`
  - `env`: `"prod"`

**Resulting Resource:**

- Entities:
  - `process`
    - type: `"process"`
    - identity:
      - `process.pid`: `12345`
- Attributes:
  - `host.id`: `"h2"`
  - `host.name`: `"detected-name"`
  - `env`: `"prod"`

##### Example 3: Identity & Attribute Conflicts

Replace an existing entity that has the same type but a different identity, and drop a conflicting entity's `EntityRef` due to a descriptive attribute key conflict, retaining its remaining attributes as unassociated.

**Initial Resource:**

- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H2"`
  - `service`
    - type: `"service"`
    - identity:
      - `service.name`: `"S1"`
    - description:
      - `env`: `"dev"`
- Attributes: *None*

**Entity to Merge:**

- `host`
  - type: `"host"`
  - identity:
    - `host.id`: `"H1"`
  - description:
    - `env`: `"prod"`

**Resulting Resource:**

- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H1"`
    - description:
      - `env`: `"prod"`
- Attributes:
  - `service.name`: `"S1"`
