# Correlations API

`CorrelationContext` is used to annotate telemetry, adding context and information to metrics, traces, and logs.
It is an abstract data type represented by a set of name/value pairs describing user-
defined properties. Each name in `CorrelationContext` MUST be associated with exactly one value.
`CorrelationContext` MUST be serialized according to the [W3C Correlation Context](https://w3c.github.io/correlation-context/) specification.

## Conflict Resolution

If a new name/value pair is added and its name is the same as an existing name, than the new pair MUST take precedence. The value
is replaced with the added value (regardless if it is locally generated or received from a remote peer). Replacement is limited to a
scope in which the conflict arises. When the scope is closed the original value prior to the conflict is restored. For example,

```
N# - names
V# - values

Enter Scope 1
   Current name/value pairs N1=V1, N2=V2
    Enter Scope 2
      Add name/value pairs N3=V3, N2=V4
      Current name/value pairs N1=V1, N2=V4, N3=V3 <== Value of N2 is replaced by V4.
    Close Scope 2
   Current name/value pairs N1=V1, N2=V2 <== N2 is restored.
Close Scope 1
```

## CorrelationContext

### GetCorrelations

Returns the name/value pairs in this `CorrelationContext`. The order of name/value pairs MUST NOT be
significant. Based on the language specification, the returned value can be
either an immutable collection or an immutable iterator to the collection of
name/value pairs in this `CorrelationContext`.

### GetCorrelation

To access the value for a name/value pair by a prior event, the Correlations API
SHALL provide a function that takes a context and a name as input, and returns a
value. Returns the value associated with the given name, or null
if the given name is not present.

REQUIRED parameters:

`Name` the name to return the value for.

OPTIONAL parameters:

`Context` the context from which to get the correlation.

### SetCorrelation

To record the value for a name/value pair, the Correlations API SHALL provide a function which
takes a context, a name, and a value as input. Returns an updated `Context` which
contains the new value.

REQUIRED parameters:

`Name` the name for which to set the value.

`Value` the value to set.

OPTIONAL parameters:

`Context` the context to which the value will be set.

### RemoveCorrelation

To delete a name/value pair, the Correlations API SHALL provide a function which takes a context
and a name as input. Returns an updated `Context` which no longer contains the selected name.

REQUIRED parameters:

`Name` the name to remove.

OPTIONAL parameters:

`Context` the context from which to remove the correlation.

### ClearCorrelations

To avoid sending any name/value pairs to an untrusted process, the Correlations API SHALL provide
a function to remove all Correlations from a context. Returns an updated `Context`
with no correlations.

OPTIONAL parameters:

`Context` the context from which to remove all correlations.

### Limits

Combined size of all name/value pairs should not exceed 8192 bytes before encoding. After the size is
reached, correlations are dropped. The size restriction applies to the deserialized name/value pairs so
that the set of decoded `CorrelationContext`s is independent of the encoding format.

### CorrelationContext Propagation

`CorrelationContext` MAY be propagated across process boundaries or across any arbitrary boundaries
(process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various reasons.
