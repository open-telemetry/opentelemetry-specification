# OpenCensus Library Resource Package
This documentation serves to document the "look and feel" of the OpenCensus resource package.
It describes their key types and overall behavior.

The resource library primarily defines a type "Resource" that captures information about the
entity for which stats or traces are recorded. For example, metrics exposed by a Kubernetes
container can be linked to a resource that specifies the cluster, namespace, pod, and container name.
The primary purpose of resources as a first-class concept in the core library is decoupling
of discovery of resource information from exporters. This allows for independent development
of easy customization for users that need to integrate with closed source environments.


## Main APIs
* [Resource](Resource.md)
