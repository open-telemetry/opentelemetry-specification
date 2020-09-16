# Process

**type:** `process`

**Description:** An operating system process.

| Attribute  | Description  | Example  | Required |
|---|---|---|--|
| process.pid | Process identifier (PID). | `1234` | Yes |
| process.executable.name | The name of the process executable. On Linux based systems, can be set to the `Name` in `proc/[pid]/status`. On Windows, can be set to the base name of `GetProcessImageFileNameW`. | `otelcol` | See below |
| process.executable.path | The full path to the process executable. On Linux based systems, can be set to the target of `proc/[pid]/exe`. On Windows, can be set to the result of `GetProcessImageFileNameW`. | `/usr/bin/cmd/otelcol` | See below |
| process.command | The command used to launch the process (i.e. the command name). On Linux based systems, can be set to the zeroth string in `proc/[pid]/cmdline`. On Windows, can be set to the first parameter extracted from `GetCommandLineW`. | `cmd/otelcol` | See below |
| process.command_line | The full command used to launch the process. The value can be either a list of strings representing the ordered list of arguments, or a single string representing the full command. On Linux based systems, can be set to the list of null-delimited strings extracted from `proc/[pid]/cmdline`. On Windows, can be set to the result of `GetCommandLineW`. | Linux: `[ cmd/otecol, --config=config.yaml ]`, Windows: `cmd/otecol --config=config.yaml` | See below |
| process.owner | The username of the user that owns the process. | `root` | No |
| process.runtime.name | The name of the runtime of this process. For compiled native binaries, this SHOULD be the name of the compiler. | `OpenJDK Runtime Environment` | No |
| process.runtime.version | The version of the runtime of this process, as returned by the runtime without modification. | `14.0.2` | No |
| process.runtime.description | An additional description about the runtime of the process, for example a specific vendor customization of the runtime environment. | `Eclipse OpenJ9 openj9-0.21.0` | No |

At least one of `process.executable.name`, `process.executable.path`, `process.command`, or `process.command_line` is required.

`process.runtime.name` SHOULD be set to one of the values listed below, unless more detailed instructions are provided.
If none of the listed values apply, a custom value best describing the runtime CAN be used.

***Erlang Runtimes:***

| Value | Description |
| --- | --- |
| `beam` | BEAM |
| `jam` | JAM |

***Go Runtimes:***

| Value | Description |
| --- | --- |
| `gc` | Go compiler |
| `gccgo` | GCC Go frontend |

***Java runtimes:***

Java instrumentation should fill in the values by copying from system properties.

- `process.runtime.name` - Fill in the value of `java.runtime.name` as is
- `process.runtime.version` - Fill in the value of `java.runtime.version` as is
- `process.runtime.description` - Fill in the value of `java.vm.vendor`, followed by a space, followed by `java.vm.version`

Examples for some Java runtimes

| Name | `process.runtime.name` | `process.runtime.version` | `process.runtime.description` |
| --- | --- | --- | --- |
| OpenJDK | OpenJDK Runtime Environment | 11.0.8+10 | Oracle Corporation 11.0.8+10 |
| AdoptOpenJDK Eclipse J9 | OpenJDK Runtime Environment | 11.0.8+10 | Eclipse OpenJ9 openj9-0.21.0 |
| AdoptOpenJDK Hotspot | OpenJDK Runtime Environment | 11.0.8+10 | AdoptOpenJDK 11.0.8+10 |
| SapMachine | OpenJDK Runtime Environment | 11.0.8+10-LTS-sapmachine | SAP SE 11.0.8+10-LTS-sapmachine |
| Zulu OpenJDK | OpenJDK Runtime Environment | 11.0.8+10-LTS | Azul Systems, Inc Zulu11.41+23-CA |

***JavaScript runtimes:***

| Value | Description |
| --- | --- |
| `nodejs` | NodeJS |
| `browser` | Web Browser |
| `iojs` | io.js |
| `graalvm` | GraalVM |

When the value is `browser`, `process.runtime.version` SHOULD be set to the User-Agent header.

***.NET Runtimes:***

| Value | Description |
| --- | --- |
| `dotnet-core` | .NET Core, .NET 5+ |
| `dotnet-framework` | .NET Framework |
| `mono` | Mono |

***Python Runtimes:***

| Value | Description |
| --- | --- |
| `cpython` | CPython |
| `graalvm` | GraalVM |
| `ironpython` | IronPython |
| `jython` | Jython |
| `pypy` | PyPy|
| `pythonnet` | PythonNet |

***Ruby Runtimes:***

| Value | Description |
| --- | --- |
| `rubymri` | Ruby MRI |
| `yarv` | YARV |
| `graalvm` | GraalVM |
| `ironruby` | IronRuby |
| `jruby` | JRuby |
| `macruby` | MacRuby |
| `maglev` | MagLev |
| `mruby` | Mruby |
| `rubinius` | Rubinius |
| `rubymotion` | RubyMotion |
