# Environment Variables as Context Propagation Carriers

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Environment Variable Propagator](#environment-variable-propagator)
  * [Standard Environment Variable Names](#standard-environment-variable-names)
  * [Environment Variable Format Restrictions](#environment-variable-format-restrictions)
    + [Key Format Restrictions](#key-format-restrictions)
    + [Value Format Restrictions](#value-format-restrictions)
    + [Size Limitations](#size-limitations)
  * [Implementation Details](#implementation-details)
    + [EnvVarTextMapPropagator](#envvartextmappropagator)
    + [EnvVarGetter](#envvargetter)
      - [Get](#get)
      - [Keys](#keys)
      - [GetAll](#getall)
    + [EnvVarSetter](#envvarsetter)
      - [Set](#set)
  * [Operational Guidance](#operational-guidance)
    + [Environment Variable Immutability](#environment-variable-immutability)
    + [Process Spawning](#process-spawning)
    + [Security Considerations](#security-considerations)
- [Cross-Platform Considerations](#cross-platform-considerations)
  * [Case Sensitivity](#case-sensitivity)
  * [UNIX-Specific Considerations](#unix-specific-considerations)
  * [Windows-Specific Considerations](#windows-specific-considerations)

<!-- tocstop -->

</details>

## Overview

In systems where processes communicate without using network protocols, context
propagation can be achieved using environment variables as carriers. This
specification extends the [API Propagators](../context/api-propagators.md) to
define how the
[TextMapPropagator](../context/api-propagators.md#textmap-propagator) can be
used with environment variables.

Common scenarios where this is useful include:

- ETL pipelines
- Batch processing systems
- CI/CD environments
- Command-line tools

## Environment Variable Propagator

### Standard Environment Variable Names

The OpenTelemetry supported specifications for context propagation SHOULD be
mapped to environment variables. It is RECOMMENDED to use the [W3C Trace Context](https://www.w3.org/TR/trace-context/)
and [W3C Baggage](https://www.w3.org/TR/baggage/) specifications mapped to
environment variables names.

When using the W3C Trace Context and Baggage propagators with environment
variables, the following standard environment variable names MUST be used:

| Context Information | Environment Variable | W3C Header Equivalent |
|---------------------|----------------------|------------------------|
| Trace Context       | `TRACEPARENT`        | `traceparent`          |
| Trace State         | `TRACESTATE`         | `tracestate`           |
| Baggage             | `BAGGAGE`            | `baggage`              |

Implementations MAY support additional propagation formats and SHOULD provide
configuration options to override the default environment variable names to
support legacy systems.

### Environment Variable Format Restrictions

#### Key Format Restrictions

Environment variable names used for context propagation:

- SHOULD use uppercase letters, digits, and underscores for maximum
  cross-platform compatibility
- MUST NOT include characters forbidden in environment variables per
  platform-specific restrictions
- SHOULD follow naming conventions that align with the propagation format
  specification they're implementing (e.g., `TRACEPARENT` for W3C trace context)

#### Value Format Restrictions

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
  [Microsoft Documentation](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setenvironmentvariable)
- UNIX: System-dependent limits exist and are typically lower than Windows.

Implementations SHOULD handle truncation gracefully when size limits are
exceeded.

### Implementation Details

#### EnvVarTextMapPropagator

The `EnvPropagator` implements the `TextMapPropagator` interface to enable
context propagation through environment variables. It uses specialized `EnvGetter` and
`EnvSetter` implementations that work with environment variables.

#### EnvGetter

The `EnvGetter` implements the TextMapPropagator's Getter interface for
environment variables.

##### Get

The `Get` function MUST return the value of the specified environment variable
or return null if the variable doesn't exist.

Required arguments:
- The carrier of propagation fields (typically the environment variable store)
- The key of the field

The `Get` function MUST handle case-sensitivity appropriately across platforms.
On Windows, where environment variables are case-insensitive, the getter SHOULD
perform case-insensitive lookups.

##### Keys

The `Keys` function MUST return the list of all environment variable names in
the carrier.

Required arguments:
- The carrier of the propagation fields (typically the environment variable
  store)

##### GetAll

The `GetAll` function MUST return all values of the given propagation key, if
supported. It SHOULD return them in the same order as they appear in the
carrier. If the key doesn't exist, it SHOULD return an empty collection.

Required arguments:
- The carrier of propagation fields (typically the environment variable store)
- The key of the field

#### EnvSetter

The `EnvSetter` implements the TextMapPropagator's Setter interface for environment variables.

##### Set

The `Set` function MUST set or replace an environment variable with the given value.

Required arguments:
- The carrier of propagation fields (typically the environment variable store)
- The key of the field
- The value to set

The `Set` function SHOULD convert environment variable names to uppercase for consistency across platforms.

### Operational Guidance

#### Environment Variable Immutability

Once set for a process, environment variables SHOULD be treated as immutable within that process:

- Environment variables SHOULD only be modified before spawning child processes
- Applications SHOULD NOT modify context-related environment variables during execution, as this can lead to inconsistent trace contexts
- If modification is required, applications SHOULD create a new environment variables dictionary with the updated values for the child process

#### Process Spawning

When spawning child processes:

- Parent processes SHOULD inject context into environment variables before spawning child processes
- Child processes SHOULD extract context from environment variables at startup
- When spawning multiple child processes with different contexts, each child SHOULD receive its own copy of the environment variables with appropriate context information

#### Security Considerations

Environment variables are generally accessible to all code running within a process:

- Implementations SHOULD NOT store sensitive information in context propagation via environment variables
- Applications running in multi-tenant environments SHOULD be aware that environment variables may be visible to other processes or users with appropriate permissions
- When using environment variables for context propagation, consider the security implications of propagating trace context across trust boundaries

## Cross-Platform Considerations

### Case Sensitivity

- Environment variable names are case-sensitive on UNIX but case-insensitive on Windows
- For maximum compatibility, implementations SHOULD:
  - Use uppercase names consistently (`TRACEPARENT` not `TraceParent`)
  - Handle case-insensitivity correctly when reading environment variables on Windows
  - Always use the canonical case when setting environment variables

### UNIX-Specific Considerations

- UNIX systems generally use uppercase for environment variables by convention
- Environment variables in UNIX are typically inherited by child processes unless explicitly cleared
- The maximum size of environment variables varies by system and should be considered when implementing

### Windows-Specific Considerations

- Windows environment variables are case-insensitive but case-preserving
- Windows has a larger maximum environment variable size limit (32,767 characters)
- Some Windows APIs may have different behavior regarding environment variable inheritance in child processes
