# Environment Variables as Context Propagation Carriers

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Overview](#overview)
- [Propagator Mechanisms](#propagator-mechanisms)
  * [Environment Variable Names](#environment-variable-names)
  * [Format Restrictions](#format-restrictions)
    + [Name Restrictions](#name-restrictions)
    + [Value Restrictions](#value-restrictions)
    + [Size Limitations](#size-limitations)
  * [Operational Guidance](#operational-guidance)
    + [Environment Variable Immutability](#environment-variable-immutability)
    + [Process Spawning](#process-spawning)
    + [Security](#security)
    + [Case Sensitivity](#case-sensitivity)

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
Propagators](../context/api-propagators.md) specification.

### Environment Variable Names

It is RECOMMENDED to use the [W3C Trace
Context](https://www.w3.org/TR/trace-context/) and [W3C
Baggage](https://www.w3.org/TR/baggage/) specifications mapped to environment
variable names for consistent context propagation.

When using the W3C Trace Context and Baggage propagators with environment
variables, the following translated standard environment variable names SHOULD
be used:

| Context Information | Environment Variable | W3C Header Equivalent |
|---------------------|----------------------|-----------------------|
| Trace Context       | `TRACEPARENT`        | `traceparent`         |
| Trace State         | `TRACESTATE`         | `tracestate`          |
| Baggage             | `BAGGAGE`            | `baggage`             |

Implementations MAY support additional propagation formats and SHOULD provide
configuration options to override the default environment variable.

### Format Restrictions

#### Name Restrictions

Environment variable names used for context propagation:

- SHOULD use uppercase letters, digits, and underscores for maximum
  cross-platform compatibility
- MUST NOT include characters forbidden in environment variables per
  platform-specific restrictions
- SHOULD follow naming conventions that align with the propagation format
  specification they're implementing (e.g., `TRACEPARENT` for W3C trace context)

#### Value Restrictions

Environment variable values used for context propagation:

- MUST only use characters that are valid in HTTP header fields per [RFC
  9110](https://tools.ietf.org/html/rfc9110)
- MUST follow the format requirements of the specific propagation protocol
  (e.g., W3C Trace Context specification for `TRACEPARENT` values)
- SHOULD NOT contain sensitive information

#### Size Limitations

Implementations SHOULD follow platform-specific environment variable size
limitations:

- Windows: Maximum 32,767 characters for name=value pairs according to
  [Microsoft Documentation](https://docs.microsoft.com/windows/win32/api/winbase/nf-winbase-setenvironmentvariable)
- UNIX: System-dependent limits exist and are typically lower than Windows.

When truncation is required due to size limitations, implementations MUST
truncate whole entries. Truncation SHOULD start at the end of the entry list.
Implementers MUST document how graceful truncation is handled and SHOULD
provide the link to the corresponding specification (e.g., [W3C tracestate
Truncation guidance][w3c-truncation]).

[w3c-truncation]: https://www.w3.org/TR/trace-context/#tracestate-limits

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
- The onus is on the end-user for receiving the set context from the SDK and
  passing it to it's own process spawning mechanism. The SDK SHOULD NOT handle
  spawning processes for the end-user.

#### Security

Environment variables are generally accessible to all code running within a
process and with the correct permissions, can be accessed from other processes.

- Implementations SHOULD NOT store sensitive information in environment
  variables.
- Applications running in multi-tenant environments SHOULD be aware that
  environment variables may be visible to other processes or users with
  appropriate permissions.

#### Case Sensitivity

Environment variable names are case-sensitive on UNIX and case-insensitive on
Windows.

- For maximum compatibility, implementations MUST:
  - Use uppercase names consistently (`TRACEPARENT` not `TraceParent`).
  - Use the canonical case when setting environment variables.

## Supplementary Guidelines

> **IMPORTANT**: This section is non-normative and provides implementation
> guidance only. It does not add requirements to the specification.

Language SDKs have flexibility in how they implement environment variable
context propagation. Two main approaches have been identified as viable.

### Approach 1: Providing a dedicated `EnvironmentContextPropagator`

SDKs can create a dedicated propagator for environment variables. For example,
the [Swift SDK][swift] implements a custom `EnvironmentContextPropagator` that
handles the environment-specific logic internally, in essence decorating the
`TextMapPropagator`.

### Approach 2: Using the carriers directly through `Setters` and `Getters`

SDKs can use the existing `TextMapPropagator` interface directly with
environment-specific carriers. Go and Python SDKs follow this pattern by
providing:

- `EnvironmentGetter` - creates an in-memory copy of the current environment
  variables and reads context from that copy.
- `EnvironmentSetter` - writes context to a dictionary/map and provides the
  dictionary/map to the end-user for them to use when spawning processes.

### Common Behaviors

Both approaches achieve the same outcome while offering different developer
experiences. SDK implementers may choose either approach based on their
language's idioms and ecosystem conventions. The behaviors in both approaches
are the same in that they:

1. **Extract context**: Read from environment variables and delegate to the
   configured `TextMapPropagator` (e.g., W3C, B3) for parsing
2. **Inject context**: Return a dictionary/map of environment variables that
   users can pass to their process spawning libraries

[swift]: https://github.com/open-telemetry/opentelemetry-swift/blob/main/Sources/OpenTelemetrySdk/Trace/Propagation/EnvironmentContextPropagator.swift
