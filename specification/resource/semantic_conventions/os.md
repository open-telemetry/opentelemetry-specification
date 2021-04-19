# Operating System

**Status**: [Experimental](../../document-status.md)

**type:** `os`

**Description**: The operating system (OS) on which the process represented by this resource is running.

In case of virtualized environments, this is the operating system as it is observed by the process, i.e., the virtualized guest rather than the underlying host.

<!-- semconv os -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `os.type` | string | The operating system type. | `windows` | Yes |
| `os.description` | string | Human readable (not intended to be parsed) OS version information, like e.g. reported by `ver` or `lsb_release -a` commands. | `Microsoft Windows [Version 10.0.18363.778]`; `Ubuntu 18.04.1 LTS` | No |

`os.type` MUST be one of the following or, if none of the listed values apply, a custom value:

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
| `solaris` | Oracle Solaris |
| `z_os` | IBM z/OS |
<!-- endsemconv -->