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

Languages are expected to use the single, widely used `Context` implementation
if one exists for them. In the cases where an extremely clear, pre-existing
option is not available, OpenTelemetry should provide its own `Context`
implementation. Depending on the language, its usage may be either explicit
or implicit.

For languages without explicit `Context` usage, this should
be considered to primarily be a SDK API, and thus be used by SDK and
cross-cutting concerns authors, rather than users writing instrumentation.

`Context` is expected to have the following operations, with their
respective language differences:

## Get value

Concerns can access their local state in the current execution state
represented by a `Context`.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
- (Required) The concern identifier.

The API SHOULD return the value in the `Context` for the specified concern
identifier.

## Set value

Concerns can record their local state in the current execution state
represented by a `Context`.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
- (Required) The concern identifier.
- (Required) The value to be set.

The API SHOULD return a new `Context` containing the new value.
The new value will not be present in the old `Context`.

## Remove value

Concerns can clear their local state in a specified `Context`.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
- (Required) The concern identifier.

The API SHOULD return a new `Context` with the value cleared.
The removed value still remains present in the old `Context`.

## Optional Global operations

These operations are optional, and are protected to be specifically
implement automatic scope switching and define higher level APIs.

### Get current Context

The API SHOULD return the `Context` associated with the caller's current execution unit.

### Set current Context

Associates a `Context` with the caller's current execution unit.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
