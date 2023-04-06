# Telemetry Stability

**Status**: [Experimental](document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Unstable Instrumentations](#unstable-instrumentations)
- [Stable Instrumentations](#stable-instrumentations)

<!-- tocstop -->

</details>

This section defines stability requirements for telemetry produced by
OpenTelemetry instrumentations.

All OpenTelemetry-authored instrumentations are labeled to be either `Unstable` or `Stable`
from the perspective of the telemetry they produce.

## Unstable Instrumentations

Unstable telemetry-producing instrumentations (unstable instrumentations for short) SHOULD
be clearly labeled so by any means the instrumentations authors consider idiomatic for
their language, e.g. via version numbers, artifact names, documentation, etc.

Unstable instrumentations provide no guarantees about the shape of
the telemetry they produce and how that shape changes over time, from version to version.
Span or metric names, attributes of any telemetry items may change without any
restrictions. The produced telemetry MAY specify a Schema URL if the telemetry data
conforms to a particular Schema.

Unstable instrumentations authored by OpenTelemetry MAY produce additional telemetry that
is not described by OpenTelemetry semantic conventions.

TODO: decide if it is necessary to indicate on the wire if the produced telemetry is
coming from an unstable instrumentation.

## Stable Instrumentations

Stable telemetry-producing instrumentations (stable instrumentations for short) SHOULD
be clearly labeled so by any means the instrumentations authors consider idiomatic for
their language, e.g. via version numbers, artifact names, documentation, etc.

Stable instrumentations authored by OpenTelemetry SHOULD include a schema URL indicating
which version of OpenTelemetry semantic conventions it conforms to.
Stable instrumentations SHOULD NOT produce telemetry that is not described by OpenTelemetry
semantic conventions.
