# Instrumentation Configuration API

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
  * [ConfigProvider](#configprovider)
    + [ConfigProvider operations](#configprovider-operations)
      - [Get instrumentation config](#get-instrumentation-config)
      - [Convenience functions](#convenience-functions)
  * [ConfigProperties](#configproperties)

<!-- tocstop -->

## Overview

The instrumentation configuration API is part of
the [declarative configuration interface](./README.md#declarative-configuration).

The API allows [instrumentation libraries](../glossary.md#instrumentation-library)
to participate in configuration by reading relevant configuration options during
initialization. It consists of the following main components:

* [ConfigProvider](#configprovider) is the entry point of the API.
* [ConfigProperties](#configproperties) is a programmatic representation of a
  file configuration node.

### ConfigProvider

`ConfigProvider` provides access to configuration properties relevant to
instrumentation.

Normally, the `ConfigProvider` is expected to be accessed from a central place.
Thus, the API should provide a way to set/register and access a global
default `ConfigProvider`.

#### ConfigProvider operations

The `ConfigProvider` MUST provide the following functions:

* [Get instrumentation config](#get-instrumentation-config)

The `ConfigProvider` MAY provide the following:

* [Convenience functions](#convenience-functions)

##### Get instrumentation config

Obtain configuration relevant to instrumentation libraries.

**Returns:** [`ConfigProperties`](#configproperties) representing
the [`.instrumentation`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L438-L439)
file configuration mapping node.

Get instrumentation config MUST return nil, null, or undefined (based on what is
idiomatic in the language ecosystem) if file configuration is not used or if
the `.instrumentation` node is not set.

##### Convenience functions

Convenience functions help instrumentation libraries interpret the contents
of [Get instrumentation config](#get-instrumentation-config). Convenience
functions shift the burden of schema knowledge from instrumentation libraries to
the OpenTelemetry API authors.

For example, consider an HTTP client instrumentation library trying to read the
set of request captured headers
at [`.instrumentation.general.http.client.request_captured_headers`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L465-L467).
Rather than requiring the instrumentation library to
call [Get instrumentation config](#get-instrumentation-config) and
access `.general.http.client.request_captured_headers` on the
resulting `ConfigProperties`, a convenience function provides direct access with
type safety:

```java
@Nullable
public static List<String> httpClientRequestCapturedHeaders(ConfigProvider configProvider);
```

Convenience functions MAY be part of `ConfigProvider`, or be pure functions
accepting `ConfigProvider` as an argument.

### ConfigProperties

`ConfigProperties` is a programmatic representation of a configuration mapping
node (i.e. a YAML mapping node).

`ConfigProperties` MUST provide accessors for reading all properties from the
mapping node it represents, including:

* scalars (string, boolean, double precision floating point, 64-bit integer)
* mappings, which SHOULD be represented as `ConfigProperties`
* sequences of scalars
* sequences of mappings, which SHOULD be represented as `ConfigProperties`
* the set of properties

`ConfigProperties` SHOULD provide access to properties in a type safe manner,
based on what is idiomatic in the language.

`ConfigProperties` SHOULD allow a caller to determine if a property is present
with a null value, versus not set.
