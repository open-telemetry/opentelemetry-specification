<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
--->

# Entities SDK

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [ResourceProvider](#resourceprovider)
  * [ResourceProvider Creation](#resourceprovider-creation)
  * [Active Resource.](#active-resource)
  * [Resolve conflicts in Schema URL](#resolve-conflicts-in-schema-url)
  * [Configuration](#configuration)
  * [Shutdown](#shutdown)
  * [ForceFlush](#forceflush)
- [Resource](#resource)
  * [Attach an Entity](#attach-an-entity)

<!-- tocstop -->

## Overview

Users of OpenTelemetry need a way for instrumentation interactions with the
OpenTelemetry API to actually produce telemetry. The OpenTelemetry Entities SDK
(henceforth referred to as the SDK) is an implementation of the OpenTelemetry
API that provides users with this functionally.

All language implementations of OpenTelemetry MUST provide an SDK.

The Entities SDK consists of these main components:

- [ResourceProvider](#resourceprovider)
- [Resource](#resource)

## ResourceProvider

The ResourceProvider MUST provide a way to retrieve the current
[Resource](../resource/sdk.md) for use in there parts of the OpenTelemetry SDK.
This `Resource` MUST include all registered `Entity`s.

### ResourceProvider Creation

The SDK SHOULD allow the creation of multiple independent `ResourceProvider`s.

### Active Resource

This SDK MUST implement the
[Get the active Resource API](api.md#get-the-active-resource).

The SDK MUST provide exactly one `Resource` per `ResourceProvider` via this API.

### Configuration

TBD

### Shutdown

TBD

### ForceFlush

TBD

## Resource

The SDK `Resource` is responsible for managing the current set of associated
`Entity`s on the `Resource.

The SDK MUST track associated `Entity`s on this `Resource`.

### Attach an Entity

The `Resource` MUST implement the [Attach an Entity](api.md#attach-an-entity)
operation.  This operation will try to associate a new `Entity` on the
`Resource`.

If the incoming `Entity`'s `entity_type` property is not found in the current
set of `Entity`s on `Resource`, then the new `Entity` is added to the set.

If the incoming `Entity`'s `entity_type` property matches an existing `Entity`
in the current set AND the `identity` attributes for these `Entity`s are
different, then the SDK MUST ignore the new entity.

If the incoming `Entity`'s `entity_type` property matches an existing `Entity`
in the current set AND the `identity` attributes for these `Entity`s are
the same but the `schema_url` is different, then the SDK MUST ignore the new
entity.

If the incoming `Entity`'s `entity_type` property matches an existing `Entity`
in the current set AND the `identity` attributes for these `Entity`s are
the same AND the `schema_url` is the same, then the SDK MUST add any new
attributes found in the `description` to the existing entity. Any new
 `description` attributes with the same keys as existing `description`
 attributes SHOULD replace previous values.

### Flattened Resource

The SDK MUST return a flattened `Resource` for usage in exporters. This
flattened resource MUST provide the fields expected in the `Resource`
data model:

- `attributes`: The complete set of all attributes
- `schema_url`: The Schema URL that should be recorded for this resource.
  See [resolve conflicts in schema url](#resolve-conflicts-in-schema-url).
- `entity_refs`: References to the `Entity` data model in `Resource`.
  These each include:
  - `type`: The type of the entity.
  - `schema_url`: The Scheam URL that was recorded for this Entity.
  - `id_keys`: The attribute keys for the Entity identity. Values are found
    in the `Resource.attributes` property.
  - `description_keys`: The attribute keys for the Entity description. Values
    are found in the `Resource.attributes` property.

### Resolve conflicts in Schema URL

If all detected entities and initial `Resource` have the same URL, then
this is chosen for the resulting `Resource`.

Otherwise, the Schema URL of the resulting `Resource` SHOULD be empty.
