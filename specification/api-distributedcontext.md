# DistributedContext API
An `Entry` is used to label anything that is associated
with a specific operation, such as an HTTP request.

`DistributedContext` is an abstract data type that represents collection of entries.
Each key of `DistributedContext` is associated with exactly one value. `DistributedContext` is serializable,
to facilitate propagating it not only inside the process but also across process boundaries.
`DistributedContext` is used to annotate telemetry with the name:value pair `Entry`.
Those values can be used to add dimension to the metric or additional context properties to logs and traces.

`DistributedContext` is a recommended name but languages can have more language-specific names like `dctx`.

# Entry
An `Entry` consists of EntryMetadata, EntryKey, and EntryValue.

## EntryKey

`EntryKey` is the name of the Entry. `EntryKey` along with `EntryValue` can be used to 
aggregate and group stats, annotate traces and logs, etc.

**Restrictions**
- Must contain only printable ASCII (codes between 32 and 126 inclusive)
- Must have length greater than zero and less than 256.
- Must not be empty.

### Create

Creates a new `EntryKey` with the given name in string. This is a static method.

Required parameter:

Name of the `EntryKey`.

### GetName

Returns the name of the `EntryKey`.

## EntryValue

`EntryValue` is a string. It MUST contain only printable ASCII (codes between
32 and 126)

### Create

Creates a new `EntryValue` with the given value in string. This is a static method.

Required parameter:

String value of the `EntryValue`.

### AsString

Returns the string value of the `EntryValue`.

## EntryMetadata

`EntryMetadata` contains properties associated with an `Entry`. For now only the property `EntryTTL`
is defined. In future, additional properties may be added to address specific situations.

The creator of entries determines metadata of an entry it creates.

### Create

Creates a new `EntryMetadata` with the `EntryTTL`. This is a static method.

Required parameter:

`EntryTTL` that represents number of hops an entry can propagate.

### GetEntryTTL

Returns the `EntryTTL`.

### EntryTTL

`EntryTTL` is an integer that represents number of hops an entry can propagate. Anytime a sender serializes an entry,
sends it over the wire and receiver deserializes the entry then the entry is considered to have travelled one hop.
There could be one or more proxy(ies) between sender and receiver. Proxies are treated as transparent
entities and they may not create additional hops. Every propagation implementation should support an option 
`decrementTTL` (default set to true) that allows proxies to set it to false.

**For now, ONLY special values (0 and -1) are supported.**

#### Special Values
- **NO_PROPAGATION (0)**: An `Entry` with `EntryTTL` value of zero is considered to have local scope and
 is used within the process it created.

- **UNLIMITED_PROPAGATION (-1)**: An `Entry` with `EntryTTL` value of -1 can propagate unlimited hops.
 `EntryTTL` value of -1 is typical used to represent a request, processing of which may span multiple entities.

#### Example for EntryTTL > 0
On a server side typically there is no information about the caller besides ip/port,
but in every process there is a notion of "service_name" entry that is added as a "caller" entry before
serialization when a RPC/HTTP call is made. For the "caller" entry, desirable `EntryTTL` value is 1.

Note that `EntryTTL` value of 1 is not supported at this time. The example is listed here simply to
show a possible use case for `EntryTTL` > 0.
 
### Processing at Receiver and Sender
For now, limited processing is required on Sender and Receiver. However, for the sake of
completeness, future processing requirement is also listed here. These requirements are marked with 
"**(future)**".

This processing is done as part of entry propagator.

#### At Receiver
Upon receiving an entry from remote entity an entry extractor

- MUST decrement the value of `EntryTTL` by one if it is greater than zero. **(future)**
- MUST treat the value of `EntryTTL` as -1 if it is not present.
- MUST discard the `Entry` for any other value of `EntryTTL`. **(future)**

#### At Sender
Upon preparing to send an entry to a remote entity an entry injector
- MUST send the entry AND include `EntryTTL` if its value is greater than 0. **(future)**
- MUST send the entry without `EntryTTL` if its value is -1. Absence of `EntryTTL` on the wire is treated as having `EntryTTL` of -1.
  This is to optimize on-the-wire representation of common case.
- MUST not send the entry if the value of `EntryTTL` is 0.

