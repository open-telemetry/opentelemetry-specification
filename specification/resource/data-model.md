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

<!-- tocstop -->

</details>

A Resource is a representation of the entity producing telemetry as Attributes.
For example, You could have a process producing telemetry that is
running in a container on Kubernetes, which is associated to a Pod running on a
Node that is a VM but also is in a namespace and possibly is part of a
Deployment. Resource could have attributes to denote information about the
Container, the Pod, the Node, the VM or the Deployment. All of these help
identify what produced the telemetry. Note that there are certain "standard
attributes" that have prescribed meanings.

A resource is composed of 0 or more [`Entities`](../entities/README.md) and 0
or more attributes not associated with any entity.

The data model below defines a logical model for an Resource (irrespective of the physical format and encoding of how resource data is recorded).

| Field      | Type     | Description     |
|------------|----------|-----------------|
| Entities   | set\<Entity\> | Defines the set of Entities associated with this resource.<p>[Entity is defined here](../entities/data-model.md) |
| Attributes | map\<string, standard attribute value\> | Additional Attributes that identify the resource.<p>MUST not change during the lifetime of the resource.<p>Follows OpenTelemetry [Standard attribute definition](../common/README.md#standard-attribute). |

## Identity

Most resources are a composition of [`Entity`](../entities/data-model.md).
Entity includes its own notion of identity. The identity of a resource is
the set of entities contained within it. Two resources are considered
different if one contains an entity not found in the other.

Some resources include raw attributes in additon to Entities. Raw attributes are
considered identifying on a resource. That is, if the key-value pairs of
raw attributes are different, then you can assume the resource is different.
