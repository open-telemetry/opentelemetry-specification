# Mappings

**Status**: [Development](../document-status.md), except where otherwise specified

This document defines the required attributes of [`Mapping`](https://github.com/open-telemetry/oteps/blob/main/text/profiles/0239-profiles-data-model.md#message-mapping) messages.

<!-- toc -->

- [Attributes](#attributes)
  * [Algorithm for `process.executable.build_id.profiling`](#algorithm-for-processexecutablebuild_idprofiling)

<!-- tocstop -->

## Attributes

A message representing a `Mapping` MUST have at least one of the following
attributes:

- `process.executable.build_id.gnu`
- `process.executable.build_id.go`
- `process.executable.build_id.profiling`

If possible all the above listed attributes SHOULD be present in a `Mapping`. To promote interoperability, it is RECOMMENDED for `process.executable.build_id.profiling` to be present in every `Mapping`.

### Algorithm for `process.executable.build_id.profiling`

In some environments GNU and/or Go build_id values are stripped or not usable - for example Alpine
Linux which is often used as a base for Docker environments. For that reason and to promote interoperability, a deterministic build_id generation algorithm that hashes the first and last page of a file together with its length is defined as:

```
Input   ← Concat(File[:4096], File[-4096:], BigEndianUInt64(Len(File)))
Digest  ← SHA256(Input)
BuildID ← Digest[:16]
```

where `Input` is the concatenation of the first and last 4096 bytes of the file (may overlap, not padded) and the 8 byte big-endian serialization of the file length. The resulting `BuildID` is the truncation of the hash digest to 16 bytes (128 bits), in hex string form.
