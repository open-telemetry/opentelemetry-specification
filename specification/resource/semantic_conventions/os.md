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
| `os.langs` | string[] | A list of BCP 47 language tags [1] | `[en-US, zh-Hant-CN]` | No |
| `os.name` | string | Human readable operating system name. | `iOS`; `Android`; `Ubuntu` | No |
| `os.tz` | string | An IANA Time Zone Database name or NormalizedCustomID value [2] | `America/Los_Angeles`; `UTC`; `GMT-08:00` | No |
| `os.version` | string | The version string of the operating system as defined in [Version Attributes](../../resource/semantic_conventions/README.md#version-attributes). | `14.2.1`; `18.04.1` | No |

**[1]:** A list of [BCP 47 language tags](https://tools.ietf.org/rfc/bcp/bcp47.txt), in user-configured preference order. This may be derived from OS APIs, such as `Locale.preferredLanguages` on macOS/iOS, `LocaleList.getDefault()` on Android, and `GlobalizationPreferences.Languages` on Windows.

**[2]:** Identifies the timezone of the operating system instance, using a timezone identifier from the IANA [Time Zone Database](https://www.iana.org/time-zones). This may be derived from OS APIs, such as `TimeZone.current` on iOS or `TimeZone.getDefault()` on Android. Systems without a means of converting to IANA identifiers may use Java's [NormalizedCustomID](https://docs.oracle.com/javase/8/docs/api/java/util/TimeZone.html#NormalizedCustomID) format.

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
| `solaris` | Oracle Solaris |
| `z_os` | IBM z/OS |
<!-- endsemconv -->