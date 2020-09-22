# YAML Model for Semantic Conventions

The YAML descriptions of semantic convention contained in this directory are intended to
be used by the various language OpenTelemetry language implementations to aid in automatic
generation of semantics-related code.

## Generation

Using these YAML models, and the [semantic convention generator](https://github.com/open-telemetry/build-tools/tree/master/semantic-conventions)
found in the OpenTelemetry build tools repository, it is possible to generate
consistently-formatted Markdown tables for all of our semantic conventions,
and to generate code for use in OpenTelemetry language projects.

See also:
* [Markdown Tables](https://github.com/open-telemetry/build-tools/tree/master/semantic-conventions#markdown-tables)
* [Code Generator](https://github.com/open-telemetry/build-tools/tree/master/semantic-conventions#code-generator)

## Description of the model

The fields and their expected values are presented in [allowed_syntax.md](./allowed_syntax.md).

For a basic attribute description, refer to the [General Attributes example](./trace/general.yaml).
