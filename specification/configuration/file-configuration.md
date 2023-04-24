# File Configuration

**Status**: [Experimental](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [Configuration Model](#configuration-model)
  * [Stability Definition](#stability-definition)
- [Configuration file](#configuration-file)
- [SDK Configuration](#sdk-configuration)
  * [In-Memory Configuration Model](#in-memory-configuration-model)
    + [Parse File to Configuration](#parse-file-to-configuration)
  * [Configurer](#configurer)
    + [Create Configurer](#create-configurer)
    + [Get TracerProvider, MeterProvider, LoggerProvider](#get-tracerprovider-meterprovider-loggerprovider)
- [References](#references)

<!-- tocstop -->

## Overview

File configuration provides a mechanism for configuring OpenTelemetry which is
more expressive and full-featured than
the [environment variable](../sdk-environment-variables.md) based scheme, and
language agnostic in a way not possible
with [programmatic configuration](../sdk-configuration.md#programmatic).

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

#### Parse File to Configuration

SDKs MUST provide an API to parse and validate
a [configuration file](#configuration-file) and return a
corresponding [Configuration Model](#in-memory-configuration-model).

The API MUST accept the following parameters:

* `file`: The [configuration file](#configuration-file) to parse. This MAY be a
  file path, or language specific file class, or a stream of a file's contents.

The API MAY return an error if:

* The `file` doesn't exist or is invalid
* The parsed `file` contents do not conform to
  the [configuration model](#configuration-model) schema.

### Configurer

`Configurer` is a class responsible for
interpreting [Configuration](#in-memory-configuration-model) and producing
configured SDK components.

It MUST be possible to [create](#create-configurer) multiple `Configurer`s with
different configurations. It is the caller's responsibility to ensure the
resulting [SDK components](#get-tracerprovider-meterprovider-loggerprovider) are
correctly wired into the application and instrumentation.

#### Create Configurer

Create a `Configurer` from a configuration model.

The API MUST accept the following parameters:

* `configuration` - The [configuration model](#in-memory-configuration-model).

#### Get TracerProvider, MeterProvider, LoggerProvider

Interpret `configuration` and return SDK components (`TracerProvider`,
`MeterProvider`, `LoggerProvider`). The SDK components MUST strictly reflect
the `Configuration` and ignore
the [environment variable configuration scheme](../sdk-environment-variables.md).

// TODO: Extend Configurer with ability to update SDK components with new
// configuration for usage with OpAmp

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
