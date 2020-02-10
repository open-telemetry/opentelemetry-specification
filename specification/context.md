# Context

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
- [Get value](#get-value)
- [Set value](#set-value)
- [Remove value](#remove-value)
- [Optional operations](#optional-operations)
    - [Get current Context](#get-current-context)
    - [Set current Context](#set-current-context)

</details>

## Overview

`Context` is a propagation mechanism which carries execution-scoped values
across API boundaries and between logically associated execution units.
Cross-cutting concerns access their data in-process using the same shared
`Context` object.

`Context` MUST be immutable, and its set and remove operations MUST
result in the creation of a new `Context` cointaining the original
values and the specified values updated.

Languages are expected to use the single, widely used `Context` implementation
if one exists for them. In the cases where an extremely clear, pre-existing
option is not available, OpenTelemetry MUST provide its own `Context`
implementation. Depending on the language, its usage may be either explicit
or implicit.

Users writing instrumentation in languages that use `Context` implicitly are
discouraged from using the `Context` API directly. In those cases, users will
manipulate `Context` through the cross-cutting concerns APIs instead.

`Context` is expected to have the following operations, with their
respective language differences:

## Get value

Concerns can access their local state in the current execution state
represented by a `Context`.

The API MUST accept the following parameters:

- The `Context`.
- The concern identifier.

The API MUST return the value in the `Context` for the specified concern
identifier.

## Set value

Concerns can record their local state in the current execution state
represented by a `Context`.

The API MUST accept the following parameters:

- The `Context`.
- The concern identifier.
- The value to be set.

The API MUST return a new `Context` containing the new value.

## Remove value

Concerns can clear their local state in a specified `Context`.

The API MUST accept the following parameters:

- The `Context`.
- The concern identifier.

The API MUST return a new `Context` with the value cleared.

## Optional Global operations

These operations are optional, and SHOULD only be used to
implement automatic scope switching and define higher level APIs
by SDK components and OpenTelemetry instrumentation libraries.

### Get current Context

The API MUST return the `Context` associated with the caller's current execution unit.

### Set current Context

Associates a `Context` with the caller's current execution unit.

The API MUST accept the following parameters:

- The `Context`.

The API SHOULD return a handle that can be used to restore the previous
`Context`.
