<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Entity Events
weight: 3
--->

# Entity Events

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [When to Use Entity Events](#when-to-use-entity-events)
- [Entity Events Data Model](#entity-events-data-model)
  * [Entity State Event](#entity-state-event)
  * [Entity Delete Event](#entity-delete-event)
- [Entity Relationships](#entity-relationships)
  * [Relationship Structure](#relationship-structure)
  * [Standard Relationship Types](#standard-relationship-types)
  * [Relationship Lifecycle](#relationship-lifecycle)
- [Examples](#examples)
  * [Kubernetes Pod Entity State](#kubernetes-pod-entity-state)
  * [Entity Delete Event](#entity-delete-event-1)

<!-- tocstop -->

</details>

## Overview

Entity events provide a way to communicate entity information as structured log events.
This approach is complementary to defining entities as part of Resource data (see [Entity Data Model](./data-model.md)).

Entity events are represented as structured events using the OpenTelemetry [Logs Data Model](../logs/data-model.md),
specifically as [Events](../logs/data-model.md#events) with a defined `EventName` and attribute structure.

## When to Use Entity Events

Entity events SHOULD be used when:

1. **No Associated Telemetry**: The entity has no telemetry signals associated with it, or
   the telemetry is less important than the entity data itself.

2. **Complex Descriptive Information**: Entity descriptive information is too complex for
   simple resource attribute values. The resource attribute values are expected to be simple
   strings, but entity descriptions can contain complex values like maps and arrays
   (e.g., Kubernetes ConfigMap content, complex cloud metadata, nested tags).

3. **Entity Relationships**: The entity information needs to include relationships to other
   entities. Resource data cannot contain relationship information.

4. **Lifecycle Tracking**: There is a need to explicitly track entity lifecycle events
   (creation, state changes, deletion) independently from telemetry signals.

## Entity Events Data Model

Entity events use the OpenTelemetry Logs Data Model with specific conventions for the
`EventName` and `Attributes` fields.

### Entity State Event

The Entity State Event stores information about the state of an entity at a particular moment in time.

**Event Name**: `entity.state`

**Required Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.type` | string | Defines the type of the entity. MUST not change during the lifetime of the entity. For example: "service", "host", "k8s.pod". |
| `entity.id` | map<string, AnyValue> | Attributes that identify the entity. MUST not change during the lifetime of the entity. The map MUST contain at least one attribute. Follows OpenTelemetry [attribute definition](../common/README.md#attribute). |

**Optional Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.description` | map<string, AnyValue> | Descriptive (non-identifying) attributes of the entity. MAY change over the lifetime of the entity. These attributes are not part of the entity's identity. Follows [AnyValue](../common/README.md#anyvalue) definition: can contain scalar values, arrays, or nested maps. SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions) for attributes. |
| `entity.interval` | int64 (milliseconds) | Defines the reporting period, i.e., how frequently information about this entity is reported via Entity State events even if the entity does not change. The next expected Entity State event for this entity is expected at (Timestamp + Interval) time. Can be used by receivers to infer that a no longer reported entity is gone, even if the Entity Delete event was not observed. |
| `entity.relationships` | array of map<string, AnyValue> | Array of relationships that this entity has with other entities. See [Entity Relationships](#entity-relationships) for details. |

**Timestamp Field**:

The `Timestamp` field of the LogRecord represents the time when the entity state described
by this event became effective. This is the time measured by the origin clock.

**State Mutations**:

An entity mutates (changes) when one or more of its descriptive attributes changes, or when
its relationships change. A new descriptive attribute may be added, an existing descriptive
attribute may be deleted, or a value of an existing descriptive attribute may be changed.
All these changes represent valid mutations of an entity over time. When these mutations
happen, the identity of the entity does not change.

When the entity's state changes, sources SHOULD emit a new Entity State event with a fresh
timestamp and the complete current state of all fields.

**Periodic Reporting**:

Entity event producers SHOULD periodically emit Entity State events even if the entity does
not change. In this case, the `entity.type`, `entity.id`, `entity.description`, and
`entity.relationships` fields will remain the same, but a fresh `Timestamp` will be recorded.
Producing such events allows the system to be resilient to event losses and serves as a
liveliness indicator.

### Entity Delete Event

The Entity Delete Event indicates that a particular entity is gone.

**Event Name**: `entity.delete`

**Required Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.type` | string | The type of the entity being deleted. |
| `entity.id` | map<string, AnyValue> | Attributes that identify the entity being deleted. |

**Optional Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.delete.reason` | string | The reason for entity deletion. Examples: "terminated", "expired", "evicted", "user_requested", "scaled_down". |

**Timestamp Field**:

The `Timestamp` field of the LogRecord represents the time when the entity was deleted,
measured by the origin clock.

**Delivery Guarantees**:

Transmitting Entity Delete events is not guaranteed when an entity is gone. Recipients of
entity signals MUST be prepared to handle this situation by expiring entities that are no
longer seeing Entity State events reported. The expiration mechanism is based on the
previously reported `entity.interval` field. Recipients can use this value to compute when
to expect the next Entity State event and, if the event does not arrive in a timely manner
(plus some slack), consider the entity to be gone even if the Entity Delete event was not observed.

## Entity Relationships

Entity relationships describe how entities are connected to each other. Relationships are
embedded within Entity State events as an array of relationship descriptors.

### Relationship Structure

Each relationship in the `entity.relationships` array is a map containing:

**Required Fields**:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `relationship.type` | string | The type of relationship. Describes the semantic meaning of the relationship (e.g., "scheduled_on", "contains", "depends_on"). See [Standard Relationship Types](#standard-relationship-types). |
| `entity.type` | string | The type of the target entity. |
| `entity.id` | map<string, AnyValue> | The identifying attributes of the target entity. |

**Optional Fields**:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `attributes` | map<string, AnyValue> | Additional relationship-specific attributes that provide context about the relationship. |

**Relationship Direction**:

Relationships have direction: `source --[type]--> target`, where:

- The **source** is the entity emitting the Entity State event
- The **target** is referenced in the relationship descriptor

### Standard Relationship Types

The following are recommended relationship types with their semantic meanings:

| Type | Direction | Meaning | Example |
| ---- | --------- | ------- | ------- |
| `runs_on` | Logical → Infrastructure | A logical entity runs on infrastructure | Process → Host |
| `scheduled_on` | Workload → Infrastructure | A workload is scheduled on infrastructure | Pod → Node |
| `contains` | Parent → Child | A parent entity contains a child entity | Pod → Container |
| `part_of` | Child → Parent | A child entity is part of a parent | Container → Pod |
| `depends_on` | Consumer → Dependency | An entity depends on another for functionality | Service → Database |
| `manages` | Controller → Controlled | An entity manages the lifecycle of another | Deployment → ReplicaSet |
| `hosts` | Infrastructure → Workload | Infrastructure hosts a workload (reverse of scheduled_on) | Node → Pod |

Custom relationship types MAY be defined to represent domain-specific relationships.
Semantic conventions MUST define standard relationship types for common entity types.

### Relationship Lifecycle

**Creating Relationships**:
Emit an Entity State event with the new relationship included in the `entity.relationships` array.

**Updating Relationships**:
Emit a new Entity State event with the updated `entity.relationships` array reflecting the current state.

**Deleting Relationships**:
Emit a new Entity State event with the relationship removed from the `entity.relationships` array.

**Implicit Deletion**:
When an entity is deleted (Entity Delete event is emitted), all relationships where that
entity is the source are implicitly deleted. Backends SHOULD handle this accordingly.

## Examples

### Kubernetes Pod Entity State

```json
{
  "timestamp": "2026-01-12T10:30:00.000000000Z",
  "eventName": "entity.state",
  "resource": {
    "attributes": {
      "k8s.cluster.name": "prod-cluster"
    }
  },
  "attributes": {
    "entity.type": "k8s.pod",
    "entity.id": {
      "k8s.pod.uid": "abc-123-def-456"
    },
    "entity.description": {
      "k8s.pod.name": "nginx-deployment-66b6c",
      "k8s.namespace.name": "default",
      "k8s.pod.labels": {
        "app": "nginx",
        "version": "1.21",
        "tier": "frontend"
      },
      "k8s.pod.phase": "Running",
    },
    "entity.interval": 60000,
    "entity.relationships": [
      {
        "relationship.type": "scheduled_on",
        "entity.type": "k8s.node",
        "entity.id": {
          "k8s.node.uid": "node-001"
        }
      },
      {
        "relationship.type": "contains",
        "entity.type": "container",
        "entity.id": {
          "container.id": "container-456"
        }
      },
      {
        "relationship.type": "contains",
        "entity.type": "container",
        "entity.id": {
          "container.id": "container-789"
        }
      },
      {
        "relationship.type": "part_of",
        "entity.type": "k8s.replicaset",
        "entity.id": {
          "k8s.replicaset.uid": "rs-456"
        }
      }
    ]
  }
}
```

### Entity Delete Event

When the Pod is terminated:

```json
{
  "timestamp": "2026-01-12T11:00:00.000000000Z",
  "eventName": "entity.delete",
  "resource": {
    "attributes": {
      "k8s.cluster.name": "prod-cluster"
    }
  },
  "attributes": {
    "entity.type": "k8s.pod",
    "entity.id": {
      "k8s.pod.uid": "abc-123-def-456"
    },
    "entity.delete.reason": "terminated"
  }
}
```