## Entry Conflict Resolution
If a new entry conflicts with an existing entry then the new entry takes precedence. Entire `Entry` along 
with `EntryValue` and `EntryMetadata` is replaced by the most recent entry (regardless of it is locally
generated or received from a remote peer). Replacement is limited to a scope in which the 
conflict arises. When the scope is closed the original value and metadata prior to the conflict is restored.
For example,
```
T# - Entry keys
V# - Entry Values
M# - Entry Metadata

Enter Scope 1
   Current Entries E1=V1/M1, E2=V2/M2
    Enter Scope 2
      Add Entries E3=V3/M3, E2=V4/M4
      Current Entries E1=V1/M1, E2=V4/M4, E3=V3/M3 <== Value/Metadata of E2 is replaced by V4/M4.
    Close Scope 2
   Current Entries E1=V1/M1, E2=V2/M2  <== E2 is restored.
Close Scope 1
``` 

# DistributedContext

## GetEntries

Returns the entries in this `DistributedContext`.
The order of entries is not significant. Based on the language specification,
the returned value can be either an immutable collection or an immutable iterator
to the collection of entries in this `DistributedContext`.

## GetEntryValue

Returns the `EntryValue` associated with the given `EntryKey`, or null if the given `EntryKey`
is not present.

Required parameter:

`EntryKey` entry key to return the value for.

## Limits
Combined size of all entries should not exceed 8192 bytes before encoding.
The size restriction applies to the deserialized entries so that the set of decoded
 `DistributedContext`s is independent of the encoding format.

## DistributedContext Propagation
`DistributedContext` may be propagated across process boundaries or across any arbitrary boundaries
(process, $OTHER_BOUNDARY1, $OTHER_BOUNDARY2, etc) for various reasons.
For example, one may propagate 'project-id' Entry across all micro-services to break down metrics
by 'project-id'. Not all entries in a `DistributedContext` should be propagated and not all entries in a `DistributedContext`
should be accepted from a remote peer. Hence, `DistributedContext` propagator must allow specifying an optional
list of ordered `EntryPropagationFilter`s for receiving entries or for forwarding entries or for both. 
An `EntryPropagationFilter` list for receiving MAY be different than that for forwarding.

If no filter is specified for receiving then all entries are received. 
If no filter is specified for forwarding then all entries are forwarded except those that have `EntryTTL` of 0.

### EntryPropagationFilter
Entry Propagation Filter consists of an action (`EntryPropagationFilterAction`) and a condition 
(`EntryPropagationFilterMatchOperator` and `EntryPropagationFilterMatchString`). An `EntryKey` 
is evaluated against condition of each `EntryPropagationFilter` in order. If the condition is evaluated
to true then action is taken according to `EntryPropagationFilterAction` and filter processing is stopped.
If the condition is evaluated to false then the `EntryKey` is processed against next `EntryPropagationFilter`
in the ordered list. If none of the condition is evaluated to true then the default
action is **Exclude**.

#### EntryPropagationFilterAction
This is an interface. Implementation of this interface takes appropriate action on the `Entry` if the 
condition (`EntryPropagationFitlerMatchOperator` and `EntryPropagationFilterMatchString`) is evaluated to true.
At a minimum, `Exclude` and `Include` actions MUST be implemented.

**Exclude**
If the `EntryPropagationFilterAction` is Exclude then any `Entry` whose `EntryKey` evaluates to true 
with the condition (`EntryPropagationFitlerMatchOperator` and `EntryPropagationFilterMatchString`)
MUST be excluded.

**Include**
If the `EntryPropagationFilterAction` is Include then any `Entry` whose `EntryKey` evaluates to true 
with the condition (`EntryPropagationFitlerMatchOperator  ` and `EntryPropagationFilterMatchString`)
MUST be included. 
  
#### EntryPropagationFilterMatchOperator

| Operator | Description |
|----------|-------------|
| EQUAL | The condition is evaluated to true if `EntryKey` is exactly same as `EntryPropagationFilterMatchString` |
| NOTEQUAL | The condition is evaluated to true if `EntryKey` is NOT exactly same as `EntryPropagationFilterMatchString` |
| HAS_PREFIX | The condition is evaluated to true if `EntryKey` begins with `EntryPropagationFilterMatchString` |

#### EntryPropagationFilterMatchString
It is a string to compare against EntryKey using `EntryPropagationFilterMatchOperator` in order to 
include or exclude an `Entry`.
 
