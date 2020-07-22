# Operating System

**type:** `os`

**Description**: The operating system (OS) on which the process represented by this resource is running.

In case of virtualized environments, this is the operating system as it is observed by the process, i.e., the virtualized guest rather than the underlying host.

| Attribute  | Type | Description  | Example  | Required |
|---|---|---|---|---|
| `os.type` | string | The operating system type. | `"WINDOWS"` | Yes |
| `os.description` | string | Human readable (not intended to be parsed) OS version information, like e.g. reported by `ver` or `lsb_release -a` commands. | `"Microsoft Windows [Version 10.0.18363.778]"`<br>`"Ubuntu 18.04.1 LTS"` | No |

`os.type` SHOULD be set to one of the values listed below.
If none of the listed values apply, a custom value best describing the family the operating system belongs to CAN be used.

| Value  | Description |
|---|---|
| `WINDOWS` | Microsoft Windows |
| `LINUX` | Linux |
| `DARWIN` | Apple Darwin |
| `FREEBSD` | FreeBSD |
| `NETBSD` | NetBSD|
| `OPENBSD` | OpenBSD |
| `DRAGONFLYBSD` | DragonFly BSD |
| `HPUX` | HP-UX (Hewlett Packard Unix) |
| `AIX` | AIX (Advanced Interactive eXecutive) |
| `SOLARIS` | Oracle Solaris |
| `ZOS` | IBM z/OS |
