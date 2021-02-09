# YAML Model for Semantic Conventions

The YAML descriptions of semantic convention contained in this directory are intended to
be used by the various OpenTelemetry language implementations to aid in automatic
generation of semantics-related code.

## Generation

These YAML files are used by the make target `table-generation` to generate consistently
formattted Markdown tables for all semantic conventions in the specification. Run it from the root of this repository using the command

```
make table-generation
```

For more information, see the [semantic convention generator](https://github.com/open-telemetry/build-tools/tree/main/semantic-conventions)
in the OpenTelemetry build tools repository.
Using this build tool, it is also possible to generate code for use in OpenTelemetry
language projects.

See also:

* [Markdown Tables](https://github.com/open-telemetry/build-tools/tree/main/semantic-conventions#markdown-tables)
* [Code Generator](https://github.com/open-telemetry/build-tools/tree/main/semantic-conventions#code-generator)

## Description of the model

The fields and their expected values are presented in [syntax.md](./syntax.md).
