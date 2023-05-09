# Operating System

**Status**: [Experimental](../../document-status.md)

**type:** `os`

**Description**: The operating system (OS) on which the process represented by this resource is running.

In case of virtualized environments, this is the operating system as it is observed by the process, i.e., the virtualized guest rather than the underlying host.

<!-- semconv os -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `os.type` | string | The operating system type. | `windows` | Required |
| `os.description` | string | Human readable (not intended to be parsed) OS version information, like e.g. reported by `ver` or `lsb_release -a` commands. | `Microsoft Windows [Version 10.0.18363.778]`; `Ubuntu 18.04.1 LTS` | Recommended |
| `os.name` | string | Human readable operating system name. | `iOS`; `Android`; `Ubuntu` | Recommended |
| `os.version` | string | The version string of the operating system as defined in [Version Attributes](../../resource/semantic_conventions/README.md#version-attributes). | `14.2.1`; `18.04.1` | Recommended |

`os.type` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `windows` | Microsoft Windows |
| `linux` | Linux |
| `darwin` | Apple Darwin |
| `freebsd` | FreeBSD |
| `netbsd` | NetBSD |
| `openbsd` | OpenBSD |
| `dragonflybsd` | DragonFly BSD |
| `hpux` | HP-UX (Hewlett Packard Unix) |
| `aix` | AIX (Advanced Interactive eXecutive) |
| `solaris` | SunOS, Oracle Solaris |
| `z_os` | IBM z/OS |
<!-- endsemconv -->