# OpenTelemetry Configuration

A new configuration interface is proposed here in the form of a configuration model, which can be expressed as a file, and validated through a published schema.

## Motivation

OpenTelemetry specifies code that can operate in a variety of ways based on the end-user’s desired mode of operation. This requires a configuration interface be provided to the user so they are able to communicate this information. Currently, OpenTelemetry specifies this interface in the form of the API exposed by the SDKs and environment variables. This environment variable interface is limited in the structure of information it can communicate and the primitives it can support.

### Environment Variable Interface Limitations

The environment variable interface suffers from the following identified limitations:

* **Flat**. Structured data is only allowed by using higher-level naming or data encoding schemes. Examples of configuration limited by lack of structured configuration include:
  * Configuring multiple span processors, periodic metric readers, or log record processors.
  * Configuring views.
  * Configuring arguments for parent based sampler (sampler parent is remote and sampled vs. not sampled, sampler when parent is local and sampled vs. not sampled).
* **Runtime dependent**. Different systems expose this interface differently (Linux, BSD, Windows). This usually means unique instructions are required to properly interact with the configuration interface on different systems.
* **Limited values**. Many systems only allow string values to be used, but OpenTelemetry specifies many configuration values other than this type. For example, OTEL_RESOURCE_ATTRIBUTES specifies a list of key value pairs to be used as resource attributes, but there is no way to specify array values, or indicate that the value should be interpreted as non-string type.
* **Limited validation**. Validation can only be performed by the receiver, there is no meta-configuration language to validate input.
* **Lacks versioning**. The lack of versioning support for environment variables prevents evolution over time.

## Explanation

Using a configuration model or configuration file, users can configure all options currently available via environment variables.

### Goals

* The configuration must be language implementation agnostic. It must not contain structure or statements that only can be interpreted in a subset of languages. This does not preclude the possibility that the configuration can have specific extensions included for a subset of languages, but it does mean that the configuration must be interpretable by all implementation languages.
* Broadly supported format. Ideally, the information encoded in the file can be decoded using native tools for all OpenTelemetry implementation languages. However, it must be possible for languages that do not natively support an encoding format to write their own parsers.
* The configuration format must support structured data. At the minimum arrays and associative arrays.
* The format must support at least boolean, string, double precision floating point (IEEE 754-1985), and signed 64 bit integer value types.
* Custom span processors, exporters, samplers, or other user defined extension components can be configured using this format.
* Configure SDK, but also configure instrumentation.
* Must offer stability guarantees while supporting evolution.
* The structure of the configuration can be validated via a schema.
* Support environment variable substitution to give users the option to avoid storing secrets in these files.

#### Out of scope

* Embedding additional configuration files within a configuration file through an expression. Additional configuration providers MAY choose to support this use-case in the future.

## Internal details

The schema for OpenTelemetry configuration is to be published in a repository to allow language implementations to leverage that definition to automatically generate code and/or validate end-user configuration. This will ensure that all implementations provide a consistent experience for any version of the schema they support. An example of such a proposed schema is available [here](./assets/0225-schema.json).

