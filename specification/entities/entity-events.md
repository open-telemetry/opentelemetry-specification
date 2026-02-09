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
- [Event Types](#event-types)
  * [Entity State Event](#entity-state-event)
  * [Entity Delete Event](#entity-delete-event)
- [Entity Relationships](#entity-relationships)
  * [Relationship Structure](#relationship-structure)
  * [Standard Relationship Types](#standard-relationship-types)
  * [Relationship Placement](#relationship-placement)
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

Entity events are particularly useful when:

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

Entity events can be used alongside telemetry signals associated with entities to provide
additional context and relationship information.

## Event Types

Entity information is communicated through the following event types:

1. **Entity State Event** (`entity.state`): Emitted when an entity is created, when its
   attributes change, or periodically to indicate the entity still exists.

2. **Entity Delete Event** (`entity.delete`): Emitted when an entity is removed.

### Entity State Event

The Entity State Event is emitted when an entity is created, when its descriptive attributes
change, or periodically to indicate the entity still exists.

**Event Name**: `entity.state`

**Required Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.type` | string | Defines the type of the entity. MUST not change during the lifetime of the entity. For example: "service", "host", "k8s.pod". |
| `entity.id` | map<string, string> | Attributes that identify the entity. MUST not change during the lifetime of the entity. The map MUST contain at least one attribute. Keys and values MUST be strings. SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions) for attribute names. |
| `entity.description` | map<string, AnyValue> | Descriptive (non-identifying) attributes of the entity. These attributes are not part of the entity's identity. Each Entity State event contains the complete current state of the entity's description. Follows [AnyValue](../common/README.md#anyvalue) definition: can contain scalar values, arrays, or nested maps. SHOULD follow OpenTelemetry [semantic conventions](https://github.com/open-telemetry/semantic-conventions) for attributes. |
| `entity.relationships` | array of maps | Relationships to other entities. Each relationship is a map containing: `type` (string, describes the relationship), `entity.type` (string, the type of the related entity), and `entity.id` (map<string, string>, identifying attributes of the related entity). |
| `report.interval` | int64 (milliseconds) | The reporting interval for this entity. MUST be a non-negative value. A value of `0` indicates that periodic reporting is disabled and only state changes will be reported. A positive value indicates the interval at which periodic state events will be emitted. Can be used by receivers to infer that a no longer reported entity is gone, even if the Entity Delete event was not observed. |

**Timestamp Field**:

The `Timestamp` field of the LogRecord represents the time when this event was generated and sent.

**Event Emission**:

Implementations SHOULD emit Entity State events whenever entity descriptive attributes change,
and periodically based on the `report.interval` value to indicate the entity still exists.
Implementations SHOULD also emit Entity Delete events when entities are removed.

**Future Considerations**:

Each Entity State event contains the complete current state of the entity. If scalability
issues arise in the future, the specification may introduce a "patch" event mechanism to
communicate only the changes rather than the full state.

### Entity Delete Event

The Entity Delete Event indicates that a particular entity is gone.

**Event Name**: `entity.delete`

**Required Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.type` | string | The type of the entity being deleted. |
| `entity.id` | map<string, string> | Attributes that identify the entity being deleted. |

**Optional Attributes**:

| Attribute | Type | Description |
| --------- | ---- | ----------- |
| `entity.delete.reason` | string | The reason for entity deletion. Examples: "terminated", "expired", "evicted", "user_requested", "scaled_down". |

**Timestamp Field**:

The `Timestamp` field of the LogRecord represents the time when the entity was deleted.

**Delivery Guarantees**:

Transmitting Entity Delete events is not guaranteed when an entity is gone. Recipients of
entity signals MUST be prepared to handle this situation by expiring entities that are no
longer seeing Entity State events reported. The expiration mechanism is based on the
previously reported `report.interval` field. Recipients can use this value to compute when
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
| `entity.id` | map<string, string> | The identifying attributes of the target entity. |

**Optional Fields**:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `attributes` | map<string, AnyValue> | Additional relationship-specific attributes that provide context about the relationship. These attributes can change over time as the entire `entity.relationships` array is replaced in subsequent Entity State events. |

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

Relationship types form an open enumeration. Custom relationship types MAY be defined to
represent domain-specific relationships. Semantic conventions SHOULD define standard
relationship types for common entity types.

### Relationship Placement

When choosing which entity should contain a relationship in its `entity.relationships` array,
implementations SHOULD prefer placing relationships on the entity type with the **shorter
lifespan** or **higher churn rate**. This minimizes the total number of Entity State events
that need to be sent.

**Rationale**: Since relationships are embedded in Entity State events, every time an entity's
relationships change, a new state event must be emitted. Placing relationships on the more
stable entity would require frequent state event emissions whenever the shorter-lived entities
are created or destroyed.

**Examples**:

- **Prefer**: `k8s.pod -> part_of -> k8s.replicaset` (relationship on the pod)
  - **Rather than**: `k8s.replicaset -> contains -> k8s.pod` (relationship on the replicaset)
  - **Reason**: Pods churn frequently. With relationships on pods, only new pod state events
    are sent when pods are created/destroyed. If relationships were on the replicaset, every
    pod creation/destruction would require a new replicaset state event with an updated list
    of all contained pods.

- **Prefer**: `container -> part_of -> k8s.pod` (relationship on the container)
  - **Rather than**: `k8s.pod -> contains -> container` (relationship on the pod)
  - **Reason**: Containers may restart independently, so placing the relationship on the
    container reduces the number of pod state events.

- **Prefer**: `process -> runs_on -> host` (relationship on the process)
  - **Rather than**: `host -> hosts -> process` (relationship on the host)
  - **Reason**: Processes start and stop frequently, while hosts are long-lived.

When both entities have similar lifespans, either direction is acceptable. Semantic conventions
SHOULD provide guidance on relationship placement for common entity types.

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

The following examples show the logical representation of entity events. These are NOT
actual OTLP wire format representations, but rather illustrate the semantic structure
of the events.

### Kubernetes Pod Entity State

When a Kubernetes Pod is created or its attributes change:

```
LogRecord:
  Timestamp: 2026-01-12T10:30:00.000000000Z
  EventName: entity.state
  Resource:
    k8s.cluster.name: prod-cluster
  Attributes:
    entity.type: k8s.pod
    entity.id:
      k8s.pod.uid: abc-123-def-456
    entity.description:
      k8s.pod.name: nginx-deployment-66b6c
      k8s.pod.labels:
        app: nginx
        version: "1.21"
        tier: frontend
      k8s.pod.phase: Running
    report.interval: 60000
    entity.relationships:
      - relationship.type: scheduled_on
        entity.type: k8s.node
        entity.id:
          k8s.node.uid: node-001
      - relationship.type: part_of
        entity.type: k8s.replicaset
        entity.id:
          k8s.replicaset.uid: rs-456
```

### Periodic Entity Report

Periodic report for the same Pod with no changes:

```
LogRecord:
  Timestamp: 2026-01-12T10:31:00.000000000Z
  EventName: entity.state
  Resource:
    k8s.cluster.name: prod-cluster
  Attributes:
    entity.type: k8s.pod
    entity.id:
      k8s.pod.uid: abc-123-def-456
    entity.description:
      k8s.pod.name: nginx-deployment-66b6c
      k8s.pod.labels:
        app: nginx
        version: "1.21"
      k8s.pod.phase: Running
    report.interval: 60000
```

### Entity Delete

When the Pod is terminated:

```
LogRecord:
  Timestamp: 2026-01-12T11:00:00.000000000Z
  EventName: entity.delete
  Resource:
    k8s.cluster.name: prod-cluster
  Attributes:
    entity.type: k8s.pod
    entity.id:
      k8s.pod.uid: abc-123-def-456
    entity.delete.reason: terminated
```
