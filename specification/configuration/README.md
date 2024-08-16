<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/configuration/_index.md
  to: configuration/README.md
--->

# Overview

OpenTelemetry SDK components are highly configurable. This specification
outlines the mechanisms by which OpenTelemetry components can be configured. It
does not attempt to specify the details of what can be configured.

## Configuration Interfaces

### Programmatic

The SDK MUST provide a programmatic interface for all configuration.
This interface SHOULD be written in the language of the SDK itself.
All other configuration mechanisms SHOULD be built on top of this interface.

An example of this programmatic interface is accepting a well-defined
struct on an SDK builder class. From that, one could build a CLI that accepts a
file (YAML, JSON, TOML, ...) and then transforms into that well-defined struct
consumable by the programmatic interface (
see [declarative configuration](#declarative-configuration)).

### Environment variables

Environment variable configuration defines a set of language agnostic
environment variables for common configuration goals.

See [OpenTelemetry Environment Variable Specification](./sdk-environment-variables.md).

### Declarative configuration

Declarative configuration provides a mechanism for configuring OpenTelemetry
which is more expressive and full-featured than
the [environment variable](#environment-variables) based scheme, and language
agnostic in a way not possible with [programmatic configuration](#programmatic).
Notably, declarative configuration defines tooling allowing users to load
OpenTelemetry components according to a file-based representation of a
standardized configuration data model.

Declarative configuration consists of the following main components:

* [Data model](./data-model.md) defines data structures which allow users to
  specify an intended configuration of OpenTelemetry SDK components and
  instrumentation. The data model includes a file-based representation.
* [Instrumentation configuration API](./api.md) allows
  instrumentation libraries to consume configuration by reading relevant
  configuration options during initialization.
* [Configuration SDK](./sdk.md) defines SDK capabilities around file
  configuration, including an In-Memory configuration model, support for
  referencing custom extension plugin interfaces in configuration files, and
  operations to parse configuration files and interpret the configuration data
  model.

### Other Mechanisms

Additional configuration mechanisms SHOULD be provided in whatever
language/format/style is idiomatic for the language of the SDK. The
SDK can include as many configuration mechanisms as appropriate.
