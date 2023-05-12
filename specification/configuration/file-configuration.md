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
  * [Operations](#operations)
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

### Operations

TODO: define how to parse configuration file to configuration model

TODO: define how to apply configuration model to produce configured sdk
components

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
