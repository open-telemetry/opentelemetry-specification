# Process and process runtime resources

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Process](#process)
- [Process runtimes](#process-runtimes)
  * [Erlang Runtimes](#erlang-runtimes)
  * [Go Runtimes](#go-runtimes)
  * [Java runtimes](#java-runtimes)
  * [JavaScript runtimes](#javascript-runtimes)
  * [.NET Runtimes](#net-runtimes)
  * [Python Runtimes](#python-runtimes)
  * [Ruby Runtimes](#ruby-runtimes)

<!-- tocstop -->

## Process

**type:** `process`

**Description:** An operating system process.

<!-- semconv process -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `process.pid` | int | Process identifier (PID). | `1234` | No |
| `process.executable.name` | string | The name of the process executable. On Linux based systems, can be set to the `Name` in `proc/[pid]/status`. On Windows, can be set to the base name of `GetProcessImageFileNameW`. | `otelcol` | See below |
| `process.executable.path` | string | The full path to the process executable. On Linux based systems, can be set to the target of `proc/[pid]/exe`. On Windows, can be set to the result of `GetProcessImageFileNameW`. | `/usr/bin/cmd/otelcol` | See below |
| `process.command` | string | The command used to launch the process (i.e. the command name). On Linux based systems, can be set to the zeroth string in `proc/[pid]/cmdline`. On Windows, can be set to the first parameter extracted from `GetCommandLineW`. | `cmd/otelcol` | See below |
| `process.command_line` | string | The full command used to launch the process as a single string representing the full command. On Windows, can be set to the result of `GetCommandLineW`. Do not set this if you have to assemble it just for monitoring; use `process.command_args` instead. | `C:\cmd\otecol --config="my directory\config.yaml"` | See below |
| `process.command_args` | string[] | All the command arguments (including the command/executable itself) as received by the process. On Linux-based systems (and some other Unixoid systems supporting procfs), can be set according to the list of null-delimited strings extracted from `proc/[pid]/cmdline`. For libc-based executables, this would be the full argv vector passed to `main`. | `[cmd/otecol, --config=config.yaml]` | See below |
| `process.owner` | string | The username of the user that owns the process. | `root` | No |
<!-- endsemconv -->

Between `process.command_args` and `process.command_line`, usually `process.command_args` should be preferred.
On Windows and other systems where the native format of process commands is a single string,
`process.command_line` can additionally (or instead) be used.

For backwards compatibility with older versions of this semantic convention,
it is possible but deprecated to use an array as type for `process.command_line`.
In that case it MUST be interpreted as if it was `process.command_args`.

At least one of `process.executable.name`, `process.executable.path`, `process.command`, `process.command_line` or `process.command_args` is required to allow back ends to identify the executable.

## Process runtimes

**type:** `process.runtime`

**Description:** The single (language) runtime instance which is monitored.

<!-- semconv process.runtime -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `process.runtime.name` | string | The name of the runtime of this process. For compiled native binaries, this SHOULD be the name of the compiler. | `OpenJDK Runtime Environment` | No |
| `process.runtime.version` | string | The version of the runtime of this process, as returned by the runtime without modification. | `14.0.2` | No |
| `process.runtime.description` | string | An additional description about the runtime of the process, for example a specific vendor customization of the runtime environment. | `Eclipse OpenJ9 Eclipse OpenJ9 VM openj9-0.21.0` | No |
<!-- endsemconv -->

How to set these attributes for particular runtime kinds is described in the following subsections.

In addition to these attributes, [`telemetry.sdk.language`](README.md#telemetry-sdk) can be used to determine the general kind of runtime used.

### Erlang Runtimes

- `process.runtime.name` - The name of the Erlang VM being used, i.e., `erlang:system_info(machine)`.
- `process.runtime.version` -  The version of the runtime (ERTS - Erlang Runtime System), i.e., `erlang:system_info(version)`.
- `process.runtime.description` - string | An additional description about the runtime made by combining the OTP version, i.e., `erlang:system_info(otp_release)`, and ERTS version.

Example:

| `process.runtime.name` | `process.runtime.version` | `process.runtime.description` |
| --- | --- | --- |
| BEAM | 11.1 |  Erlang/OTP 23 erts-11.1 |

### Go Runtimes

TODO(<https://github.com/open-telemetry/opentelemetry-go/issues/1181>): Confirm the contents here

| Value | Description |
| --- | --- |
| `gc` | Go compiler |
| `gccgo` | GCC Go frontend |

### Java runtimes

Java instrumentation should fill in the values by copying from system properties.

- `process.runtime.name` - Fill in the value of `java.runtime.name` as is
- `process.runtime.version` - Fill in the value of `java.runtime.version` as is
- `process.runtime.description` - Fill in the values of `java.vm.vendor`, `java.vm.name`, `java.vm.version`
  in that order, separated by spaces.

Examples for some Java runtimes

| Name | `process.runtime.name` | `process.runtime.version` | `process.runtime.description` |
| --- | --- | --- | --- |
| OpenJDK | OpenJDK Runtime Environment | 11.0.8+10 | Oracle Corporation OpenJDK 64-Bit Server VM 11.0.8+10 |
| AdoptOpenJDK Eclipse J9 | OpenJDK Runtime Environment | 11.0.8+10 | Eclipse OpenJ9 Eclipse OpenJ9 VM openj9-0.21.0 |
| AdoptOpenJDK Hotspot | OpenJDK Runtime Environment | 11.0.8+10 | AdoptOpenJDK OpenJDK 64-Bit Server VM 11.0.8+10 |
| SapMachine | OpenJDK Runtime Environment | 11.0.8+10-LTS-sapmachine | SAP SE OpenJDK 64-Bit Server VM 11.0.8+10-LTS-sapmachine |
| Zulu OpenJDK | OpenJDK Runtime Environment | 11.0.8+10-LTS | Azul Systems, Inc OpenJDK 64-Bit Server VM Zulu11.41+23-CA |
| Oracle Hotspot 8 (32 bit) | Java(TM) SE Runtime Environment | 1.8.0_221-b11 | Oracle Corporation Java HotSpot(TM) Client VM 25.221-b11 |
| IBM J9 8 | Java(TM) SE Runtime Environment | 8.0.5.25 - pwa6480sr5fp25-20181030_01(SR5 FP25) | IBM Corporation IBM J9 VM 2.9 |
| Android 11 | Android Runtime | 0.9 | The Android Project Dalvik 2.1.0 |

### JavaScript runtimes

TODO(<https://github.com/open-telemetry/opentelemetry-js/issues/1544>): Confirm the contents here

| Value | Description |
| --- | --- |
| `nodejs` | NodeJS |
| `browser` | Web Browser |
| `iojs` | io.js |
| `graalvm` | GraalVM |

When the value is `browser`, `process.runtime.version` SHOULD be set to the User-Agent header.

### .NET Runtimes

TODO(<https://github.com/open-telemetry/opentelemetry-dotnet/issues/1281>): Confirm the contents here

| Value | Description |
| --- | --- |
| `dotnet-core` | .NET Core, .NET 5+ |
| `dotnet-framework` | .NET Framework |
| `mono` | Mono |

### Python Runtimes

Python instrumentation should fill in the values as follows:

- `process.runtime.name` -
  Fill in the value of [`sys.implementation.name`][py_impl]
- `process.runtime.version` -
  Fill in the [`sys.implementation.version`][py_impl] values separated by dots.
  Leave out the release level and serial if the release level
  equals `final` and the serial equals zero
  (leave out either both or none).

  This can be implemented with the following Python snippet:

  ```python
  vinfo = sys.implementation.version
  result =  ".".join(map(
      str,
      vinfo[:3]
      if vinfo.releaselevel == "final" and not vinfo.serial
      else vinfo
  ))
  ```

- `process.runtime.description` - Fill in the value of [`sys.version`](https://docs.python.org/3/library/sys.html#sys.version) as-is.

[py_impl]: https://docs.python.org/3/library/sys.html#sys.implementation

Examples for some Python runtimes:

| Name | `process.runtime.name` | `process.runtime.version` | `process.runtime.description` |
| --- | --- | --- | --- |
| CPython 3.7.3 on Windows | cpython | 3.7.3 | 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 22:22:05) [MSC v.1916 64 bit (AMD64)] |
| CPython 3.8.6 on Linux | cpython | 3.8.6 | 3.8.6 (default, Sep 30 2020, 04:00:38) <br>[GCC 10.2.0] |
| PyPy 3 7.3.2 on Linux | pypy | 3.7.4 | 3.7.4 (?, Sep 27 2020, 15:12:26)<br>[PyPy 7.3.2-alpha0 with GCC 10.2.0] |

Note that on Linux, there is an actual newline in the `sys.version` string,
and the CPython string had a trailing space in the first line.

Pypy provided a CPython-compatible version in `sys.implementation.version` instead of the actual implementation version which is available in `sys.version`.

### Ruby Runtimes

Ruby instrumentation should fill in the values by copying from built-in runtime constants.

- `process.runtime.name` - Fill in the value of `RUBY_ENGINE` as is
- `process.runtime.version` - Fill in the value of `RUBY_VERSION` as is
- `process.runtime.description` - Fill in the value of `RUBY_DESCRIPTION` as is

Examples for some Ruby runtimes

| Name | `process.runtime.name` | `process.runtime.version` | `process.runtime.description` |
| --- | --- | --- | --- |
| MRI | ruby | 2.7.1 | ruby 2.7.1p83 (2020-03-31 revision a0c7c23c9c) [x86_64-darwin19] |
| TruffleRuby | truffleruby | 2.6.2 | truffleruby (Shopify) 20.0.0-dev-92ed3059, like ruby 2.6.2, GraalVM CE Native [x86_64-darwin] |
