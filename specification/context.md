# Context

<details>
<summary>
Table of Contents
</summary>

- [Create a key](#create-a-key)
- [Get value](#get-value)
- [Set value](#set-value)
- [Remove value](#remove-value)
- [Optional operations](#optional-operations)
    - [Get current Context](#get-current-context)
    - [Set current Context](#set-current-context)

</details>

`Context` is a propagation mechanism which carries execution-scoped-values
across API boundaries and between execution units.

Languages are expected to use the single, widely used `Context` implementation
if one exists for them. In the cases where an extremely clear, pre-existing
option is not available, OpenTelemetry should provide its own `Context`
implementation. Depending on the language, its usage may be either explicit
or implicit.

The `Context` mechanism is expected to have the following operations, with their
respective language differences:

#### Create a key

Keys are used to allow concerns to control access to their local state, and they
cannot be guessed by third parties. It is recommended that concerns mediate
data access via an API, rather than provide direct public access to their keys.

The API SHOULD accept the following parameters:

- (Required) The key name.

The API SHOULD return an opaque object representing the newly created key.

#### Get value

Concerns can access their local state out of a specified `Context`.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
- (Required) The key.

The API SHOULD return the value in the `Context` for the specified key.

#### Set value

Concerns can record their local state in a specified `Context`.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
- (Required) The key.
- (Required) The value to be set.

The API SHOULD return a new `Context` containing the new value.
The new value will not be present in the old `Context`.

#### Remove value

Concerns can clear their local state in a specified `Context`.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
- (Required) The key.

The API SHOULD return a new `Context` with the value cleared.
The removed value still remains present in the old `Context`.

### Optional operations

#### Get current Context

The API SHOULD return the `Context` associated with program execution.

#### Set current Context

Associates a `Context` with program execution.

The API SHOULD accept the following parameters:

- (Required) The `Context`.
