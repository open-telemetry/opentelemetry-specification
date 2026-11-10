# Environment Variables as Context Propagation Carriers

**Status**: [Stable](../document-status.md) except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- START doctoc -->

- [Overview](#overview)
- [Propagator Mechanisms](#propagator-mechanisms)
  * [Key Name Normalization](#key-name-normalization)
  * [Operational Guidance](#operational-guidance)
    + [Environment Variable Immutability](#environment-variable-immutability)
    + [Process Spawning](#process-spawning)
    + [Security](#security)
- [Implementation Guidelines](#implementation-guidelines)
- [Instrumentation Guidelines](#instrumentation-guidelines)
  * [Configuration and Defaults](#configuration-and-defaults)
  * [Incoming Context](#incoming-context)
  * [Child Process Injection](#child-process-injection)
  * [Manual Propagation](#manual-propagation)

<!-- END doctoc -->

</details>

## Overview

Environment variables provide a mechanism to propagate context and baggage
information across process boundaries when network protocols are not
applicable. This specification extends the [API Propagators](../context/api-propagators.md)
to define how the
[TextMapPropagator](../context/api-propagators.md#textmap-propagator) can be
used with environment variables.

Common systems where context propagation via environment variables is useful
include:

- Batch processing systems
- CI/CD environments
- Command-line tools

## Propagator Mechanisms

Propagating context via environment variables involves reading and writing to
environment variables. A `TextMapPropagator` SHOULD be used alongside its
normal `Get`, `Set`, `Extract`, and `Inject` functionality as described in the [API
Propagators](api-propagators.md) specification.

When using environment variables as carriers:

- The **environment variable carrier** MUST be format-agnostic and MUST treat
  values as opaque strings and MUST NOT apply propagation-format-specific logic
  such as validating, parsing values, or enforcing other format-specific
  constraints.
- The **propagators** that implement specific propagation formats (for example,
  W3C Trace Context or W3C Baggage) remain solely responsible for:
  - choosing the key names they use with the carrier
  - enforcing naming conventions defined by those propagation formats
  - validating and parsing values
  - applying any truncation or other format-specific behaviors

Language implementations SHOULD document
[operational guidance](#operational-guidance), including initialization-time
extraction, child process environment handling, and security considerations.

Language implementations MUST NOT spawn child processes as part of environment
variable context propagation.

### Key Name Normalization

Language implementations MUST ensure that environment variable `Get`, `Set`,
and `Keys` operations use normalized key names for context propagation. To
normalize a key name, implementations MUST:

- replace an empty key name with a single underscore (`_`),
- uppercase ASCII letters,
- replace every character that is not an ASCII letter, digit, or underscore
  (`_`) with an underscore (`_`),
- prefix the name with an underscore (`_`) if it would otherwise start with an
  ASCII digit.

A normalized environment variable name is a non-empty environment variable name
that is unchanged by applying this normalization. Equivalently, a normalized
environment variable name matches the regular expression `^[A-Z_][A-Z0-9_]*$`.
An empty environment variable name is non-normalized and normalizes to `_`.

Environment variable names that do not match this pattern are non-normalized.

These requirements apply to whichever component implements the operation in a
language, such as a carrier, `Getter`, `Setter`, or other language-specific API:

- `Set` MUST write values using the normalized form of the key provided by the
  propagator.
- `Get` MUST normalize the key requested by the propagator and MUST use the
  normalized key name to read from the carrier.
- `Keys` MUST return only key names that are already normalized.

For example, if a propagator requests the key `x-b3-traceid`, the
environment-specific `Get` operation MUST normalize the requested key to
`X_B3_TRACEID` and read the `X_B3_TRACEID` environment variable. It MUST NOT
read a non-normalized environment variable named `x-b3-traceid`, even though
that name normalizes to `X_B3_TRACEID`.

> [!NOTE]
> On platforms with case-insensitive environment variable lookup, such as
> Windows, the platform lookup performed by `Get` may match an environment
> variable whose name differs from the normalized key only by case. For example,
> if a Windows process environment contains `traceparent`, reading the
> normalized key `TRACEPARENT` may return the value of `traceparent`.

> [!NOTE]
> This normalization is consistent with the environment variable naming rules
> defined in [POSIX.1-2024](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap08.html).

### Operational Guidance

> [!IMPORTANT]
> This section is non-normative and provides usage guidance only. It does not
> add requirements to the specification.

#### Environment Variable Immutability

Context-related environment variables are best treated as process-startup input:

- Applications typically read context-related environment variables during
  initialization.
- Applications avoid modifying context-related environment variables in the
  environment in which the parent process exists.

#### Process Spawning

When spawning child processes:

- A typical parent process flow copies the current environment variables (if
  applicable), modifies that copy, and injects context into the copy when
  spawning child processes.
- Child-process startup is the point where context is extracted from
  environment variables.
- For multiple child processes with different contexts or baggage, separate
  environment variable copies keep the appropriate information isolated per
  child process.
- Application code or instrumentation remains responsible for receiving context
  from the SDK and passing it to the application's process spawning mechanism.

#### Security

Environment variables are generally accessible to all code running within a
process. On many systems, they can also be accessed by other processes or users
with appropriate permissions.

- Context propagation via environment variables is not appropriate for sensitive
  information.
- Multi-tenant environments have extra exposure risk when environment variables
  are visible to other processes or users with appropriate permissions.

## Implementation Guidelines

> [!IMPORTANT]
> This section is non-normative and provides implementation guidance only. It
> does not add requirements to the specification.

Language implementations of OpenTelemetry have flexibility in how they expose
environment variable context propagation. The existing `TextMapPropagator` can
be used with environment-specific carriers, environment-specific
[`Getter`](api-propagators.md#getter-argument) and
[`Setter`](api-propagators.md#setter-argument) implementations, or carrier types
that implement these operations themselves. Whichever component performs `Get`,
`Set`, or `Keys` for environment variables is responsible for the normalization
behavior described above. Language-specific helper components are only expected
to operate on the carrier shapes supported by that language implementation.

Example implementations:

- [OpenTelemetry .NET implementation][di]
- [OpenTelemetry C++ implementation][ci]
- [OpenTelemetry Go implementation][gi]
- [OpenTelemetry Java implementation][ji]
- [OpenTelemetry JavaScript implementation][jsi]
- [OpenTelemetry Python implementation][pi]
- [OpenTelemetry Swift implementation][si]

## Instrumentation Guidelines

**Status**: [Alpha](../document-status.md)

> [!IMPORTANT]
> This section is non-normative and adds no specification requirements.

Agents, framework integrations, test runners, and wrappers can automate context
propagation through environment variables. Instrumentation identifies the
command, job, or test invocation that receives context and intercepts supported
child process launches. SDK initialization alone does not define these
boundaries.

Extraction and injection use the
[configured propagators](api-propagators.md#global-propagators) and
[key name normalization](#key-name-normalization).

### Configuration and Defaults

Recommended defaults for enabled process instrumentation are incoming context
in `parent` mode and child-process injection enabled, with separate controls
to disable either direction.

Settings belong to the instrumentation and can be technology-specific.
This guidance defines no new SDK properties or portable option names.
Instrumentation documentation describes its supported modes and controls,
invocation boundaries, precedence for application-provided context and
explicitly supplied child fields, unsupported launch mechanisms, and behavior
without a valid current span.

### Incoming Context

Treat the environment as [startup input](#environment-variable-immutability)
and retain extracted context for the invocation it describes.

Incoming context can be handled in three modes:

- **`parent` (default):** Use the extracted context as the invocation span's
  remote parent, continuing the incoming trace. An explicit application
  parent/root choice or an existing current span takes precedence.
- **`link`:** Add the extracted span context as a link to the invocation span,
  preserving the selected parent or root. This records the relationship without
  requiring the invocation to join the incoming trace.
- **`none`:** Do not automatically extract context or baggage from the
  environment. Child-process injection is controlled separately.

Supply the parent or link at
[span creation](../trace/api.md#span-creation), before sampling, preserving the
extracted span context's remote status, trace flags, and trace state.

When instrumentation creates an invocation span, scope its active context to
the operation's full lifetime, including asynchronous work, and restore the
previous context afterward.
Avoid applying startup context to unrelated future requests in long-running
processes. Baggage follows normal context inheritance and application updates;
reapplying startup baggage can overwrite later changes.

### Child Process Injection

At each supported application-initiated launch, copy the environment the
application would pass to the child. Inject current context and baggage into
that copy, preserving the parent environment and caller-owned launch settings.

Before injecting, remove inherited fields identified by the configured
propagators' [Fields](api-propagators.md#fields), using normalized names.
This also prevents stale values when injection omits fields.
Apply the documented precedence when clearing or replacing explicitly
supplied child fields.

### Manual Propagation

Application code can use the same invocation and child-environment guidance for
manual propagation, as shown in the
[Go examples](https://pkg.go.dev/go.opentelemetry.io/contrib/propagators/envcar).

[di]: https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry.Api/Context/Propagation/EnvironmentVariableCarrier.cs
[ci]: https://github.com/open-telemetry/opentelemetry-cpp/blob/main/api/include/opentelemetry/context/propagation/environment_carrier.h
[gi]: https://github.com/open-telemetry/opentelemetry-go-contrib/tree/main/propagators/envcar
[ji]: https://github.com/open-telemetry/opentelemetry-java/tree/main/api/incubator/src/main/java/io/opentelemetry/api/incubator/propagation
[jsi]: https://github.com/open-telemetry/opentelemetry-js/tree/main/experimental/packages/opentelemetry-propagator-env-carrier
[pi]: https://github.com/open-telemetry/opentelemetry-python/blob/main/opentelemetry-api/src/opentelemetry/propagators/_envcarrier.py
[si]: https://github.com/open-telemetry/opentelemetry-swift-core/blob/main/Sources/OpenTelemetrySdk/Trace/Propagation/EnvironmentContextPropagator.swift
