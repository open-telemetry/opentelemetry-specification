<!--- Hugo front matter used to generate the website version of this page:
linkTitle: API
weight: 1
--->

# Instrumentation Configuration API

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
  * [ConfigProvider](#configprovider)
    + [ConfigProvider operations](#configprovider-operations)
      - [Get instrumentation config](#get-instrumentation-config)
      - [Add config change listener](#add-config-change-listener)
  * [ConfigProperties](#configproperties)

<!-- tocstop -->

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
* [Add config change listener](#add-config-change-listener)

TODO: decide if additional operations are needed to improve API ergonomics

##### Get instrumentation config

Obtain configuration relevant to instrumentation libraries.

**Returns:** [`ConfigProperties`](#configproperties) representing
the [`.instrumentation`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L438-L439)
configuration mapping node.

If the `.instrumentation` node is not set, get instrumentation config SHOULD
return an empty `ConfigProperties` (as if `.instrumentation: {}` was set).

##### Add config change listener

Register a listener to be notified when configuration at a specific watched path
changes.

This API MUST accept the following parameters:

* `path`: declarative configuration path to watch.
* `listener`: callback invoked on changes.

**Returns:** A registration handle with a close operation.

Path requirements:

* `path` MUST be an absolute declarative configuration path.
* `path` matching is exact. Wildcards and prefix matching are not supported.
* In this version, paths are defined only for named properties. Sequence/array indexing is not supported
* API implementations SHOULD document accepted path syntax in language-specific
  docs and include examples such as `.instrumentation/development.general.http`
  and `.instrumentation/development.java.methods`.

Callback requirements:

* If a watched path changes, the callback MUST receive:
  * `path`: the changed watched path.
  * `newConfig`: the updated [`ConfigProperties`](#configproperties) for that
    path.
* `newConfig` MUST be a valid [`ConfigProperties`](#configproperties) instance
  (never null/nil/None).
* If the watched node is unset or cleared, `newConfig` MUST represent an empty
  mapping node (equivalent to `{}`).
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

* If callback execution throws an exception, implementations SHOULD isolate the
  failure to that callback and SHOULD continue notifying other callbacks.
* If a provider does not support change notifications, registration MUST still
  succeed by returning a no-op registration handle, and callbacks MUST NOT be
  invoked.

### ConfigProperties

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
