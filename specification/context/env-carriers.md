# Environment Variables as Context Propagation Carriers

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

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
- [Propagator API](#propagator-api)
  * [Environment Variable Propagator Decorator](#environment-variable-propagator-decorator)
    + [Examples](#examples)
      - [Go](#go)
      - [Python](#python)
      - [Swift](#swift)

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

## Propagator API

### Environment Variable Propagator Decorator

The `EnvVarPropagator` is a [decorator][dec] that wraps a `TextMapPropagator`,
handling the injection and extraction of context and baggage into and from
environment variables.

The `EnvVarPropagator` SHOULD be configurable to match platform-specific
restrictions and handle environment variable naming conventions as described in
the [Environment Variable Names](#environment-variable-names) and [Format
Restrictions](#format-restrictions) sections.

The `EnvVarPropagator` MAY define an `EnvVarCarrier` type that implements the
`TextMap` carrier interface when calling `Inject` and `Extract operations.

#### Examples

##### Go

```go
type TextMapPropagator interface {
    // Includes Inject, Extract, and Fields
    ...
}

type EnvVarPropagator func(TextMapPropagator) TextMapPropagator

func (envp EnvVarPropagator) Inject(ctx context.Context, carrier TextMapCarrier) {
    env := os.Environ()
    // Inject context into environment variable copy
    ...
}

func (envp EnvVarPropagator) Extract(ctx context.Context, carrier TextMapCarrier) context.Context {
    // Extract context from environment variables
    ...
}
...
```

##### Python

```python
class EnvVarPropagator(TextMapPropagator):
    def inject(self, context, carrier):
        env_dict = os.environ.copy()
        # Inject context into environment variables
        ...
    def extract(self, carrier):
        # Extract context from environment variables
        ...
```

##### Swift

```swift
public struct EnvVarPropagator: TextMapPropagator {
    public func inject(...) {
        // Inject context into environment variables
        ...
    }
    public func extract(...) -> SpanContext? {
        // Extract context from environment variables
        ...
    }
}
```

[dec]: https://wikipedia.org/wiki/Decorator_pattern
