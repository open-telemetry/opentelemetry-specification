# Default SDK Configuration

<details>

<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [Mechanisms](#mechanisms)
* [Details](#details)

</details>

## Abstract
The default Open Telemetry SDK is a complex piece of software. This document
outlines the mechanisms ("how") by which the SDK can be configured, and
the details ("what") about what is configurable.

## Mechanisms

### Programmatic
All default SDK implementations *MUST* provide a programmatic configuration
mechanism, in the language of the SDK itself. All other mechanisms *SHOULD*
be able to be built on top of this mechanism, if at all possible.

### Other Mechanisms
Additional configuration mechanisms SHOULD be provided in whatever
language/format/style is idiomatic for the language of the SDK. The
default SDK should be shipped with as many as these as deemed appropriate
for the language community in question.

## Details (needs a better title)

### General
#### Resources
See the [Resource](sdk-resource.md) specification.

#### Logging
Configuration of SDK logging should be done in a language idiomatic fashion.
This *MAY* be based only on configuration files (as opposed to the programmatic option)
if that is the most idiomatic way for the language-specific logging
system that the SDK uses.

### Tracing
See the [Tracing](sdk-tracing.md) specification for configurable options.

### Metrics
TODO: link to the metrics sdk specification when available.
