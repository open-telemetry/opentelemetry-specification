# Propagators API

<details>
<summary>
Table of Contents
</summary>

- [Binary Format](#binary-format)
  - [ToBytes](#tobytes)
  - [FromBytes](#frombytes)
- [HTTP Text Format](#http-text-format)
  - [Fields](#fields)
  - [Inject](#inject)
  - [Setter](#setter)
    - [Put](#put)
  - [Extract](#extract)
  - [Getter](#getter)
    - [Get](#get)

</details>

Propagators API consists of two main formats:
- `BinaryFormat` is used to serialize and deserialize a value into a binary representation.
- `HTTPTextFormat` is used to inject and extract a value as text into carriers that travel
in-band across process boundaries.

## Binary Format

`BinaryFormat` is a formatter to serialize and deserialize a value into a binary format.

`BinaryFormat` MUST expose the APIs that serializes values into bytes,
and deserializes values from bytes.

### ToBytes

Serializes the given value into the on-the-wire representation.

Required arguments:
- the value to serialize, can be `SpanContext` or `DistributedContext`.

Returns the on-the-wire byte representation of the value.

### FromBytes

Creates a value from the given on-the-wire encoded representation.

If the value could not be parsed, the underlying implementation SHOULD decide to return ether
an empty value, an invalid value, or a valid value.

Required arguments:
- on-the-wire byte representation of the value.

Returns a value deserialized from bytes.

## HTTP Text Format

`HTTPTextFormat` is a formatter that injects and extracts a value as text into carriers that 
travel in-band across process boundaries.

Encoding is expected to conform to the HTTP Header Field semantics. Values are often encoded as
RPC/HTTP request headers.

The carrier of propagated data on both the client (injector) and server (extractor) side is
usually an http request. Propagation is usually implemented via library-specific request
interceptors, where the client-side injects values and the server-side extracts them.

`HTTPTextFormat` MUST expose the APIs that injects values into carriers,
and extracts values from carriers.

### Fields

The propagation fields defined. If your carrier is reused, you should delete the fields here
before calling [inject](#inject).

For example, if the carrier is a single-use or immutable request object, you don't need to
clear fields as they couldn't have been set before. If it is a mutable, retryable object,
successive calls should clear these fields first.

The use cases of this are:
- allow pre-allocation of fields, especially in systems like gRPC Metadata
- allow a single-pass over an iterator

Returns list of fields that will be used by this formatter.

### Inject

Injects the value downstream. For example, as http headers.

Required arguments:
- the value to be injected, can be `SpanContext` or `DistributedContext`.
- the carrier that holds propagation fields. For example, an outgoing message or http request.
- the setter invoked for each propagation key to add or remove.

### Setter

`Setter` allows a `HTTPTextFormat` to set propagated fields into a carrier.

`Setter` MUST be stateless and allowed to be saved as a constant to avoid runtime allocations.

#### Put

Replaces a propagated field with the given value.

Required arguments:
- the carrier holds propagation fields. For example, an outgoing message or http request.
- the key of the field.
- the value of the field.

### Extract

Extracts the value from upstream. For example, as http headers.

If the value could not be parsed, the underlying implementation will decide to return an
object representing either an empty value, an invalid value, or a valid value. Implementation
MUST not return null.

Required arguments:
- the carrier holds propagation fields. For example, an outgoing message or http request.
- the getter invoked for each propagation key to get.

Returns the non-null extracted value.

### Getter

`Getter` allows a `HttpTextFormat` to read propagated fields from a carrier.

`Getter` MUST be stateless and allowed to be saved as a constant to avoid runtime allocations.

#### Get

Returns the first value of the given propagation key or returns null if the key doesn't exist.

Required arguments:
- the carrier of propagation fields, such as an http request.
- the key of the field.

Returns the first value of the given propagation key or returns null if the key doesn't exist.
