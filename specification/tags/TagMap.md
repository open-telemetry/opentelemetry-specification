# Summary
A `Tag` is used to label anything that is associated
with a specific operation, such as an HTTP request. These `Tag`s are used to
aggregate measurements in a [`View`](https://github.com/census-instrumentation/opencensus-specs/blob/master/stats/DataAggregation.md#view) 
according to unique value of the `Tag`s. The `Tag`s can also be used to filter (include/exclude)
measurements in a `View`. `Tag`s can further be used for logging and tracing.

# Tag
A `Tag` consists of TagMetadata, TagKey, and TagValue.

## TagKey

`TagKey` is the name of the Tag. TagKey along with `TagValue` is used to aggregate
and group stats, annotate traces and logs.

**Restrictions**
- Must contain only printable ASCII (codes between 32 and 126 inclusive)
- Must have length greater than zero and less than 256.
- Must not be empty.

## TagValue

`TagValue` is a string. It MUST contain only printable ASCII (codes between
32 and 126)

## TagMetadata

`TagMetadata` contains properties associated with a `Tag`. For now only the property `TagTTL`
is defined. In future, additional properties may be added to address specific situations.

A tag creator determines metadata of a tag it creates.

### TagTTL

`TagTTL` is an integer that represents number of hops a tag can propagate. Anytime a sender serializes a tag,
sends it over the wire and receiver unserializes the tag then the tag is considered to have travelled one hop. 
There could be one or more proxy(ies) between sender and receiver. Proxies are treated as transparent
entities and they may not create additional hops. Every propagation implementation should support an option 
`decrementTTL` (default set to true) that allows proxies to set it to false.

**For now, ONLY special values (0 and -1) are supported.**

#### Special Values
- **NO_PROPAGATION (0)**: Tag with `TagTTL` value of zero is considered to have local scope and
 is used within the process it created.
 
- **UNLIMITED_PROPAGATION (-1)**: A Tag with `TagTTL` value of -1 can propagate unlimited hops.
 However, it is still subject to outgoing and incoming (on remote side) filter criteria. 
 See `TagPropagationFilter` in [Tag Propagation](#Tag Propagation). `TagTTL` value of -1
 is typical used to represent a request, processing of which may span multiple entities.

#### Example for TagTTL > 0
On a server side typically there is no information about the caller besides ip/port,
but in every process there is a notion of "service_name" tag that is added as a "caller" tag before
serialization when a RPC/HTTP call is made. For the "caller" tag, desirable `TagTTL` value is 1.

Note that TagTTL value of 1 is not supported at this time. The example is listed here simply to
show a possible use case for TagTTL > 0.
 
### Processing at Receiver and Sender
For now, limited processing is required on Sender and Receiver. However, for the sake of
completeness, future processing requirement is also listed here. These requirements are marked with 
"**(future)**".

This processing is done as part of tag propagator.

#### At Receiver
Upon receiving a tag from remote entity a tag extractor

- MUST decrement the value of `TagTTL` by one if it is greater than zero. **(future)**
- MUST treat the value of `TagTTL` as -1 if it is not present.
- MUST discard the `Tag` for any other value of `TagTTL`. **(future)**

#### At Sender
Upon preparing to send a tag to a remote entity a tag injector
- MUST send the tag AND include `TagTTL` if its value is greater than 0. **(future)**
- MUST send the tag without 'TagTTL' if its value is -1. Absence of TagTTL on the wire is treated as having TagTTL of -1.
  This is to optimize on-the-wire representation of common case.
- MUST not send the tag if the value of `TagTTL` is 0.

A tag accepted for sending/receiving based on `TagTTL` value could still be excluded from sending/receiving based on
`TagPropagationFilter`.

## Tag Conflict Resolution
If a new tag conflicts with an existing tag then the new tag takes precedence. Entire `Tag` along 
with `TagValue` and `TagMetadata` is replaced by the most recent tag (regardless of it is locally
generated or received from a remote peer). Replacement is limited to a scope in which the 
conflict arises. When the scope is closed the orignal value and metadata prior to the conflict is restored.
For example,
```
T# - Tag keys
V# - Tag Values
M# - Tag Metadata

Enter Scope 1
   Current Tags T1=V1/M1, T2=V2/M2
    Enter Scope 2
      Add Tags T3=V3/M3, T2=v4/M4
      Current Tags T1=V1/M1, T2=V4/M4, T3=V3/M3 <== Value/Metadata of T2 is replaced by V4/M4.
    Close Scope 2
   Current Tags T1=V1/M1, T2=V2/M2  <== T2 is restored.
Close Scope 1
``` 


# TagMap 
`TagMap` is an abstract data type that represents collection of tags. 
i.e., each key is associated with exactly one value.  `TagMap` is serializable, and it represents
all of the information that could be propagated inside the process and across process boundaries.  
`TagMap` is a recommended name but languages can have more language specific name.

## Limits
Combined size of all `Tag`s should not exceed 8192 bytes before encoding.
The size restriction applies to the deserialized tags so that the set of decoded
 `TagMap`s is independent of the encoding format.

## TagMap Propagation
`TagMap` may be propagated across process boundaries or across any arbitrary boundaries for various 
reasons. For example, one may propagate 'project-id' Tag across all micro-services to break down metrics
by 'project-id'. Not all `Tag`s in a `TagMap` should be propagated and not all `Tag`s in a `TagMap`
should be accepted from a remote peer. Hence, `TagMap` propagator must allow specifying an optional
list of ordered `TagPropagationFilter`s for receiving `Tag`s or for forwarding `Tag`s or for both. 
A `TagPropagationFilter` list for receiving MAY be different then that for forwarding.

If no filter is specified for receiving then all `Tag`s are received. 
If no filter is specified for forwarding then all `Tag`s are forwarded except those that have `TagTTL` of 0.

### TagPropagationFilter
Tag Propagation Filter consists of action (`TagPropagationFilterAction`) and condition 
(`TagPropagationFilterMatchOperator` and `TagPropagationFilterMatchString`). A `TagKey` 
is evaluated against condition of each `TagPropagationFilter` in order. If the condition is evaluated
to true then action is taken according to `TagPropagationFilterAction` and filter processing is stopped.
If the condition is evaluated to false then the `TagKey` is processed against next `TagPropagationFilter`
in the ordered list. If none of the condition is evaluated to true then the default
action is **Exclude**.

#### TagPropagationFilterAction
This is an interface. Implementation of this interface takes appropriate action on the `Tag` if the 
condition (`TagPropagationFitlerMatchOperator` and `TagPropagationFilterMatchString`) is evaluated to true.
At a minimum, `Exclude` and `Include` actions MUST be implemented.

**Exclude**
If the `TagPropagationFilterAction` is Exclude then any `Tag` whose `TagKey` evaluates to true 
with the condition (`TagPropagationFitlerMatchOperator` and `TagPropagationFilterMatchString`)
MUST be excluded.

**Include**
If the `TagPropagationFilterAction` is Include then any `Tag` whose `TagKey` evaluates to true 
with the condition (`TagPropagationFitlerMatchOperator  ` and `TagPropagationFilterMatchString`)
MUST be included. 
  
#### TagPropagationFilterMatchOperator

| Operator | Description |
|----------|-------------|
| EQUAL | The condition is evaluated to true if `TagKey` is exactly same as `TagPropagationFilterMatchString` |
| NOTEQUAL | The condition is evaluated to true if `TagKey` is NOT exactly same as `TagPropagationFilterMatchString` |
| HAS_PREFIX | The condition is evaluated to true if `TagKey` begins with `TagPropagationFilterMatchString` |

#### TagPropagationFilterMatchString
It is a string to compare against TagKey using `TagPropagationFilterMatchOperator` in order to 
include or exclude a `Tag`.

## Encoding

### Wire Format
TBD:

#### Over gRPC
TagMap should be encoded using [BinaryEncoding](https://github.com/census-instrumentation/opencensus-specs/tree/master/encodings)
and propagated using gRPC metadata `grpc-tags-bin`. The propagation MUST inject a TagMap and MUST extract a TagMap from the gRPC metadata.

#### Over HTTP

TBD: W3C [correlation context](https://github.com/w3c/correlation-context/blob/master/correlation_context/HTTP_HEADER_FORMAT.md)
may be an appropriate choice.

                                                
### Error handling
- Call should continue irrespective of any error related to encoding/decoding.
- There are no partial failures for encoding or decoding. The result of encoding or decoding
  should always be a complete `TagMap` or an error.  The type of error
  reporting depends on the language.
- Serialization should result in an error if the `TagMap` does not meet the
  size restriction above.
- Deserialization should result in an error if the serialized `TagMap`
  - cannot be parsed.
  - contains a `TagKey` or `TagValue` that does not meet the restrictions above.
  - does not meet the size restriction above.
