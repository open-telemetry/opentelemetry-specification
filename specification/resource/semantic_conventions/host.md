# Host

**Status**: [Experimental](../../document-status.md)

**type:** `host`

**Description:** A host is defined as a general computing instance.

<!-- semconv host -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `host.id` | string | Unique host ID. For Cloud, this must be the instance_id assigned by the cloud provider. | `opentelemetry-test` | No |
| `host.name` | string | Name of the host. On Unix systems, it may contain what the hostname command returns, or the fully qualified hostname, or another name specified by the user. | `opentelemetry-test` | No |
| `host.type` | string | Type of host. For Cloud, this must be the machine type. | `n1-standard-1` | No |
| `host.arch` | string | The CPU architecture the host system is running on. | `amd64` | No |
| `host.image.name` | string | Name of the VM image or OS install the host was instantiated from. | `infra-ami-eks-worker-node-7d4ec78312`; `CentOS-8-x86_64-1905` | No |
| `host.image.id` | string | VM image ID. For Cloud, this value is from the provider. | `ami-07b06b442921831e5` | No |
| `host.image.version` | string | The version string of the VM image as defined in [Version Attributes](README.md#version-attributes). | `0.1` | No |

`host.arch` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `amd64` | AMD64 |
| `arm32` | ARM32 |
| `arm64` | ARM64 |
| `ia64` | Itanium |
| `ppc32` | 32-bit PowerPC |
| `ppc64` | 64-bit PowerPC |
| `x86` | 32-bit x86 |
<!-- endsemconv -->
