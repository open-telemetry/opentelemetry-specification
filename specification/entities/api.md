<!--- Hugo front matter used to generate the website version of this page:
linkTitle: API
--->

# Entities API

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [ResourceProvider](#resourceprovider)
  * [ResourceProvider operations](#resourceprovider-operations)
    + [Get the active Resource](#get-the-active-resource)
  * [Resource](#resource)
  * [Attach an Entity](#attach-an-entity)

<!-- tocstop -->

## Overview

The Entities API is provided for instrumentation authors to build
[Entities](./data-model.md#entity-data-model) and report them
against the OpenTelemetry [Resource](../resource/README.md) for all signals.

This detection of the environment and its entities is expected
to happen early / immediately in the lifespan of a system being
observed, however, the Entities are allowed to change over the
lifespan of the Resource.

The Entities API consists of these main components:

- [ResourceProvider](#resourceprovider)
- [Resource](#resource)

## ResourceProvider

`Resource`s can be accessed with a `ResourceProvider`.

Normally, the `ResourceProvider` is expected to be accessed from a central place.
Thus, the API SHOULD provide a way to set/register and access a global default
`ResourceProvider`.

### ResourceProvider operations

The `ResourceProvider` MUST provide the following functions:

* Get the active `Resource`

#### Get the active Resource

This API MUST return the current `Resource` for which Telemetry
is being reported.

### Resource

The `Resource` is responsible for emitting `Entity`s and tracking
the current set of entities attached to the `Resource`.

The `Resource` MUST provide a function to:

- [Attach an Entity](#attach-an-entity)

### Attach an Entity

The effect of calling this API is to attach (or update) an Entity
to the current `Resource`.

The API MUST accept the following parameters:

- `entity_type`: A string that uniquely identifies the type of Entity.
  See [entity data model](./data-model.md#entity-data-model) for details.
- `identity`: Specifies the attributes which identify the entity.
  This API MUST be structured to accept a variable number of
  attributes, but must see at least one attribute.
- `description` (optional): Specifies the attributes which describe the
  entity. This API MUST be structured to accept a variable number
  of attributes, including none.
- `schema_url` (optional): Specifies the Schema URL that should be recorded in
  the emitted telemetry.
