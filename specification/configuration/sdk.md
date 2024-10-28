# Configuration SDK

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
  * [In-Memory configuration model](#in-memory-configuration-model)
  * [ConfigProvider](#configprovider)
  * [SDK extension components](#sdk-extension-components)
    + [ComponentProvider](#componentprovider)
      - [ComponentsProvider operations](#componentsprovider-operations)
        * [Create Plugin](#create-plugin)
  * [Config operations](#config-operations)
    + [Parse](#parse)
    + [Create](#create)
    + [Register ComponentProvider](#register-componentprovider)
  * [Examples](#examples)
    + [Via configuration API](#via-configuration-api)
    + [Via OTEL_EXPERIMENTAL_CONFIG_FILE](#via-otel_experimental_config_file)
  * [References](#references)

<!-- tocstop -->

## Overview

The configuration SDK is part of
the [declarative configuration interface](./README.md#declarative-configuration).

The SDK is an implementation
of [Instrumenation Config API](./api.md) and other
user facing declarative configuration capabilities. It consists of the following main
components:

* [In-Memory configuration model](#in-memory-configuration-model) is an
  in-memory representation of the [configuration model](./data-model.md).
* [ConfigProvider](#configprovider) defines the SDK implementation
  of the [ConfigProvider API](./api.md#configprovider).
* [SDK extension components](#sdk-extension-components) defines how users and
  libraries extend file configuration with custom SDK extension plugin
  interfaces (exporters, processors, etc).
* [Config operations](#config-operations) defines user APIs to parse
  configuration files and produce SDK components from their contents.

### In-Memory configuration model

SDKs SHOULD provide an in-memory representation of
the [configuration model](./data-model.md).
Whereas [`ConfigProperties`](./api.md#configproperties) is a schemaless
representation of any mapping node, the in-memory configuration model SHOULD
reflect the schema of the configuration model.

SDKs are encouraged to provide this in-memory representation in a manner that is
idiomatic for their language. If an SDK needs to expose a class or interface,
the name `Configuration` is RECOMMENDED.

### ConfigProvider

The SDK implementation of [`ConfigProvider`](./api.md#configprovider) MUST be
created using a [`ConfigProperties`](./api.md#configproperties) representing
the [`.instrumentation`](https://github.com/open-telemetry/opentelemetry-configuration/blob/670901762dd5cce1eecee423b8660e69f71ef4be/examples/kitchen-sink.yaml#L438-L439)
mapping node of the [configuration model](./data-model.md).

### SDK extension components

The SDK supports a variety of
extension [plugin interfaces](../glossary.md#sdk-plugins), allowing users and
libraries to customize behaviors including the sampling, processing, and
exporting of data. In general, the [configuration data model](./data-model.md)
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
equivalent [`ConfigProperties`](./api.md#configproperties) representation (
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

See [create](#create), which details `ComponentProvider` usage in
configuration model interpretation.

##### ComponentsProvider operations

The `ComponentsProvider` MUST provide the following functions:

* [Create Plugin](#create-plugin)

###### Create Plugin

Interpret configuration to create a instance of a SDK extension plugin
interface.

**Parameters:**

* `properties` - The [`ConfigProperties`](./api.md#configproperties) representing the
  configuration specified for the component in
  the [configuration model](#in-memory-configuration-model).

**Returns:** A configured SDK extension plugin interface implementation.

The plugin interface MAY have properties which are optional or required, and
have specific requirements around type or format. The set of properties a
`ComponentProvider` accepts, along with their requirement level and expected
type, comprise a configuration schema. A `ComponentProvider` SHOULD document its
configuration schema and include examples.

When Create Plugin is invoked, the `ComponentProvider` interprets `properties`
and attempts to extract data according to its configuration schema. If this
fails (e.g. a required property is not present, a type is mismatches, etc.),
Create Plugin SHOULD return an error.

### Config operations

SDK implementations of configuration MUST provide the following operations.

Note: Because these operations are stateless pure functions, they are not
defined as part of any type, class, interface, etc. SDKs may organize them in
whatever manner is idiomatic for the language.

TODO: Add operation to update SDK components with new configuration for usage
with OpAmp

#### Parse

Parse and validate a [configuration file](./data-model.md#file-based-configuration-model).

**Parameters:**

* `file`: The [configuration file](./data-model.md#file-based-configuration-model) to parse. This MAY be a
  file path, or language specific file data structure, or a stream of a file's content.
* `file_format`: The file format of the `file` (e.g. [yaml](./data-model.md#yaml-file-format)).
  Implementations MAY accept a `file_format` parameter, or infer it from
  the `file` extension, or include file format specific overloads of `parse`,
  e.g. `parseYaml(file)`. If `parse` accepts `file_format`, the API SHOULD be
  structured so a user is obligated to provide it.

**Returns:** [configuration model](#in-memory-configuration-model)

Parse MUST perform [environment variable substitution](./data-model.md#environment-variable-substitution).

Parse MUST differentiate between properties that are missing and properties that
are present but null. For example, consider the following snippet,
noting `.meter_provider.views[0].stream.drop` is present but null:

```yaml
meter_provider:
  views:
    - selector:
        name: some.metric.name
      stream:
        aggregation:
          drop:
```

As a result, the view stream should be configured with the `drop` aggregation.
Note that some aggregations have additional arguments, but `drop` does not. The
user MUST not be required to specify an empty object (i.e. `drop: {}`) in these
cases.

When encountering a reference to
a [SDK extension component](#sdk-extension-components) which is not built in to
the SDK, Parse MUST resolve corresponding configuration to a
generic [ConfigProperties](./api.md#configproperties) representation as described
in [Create Plugin](#create-plugin).

Parse SHOULD return an error if:

* The `file` doesn't exist or is invalid
* The parsed `file` content does not conform to
  the [configuration model](data-model.md) schema.

#### Create

Interpret configuration model and return SDK components.

**Parameters:**

* `configuration` - An [in-memory configuration model](#in-memory-configuration-model).

**Returns:** Top level SDK components:

* [TracerProvider](../trace/sdk.md#tracer-provider)
* [MeterProvider](../metrics/sdk.md#meterprovider)
* [LoggerProvider](../logs/sdk.md#loggerprovider)
* [Propagators](../context/api-propagators.md#composite-propagator)
* [ConfigProvider](#configprovider)

The multiple responses MAY be returned using a tuple, or some other data
structure encapsulating the components.

If a property has a default value defined (i.e. is _not_ required) and is
missing or present but null, Create MUST ensure the SDK component is configured
with the default value. If a property is required and is missing or present but
null, Create SHOULD return an error. For example, if configuring
the [span batching processor](../trace/sdk.md#batching-processor) and
the `scheduleDelayMillis` property is missing or present but null, the component
is configured with the default value of `5000`. However, if the `exporter`
property is missing or present but null, Create fails fast since there is no
default value for `exporter`.

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
register [`ComponentProvider`](#componentprovider). The mechanism MAY be
language-specific and automatic. For example, a java implementation might use
the [service provider interface](https://docs.oracle.com/javase/tutorial/sound/SPI-intro.html)
mechanism to register implementations of a particular interface
as `ComponentProvider`s.

**Parameters:**

* `component_provider` - The `ComponentProvider`.
* `type` - The type of plugin interface it provides (e.g. SpanExporter, Sampler,
  etc).
* `name` - The name used to identify the type of component. This is used
  in [configuration model](./data-model.md) to specify that the
  corresponding `component_provider` is to provide the component.

The `type` and `name` comprise a unique key. Register MUST return an error if it
is called multiple times with the same `type` and `name` combination.

### Examples

#### Via configuration API

The configuration [Parse](#parse) and [Create](#create) operations along
with the [Configuration Model](./data-model.md) can be combined in a
variety of ways to achieve simple or complex configuration goals.

For example, a simple case would consist of calling `Parse` with a configuration
file, and passing the result to `Create` to obtain configured SDK components:

```java
OpenTelemetry openTelemetry = OpenTelemetry.noop();
try {
    // Parse configuration file to configuration model
    OpenTelemetryConfiguration configurationModel = parse(new File("/app/sdk-config.yaml"));
    // Create SDK components from configuration model
    openTelemetry = create(configurationModel);
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
    OpenTelemetryConfiguration localConfigurationModel = parse(new File("/app/sdk-config.yaml"));
    OpenTelemetryConfiguration remoteConfigurationModel = parse(getRemoteConfiguration("http://example-host/config/my-application"));
    
    // Merge the configuration models using custom logic
    OpenTelemetryConfiguration resolvedConfigurationModel = merge(localConfigurationModel, remoteConfigurationModel);
    
    // Create SDK components from resolved configuration model
    openTelemetry = create(resolvedConfigurationModel);
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

#### Via OTEL_EXPERIMENTAL_CONFIG_FILE

Setting
the [OTEL_EXPERIMENTAL_CONFIG_FILE](./sdk-environment-variables.md#declarative-configuration)
environment variable (for languages that support it) provides users a convenient
way to initialize OpenTelemetry components without needing to learn
language-specific configuration details or use a large number of environment
variables. The pattern for accessing the configured components and installing
into instrumentation will vary by language. For example, the usage in Java might
resemble:

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

### References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
