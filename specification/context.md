# Context

<details>
<summary>
Table of Contents
</summary>

- [Overview](#overview)
- [Create a key](#create-a-key)
- [Get value](#get-value)
- [Set value](#set-value)
- [Optional operations](#optional-operations)
    - [Get current Context](#get-current-context)
    - [Attach Context](#attach-context)
    - [Detach Context](#detach-context)

</details>

## Overview

A `Context` is a propagation mechanism which carries execution-scoped values
across API boundaries and between logically associated execution units.
Cross-cutting concerns access their data in-process using the same shared
`Context` object.

A `Context` MUST be immutable, and its write operations MUST
result in the creation of a new `Context` containing the original
values and the specified values updated.

Languages are expected to use the single, widely used `Context` implementation
if one exists for them. In the cases where an extremely clear, pre-existing
option is not available, OpenTelemetry MUST provide its own `Context`
implementation. Depending on the language, its usage may be either explicit
or implicit.

Users writing instrumentation in languages that use `Context` implicitly are
discouraged from using the `Context` API directly. In those cases, users will
manipulate `Context` through cross-cutting concerns APIs instead, in order to
perform operations such as setting trace or correlation context values for
a specified `Context`.

A `Context` is expected to have the following operations, with their
respective language differences:

## Create a key

Keys are used to allow cross-cutting concerns to control access to their local state.
They are unique such that other libraries which may use the same context
cannot accidentally use the same key. It is recommended that concerns mediate
data access via an API, rather than provide direct public access to their keys.

The API MUST accept the following parameter:

- The key name. The key name exists for debugging purposes and does not uniquely identify the key. Multiple calls to `CreateKey` with the same name SHOULD NOT return the same value unless language constraints dictate otherwise. Different languages may impose different restrictions on the expected types, so this parameter remains an implementation detail.

The API MUST return an opaque object representing the newly created key.

## Get value

Concerns can access their local state in the current execution state
represented by a `Context`.

The API MUST accept the following parameters:

- The `Context`.
- The key.

The API MUST return the value in the `Context` for the specified key.

## Set value

Concerns can record their local state in the current execution state
represented by a `Context`.

The API MUST accept the following parameters:

- The `Context`.
- The key.
- The value to be set.

The API MUST return a new `Context` containing the new value.

## Optional Global operations

These operations are expected to only be implemented by languages
using `Context` implicitly, and thus are optional. These operations
SHOULD only be used to implement automatic scope switching and define
higher level APIs by SDK components and OpenTelemetry instrumentation libraries.

### Get current Context

The API MUST return the `Context` associated with the caller's current execution unit.

### Attach Context

Associates a `Context` with the caller's current execution unit.

The API MUST accept the following parameters:

- The `Context`.

The API MUST return a value that can be used as a `Token` to restore the previous
`Context`.

### Detach Context

Resets the `Context` associated with the caller's current execution unit
to the value it had before attaching a specified `Context`.

The API MUST accept the following parameters:

- A `Token` that was returned by a previous call to attach a `Context`.
