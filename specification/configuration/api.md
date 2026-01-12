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

TODO: decide if additional operations are needed to improve API ergonomics

##### Get instrumentation config

Obtain configuration relevant to instrumentation libraries.

**Returns:** [`ConfigProperties`](#configproperties) representing
the [`.instrumentation`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L438-L439)
configuration mapping node.

If the `.instrumentation` node is not set, get instrumentation config SHOULD
return an empty object (as if `.instrumentation: {}` was set).

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
