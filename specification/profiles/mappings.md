# Mappings

**Status**: [Development](../document-status.md), except where otherwise specified

This document defines how to record `Mapping`s and their required attributes.

<!-- toc -->

- [Attributes](#attributes)

<!-- tocstop -->

## Attributes

A message representing a `Mapping` MUST have at least one of the following
attributes:

- `process.executable.build_id.go`
- `process.executable.build_id.gnu`

If possible all the above listed attributes SHOULD be present in a `Mapping`.
