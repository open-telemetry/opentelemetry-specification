# Host

**Status**: [Experimental](../../document-status.md)

**type:** `host`

**Description:** A host is defined as a general computing instance.

<!-- semconv host -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `host.id` | string | Unique host ID. For Cloud, this must be the instance_id assigned by the cloud provider. For non-containerized systems, this should be the `machine-id`. See the table below for the sources to use to determine the `machine-id` based on operating system. | `fdbf79e8af94cb7f9e8df36789187052` | Recommended |
| `host.name` | string | Name of the host. On Unix systems, it may contain what the hostname command returns, or the fully qualified hostname, or another name specified by the user. | `opentelemetry-test` | Recommended |
| `host.type` | string | Type of host. For Cloud, this must be the machine type. | `n1-standard-1` | Recommended |
| `host.arch` | string | The CPU architecture the host system is running on. | `amd64` | Recommended |
| `host.image.name` | string | Name of the VM image or OS install the host was instantiated from. | `infra-ami-eks-worker-node-7d4ec78312`; `CentOS-8-x86_64-1905` | Recommended |
| `host.image.id` | string | VM image ID. For Cloud, this value is from the provider. | `ami-07b06b442921831e5` | Recommended |
| `host.image.version` | string | The version string of the VM image as defined in [Version Attributes](README.md#version-attributes). | `0.1` | Recommended |

`host.arch` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `amd64` | AMD64 |
| `arm32` | ARM32 |
| `arm64` | ARM64 |
| `ia64` | Itanium |
| `ppc32` | 32-bit PowerPC |
| `ppc64` | 64-bit PowerPC |
| `s390x` | IBM z/Architecture |
| `x86` | 32-bit x86 |
<!-- endsemconv -->

## Collecting host.id from non-containerized systems

### Non-privileged Machine ID Lookup

When collecting `host.id` for non-containerized systems non-privileged lookups
of the machine id are preferred. SDK detector implementations MUST use the
sources listed below to obtain the machine id.

| OS      | Primary                                                                             | Fallback                               |
|---------|-------------------------------------------------------------------------------------|----------------------------------------|
| Linux   | contents of `/etc/machine-id`                                                       | contents of `/var/lib/dbus/machine-id` |
| BSD     | contents of `/etc/hostid`                                                           | output of `kenv -q smbios.system.uuid` |
| MacOS   | `IOPlatformUUID` line from the output of `ioreg -rd1 -c "IOPlatformExpertDevice"`   | -                                      |
| Windows | `MachineGuid` from registry `HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography` | -                                      |

### Privileged Machine ID Lookup

The `host.id` can be looked up using privileged sources. For example, Linux
systems can use the output of `dmidecode -t system`, `dmidecode -t baseboard`,
`dmidecode -t chassis`, or read the corresponding data from the filesystem
(e.g. `cat /sys/devices/virtual/dmi/id/product_id`,
`cat /sys/devices/virtual/dmi/id/product_uuid`, etc), however, SDK resource
detector implementations MUST not collect `host.id` from privileged sources. If
privileged lookup of `host.id` is required, the value should be injected via the
`OTEL_RESOURCE_ATTRIBUTES` environment variable.
