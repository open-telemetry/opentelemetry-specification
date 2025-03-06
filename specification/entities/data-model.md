# Entity Data Model

**Status**: [Development](../document-status.md)


<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Minimally Sufficient Id](#minimally-sufficient-id)
- [Examples of Entities](#examples-of-entities)

<!-- tocstop -->

</details>

Entity represents an object of interest associated with produced telemetry:
traces, metrics or logs.

For example, telemetry produced using OpenTelemetry SDK is normally associated with
a `service` entity. Similarly, OpenTelemetry defines system metrics for a `host`. The `host` is the
entity we want to associate metrics with in this case.

Entities may be also associated with produced telemetry indirectly.
For example a service that produces
telemetry is also related with a process in which the service runs, so we say that
the Service entity is related to the `process` entity. The process normally also runs
on a host, so we say that the `process` entity is related to the `host` entity.

> Note: How entities are associated will be refined in future specification work.

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
    <td>Description
    </td>
    <td>map&lt;string, any&gt;
    </td>
    <td>Descriptive (non-identifying) attributes of the entity.
<p>
MAY change over the lifetime of the entity. MAY be empty. These
attributes are not part of entity's identity.
<p>
Follows <a
href="../../specification/logs/data-model.md#type-any">any</a>
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

### Minimally Sufficient Id

Commonly, a number of attributes of an entity are readily available for the telemetry
producer to compose an Id from. Of the available attributes the entity Id should
include the minimal set of attributes that is sufficient for uniquely identifying
that entity. For example
a Process on a host can be uniquely identified by (`process.pid`,`process.start_time`)
attributes. Adding for example `process.executable.name` attribute to the Id is
unnecessary and violates the Minimally Sufficient Id rule.

### Examples of Entities

_This section is non-normative and is present only for the purposes of demonstrating
the data model._

Here are examples of entities, the typical identifying attributes they
have and some examples of non-identifying attributes that may be
associated with the entity.

*Note: These examples MAY diverge from semantic conventions.*

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
