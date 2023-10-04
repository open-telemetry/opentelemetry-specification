<!--- Hugo front matter used to generate the website version of this page:
linkTitle: File
--->

# File Configuration

**Status**: [Experimental](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [Configuration Model](#configuration-model)
  * [Stability Definition](#stability-definition)
- [Configuration file](#configuration-file)
- [SDK Configuration](#sdk-configuration)
  * [In-Memory Configuration Model](#in-memory-configuration-model)
  * [Configurator](#configurator)
    + [Parse](#parse)
    + [Create](#create)
- [References](#references)

<!-- tocstop -->

## Overview

File configuration provides a mechanism for configuring OpenTelemetry which is
more expressive and full-featured than
the [environment variable](sdk-environment-variables.md) based scheme, and
language agnostic in a way not possible
with [programmatic configuration](sdk-configuration.md#programmatic).

File configuration defines a [Configuration Model](#configuration-model),
which can be expressed in a [configuration file](#configuration-file).
Configuration files can be validated against the Configuration Schema, and
interpreted to produce configured OpenTelemetry components.

## Configuration Model

The configuration model is defined
in [opentelemetry-configuration](https://github.com/open-telemetry/opentelemetry-configuration)
using the [JSON Schema](https://json-schema.org/).

### Stability Definition

TODO: define stability guarantees and backwards compatibility

## Configuration file

A configuration file is a file representation of
the [Configuration Model](#configuration-model).

TODO: define acceptable file formats

TODO: define environment variable substitution

## SDK Configuration

SDK configuration defines the interfaces and operations that SDKs are expected
to expose to enable file based configuration.

### In-Memory Configuration Model

SDKs SHOULD provide an in-memory representation of
the [Configuration Model](#configuration-model). In general, SDKs are encouraged
to provide this in-memory representation in a manner that is idiomatic for their
language. If an SDK needs to expose a class or interface, the
name `Configuration` is RECOMMENDED.

### Configurator

`Configurator` is responsible for parsing configuration files and
interpreting [Configuration](#in-memory-configuration-model) to produce
configured SDK components.

TODO: Extend ConfigurationFactory with ability to update SDK components with
new configuration for usage with OpAmp

#### Parse

Parse and validate a [configuration file](#configuration-file).

**Parameters:**

* `file`: The [configuration file](#configuration-file) to parse. This MAY be a
  file path, or language specific file data structure, or a stream of a file's content.

**Returns:** [configuration model](#in-memory-configuration-model)

This SHOULD return an error if:

* The `file` doesn't exist or is invalid
* The parsed `file` content does not conform to
  the [configuration model](#configuration-model) schema.

TODO: define behavior if some portion of configuration model is not supported

#### Create

Interpret [configuration model](#in-memory-configuration-model) and return SDK components.

**Parameters:**

* `configuration` - The configuration model.

**Returns:** Top level SDK components:

* `TracerProvider`
* `MeterProvider`
* `LoggerProvider`
* `Propagators`

The multiple responses MAY be returned using a tuple, or some other data structure encapsulating the components.

This SHOULD return an error if it encounters an error in `configuration` (i.e. fail fast).

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
