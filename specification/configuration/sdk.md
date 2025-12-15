<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
weight: 3
--->

# Configuration SDK

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
  * [In-Memory configuration model](#in-memory-configuration-model)
  * [ConfigProvider](#configprovider)
  * [SDK extension components](#sdk-extension-components)
    + [ComponentProvider](#componentprovider)
      - [Supported SDK extension plugins](#supported-sdk-extension-plugins)
      - [ComponentsProvider operations](#componentsprovider-operations)
        * [Create Plugin](#create-plugin)
  * [SDK operations](#sdk-operations)
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
of [Instrumentation Config API](./api.md) and other
user facing declarative configuration capabilities. It consists of the following main
components:

* [In-Memory configuration model](#in-memory-configuration-model) is an
  in-memory representation of the [configuration model](./data-model.md).
* [ConfigProvider](#configprovider) defines the SDK implementation
  of the [ConfigProvider API](./api.md#configprovider).
* [SDK extension components](#sdk-extension-components) defines how users and
  libraries extend file configuration with custom SDK extension plugin
  interfaces (exporters, processors, etc).
* [SDK operations](#sdk-operations) defines user APIs to parse
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

##### Supported SDK extension plugins

The [configuration data model](./data-model.md) SHOULD support configuration of
all SDK extension plugin interfaces. SDKs SHOULD
support [registration](#register-componentprovider) of custom implementations of
SDK extension plugin interfaces via the `ComponentProvider` mechanism.

The following table lists the current status of all SDK extension plugin
interfaces in the configuration data model:

| SDK extension plugin interface                                                              | Status                                                                             |
|---------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| [resource detector](../resource/sdk.md#detecting-resource-information-from-the-environment) | +                                                                                  |
| [text map propagator](../context/api-propagators.md#textmap-propagator)                     | +                                                                                  |
| [span exporter](../trace/sdk.md#span-exporter)                                              | +                                                                                  |
| [span processor](../trace/sdk.md#span-processor)                                            | +                                                                                  |
| [sampler](../trace/sdk.md#sampler)                                                          | +                                                                                  |
| [id generator](../trace/sdk.md#id-generators)                                               | - [#70](https://github.com/open-telemetry/opentelemetry-configuration/issues/70)   |
| [pull metric reader](../metrics/sdk.md#metricreader)                                        | +                                                                                  |
| [push metric exporter](../metrics/sdk.md#metricexporter)                                    | +                                                                                  |
| [metric producer](../metrics/sdk.md#metricproducer)                                         | +                                                                                  |
| [exemplar reservoir](../metrics/sdk.md#exemplarreservoir)                                   | - [#189](https://github.com/open-telemetry/opentelemetry-configuration/issues/189) |
| [log record exporter](../logs/sdk.md#logrecordexporter)                                     | +                                                                                  |
| [log record processor](../logs/sdk.md#logrecordprocessor)                                   | +                                                                                  |

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

### SDK operations

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
  the [configuration model](data-model.md) schema. Note that this includes
  enforcing all constraints encoded into the schema (e.g. required properties
  are present, that properties adhere to specified types, etc.).

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

Create requirements around default and null behavior are described below. Note that
[`defaultBehavior` and `nullBehavior`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/CONTRIBUTING.md#json-schema-source-and-output)
are defined in the configuration data model.

* If a property is present and the value is null, Create MUST use the
  `nullBehavior`, or `defaultBehavior` if `nullBehavior` is not set.
* If a property is required, and not present, Create MUST return an error.

A few examples to illustrate:

* If configuring [`BatchSpanProcessor`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/schema-docs.md#batchspanprocessor-)
  and `schedule_delay` is not present or present but null, the component is
  configured according to the `defaultBehavior` of `5000`.
* If configuring [`SpanExporter`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/schema-docs.md#spanexporter)
  and `console` is present and null, the component is configured with a
  `console` exporter with default configuration since `console` is nullable.

The [configuration model](data-model.md) uses the JSON schema
[`description`](https://json-schema.org/understanding-json-schema/reference/annotations)
annotation to capture property semantics which cannot be encoded using standard
JSON schema keywords. Create SHOULD return an error if it encounters a value
which is invalid according to the property `description`. For example, if
configuring [`HttpTls`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/schema-docs.md#httptls-)
and `ca_file` is not an absolute file path as defined in the property
description, return an error.

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

SDK implementations MAY provide options to allow programmatic customization of
the components initialized by `Create`. This allows configuration of concepts which
are not yet or may never be representable in the configuration model. For example,
java OTLP exporters allow configuration of the [ExecutorService](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ExecutorService.html),
a niche but important option for applications which need strict control of thread pools.
This programmatic customization might take the form of passing an optional callback to
`Create`, invoked with each SDK subcomponent (or a subset of SDK component types) as
they are initialized. For example, consider the following snippet:

```yaml
file_format: 1.0
tracer_provider:
  processors:
    - batch:
        exporter:
          otlp_http:
```

The callback would be invoked with the SDK representation of an OTLP HTTP exporter, a
Batch SpanProcessor, and a Tracer Provider. This pattern provides the opportunity
to programmatically configure lower-level without needing to walk to a particular
component from the resolved top level SDK components.

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
* `type` - The type of plugin interface it provides.
* `name` - The name used to identify the type of component. This is used
  in [configuration model](./data-model.md) to specify that the
  corresponding `component_provider` is to provide the component.

The `type` and `name` comprise a unique key. Register MUST return an error if it
is called multiple times with the same `type` and `name` combination.

SDKs should represent `type` in a manner that is idiomatic for their language.
For example, a class literal, an enumeration, or similar.
See [supported SDK extension plugins](#sdk-extension-components) for the set of
supported `type` values.

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
