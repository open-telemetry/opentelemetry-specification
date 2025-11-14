<!--- Hugo front matter used to generate the website version of this page:
title: Common Configuration Specification
linkTitle: Env var
aliases:
  - /docs/reference/specification/common
  - /docs/specs/otel/common-configuration
--->

# OpenTelemetry Common Configuration Specification

**Status**: [Stable](../document-status.md) except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Type-specific guidance](#type-specific-guidance)
  * [Numeric](#numeric)
    + [Integer](#integer)
    + [Duration](#duration)
    + [Timeout](#timeout)
  * [String](#string)
    + [Enum](#enum)

<!-- tocstop -->

</details>

The goal of this specification is to describe common guidance that is applicable
to all OpenTelemetry SDK configuration sources.

Implementations MAY choose to allow configuration via any source in this specification, but are not required to.
If they do, they SHOULD follow the guidance listed in this document.

## Type-specific guidance

### Numeric

Configuration sources accepting numeric values are sub-classified into:

* [Integer](#integer)
* [Duration](#duration)
* [Timeout](#timeout)

The following guidance applies to all numeric types.

> The following paragraph was added after stabilization and the requirements are
> thus qualified as "SHOULD" to allow implementations to avoid breaking changes.
> For new
> implementations, these should be treated as MUST requirements.

For sources accepting a numeric value, if the user provides a value the
implementation cannot parse, or which is outside the valid range for the
configuration item, the implementation SHOULD generate a warning and gracefully
ignore the setting, i.e., treat them as not set. In particular, implementations
SHOULD NOT assign a custom interpretation e.g. to negative values if a negative
value does not naturally apply to a configuration and does not have an
explicitly specified meaning, but treat it like any other invalid value.

For example, a value specifying a buffer size must naturally be non-negative.
Treating a negative value as "buffer everything" would be an example of such a
discouraged custom interpretation. Instead the default buffer size should be
used.

Note that this could make a difference even if the custom interpretation is
identical with the default value, because it might reset a value set from other
configuration sources with the default.

#### Integer

If an implementation chooses to support an integer-valued configuratin source,
it SHOULD support non-negative values between 0 and 2³¹ − 1 (inclusive).
Individual SDKs MAY choose to support a larger range of values.

#### Duration

Any value that represents a duration MUST be an integer representing a number of
milliseconds. The value is non-negative - if a negative value is provided, the
implementation MUST generate a warning, gracefully ignore the setting and use
the default value if it is defined.

For example, the value `12000` indicates 12000 milliseconds, i.e., 12 seconds.

#### Timeout

Timeout values are similar to [duration](#duration) values, but are treated as a
separate type because of differences in how they interpret timeout zero values (
see below).

Any value that represents a timeout MUST be an integer representing a number of
milliseconds. The value is non-negative - if a negative value is provided, the
implementation MUST generate a warning, gracefully ignore the setting and use
the default value if it is defined.

For example, the value `12000` indicates 12000 milliseconds, i.e., 12 seconds.

Implementations SHOULD interpret timeout zero values (i.e. `0` indicating 0
milliseconds) as no limit (i.e. infinite). In practice, implementations MAY
treat no limit as "a very long time" and substitute a very large duration (
e.g. the maximum milliseconds representable by a 32-bit integer).

### String

String values are sub-classified into:

* [Enum][].

Normally, string values include notes describing how they are interpreted by
implementations.

#### Enum

Enum values SHOULD be interpreted in a case-insensitive manner.

For configuration sources which accept a known value out of a set, i.e., an enum
value, implementations MAY support additional values not listed here.

For sources accepting an enum value, if the user provides a value
the implementation does not recognize, the implementation MUST generate
a warning and gracefully ignore the setting.
When reporting configuration errors, implementations SHOULD display the original
user-provided value to aid debugging.

If a null object (empty, no-op) value is acceptable, then the enum value
representing it MUST be `"none"`.
