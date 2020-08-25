# Host

**type:** `host`

**Description:** A host is defined as a general computing instance.

| Attribute  | Description  | Example  |
|---|---|---|
| host.id | Unique host id.<br/> For Cloud this must be the instance_id assigned by the cloud provider | `opentelemetry-test` |
| host.name | Name of the host.<br/>On Unix systems, it may contain what the `hostname` command returns, or the fully qualified hostname, or another name specified by the user. | `opentelemetry-test` |
| host.type | Type of host.<br/> For Cloud this must be the machine type.| `n1-standard-1` |
| host.image.name | Name of the VM image or OS install the host was instantiated from. | `infra-ami-eks-worker-node-7d4ec78312`, `CentOS-8-x86_64-1905` |
| host.image.id | VM image id. For Cloud, this value is from the provider. | `ami-07b06b442921831e5` |
| host.image.version | The version string of the VM image as defined in [Version Attributes](./README.md#version-attributes). | `0.1` |
