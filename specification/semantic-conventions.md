# Semantic Conventions

**Status**: [Experimental](./document-status.md)

This document overviews OpenTelemetry semantic conventions
and implementation requirements from the OpenTelemetry collector
and the libraries.

Semantic conventions defined by OpenTelemetry:

* [Resource](./resource/semantic_conventions)
* [Metrics](./metrics/semantic_conventions)
* [Trace](./trace/semantic_conventions)

Both the collector and the libraries SHOULD autogenerate semantic
convention keys into constants (or language idomatic equivalent).
The [YAML](../semantic_conventions) files MUST be used as the 
source of truth for generation. Each language implementation SHOULD 
provide language-specific support to the
[code generator](https://github.com/open-telemetry/build-tools/tree/main/semantic-conventions#code-generator).
