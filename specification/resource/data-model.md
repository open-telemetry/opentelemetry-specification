<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Data Model
weight: 2
--->

# Resource Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Identity](#identity)
- [Merging Resources](#merging-resources)
  * [Merging Entities into a Resource](#merging-entities-into-a-resource)

<!-- tocstop -->

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

### Merging Entities into a Resource

We define the following algorithm for merging entities into an existing
resource.

- Construct a set of existing entities on the resource, `E`.
  - For each entity, `new_entity`, in priority order (highest first),
    do one of the following:
    - If an entity `e` exists in `E` with the same entity type as `new_entity`:
      - Perform an [Entity DataModel Merge](../entities/data-model.md#merging-of-entities) with `e` and `new_entity`
      - Note: If unable to merge `e` and `new_entity`, then no change is made.
    - Otherwise, add the entity `new_entity` to set `E`
- Update the Resource to use the set of entities `E`.
  - If all entities within `E` have the same `schema_url`, set the
    resources `schema_url` to match.
  - Otherwise set the Resource `schema_url` blank.
  - Remove any attribute from `Attributes` which exists in either the
    description or identity of an entity in `E`.
- Solve for resource flattening issues (See
  [Attribute Referencing Model](../entities/data-model.md#attribute-referencing-model)).
  - If, for all entities, there are now overlapping attribute keys, then nothing
    is needed.
  - If there is a conflict where two entities use the same attribute key then
    remove the lower priority entity from the Resource.

#### Examples

_These examples demonstrate how conflicts are resolved during a merge._

##### Example 1: Entity replaces loose attribute

The conflict between loose attributes and those belonging to an entity. Here when entity is added it removes previous attributes.

**Initial Resource:**
- Entities: _None_
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

The conflict between loose attributes and those belonging to an entity. Here when the loose attribute is added, the entity must be removed due to conflict.

**Initial Resource:**
- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H1"`
    - description:
      - `host.name`: `"detected-name"`
- Attributes: _None_

**Resource to Merge:**
- Entities: _None_
- Attributes:
  - `host.id`: `"h2"`
  - `env`: `"prod"`

**Resulting Resource:**
- Entities: _None_
- Attributes:
  - `host.id`: `"h2"`
  - `env`: `"prod"`

##### Example 3: Identity & Attribute Conflicts

Reject an entity with a different identity of the same type, and drop a lower priority entity due to an attribute key conflict.

**Initial Resource:**
- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H1"`
    - description:
      - `env`: `"prod"`
- Attributes: _None_

**Entities to Merge (by priority):**
1. `host`
   - type: `"host"`
   - identity:
     - `host.id`: `"H2"`
2. `service`
   - type: `"service"`
   - identity:
     - `service.name`: `"S1"`
   - description:
     - `env`: `"dev"`

**Resulting Resource:**
- Entities:
  - `host`
    - type: `"host"`
    - identity:
      - `host.id`: `"H1"`
    - description:
      - `env`: `"prod"`
- Attributes: _None_

