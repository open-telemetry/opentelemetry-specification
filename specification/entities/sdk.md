<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
--->

# Entities SDK

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [Entity](#entity)
  * [Entity Creation](#entity-creation)
  * [Entity properties](#entity-properties)
- [EntityDetector](#entitydetector)
  * [EntityDetector operations](#entitydetector-operations)
    + [Detect a set of `Entity`](#detect-a-set-of-entity)
- [EntityProvider](#entityprovider)
  * [EntityProvider creation](#entityprovider-creation)
  * [EntityProvider operations](#entityprovider-operations)
    + [Providing the current Resource](#providing-the-current-resource)
  * [Dealing with conflicts in Entity and Resource](#dealing-with-conflicts-in-entity-and-resource)
  * [Merge Algorithm](#merge-algorithm)
    + [Construct a set of detected entities](#construct-a-set-of-detected-entities)
  * [Resolve conflicts with raw attributes](#resolve-conflicts-with-raw-attributes)
  * [Resolve conflicts in Schema URL](#resolve-conflicts-in-schema-url)

<!-- tocstop -->

## Overview

The Entities SDK consists of these main components:

- [Entity](#entity)
- [EntityDetector](#entitydetector)
- [EntityProvider](#entityprovider)

## Entity

An `Entity` represents an object of interested associated with
produced telemetry: traces, metrics, profiles or logs. Every entity
typically describes one object for its entire lifetime.

### Entity Creation

The SDK MUST accept the following parameters:

- The entity's `type`.
- The entity's `identity` attributes.
- (optional) The entity's `description` attributes.
- (optional) The Schema URL associated with emitted entity.

The SDK MAY use a builder pattern or other language convention for
constructing entities.

### Entity properties

The SDK MUST allow access to Entity properties:

- The entity's `type`.
- The entity's `identity` attributes.
- The entity's `description` attributes.
- The SchemaURL associated with the entity.

These MAY be provided using language conventions, e.g. public
fields, "Getter" methods, etc.

## EntityDetector

An `EntityDetector` is responsible for detecting the identity and
description for entities. A set of `EntityDetector`s will be used
by the SDK for the purpose of determining associated `Entity`s on
produced telemetry (metrics, log, traces).

### EntityDetector operations

The `EntityDetector` MUST provide the following functions:

* Detect a set of `Entity`.

#### Detect a set of `Entity`

This operation MAY take input parameters related to the environment
the SDK is running in, or used for SDK diagnostics and debugging.

This operation MUST return a collection or set of `Entity` objects
that were detected by the `EntityDetector`.

This operation MAY return an error, in the event the detection
resulted in some kind of exceptional situation and was unable to
complete.

## EntityProvider

 The `EntityProvider` is responsible for the following:

- Constructing a `Resource` for the SDK from detectors.
- Dealing with conflicts between detectors and raw `Resource`.
- Providing SDK-internal access to the final `Resource`.

An `EntityProvider` MAY decide when to run entity detection
and update the current `Resource`.

### EntityProvider creation

The SDK MUST accept the following parameters:

- `detectors`: A collection or set of `EntityDetector`s.
  Note: SDKs MUST provide a mechanism to prioritize or order
  `EntityDetector`s.
- (optional) `resource`: A `Resource` created using existing
  Resource SDK.

### EntityProvider operations

The `EntityProvider` MUST provide the following functions:

- Providing the current  `Resource`.

#### Providing the current Resource

This operation MUST return the current, complete `Resource`
the SDK should use when producing signals.

This operation SHOULD be thread-safe, for languages or environments
that allow threads or concurrency.

The returned resource SHOULD represent the most up-to-date
`Resource`, which includes all `Entity` found from
`EntityDetector`s and any original `Resource`.
The`EntityProvider` SHOULD NOT attempt to use `EntityDetector`s
every time this method is called, but instead cache a a result.

### Dealing with conflicts in Entity and Resource

The `EntityProvider` MUST resolve conflicts between `Resource`
and `EntityDetector`s that are registered with it.
The `EntityProvider` SHOULD use the [merge algorithm](#merge-algorithm) defined to deal with these conflicts.

### Merge Algorithm

The `EntityProvider` SHOULD use the following algorithm
(or an equivalent) to construct a single `Resource` using
`EntityDetector` and `Resource` provided to it.

First, [construct a set of detected entities](#construct-a-set-of-detected-entities).

Next, merge loose attributes (from `Resource`) with the
set of entities. [Resolve all conflicts](#resolve-conflicts-with-raw-attributes).

Finally, select a Schema URL for the `Resource` by
[resolving conflicts between detected entities and resource](#resolve-conflicts-in-schema-url).

The resulting `Resource` should include the remaining `Entity`
set, raw `Attribute`s and Schema URL.

#### Construct a set of detected entities

Construct a set of detected entities (`E`)

- All entity detectors are sorted by priority (highest first).
- For each entity detector (`D`), use the "detect a set of
  entities" operation.
  - For each entity detected (`d'`):
    - If an entity (`e'`) exists in the current set of detected
      entities (`E`) with the same `type` as the detected
      entity (`d'`), do one of the following:
      - If the entity `identity` and `schema_url` are the same,
        merge the `description` of the detected entity (`d'`) into
        the previously detected entity (`e'`).
        - For each attribute (`da'`) in the description
          - If the attribute key does not exist in the previously
            detected entity (`e'`), then add the full attribute
            (`da'`).
          - otherwise, ignore the attribute.
      - If the entity `identity` is the same, but `schema_url` is
        different, drop the new entity (`d'`).
        *Note: SDKs MAY provide configuration to preserve
        non-conflicting description attributes in this case.*
      - If the entity identity is different, drop the new
        entity (`d'`).
      - Otherwise, add the detected entity (`d'`) to the set of
        detected entities (`E`).

### Resolve conflicts with raw attributes

When a "raw" attribute from `Resource` (those not associated with
an entity) has the same key as an `Entity`'s `identity` or
`description` attributes, then there is a conflict.

If the *value* of the attribute is the same, the SDK can ignore the
"raw" attribute.

If the *value* of the attribute is different, then the SDK must
resolve the conflict.

- The SDK MUST remove the `Entity` from the detected `Entity` set
  if the conflict is with an `identity` attribute.
- The SDK MAY remove the `Entity` or just the conflicting attribute
  from the `Entity` if the conflict is with a `description`
  attribute.

### Resolve conflicts in Schema URL

If the detected `Entity` set and raw `Resource` all share the
same Schema URL, then this Schema URL SHOULD be returned.

If the detected `Entity` set have non-empty Schema URLs and
these conflict, then Schema URL SHOULD NOT be set on the Resource.

If the detected `Entity` set is empty or does not have any Schema
URLs defined, then the raw `Resource` Schema URL SHOULD be used.
