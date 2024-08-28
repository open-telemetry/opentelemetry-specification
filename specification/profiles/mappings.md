# Mappings

**Status**: [Development](../document-status.md), except where otherwise specified

This document defines the required attributes of [`Mapping`](https://github.com/open-telemetry/oteps/blob/main/text/profiles/0239-profiles-data-model.md#message-mapping)s.

<!-- toc -->

- [Attributes](#attributes)

<!-- tocstop -->

## Attributes

A message representing a `Mapping` MUST have at least one of the following
attributes:

- `process.executable.build_id.go`
- `process.executable.build_id.gnu`

If possible all the above listed attributes SHOULD be present in a `Mapping`.
