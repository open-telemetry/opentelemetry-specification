# Mappings

**Status**: [Development](../document-status.md), except where otherwise specified

This document defines the required attributes of [`Mapping`](https://github.com/open-telemetry/oteps/blob/main/text/profiles/0239-profiles-data-model.md#message-mapping)s.

<!-- toc -->

- [Attributes](#attributes)

<!-- tocstop -->

## Attributes

A message representing a `Mapping` MUST have at least one of the following
attributes:

- `process.executable.build_id.gnu`
- `process.executable.build_id.go`
- `process.executable.build_id.profiling`

If possible all the above listed attributes SHOULD be present in a `Mapping`.

### Algorithm for `process.executable.build_id.profiling`

In some environments GNU and/or Go build_id values are stripped or not usable - for example Alpine
Linux which is often used as a base for Docker environments. In such cases, profiling generates
build ids using a specified algorithm. The algorithm hashes the first and last page of a file
together with its length:

SHA256(first4k, last4k, fileLen)
