<!--- Hugo front matter used to generate the website version of this page:
linkTitle: File
--->

# File Configuration

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [Configuration model](#configuration-model)
  * [Stability definition](#stability-definition)
- [Configuration file](#configuration-file)
  * [YAML file format](#yaml-file-format)
  * [Environment variable substitution](#environment-variable-substitution)
- [Instrumentation configuration API](#instrumentation-configuration-api)
  * [ConfigProvider](#configprovider)
    + [ConfigProvider operations](#configprovider-operations)
      - [Get instrumentation config](#get-instrumentation-config)
      - [Convenience functions](#convenience-functions)
  * [ConfigProperties](#configproperties)
- [Configuration SDK](#configuration-sdk)
  * [In-Memory configuration model](#in-memory-configuration-model)
  * [SDK ConfigProvider](#sdk-configprovider)
  * [SDK extension components](#sdk-extension-components)
    + [ComponentProvider](#componentprovider)
      - [ComponentsProvider operations](#componentsprovider-operations)
        * [Create Plugin](#create-plugin)
  * [File config operations](#file-config-operations)
    + [Parse](#parse)
    + [Create](#create)
    + [Register ComponentProvider](#register-componentprovider)
- [Examples](#examples)
  * [Via File Configuration API](#via-file-configuration-api)
  * [Via OTEL_EXPERIMENTAL_CONFIG_FILE](#via-otel_experimental_config_file)
- [References](#references)

<!-- tocstop -->

## Overview

File configuration provides a mechanism for configuring OpenTelemetry which is
more expressive and full-featured than
the [environment variable](sdk-environment-variables.md) based scheme, and
language agnostic in a way not possible
with [programmatic configuration](sdk-configuration.md#programmatic).

File configuration consists of the following main components:

* [Configuration model](#configuration-model) defines the data model for
  configuration.
* [Configuration file](#configuration-file) defines how the configuration model
  is represented in files.
* [Instrumentation configuration API](#instrumentation-configuration-api) allows
  instrumentation libraries to read relevant configuration options during
  initialization.
* [Configuration SDK](#configuration-sdk) defines SDK capabilities around file
  configuration, including an In-Memory configuration model, support for
  referencing custom extension plugin interfaces in configuration files, and
  operations to parse and interpret configuration files.
* [Examples](#examples) end to end examples demonstrating file configuration
  concepts.

## Configuration model

The configuration model is defined
in [opentelemetry-configuration](https://github.com/open-telemetry/opentelemetry-configuration)
using the [JSON Schema](https://json-schema.org/).

### Stability definition

TODO: define stability guarantees and backwards compatibility

## Configuration file

A configuration file is a serialized file-based representation of
the [Configuration Model](#configuration-model).

Configuration files SHOULD use one the following serialization formats:

* [YAML file format](#yaml-file-format)

### YAML file format

[YAML](https://yaml.org/spec/1.2.2/) configuration files SHOULD follow YAML spec
revision >= 1.2.

YAML configuration files SHOULD be parsed using [v1.2 YAML core schema](https://yaml.org/spec/1.2.2/#103-core-schema).

YAML configuration files MUST use file extensions `.yaml` or `.yml`.

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
example, see references to `INVALID_MAP_VALUE` environment variable below.

It MUST NOT be possible to inject environment variable by environment variables.
For example, see references to `DO_NOT_REPLACE_ME` environment variable below.

For example, consider the following environment variables,
and [YAML](#yaml-file-format) configuration file:

```shell
export STRING_VALUE="value"
export BOOL_VALUE="true"
export INT_VALUE="1"
export FLOAT_VALUE="1.1"
export HEX_VALUE="0xdeadbeef"                         # A valid integer value written in hexadecimal
export INVALID_MAP_VALUE="value\nkey:value"           # An invalid attempt to inject a map key into the YAML
export DO_NOT_REPLACE_ME="Never use this value"       # An unused environment variable
export REPLACE_ME='${DO_NOT_REPLACE_ME}'              # A valid replacement text, used verbatim, not replaced with "Never use this value"
```

```yaml
string_key: ${STRING_VALUE}                           # Valid reference to STRING_VALUE
env_string_key: ${env:STRING_VALUE}                   # Valid reference to STRING_VALUE
other_string_key: "${STRING_VALUE}"                   # Valid reference to STRING_VALUE inside double quotes
another_string_key: "${BOOL_VALUE}"                   # Valid reference to BOOL_VALUE inside double quotes
string_key_with_quoted_hex_value: "${HEX_VALUE}"      # Valid reference to HEX_VALUE inside double quotes
yet_another_string_key: ${INVALID_MAP_VALUE}          # Valid reference to INVALID_MAP_VALUE, but YAML structure from INVALID_MAP_VALUE MUST NOT be injected
bool_key: ${BOOL_VALUE}                               # Valid reference to BOOL_VALUE
int_key: ${INT_VALUE}                                 # Valid reference to INT_VALUE
int_key_with_unquoted_hex_value: ${HEX_VALUE}         # Valid reference to HEX_VALUE without quotes
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
string_key: value                              # Interpreted as type string, tag URI tag:yaml.org,2002:str
env_string_key: value                          # Interpreted as type string, tag URI tag:yaml.org,2002:str
other_string_key: "value"                      # Interpreted as type string, tag URI tag:yaml.org,2002:str
another_string_key: "true"                     # Interpreted as type string, tag URI tag:yaml.org,2002:str
string_key_with_quoted_hex_value: "0xdeadbeef" # Interpreted as type string, tag URI tag:yaml.org,2002:str
yet_another_string_key: "value\nkey:value"     # Interpreted as type string, tag URI tag:yaml.org,2002:str
bool_key: true                                 # Interpreted as type bool, tag URI tag:yaml.org,2002:bool
int_key: 1                                     # Interpreted as type int, tag URI tag:yaml.org,2002:int
int_key_with_unquoted_hex_value: 3735928559    # Interpreted as type int, tag URI tag:yaml.org,2002:int
float_key: 1.1                                 # Interpreted as type float, tag URI tag:yaml.org,2002:float
combo_string_key: foo value 1.1                # Interpreted as type string, tag URI tag:yaml.org,2002:str
string_key_with_default: fallback              # Interpreted as type string, tag URI tag:yaml.org,2002:str
undefined_key:                                 # Interpreted as type null, tag URI tag:yaml.org,2002:null
${STRING_VALUE}: value                         # Interpreted as type string, tag URI tag:yaml.org,2002:str
recursive_key: ${DO_NOT_REPLACE_ME}            # Interpreted as type string, tag URI tag:yaml.org,2002:str
```

## Instrumentation configuration API

The instrumentation configuration API (referred to as the API)
allows [instrumentation libraries](../glossary.md#instrumentation-library) to
participate in file configuration by reading relevant configuration options
during initialization. It consists of the following main components:

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

`ConfigProperties` is a programmatic representation of a file configuration
mapping node (i.e. a YAML mapping node).

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

## Configuration SDK

The configuration SDK (referred to as the SDK) is an implementation
of [Instrumenation Config API](#instrumentation-configuration-api) and other
user facing file configuration capabilities. It consists of the following main
components:

* [In-Memory configuration model](#in-memory-configuration-model) is an
  in-memory representation of the configuration model.
* [SDK ConfigProvider](#sdk-configprovider) defines the SDK implementation
  of `ConfigProvider`.
* [SDK extension components](#sdk-extension-components) defines how users and
  libraries extend file configuration with custom SDK extension plugin
  interfaces (exporters, processors, etc).
* [File config operations](#file-config-operations) defines user APIs to parse
  configuration files and produce SDK components from their contents.

### In-Memory configuration model

SDKs SHOULD provide an in-memory representation of
the [Configuration Model](#configuration-model).
Whereas [`ConfigProperties`](#configproperties) is a schemaless representation
of any mapping node from a configuration file, the in-memory configuration model
SHOULD reflect the schema of the configuration model.

SDKs are encouraged to provide this in-memory representation in a manner that is
idiomatic for their language. If an SDK needs to expose a class or interface,
the name `Configuration` is RECOMMENDED.

### SDK ConfigProvider

The SDK implementation of [`ConfigProvider`](#configprovider) MUST be created
using a [`ConfigProperties`](#configproperties) representing
the [`.instrumentation`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L438-L439)
mapping node from a configuration file.

### SDK extension components

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
a [`ComponentProvider`](#componentprovider) must
be [registered](#register-componentprovider) with `type: SpanExporter`,
and `name: my-exporter`. When [parse](#parse) is called, the implementation will
encounter `my-exporter` and translate the corresponding configuration to an
equivalent [`ConfigProperties`](#configproperties) representation (
i.e. `properties: {config-parameter: value}`). When [create](#create) is called,
the implementation will encounter `my-exporter` and
invoke [create plugin](#create-plugin) on the registered `ComponentProvider`with
the `ConfigProperties` determined during `parse`.

Given the inherent differences across languages, the details of extension
component mechanisms are likely to vary to a greater degree than is the case
with other APIs defined by OpenTelemetry. This is to be expected and is
acceptable so long as the implementation results in the defined behaviors.

#### ComponentProvider

A `ComponentProvider` is responsible for interpreting configuration and returning
an implementation of a particular type of SDK extension plugin interface.

`ComponentProvider`s are registered with an SDK implementation of configuration
via [register](#register-componentprovider). This MAY be done automatically or
require manual intervention by the user based on what is possible and idiomatic
in the language ecosystem. For example in Java, `ComponentProvider`s might be
registered automatically using
the [service provider interface (SPI)](https://docs.oracle.com/javase/tutorial/sound/SPI-intro.html)
mechanism.

See [create](#create), which details `ComponentProvider` usage in file
configuration interpretation.

##### ComponentsProvider operations

The `ComponentsProvider` MUST provide the following functions:

* [Create Plugin](#create-plugin)

###### Create Plugin

Interpret configuration to create a instance of a SDK extension plugin
interface.

**Parameters:**

* `properties` - The [`ConfigProperties`](#configproperties) representing the
  configuration specified for the component in
  the [configuration file](#configuration-file).

**Returns:** A configured SDK extension plugin interface implementation.

The plugin interface MAY have properties which are optional or required, and
have specific requirements around type or format. The set of properties a
`ComponentProvider` accepts, along with their requirement level and expected
type, comprise a configuration schema. A `ComponentProvider` SHOULD document its
configuration schema.

When Create Plugin is invoked, the `ComponentProvider` interprets `properties`
and attempts to extract data according to its configuration schema. If this
fails (e.g. a required property is not present, a type is mismatches, etc.),
Create Plugin SHOULD return an error.

### File config operations

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
* `ConfigProvider`

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
of the [`ComponentProvider`](#componentprovider) of the corresponding `type`
and `name` used to [register](#register-componentprovider), including the
configuration `properties` as an argument. If no `ComponentProvider` is
registered with the `type` and `name`, Create SHOULD return an error.
If [Create Plugin](#create-plugin) returns an error, Create SHOULD propagate the
error.

This SHOULD return an error if it encounters an error in `configuration` (i.e.
fail fast) in accordance with
initialization [error handling principles](../error-handling.md#basic-error-handling-principles).

TODO: define behavior if some portion of configuration model is not supported

#### Register ComponentProvider

The SDK MUST provide a mechanism to
register [`ComponentProvider`](#componentprovider).

**Parameters:**

* `component_provider` - The `ComponentProvider`.
* `type` - The type of plugin interface it provides (e.g. SpanExporter, Sampler,
  etc).
* `name` - The name used to identify the type of component. This is used
  in [configuration files](#configuration-file) to specify that the
  corresponding `component_provider` is to provide the component.

The `type` and `name` comprise a unique key. Register MUST return an error if it
is called multiple times with the same `type` and `name` combination.

## Examples

### Via File Configuration API

The file configuration [Parse](#parse) and [Create](#create) operations along
with the [Configuration Model](#configuration-model) can be combined in a
variety of ways to achieve simple or complex configuration goals.

For example, a simple case would consist of calling `Parse` with a configuration
file, and passing the result to `Create` to obtain configured SDK components:

```java
OpenTelemetry openTelemetry = OpenTelemetry.noop();
try {
    // Parse configuration file to configuration model
    OpenTelemetryConfiguration configurationModel = FileConfiguration.parse(new File("/app/sdk-config.yaml"));
    // Create SDK components from configuration model
    openTelemetry = FileConfiguration.create(configurationModel);
} catch (Throwable e) {
    log.error("Error initializing SDK from configuration file", e);    
}

// Access SDK components and install instrumentation
TracerProvider tracerProvider = openTelemetry.getTracerProvider();
MeterProvider meterProvider = openTelemetry.getMeterProvider();
LoggerProvider loggerProvider = openTelemetry.getLogsBridge();
ContextPropagators propagators = openTelemetry.getPropagators();
ConfigProvider configProvider = openTelemetry.getConfigProvider();
```

A more complex case might consist of parsing multiple configuration files from
different sources, merging them using custom logic, and creating SDK components
from the merged configuration model:

```java
OpenTelemetry openTelemetry = OpenTelemetry.noop();
try {
    // Parse local and remote configuration files to configuration models
    OpenTelemetryConfiguration localConfigurationModel = FileConfiguration.parse(new File("/app/sdk-config.yaml"));
    OpenTelemetryConfiguration remoteConfigurationModel = FileConfiguration.parse(getRemoteConfiguration("http://example-host/config/my-application"));
    
    // Merge the configuration models using custom logic
    OpenTelemetryConfiguration resolvedConfigurationModel = merge(localConfigurationModel, remoteConfigurationModel);
    
    // Create SDK components from resolved configuration model
    openTelemetry = FileConfiguration.create(resolvedConfigurationModel);
} catch (Throwable e) {
    log.error("Error initializing SDK from configuration file", e);    
}

// Access SDK components and install instrumentation
TracerProvider tracerProvider = openTelemetry.getTracerProvider();
MeterProvider meterProvider = openTelemetry.getMeterProvider();
LoggerProvider loggerProvider = openTelemetry.getLogsBridge();
ContextPropagators propagators = openTelemetry.getPropagators();
ConfigProvider configProvider = openTelemetry.getConfigProvider();
```

### Via OTEL_EXPERIMENTAL_CONFIG_FILE

If an SDK
supports [OTEL_EXPERIMENTAL_CONFIG_FILE](./sdk-environment-variables.md#file-configuration),
then setting `OTEL_EXPERIMENTAL_CONFIG_FILE` provides a simple way to obtain an
SDK initialized from the specified config file. The pattern for accessing the
configured SDK components and installing into instrumentation will vary by
language. For example, the usage in Java might resemble:

```shell
# Set the required env var to the location of the configuration file
export OTEL_EXPERIMENTAL_CONFIG_FILE="/app/sdk-config.yaml"
```

```java
// Initialize SDK using autoconfigure model, which recognizes that OTEL_EXPERIMENTAL_CONFIG_FILE is set and configures the SDK accordingly
OpenTelemetry openTelemetry = AutoConfiguredOpenTelemetrySdk.initialize().getOpenTelemetrySdk();

// Access SDK components and install instrumentation
TracerProvider tracerProvider = openTelemetry.getTracerProvider();
MeterProvider meterProvider = openTelemetry.getMeterProvider();
LoggerProvider loggerProvider = openTelemetry.getLogsBridge();
ContextPropagators propagators = openTelemetry.getPropagators();
ConfigProvider configProvider = openTelemetry.getConfigProvider();
```

If using auto-instrumentation, this initialization flow might occur
automatically.

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
