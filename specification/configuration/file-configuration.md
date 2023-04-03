# File Configuration

**Status**: [Experimental](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [Configuration Schema](#configuration-schema)
  * [Stability Definition](#stability-definition)
- [Configuration file](#configuration-file)
- [SDK Configuration](#sdk-configuration)
  * [Configuration Model](#configuration-model)
  * [Operations](#operations)
- [References](#references)

<!-- tocstop -->

## Overview

File configuration provides a mechanism for configuring OpenTelemetry which is
more expressive and full-featured than
the [environment variable](../sdk-environment-variables.md) based scheme, and
language agnostic in a way not possible
with [programmatic configuration](../sdk-configuration.md#programmatic).

File configuration defines a [Configuration Schema](#configuration-schema),
which can be expressed in a [configuration file](#configuration-file).
Configuration files can be validated against the Configuration Schema, and
interpreted to produce configured OpenTelemetry components.

## Configuration Schema

The configuration schema is defined in [./schema/](./schema/)
using [JSON Schema](https://json-schema.org/).

### Stability Definition

TODO: define stability guarantees and backwards compatibility

## Configuration file

A configuration file is a file representation of the model defined
by [./Configuration Schema](#configuration-schema).

TODO: define acceptable file formats

TODO: define environment variable substitution

## SDK Configuration

SDK configuration defines the interfaces and operations that SDKs are expected
to expose to enable file based configuration.

### Configuration Model

`Configuration` is an in-memory representation of the model defined
by [./Configuration Schema](#configuration-schema).

### Operations

TODO: define how to parse configuration file to configuration model

TODO: define how to apply configuration model to produce configured sdk
components

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
