# Environment Variables as Context Propagation Carriers

**Status**: [Release Candidate](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Propagator Mechanisms](#propagator-mechanisms)
  * [Key Name Normalization](#key-name-normalization)
  * [Operational Guidance](#operational-guidance)
    + [Environment Variable Immutability](#environment-variable-immutability)
    + [Process Spawning](#process-spawning)
    + [Security](#security)
- [Supplementary Guidelines](#supplementary-guidelines)

<!-- tocstop -->

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

### Key Name Normalization

Language implementations MUST ensure that environment variable `Get`, `Set`,
and `Keys` operations use normalized key names for context propagation. To
normalize a key name, implementations MUST:

- uppercase ASCII letters,
- replace every character that is not an ASCII letter, digit, or underscore
  (`_`) with an underscore (`_`),
- prefix the name with an underscore (`_`) if it would otherwise start with an
  ASCII digit.

A normalized environment variable name is an environment variable name that is
unchanged by applying this normalization. Equivalently, a normalized environment
variable name matches the regular expression `^[A-Z_][A-Z0-9_]*$`.

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
> This normalization is consistent with the environment variable naming rules
> defined in [POSIX.1-2024](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap08.html).

### Operational Guidance

#### Environment Variable Immutability

Once set for a process, environment variables SHOULD be treated as immutable
within that process:

- Applications SHOULD read context-related environment variables during
  initialization.
- Applications SHOULD NOT modify context-related environment variables of the
  environment in which the parent process exists.

#### Process Spawning

When spawning child processes:

- Parent processes SHOULD copy the current environment variables (if
  applicable), modify, and inject context when spawning child processes.
- Child processes SHOULD extract context from environment variables at startup.
- When spawning multiple child processes with different contexts or baggage,
  each child SHOULD receive its own copy of the environment variables with
  appropriate information.
- The onus is on the application owner for receiving the set context from the
  SDK and passing it to its own process spawning mechanism. The language
  implementations MUST NOT handle spawning processes.

#### Security

Environment variables are generally accessible to all code running within a
process and with the correct permissions, can be accessed from other processes.

- Implementations SHOULD NOT store sensitive information in environment
  variables.
- Applications running in multi-tenant environments SHOULD be aware that
  environment variables may be visible to other processes or users with
  appropriate permissions.

## Supplementary Guidelines

> [!IMPORTANT]
> This section is non-normative and provides implementation
> guidance only. It does not add requirements to the specification.

Language implementations of OpenTelemetry have flexibility in how they expose
environment variable context propagation. The existing `TextMapPropagator` can
be used with environment-specific carriers, environment-specific
[`Getter`](api-propagators.md#getter-argument) and
[`Setter`](api-propagators.md#setter-argument) implementations, or carrier types
that implement these operations themselves. Whichever component performs `Get`,
`Set`, or `Keys` for environment variables is responsible for the normalization
behavior described above. Language-specific helper components are only expected
to operate on the carrier shapes supported by that language implementation.
Implementations commonly provide one or more of the following:

- `Getter` - creates an in-memory copy of the current environment variables and
  reads context from that copy.
- `Setter` - writes context to a dictionary/map and provides the dictionary/map
  to the application owner for them to use when spawning processes.
- An environment-specific carrier type - implements environment variable `Get`,
  `Set`, or `Keys` operations directly when the language combines carrier and
  accessor APIs.

Examples:

- [OpenTelemetry .NET implementation][di]
- [OpenTelemetry C++ implementation][ci]
- [OpenTelemetry Go implementation][gi]
- [OpenTelemetry Java implementation][ji]
- [OpenTelemetry Python implementation][pi]
- [OpenTelemetry Swift implementation][si]

[di]: https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry.Api/Context/Propagation/EnvironmentVariableCarrier.cs
[ci]: https://github.com/open-telemetry/opentelemetry-cpp/blob/main/api/include/opentelemetry/context/propagation/environment_carrier.h
[gi]: https://github.com/open-telemetry/opentelemetry-go-contrib/tree/main/propagators/envcar
[ji]: https://github.com/open-telemetry/opentelemetry-java/tree/main/api/incubator/src/main/java/io/opentelemetry/api/incubator/propagation
[pi]: https://github.com/open-telemetry/opentelemetry-python/blob/main/opentelemetry-api/src/opentelemetry/propagators/_envcarrier.py
[si]: https://github.com/open-telemetry/opentelemetry-swift-core/blob/main/Sources/OpenTelemetrySdk/Trace/Propagation/EnvironmentContextPropagator.swift
