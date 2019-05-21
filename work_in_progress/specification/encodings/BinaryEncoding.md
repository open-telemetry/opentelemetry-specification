# BINARY FORMAT

The binary format can be used to encode different data types, each with different fields. This
document first describes the general format and then applies it to specific data types,
including Trace Context and Tag Context.

## General Format
Each encoding will have a 1 byte version followed by the version format encoding:

`<version><version_format>`

This will allow us to, in 1 deprecation cycle to completely switch to a new format if needed.

## Version Format (version_id = 0)
The version format for the version_id = 0 is based on ideas from proto encoding. The main 
requirements are to allow adding and removing fields in less than 1 deprecation cycle. It
contains a list of fields:

`<field><field>...`

### Field
Each field is a 1-byte field ID paired with a field value, where the format of the field value is
determined by both the field ID and the data type. For example, field 0 in `Trace Context` may
have a completely different format than field 0 in `Tag Context` or field 1 in `Trace Context`.

Each field that we send on the wire will have the following format:

`<field_id><field_format>`

* `field_id` is a single byte.

* `field_format` must be defined for each field separately.

The specification for a data type's format must also specify whether each field is optional or
repeated. For example, `Trace-id` in `Trace Context` is optional, and `Tag` in `Tag Context`
is repeated. The specification for a data type's format MAY define a default value for any
optional field, which must be used when the field is missing.

The specification for a data type can define versions within a version of the format, called data
type version, where each data type version adds new fields. The data type version can be useful
for describing what fields an implementation supports, but it is not included in the
serialized data.

### Serialization Rules
Fields MUST be serialized in data type version order (i.e. all fields from version (i) of a data
type must precede all fields from version (i+1)). That is because each field has its own format,
and old implementations may not be able to determine where newer field values end. This ordering
allows old decoders to ignore any new fields when they do not know the format for those fields.
Fields within a data type version can be serialized in any order, and fields with the same field
ID do not need to be serialized consecutively.

### Deserialization Rules
Because all the fields will be decoded in data type version order, the deserialization will
simply read the encoded input until the end of the input or until the first unknown field_id. An
unknown field id should not be considered a parse error. Implementations MAY pass on any fields
that they cannot decode, when possible (by passing-through the whole opaque tail of bytes
starting with the first field id that the current binary does not understand).

### How can we add new fields?
If we follow the rules that we always append the new ids at the end of the buffer we can add up 
to 127.

TODO(bdrutu): Decide what to do after 127: a) use varint encoding or b) just reserve 255 as a 
continuation byte.

### How can we remove a field?
We can stop sending any field at any moment and the decoders will be able to skip the missing ids
and use the default values.

### Trace Context

#### Fields added in Trace Context version 0

##### Trace-id

* optional
* `field_id` = 0
* `len` = 16

Is the ID of the whole trace forest. It is represented as an opaque 16-bytes array,
e.g. (in hex), `4bf92f3577b34da6a3ce929d000e4736`. All bytes 0 is considered invalid.

##### Span-id

* optional
* `field_id` = 1
* `len` = 8

Is the ID of the caller span (parent). It is represented as an opaque 8-bytes array,
e.g. (in hex), `34f067aa0ba902b7`. All bytes 0 is considered invalid.

##### Trace-options

* optional
* `field_id` = 2
* `len` = 1

Controls tracing options such as sampling, trace level etc. It is a 1-byte
representing a 8-bit unsigned integer. The least significant bit provides
recommendation whether the request should be traced or not (1 recommends the
request should be traced, 0 means the caller does not make a decision to trace
and the decision might be deferred). The flags are recommendations given by the
caller rather than strict rules to follow for 3 reasons:

1.  Trust and abuse.
2.  Bug in caller
3.  Different load between caller service and callee service might force callee to down sample.

The behavior of other bits is currently undefined.

#### Valid example
{0,
0, 75, 249, 47, 53, 119, 179, 77, 166, 163, 206, 146, 157, 0, 14, 71, 54,
1, 52, 240, 103, 170, 11, 169, 2, 183,
2, 1}

This corresponds to:
* `traceId` = {75, 249, 47, 53, 119, 179, 77, 166, 163, 206, 146, 157, 0, 14, 71, 54}
* `spanId` = {52, 240, 103, 170, 11, 169, 2, 183}
* `traceOptions` = 1

### Tag Context
The Tag Context format uses Varint encoding, which is described in
https://developers.google.com/protocol-buffers/docs/encoding#varints.

#### Fields added in Tag Context version 0

##### Tag

* repeated
* `field_id` = 0
* `field_format` = `<tag_key_len><tag_key><tag_val_len><tag_val>` where

  * `tag_key_len` is a varint encoded integer.
  * `tag_key` is `tag_key_len` bytes comprising the tag key name.
  * `tag_val_len` is a varint encoded integer.
  * `tag_val` is `tag_val_len` bytes comprising the tag value.
* Tags can be serialized in any order.
* Multiple tag fields can contain the same tag key. All but the last value for
  that key should be ignored.
* The
  [size limit for serialized Tag Contexts](https://github.com/census-instrumentation/opencensus-specs/blob/master/tags/TagMap.md#limits)
  should apply to all tag fields, even if some of them have duplicate keys. For
  example, a serialized tag context with 10,000 small tags that all have the
  same key should be considered too large.

