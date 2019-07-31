# Resource API Overview
The resource library primarily defines a type that captures information about the entity
for which metrics or traces are reported. It further provides a framework for detection of
resource information from the environment and progressive population as signals propagate
from the core instrumentation library to a backend's exporter.

## Resource type
A `Resource` describes the entity for which a signal was collected through two fields:
* `type`: an optional string which describes a well-known type of resource.
* `labels`: a dictionary of labels with string keys and values that provide information
about the entity.

Type, label keys, and label values MUST contain only printable ASCII (codes between 32
and 126, inclusive) and not exceed 256 characters.
Type and label keys MUST have a length greater than zero. Label keys SHOULD start with the type
and separate hierarchies with `.` characters, e.g. `k8s.namespace.name`.

Implementations MAY define a `Resource` data type, constructed from the parameters above.
`Resource` MUST have getters for retrieving all the information used in `Resource` definition.

Example in Go:
```go
type Resource {
	Type   string
	Labels map[string]string
}
```

For the proto definition see [here][resource-proto-link]

## Populating resources
Resource information MAY be populated at any point between startup of the instrumented
application and passing it to a backend-specific exporter. This explicitly includes
the path through future OpenCensus components such as agents or services.

For example, process-identifying information may be populated through the library while
an agent attaches further labels about the underlying VM, the cluster, or geo-location.

### From environment variables
Population of resource information from environment variables MUST be provided by the
core library. It provides the user with an ubiquitous way to manually provide information
that may not be detectable automatically through available integration libraries.

Two environment variables are used:
* `OC_RESOURCE_TYPE`: defines the resource type. Leading and trailing whitespaces are trimmed.
* `OC_RESOURCE_LABELS`: defines resource labels as a comma-separated list of key/value pairs
(`[ <key>="value" [ ,<key>="<value>" ... ] ]`). `"` characters in values MUST be escaped with `\`.

For example:
* `OC_RESOURCE_TYPE=container`
* `OC_RESOURCE_LABELS=container.name="c1",k8s.pod.name="pod-xyz-123",k8s.namespace.name="default"`

Population from environment variables MUST be the first applied detection process unless
the user explicitly overwrites this behavior.

### Auto-detection
Auto-detection of resource information in specific environments, e.g. specific cloud
vendors, MUST be implemented outside of the core libraries in third party or
[census-ecosystem][census-ecosystem] repositories.

### Detectors
To make auto-detection implementations easy to use, the core resource package SHOULD define
an interface to retrieve resource information. Additionally, helper functionality MAY be
provided to effectively make use of this interface.
The exact shape of those interfaces and helpers SHOULD be idiomatic to the respective language.

Example in Go:

```go
type Detector func(context.Context) (*Resource, error)

// Returns a detector that runs all input detectors sequentially and merges their results.
func ChainedDetector(...Detector) Detector
```

### Updates
OpenCensus's resource representation is focused on providing static, uniquely identifying
information and thus those mutable attributes SHOULD NOT be included in the resource
representation.
Resource type and labels MUST NOT be mutated after initialization. Any changes MUST be
effectively be treated as a different resource and any associated signal state MUST be reset.

## Exporter translation
A resource object MUST NOT be mutated further once it is passed to a backend-specific exporter.
From the provided resource information, the exporter MAY transform, drop, or add information
to build the resource identifying data type specific to its backend.
If the passed resource does not contain sufficient information, an exporter MAY drop
signal data entirely, if no sufficient resource information is provided to perform a correct
write.

For example, from a resource object

```javascript
{
	"type": "container",
	"labels": {
		// Populated from VM environment through auto-detection library.
		"host.id": "instance1",
		"cloud.zone": "eu-west2-a",
		"cloud.account.id": "project1",
		// Populated through OpenCensus resource environment variables.
		"k8s.cluster_name": "cluster1",
		"k8s.namespace.name": "ns1",
		"k8s.pod.name": "pod1",
		"container.name": "container1",
	},
}
```

an exporter for Stackdriver would create the following "monitored resource", which is a
resource type with well-known identifiers specific to its API:

```javascript
{
	"type": "k8s_container",
	"labels": {
		"project_id": "project1",
		"location": "eu-west2-a",
		"cluster_name": "cluster1",
		"namespace_name": "ns1",
		"pod_name": "pod1",
		"container_name": "container1",
	},
}
```

For another, hypothetical, backend a simple unique identifier might be constructed instead
by its exporter:

```
cluster1/ns1/pod1/container1
```

Exporter libraries MAY provide a default translation for well-known input resource types and labels.
Those would generally be based on community-supported detection integrations maintained in the
[census-ecosystem][census-ecosystem-link] organisation.

Additionally, exporters SHOULD provide configuration hooks for users to provide their own
translation unless the exporter's backend does not support resources at all. For such backends,
exporters SHOULD allow attaching converting resource labels to metric tags.

[census-ecosystem-link]: https://github.com/census-ecosystem
[resource-proto-link]: https://github.com/census-instrumentation/opencensus-proto/blob/master/src/opencensus/proto/resource/v1/resource.proto
