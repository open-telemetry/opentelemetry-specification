<!--- Hugo front matter used to generate the website version of this page:
linkTitle: API
weight: 1
--->

# Instrumentation Configuration API

**Status**: [Mixed](../document-status.md)

<!-- START DOCTOC -->

- [Overview](#overview)
  * [ConfigProvider](#configprovider)
    + [ConfigProvider operations](#configprovider-operations)
      - [Get instrumentation config](#get-instrumentation-config)
      - [Add change listener](#add-change-listener)
  * [ConfigProperties](#configproperties)

<!-- END DOCTOC -->

## Overview

The instrumentation configuration API is part of
the [declarative configuration interface](./README.md#declarative-configuration).

The API allows [instrumentation libraries](../glossary.md#instrumentation-library)
to consume configuration by reading relevant configuration during
initialization. For example, an instrumentation library for an HTTP client can
read the set of HTTP request and response headers to capture.

It consists of the following main components:

* [ConfigProvider](#configprovider) is the entry point of the API.
* [ConfigProperties](#configproperties) is a programmatic representation of a
  configuration mapping node.

### ConfigProvider

**Status**: [Development](../document-status.md)

`ConfigProvider` provides access to configuration properties relevant to
instrumentation.

Instrumentation libraries access `ConfigProvider` during
initialization. `ConfigProvider` may be passed as an argument to the
instrumentation library, or the instrumentation library may access it from a
central place. Thus, the API SHOULD provide a way to access a global
default `ConfigProvider`, and set/register it.

#### ConfigProvider operations

The `ConfigProvider` MUST provide the following functions:

* [Get instrumentation config](#get-instrumentation-config)
* [Add change listener](#add-change-listener)

TODO: decide if additional operations are needed to improve API ergonomics

##### Get instrumentation config

Obtain configuration relevant to instrumentation libraries.

**Returns:** [`ConfigProperties`](#configproperties) representing
the [`.instrumentation`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L438-L439)
configuration mapping node.

If the `.instrumentation` node is not set, get instrumentation config SHOULD
return an empty `ConfigProperties` (as if `.instrumentation: {}` was set).

##### Add change listener

Register a listener to be notified when configuration at a specific watched path
changes.

This API MUST accept the following parameters:

* `path`: declarative configuration path to watch.
* `listener`: callback invoked on changes.

**Returns:** A registration handle. The handle MUST provide a close (or language-equivalent) operation that unregisters the listener.

Path requirements:

* `path` MUST use the declarative configuration path syntax defined here.
* `path` MUST start with `.`.
* Nested named properties MUST be separated with `.`.
* `path` matching is exact. Wildcards and prefix matching are not supported.
* In this version, paths are defined only for named properties. Sequence/array
  indexing is not supported.
* Examples include `.instrumentation/development.general.http` and
  `.instrumentation/development.java.methods`.

Callback requirements:

* Implementations MUST allow multiple listeners to be registered for the same
  watched path. Each registration is independent and has its own registration
  handle.
* If a watched path changes, the callback MUST receive:
  * `path`: the changed watched path.
  * `newConfig`: the updated [`ConfigProperties`](#configproperties) for that
    path.
* If the watched path resolves to a mapping node, `newConfig` MUST be a valid
  [`ConfigProperties`](#configproperties) instance representing that mapping
  node, including an explicitly empty mapping node (`{}`).
* If the watched path is unset or cleared, `newConfig` MUST be null/nil/None,
  according to what is idiomatic for the language.
* Implementations MAY coalesce rapid successive updates for the same watched
  path. If coalescing is performed, callback delivery MUST use the latest
  configuration state.
* Ordering of callback delivery is not specified, including for updates touching
  multiple watched paths in one configuration transaction.

Concurrency and lifecycle requirements:

* Callback implementations SHOULD be reentrant and SHOULD avoid blocking
  operations.
* Implementations MUST document callback concurrency guarantees. If they do not,
  users MUST assume callbacks may be invoked concurrently.
* Closing a registration handle MUST unregister the listener.
* Close MUST be idempotent (subsequent calls have no effect).
* After close returns, implementations SHOULD stop new callback delivery for that
  registration. A callback already in progress MAY complete.
* Registrations SHOULD be dropped automatically when the corresponding
  `ConfigProvider` is shut down or otherwise disposed.

Error handling and unsupported providers:

* If callback execution throws an error, implementations SHOULD isolate the
  failure to that callback and SHOULD continue notifying other callbacks.

### ConfigProperties

**Status**: [Stable](../document-status.md)

`ConfigProperties` is a programmatic representation of a configuration mapping
node (i.e. a YAML mapping node).

`ConfigProperties` MUST provide accessors for reading all properties from the
mapping node it represents, including:

* scalars (string, boolean, double precision floating point, 64-bit integer)
* mappings, which SHOULD be represented as `ConfigProperties`
* sequences of scalars
* sequences of mappings, which SHOULD be represented as `ConfigProperties`
* the set of property keys present

`ConfigProperties` SHOULD provide access to properties in a type safe manner,
based on what is idiomatic in the language.

`ConfigProperties` SHOULD allow a caller to determine if a property is present
with a null value, versus not set.
