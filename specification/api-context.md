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
    - [Get current context](#get-current-context)
    - [Set current context](#set-current-context)

</details>

Context is a propagation mechanism which carries execution-scoped-values
across API boundaries and between execution units.

Languages are expected to use the single, widely used context implementation
if one exists for them. In the cases where an extremely clear, pre-existing
option is not available, OpenTelemetry should provide its own context
implementation. Depending on the language, its usage may be either explicit
or implicit.

The context mechanism is expected to have the following operations, with their
respective language differences:

#### Create a key

Keys are used to allow concerns to control access to their local state, and they
cannot be guessed by third parties. It is recommended that concerns mediate
data access via an API, rather than provide direct public access to their keys.

The API SHOULD accept the following parameters:

- (Required) The key name.

The API SHOULD return an opaque object representing the newly created key.

#### Get value

Concerns can access their local state out of a specified context.

The API SHOULD accept the following parameters:

- (Required) The context.
- (Required) The key.

The API SHOULD return the value in the context for the specified key.

#### Set value

Concerns can record their local state in a specified context.

The API SHOULD accept the following parameters:

- (Required) The context.
- (Required) The key.
- (Required) The value to be set.

The API SHOULD return a new context containing the new value.
The new value will not be present in the old context.

#### Remove value

Concerns can clear their local state in a specified context.

The API SHOULD accept the following parameters:

- (Required) The context.
- (Required) The key.

The API SHOULD return a new context with the value cleared.
The removed value still remains present in the old context.

### Optional operations

#### Get current context

The API SHOULD return the context associated with program execution.

#### Set current context

Associates a context with program execution.

The API SHOULD accept the following parameters:

- (Required) The context.
