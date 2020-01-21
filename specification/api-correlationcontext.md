# Correlations API

`CorrelationContext` is an abstract data type represented by set of name/value pairs describing user
defined properties. Each name in `CorrelationContext` is associated with exactly one value.
`CorrelationContext` is serialized using the [W3C Correlation Context](https://w3c.github.io/correlation-context/) specification and is
used to annotate telemetry. Those values can be used to add dimension to the metric or
additional context properties to logs and traces.

`CorrelationContext` is a recommended name but languages can have more
language-specific names like `cctx`.

### Conflict Resolution

If a new name/value pair is added and its name conflicts with an existing pair, then the new pair takes precedence. The value
is replaced by the most recent value (regardless of it is locally generated or received from a remote peer). Replacement is limited to a
scope in which the conflict arises. When the scope is closed the original value prior to the conflict is restored. For example,

```
T# - entry names
V# - entry values

Enter Scope 1
   Current Entries E1=V1, E2=V2
    Enter Scope 2
      Add entries E3=V3, E2=V4
      Current Entries E1=V1, E2=V4, E3=V3/M3 <== Value of E2 is replaced by V4.
    Close Scope 2
   Current Entries E1=V1, E2=V2 <== E2 is restored.
Close Scope 1
```

## CorrelationContext

### GetCorrelations

Returns the entries in this `CorrelationContext`. The order of entries is not
significant. Based on the language specification, the returned value can be
either an immutable collection or an immutable iterator to the collection of
entries in this `CorrelationContext`.

### GetCorrelation

To access the value for an entry by a prior event, the Correlations API
provides a function which takes a context and a name as input, and returns a
value. Returns the `Value` associated with the given `Name`, or null
if the given `Name` is not present.

Required parameter:

`Context` the context from which to get the correlation.

`Name` entry name to return the value for.

### SetCorrelation

To record the value for an entry, the Correlations API provides a function which
takes a context, a name, and a value as input. Returns an updated `Context` which
contains the new value.

Required parameter:

`Context` the context to which the value will be set.

`Name` entry name for which to set the value.

`Value` entry value to set.

### RemoveCorrelation

To delete an entry, the Correlations API provides a function which takes a context
and a name as input. Returns an updated `Context` which no longer contains the selected `Name`.

Required parameter:

`Context` the context from which to remove the correlation.

`Name` entry name to remove.

### ClearCorrelations

To avoid sending any entries to an untrusted process, the Correlation API provides
a function to remove all Correlations from a context. Returns an updated `Context`
with no correlations.

Required parameter:

`Context` the context from which to remove all correlations.

### Limits

Combined size of all entries should not exceed 8192 bytes before encoding.
The size restriction applies to the deserialized entries so that the set of decoded
 `CorrelationContext`s is independent of the encoding format.

### CorrelationContext Propagation

`CorrelationContext` may be propagated across process boundaries or across any arbitrary boundaries
(process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various reasons.
For example, one may propagate 'project-id' entry across all micro-services to break down metrics
by 'project-id'.
