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

At least one of `process.executable.name`, `process.executable.path`, `process.command`, or `process.command_line` is required.
