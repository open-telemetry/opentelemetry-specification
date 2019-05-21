# Metrics
Metrics are a data model for what stats exporters take as input.

Different exporters have different capabilities (e.g. which data types
are supported) and different constraints (e.g. which characters are allowed in
label keys). Metrics is intended to be a superset of what's possible, not a
lowest common denominator that's supported everywhere.

Because of this, Metrics puts minimal constraints on the data (e.g. which
characters are allowed in keys), and code dealing with Metrics should avoid
validation and sanitization of the Metrics data. Instead, pass the data to the
backend, rely on the backend to perform validation, and pass back any errors
from the backend.

The Metrics data model is defined as
[metrics.proto](https://github.com/census-instrumentation/opencensus-proto/blob/master/src/opencensus/proto/metrics/v1/metrics.proto),
but the proto is just to illustrate the concepts. OpenCensus implementations
don't have to use the actual proto, and can instead use a language-specific
in-memory data structure that captures what exporters need. This structure
should use the names and fields from the data model, for API consistency across
languages.
