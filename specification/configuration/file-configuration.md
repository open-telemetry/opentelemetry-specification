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
  * [YAML file format](#yaml-file-format)
  * [Environment variable substitution](#environment-variable-substitution)
- [SDK Configuration](#sdk-configuration)
  * [In-Memory Configuration Model](#in-memory-configuration-model)
  * [SDK Extension Components](#sdk-extension-components)
    + [Component Provider](#component-provider)
    + [Create Plugin](#create-plugin)
  * [Operations](#operations)
    + [Parse](#parse)
    + [Create](#create)
    + [Register Component Provider](#register-component-provider)
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

A configuration file is a serialized file-based representation of
the [Configuration Model](#configuration-model).

Configuration files SHOULD use one the following serialization formats:

### YAML file format

[YAML](https://yaml.org/spec/1.2.2/) configuration files SHOULD follow YAML spec
revision >= 1.2.

YAML configuration files MUST use file extensions `.yaml` or `.yml`.

TODO: decide if JSON file format is required

### Environment variable substitution

Configuration files support environment variables substitution for references
which match the following PCRE2 regular expression:

```regexp
\$\{(?:env:)?(?<ENV_NAME>[a-zA-Z_][a-zA-Z0-9_]*)(:-(?<DEFAULT_VALUE>[^\n]*))?\}
```

The `ENV_NAME` MUST start with an alphabetic or `_` character, and is followed
by 0 or more alphanumeric or `_` characters.

For example, `${API_KEY}` and `${env:API_KEY}` are valid, while `${1API_KEY}`
and `${API_$KEY}` are invalid.

Environment variable substitution MUST only apply to scalar values. Mapping keys
are not candidates for substitution.

The `DEFAULT_VALUE` is an optional fallback value which is substituted
if `ENV_NAME` is null, empty, or undefined. `DEFAULT_VALUE` consists of 0 or
more non line break characters (i.e. any character except `\n`). If a referenced
environment variable is not defined and does not have a `DEFAULT_VALUE`, it MUST
be replaced with an empty value.

When parsing a configuration file that contains a reference not matching
the references regular expression but does match the following PCRE2
regular expression, the parser MUST return an empty result (no partial
results are allowed) and an error describing the parse failure to the user.

```regexp
\$\{(?<INVALID_IDENTIFIER>[^}]+)\}
```

Node types MUST be interpreted after environment variable substitution takes
place. This ensures the environment string representation of boolean, integer,
or floating point fields can be properly converted to expected types.

It MUST NOT be possible to inject YAML structures by environment variables. For
example, references to `INVALID_MAP_VALUE` environment variable below.

It MUST NOT be possible to inject environment variable by environment variables.
For example, references to `DO_NOT_REPLACE_ME` environment variable below.

For example, consider the following environment variables,
and [YAML](#yaml-file-format) configuration file:

```shell
export STRING_VALUE="value"
export BOOl_VALUE="true"
export INT_VALUE="1"
export FLOAT_VALUE="1.1"
export INVALID_MAP_VALUE="value\nkey:value"           # An invalid attempt to inject a map key into the YAML
export DO_NOT_REPLACE_ME="Never use this value"       # An unused environment variable
export REPLACE_ME='${DO_NOT_REPLACE_ME}'              # A valid replacement text, used verbatim, not replaced with "Never use this value"
```

```yaml
string_key: ${STRING_VALUE}                           # Valid reference to STRING_VALUE
env_string_key: ${env:STRING_VALUE}                   # Valid reference to STRING_VALUE
other_string_key: "${STRING_VALUE}"                   # Valid reference to STRING_VALUE inside double quotes
another_string_key: "${BOOl_VALUE}"                   # Valid reference to BOOl_VALUE inside double quotes
yet_another_string_key: ${INVALID_MAP_VALUE}          # Valid reference to INVALID_MAP_VALUE, but YAML structure from INVALID_MAP_VALUE MUST NOT be injected
bool_key: ${BOOl_VALUE}                               # Valid reference to BOOl_VALUE
int_key: ${INT_VALUE}                                 # Valid reference to INT_VALUE
float_key: ${FLOAT_VALUE}                             # Valid reference to FLOAT_VALUE
combo_string_key: foo ${STRING_VALUE} ${FLOAT_VALUE}  # Valid reference to STRING_VALUE and FLOAT_VALUE
string_key_with_default: ${UNDEFINED_KEY:-fallback}   # UNDEFINED_KEY is not defined but a default value is included
undefined_key: ${UNDEFINED_KEY}                       # Invalid reference, UNDEFINED_KEY is not defined and is replaced with ""
${STRING_VALUE}: value                                # Invalid reference, substitution is not valid in mapping keys and reference is ignored
recursive_key: ${REPLACE_ME}                          # Valid reference to REPLACE_ME
# invalid_identifier_key: ${STRING_VALUE:?error}      # If uncommented, this is an invalid identifier, it would fail to parse
```

Environment variable substitution results in the following YAML:

```yaml
string_key: value                           # Interpreted as type string, tag URI tag:yaml.org,2002:str
env_string_key: value                       # Interpreted as type string, tag URI tag:yaml.org,2002:str
other_string_key: "value"                   # Interpreted as type string, tag URI tag:yaml.org,2002:str
another_string_key: "true"                  # Interpreted as type string, tag URI tag:yaml.org,2002:str
yet_another_string_key: "value\nkey:value"  # Interpreted as type string, tag URI tag:yaml.org,2002:str
bool_key: true                              # Interpreted as type bool, tag URI tag:yaml.org,2002:bool
int_key: 1                                  # Interpreted as type int, tag URI tag:yaml.org,2002:int
float_key: 1.1                              # Interpreted as type float, tag URI tag:yaml.org,2002:float
combo_string_key: foo value 1.1             # Interpreted as type string, tag URI tag:yaml.org,2002:str
string_key_with_default: fallback           # Interpreted as type string, tag URI tag:yaml.org,2002:str
undefined_key:                              # Interpreted as type null, tag URI tag:yaml.org,2002:null
${STRING_VALUE}: value                      # Interpreted as type string, tag URI tag:yaml.org,2002:str
recursive_key: ${DO_NOT_REPLACE_ME}         # Interpreted as type string, tag URI tag:yaml.org,2002:str
```

## SDK Configuration

SDK configuration defines the interfaces and operations that SDKs are expected
to expose to enable file based configuration.

### In-Memory Configuration Model

SDKs SHOULD provide an in-memory representation of
the [Configuration Model](#configuration-model). In general, SDKs are encouraged
to provide this in-memory representation in a manner that is idiomatic for their
language. If an SDK needs to expose a class or interface, the
name `Configuration` is RECOMMENDED.

### SDK Extension Components

The SDK supports a variety of
extension [plugin interfaces](../glossary.md#sdk-plugins), allowing users and
libraries to customize behaviors including the sampling, processing, and
exporting of data. In general, the [configuration model](#configuration-model)
defines specific types for built-in implementations of these plugin interfaces.
For example,
the [BatchSpanProcessor](https://github.com/open-telemetry/opentelemetry-configuration/blob/f38ac7c3a499ae5f81924ef9c455c27a56130562/schema/tracer_provider.json#L22)
type refers to the
built-in [Batching span processor](../trace/sdk.md#batching-processor). The
schema SHOULD also support the ability to specify custom implementations of
plugin interfaces defined by libraries or users.

For example, a custom [span exporter](../trace/sdk.md#span-exporter) might be configured as follows:

```yaml
tracer_provider:
  processors:
    - batch:
        exporter:
          my-exporter:
            config-parameter: value
```

Here we specify that the tracer provider has a batch span processor
paired with a custom span exporter named `my-exporter`, which is configured
with `config-parameter: value`. For this configuration to succeed,
a [component provider](#component-provider) must
be [registered](#register-component-provider) with `type: SpanExporter`,
and `name: my-exporter`. When [parse](#parse) is called, the implementation will
encounter `my-exporter` and translate the corresponding configuration to an
equivalent generic `properties` representation (
i.e. `properties: {config-parameter: value}`). When [create](#create) is called,
the implementation will encounter `my-exporter` and
invoke [create plugin](#create-plugin) on the registered component provider
with the configuration `properties` determined during `parse`.

Given the inherent differences across languages, the details of extension
component mechanisms are likely to vary to a greater degree than is the case
with other APIs defined by OpenTelemetry. This is to be expected and is
acceptable so long as the implementation results in the defined behaviors.

#### Component Provider

A component provider is responsible for interpreting configuration and returning
an implementation of a particular type of SDK extension plugin interface.

Component providers are registered with an SDK implementation of configuration
via [register](#register-component-provider). This MAY be done automatically or
require manual intervention by the user based on what is possible and idiomatic
in the language ecosystem. For example in Java, component providers might be
registered automatically using
the [service provider interface (SPI)](https://docs.oracle.com/javase/tutorial/sound/SPI-intro.html)
mechanism.

See [create](#create), which details component provider usage in file
configuration interpretation.

#### Create Plugin

Interpret configuration to create a instance of a SDK extension plugin
interface.

**Parameters:**

* `properties` - The configuration properties. Properties MUST fully represent
  the configuration as specified in
  the [configuration file](#configuration-file), including the ability to access
  scalars, mappings, and sequences (of scalars and other structures). It MUST be
  possible to determine if a particular property is present. It SHOULD be
  possible to access properties in a type safe manner, based on what is idiomatic
  in the language.

**Returns:** A configured SDK extension plugin interface implementation.

The plugin interface MAY have properties which are optional or required, and
have specific requirements around type or format. The set of properties a
component provider accepts, along with their requirement level and expected
type, comprise a configuration schema. A component provider SHOULD document its
configuration schema.

When Create Plugin is invoked, the component provider interprets `properties`
and attempts to extract data according to its configuration schema. If this
fails (e.g. a required property is not present, a type is mismatches, etc.),
Create Plugin SHOULD return an error.

### Operations

SDK implementations of configuration MUST provide the following operations.

Note: Because these operations are stateless pure functions, they are not
defined as part of any type, class, interface, etc. SDKs may organize them in
whatever manner is idiomatic for the language.

TODO: Add operation to update SDK components with new configuration for usage
with OpAmp

#### Parse

Parse and validate a [configuration file](#configuration-file).

**Parameters:**

* `file`: The [configuration file](#configuration-file) to parse. This MAY be a
  file path, or language specific file data structure, or a stream of a file's content.
* `file_format`: The file format of the `file` (e.g. [yaml](#yaml-file-format)).
  Implementations MAY accept a `file_format` parameter, or infer it from
  the `file` extension, or include file format specific overloads of `parse`,
  e.g. `parseYaml(file)`. If `parse` accepts `file_format`, the API SHOULD be
  structured so a user is obligated to provide it.

**Returns:** [configuration model](#in-memory-configuration-model)

Parse MUST perform [environment variable substitution](#environment-variable-substitution).

Parse MUST interpret null as equivalent to unset.

When encountering a reference to
a [SDK extension component](#sdk-extension-components) which is not built in to
the SDK, Parse MUST resolve corresponding configuration to a
generic `properties` representation as described
in [Create Plugin](#create-plugin).

Parse SHOULD return an error if:

* The `file` doesn't exist or is invalid
* The parsed `file` content does not conform to
  the [configuration model](#configuration-model) schema.

#### Create

Interpret [configuration model](#in-memory-configuration-model) and return SDK components.

**Parameters:**

* `configuration` - The configuration model.

**Returns:** Top level SDK components:

* `TracerProvider`
* `MeterProvider`
* `LoggerProvider`
* `Propagators`

The multiple responses MAY be returned using a tuple, or some other data
structure encapsulating the components.

If a field is null or unset and a default value is defined, Create MUST ensure
the SDK component is configured with the default value. If a field is null or
unset and no default value is defined, Create SHOULD return an error. For
example, if configuring
the [span batching processor](../trace/sdk.md#batching-processor) and
the `scheduleDelayMillis` field is null or unset, the component is configured
with the default value of `5000`. However, if the `exporter` field is null or
unset, Create fails fast since there is no default value for `exporter`.

When encountering a reference to
a [SDK extension component](#sdk-extension-components) which is not built in to
the SDK, Create MUST resolve the component using [Create Plugin](#create-plugin)
of the [component provider](#component-provider) of the corresponding `type`
and `name` used to [register](#register-component-provider), including the
configuration `properties` as an argument. If no component provider is
registered with the `type` and `name`, Create SHOULD return an error.
If [Create Plugin](#create-plugin) returns an error, Create SHOULD propagate the
error.

This SHOULD return an error if it encounters an error in `configuration` (i.e.
fail fast) in accordance with
initialization [error handling principles](../error-handling.md#basic-error-handling-principles).

TODO: define behavior if some portion of configuration model is not supported

#### Register Component Provider

The file configuration implementation MUST provide a mechanism to
register [component providers](#component-provider).

**Parameters:**

* `component_provider` - The [component provider](#component-provider).
* `type` - The type of plugin interface it provides (e.g. SpanExporter, Sampler,
  etc).
* `name` - The name used to identify the type of component. This is used
  in [configuration files](#configuration-file) to specify that the
  corresponding `component_provider` is to provide the component.

The `type` and `name` comprise a unique key. Register MUST return an error if it
is called multiple times with the same `type` and `name` combination.

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