The working group proposes the use of [JSON Schema](https://json-schema.org/) as the language to define the schema. It provides:

* support for client-side validation
* code generation
* broad support across languages

In order to provide a minimal API surface area, implementations *MUST* support the following:

### Parse(file) -> config

An API called `Parse` receives a file object. The method loads the contents of the file, parses it, and validates that the configuration against the schema. At least one of JSON or YAML MUST be supported. If either format can be supported without additional dependencies, that format SHOULD be preferred. If neither or both formats are supported natively, YAML should be the preferred choice. If YAML is not supported due to dependency concerns, there MAY be a way for a user to explicitly enable it by installing their own dependency.

The method returns a [Configuration model](#configuration-model) that has been validated. This API *MAY* return an error or raise an exception, whichever is idiomatic to the implementation for the following reasons:

* file doesn't exist or is invalid
* configuration parsed is invalid according to schema

#### Python Parse example

```python

filepath = "./config.yaml"


try:
  cfg = opentelemetry.Parse(filepath)
except Exception as e:
  print(e)

filepath = "./config.json"

try:
  cfg = opentelemetry.Parse(filepath)
except Exception as e:
  raise e

```

#### Go Parse example

```go

filepath := "./config.yaml"
cfg, err := otel.Parse(filepath)
if err != nil {
  return err
}

filepath := "./config.json"
cfg, err := otel.Parse(filepath)
if err != nil {
  return err
}

```

Implementations *MUST* allow users to specify an environment variable to set the configuration file. This gives flexibility to end users of implementations that do not support command line arguments. The proposed name for this variable:

* `OTEL_CONFIG_FILE`

The format for the configuration file will be detected using the file extension of this variable.

### Configurer

`Configurer` interprets a [Configuration model](#configuration-model) and produces configured SDK components.

Multiple `Configurer`s can be [created](#createconfig---configurer) with different configurations. It is the caller's responsibility to ensure the [resulting SDK components](#get-tracerprovider-meterprovider-loggerprovider) are correctly wired into the application and instrumentation.

`Configurer` **MAY** be extended in the future with functionality to apply an updated configuration model to the resulting SDK components.

#### Create(config) -> Configurer

Create a `Configurer` from a [configuration model](#configuration-model).

#### Get TracerProvider, MeterProvider, LoggerProvider

Interpret the [configuration model](#configuration-model) and return SDK TracerProvider, MeterProvider, LoggerProvider which strictly reflect the configuration object's details and ignores the [opentelemetry environment variable configuration scheme](../specification/configuration/sdk-environment-variables.md).

### Configuration model

To allow SDKs and instrumentation libraries to accept configuration without having to implement the parsing logic, a `Configuration` model *MAY* be provided by implementations. This object:

* has already been parsed from a file or data structure
* is structurally valid (errors may yet occur when SDK or instrumentation interprets the object)

### Configuration file

The following demonstrates an example of a configuration file format (full example [here](./assets/0225-config.yaml)):

```yaml
# include version specification in configuration files to help with parsing and schema evolution.
file_format: 0.1
sdk:
  # Disable the SDK for all signals.
  #
  # Boolean value. If "true", a no-op SDK implementation will be used for all telemetry
  # signals. Any other value or absence of the variable will have no effect and the SDK
  # will remain enabled. This setting has no effect on propagators configured through
  # the OTEL_PROPAGATORS variable.
  #
  # Environment variable: OTEL_SDK_DISABLED
  disabled: false
  # Configure resource attributes and resource detection for all signals.
  resource:
    # Key-value pairs to be used as resource attributes.
    #
    # Environment variable: OTEL_RESOURCE_ATTRIBUTES
    attributes:
      # Sets the value of the `service.name` resource attribute
      #
      # Environment variable: OTEL_SERVICE_NAME
      service.name: !!str "unknown_service"
  # Configure context propagators. Each propagator has a name and args used to configure it. None of the propagators here have configurable options so args is not demonstrated.
  #
  # Environment variable: OTEL_PROPAGATORS
  propagators: [tracecontext, baggage]
  # Configure the tracer provider.
  tracer_provider:
    # Span exporters. Each exporter key refers to the type of the exporter. Values configure the exporter. Exporters must be associated with a span processor.
    exporters:
      # Configure the zipkin exporter.
      zipkin:
        # Sets the endpoint.
        #
        # Environment variable: OTEL_EXPORTER_ZIPKIN_ENDPOINT
        endpoint: http://localhost:9411/api/v2/spans
        # Sets the max time to wait for each export.
        #
        # Environment variable: OTEL_EXPORTER_ZIPKIN_TIMEOUT
        timeout: 10000
    # List of span processors. Each span processor has a name and args used to configure it.
    span_processors:
      # Add a batch span processor.
      #
      # Environment variable: OTEL_BSP_*, OTEL_TRACES_EXPORTER
      - name: batch
        # Configure the batch span processor.
        args:
          # Sets the delay interval between two consecutive exports.
          #
          # Environment variable: OTEL_BSP_SCHEDULE_DELAY
          schedule_delay: 5000
          # Sets the maximum allowed time to export data.
          #
          # Environment variable: OTEL_BSP_EXPORT_TIMEOUT
          export_timeout: 30000
          # Sets the maximum queue size.
          #
          # Environment variable: OTEL_BSP_MAX_QUEUE_SIZE
          max_queue_size: 2048
          # Sets the maximum batch size.
          #
          # Environment variable: OTEL_BSP_MAX_EXPORT_BATCH_SIZE
          max_export_batch_size: 512
          # Sets the exporter. Exporter must refer to a key in sdk.tracer_provider.exporters.
          #
          # Environment variable: OTEL_TRACES_EXPORTER
          exporter: zipkin
      # custom processor
      - name: my-custom-processor
        args:
          foo: bar
          baz: qux

  # Configure the meter provider.
  ...
```

Note that there is no consistent mapping between environment variable names and the keys in the configuration file.

### Environment variable substitution

Configuration files *MUST* support environment variable expansion. While this accommodates the scenario in which a configuration file needs to reference sensitive data and is not able to be stored securely, environment variable expansion is not limited to sensitive data.

As a starting point for development, the syntax for environment variable expansion *MAY* mirror the [collector](https://opentelemetry.io/docs/collector/configuration/#environment-variables).

For example, given an environment where `API_KEY=1234`, the configuration file contents:

```yaml
file_format: 0.1
sdk:
  tracer_provider:
    exporters:
      otlp:
        endpoint: https://example.host:4317/v1/traces
        headers:
          api-key: ${env:API_KEY}
```

Result in the following after substitution:

```yaml
file_format: 0.1
sdk:
  tracer_provider:
    exporters:
      otlp:
        endpoint: https://example.host:4317/v1/traces
        headers:
          api-key: 1234
```

Implementations *MUST* perform environment variable substitution before validating and parsing configuration file contents.

If a configuration file references an environment variable which is undefined, implementations *MUST* return an error or raise an exception.

#### Handling environment variable & file config overlap

The behaviour when both configuration file and environment variables are present will be decided in the final design. Here are four options that should be considered:

1. implementations ignore environment variables in preference of the configuration file
2. implementations give preference to the environment variables over the configuration file
3. an exception arises causing the application to fail to start
4. the behaviour is left unspecified

The support for environment variable substitution in the configuration file gives users a mechanism for migrating away from environment variables in favour of configuration files.

### Version guarantees & backwards compatibility

Each version of the configuration schema carries a major and minor version. Configurations specify the major and minor version they adhere to. Before reaching 1.0, each minor version change is equivalent to major version change. That is, there are no guarantees about compatibility and all changes are permitted. As of 1.0, we provide the following stability guarantees:

* For major version: No guarantees.
* For minor versions: TBD

Allowable changes:

* For major versions: All changes are permitted.
* For minor versions: TBD

SDKs validating configuration *MUST* fail when they encounter a configuration with an unsupported version. Generally, this means fail when encountering a major version which is not recognized. An SDK might choose to maintain a library of validators / parsers for each major version, and use the configuration version to select and use the correct instance. Differences in minor versions (except pre-1.0 minor versions) *MUST* be acceptable.

## Trade-offs and mitigations

### Additional method to configure OpenTelemetry

If the implementation suggested in this OTEP goes ahead, users will be presented with another mechanism for configuring OpenTelemetry. This may cause confusion for users who are new to the project. It may be possible to mitigate the confusion by providing users with best practices and documentation.

### Many ways to configure may result in users not knowing what is configured

As there are multiple mechanisms for configuration, it's possible that the active configuration isn't what was expected. This could happen today, and one way it could be mitigated would be by providing a mechanism to list the active OpenTelemetry configuration.

### Errors or difficulty in configuration files

Configuration files provide an opportunity for misconfiguration. A way to mitigate this would be to provide clear messaging and fail quickly when misconfiguration occurs.

## Prior art and alternatives

The working group looked to the OpenTelemetry Collector and OpenTelemetry Operator for inspiration and guidance.

### Alternative schema languages

In choosing to recommend JSON schema, the working group looked at the following options:

* [Cue](https://cuelang.org/) - A promising simpler language to define a schema, the working group decided against CUE because:
  * Tooling available for validating CUE files in languages outside of Go were limited.
  * Familiarity and learning curve would create problems for both users and contributors of OpenTelemetry.
* [Protobuf](https://protobuf.dev) - With protobuf already used heavily in OpenTelemetry, the format was worth investigating as an option to define the schema. The working group decided against Protobuf because:
  * Validation errors are the result of serialization errors which can be difficult to interpret.
  * Limitations in the schema definition language result in poor ergonomics if type safety is to be retained.

## Open questions

### How to handle no-code vs programmatic configuration?

How should the SDK be configured when both no-code configuration (either environment variable or file config) and programmatic configuration are present? NOTE: this question exists today with only the environment variable interface available.

* Solution 1: Make it clear that interpretation of the environment shouldn’t be built into components. Instead, SDKs should have a component that explicitly interprets the environment and returns a configured instance of the SDK. This is how the java SDK works today and it nicely separates concerns.

### What is the exact configuration file format to use?

Included in this OTEP is an example configuration file format.
This included format was settled on so the configuration file schemas being proposed here could all be evaluated as viable options.
It acted as proof-of-concept that *a* configuration file format existed that could describe needed OTel configuration and be described by a schema.
However, the configuration file format presented here is not meant as the final, nor optimal, design for use by OpenTelemetry.

What that final design will be is left to discussion when this OTEP is implemented in the OpenTelemetry specification.
It is explicitly something this OTEP is not intended to resolved.

The following are existing questions that will need to be resolved in the final design:

1. Should the trace exporter be at the same level as the span processors?
2. Should the sampler config be separate from the sampler?
3. Is the `sdk` key appropriate? Should alternate configuration live under its own key but the SDKs configuration be at the top level?
4. Should the `disabled` key be renamed as `enabled`?

This list is not intended as comprehensive.
There are likely more questions related to the final design that will be discussed when implemented in the OpenTelemetry specification.

## Future possibilities

### Additional configuration providers

Although the initial proposal for configuration supports only describes in-code and file representations, it's possible additional sources (remote, opamp, ...) for configuration will be desirable. The implementation of the configuration model and components should be extensible to allow for this.

### Integration with auto-instrumentation

The configuration model could be integrated to work with the existing auto-instrumentation tooling in each language implementation.

#### Java

The Java implementation provides a JAR that supports configuring various parameters via system properties. This implementation could leverage a configuration file by supporting its configuration a system property:

```bash
java -javaagent:path/to/opentelemetry-javaagent.jar \
     -Dotel.config.file=./config.yaml
     -jar myapp.jar
```

#### Python

The Python implementation has a command available that allows users to leverage auto-instrumentation. The `opentelemetry-instrument` command could use a `--config` flag to pass in a config file:

```bash
# install the instrumentation package
pip install opentelemetry-instrumentation
# use a --config parameter to pass in the configuration file
# NOTE: this parameter does not currently exist and would need to be added
opentelemetry-instrument --config ./config.yaml ./python/app.py
```

#### OpAmp

The configuration may be used in the future in conjunction with the OpAmp protocol to make remote configuration of SDKs available as a feature supported by OpenTelemetry.

## Related Spec issues address

* [https://github.com/open-telemetry/opentelemetry-specification/issues/1773](https://github.com/open-telemetry/opentelemetry-specification/issues/1773)
* [https://github.com/open-telemetry/opentelemetry-specification/issues/2857](https://github.com/open-telemetry/opentelemetry-specification/issues/2857)
* [https://github.com/open-telemetry/opentelemetry-specification/issues/2746](https://github.com/open-telemetry/opentelemetry-specification/issues/2746)
* [https://github.com/open-telemetry/opentelemetry-specification/issues/2860](https://github.com/open-telemetry/opentelemetry-specification/issues/2860)
