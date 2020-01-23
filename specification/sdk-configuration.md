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
All default SDK implementations MUST provide a programmatic configuration
mechanism, in the language of the SDK itself. All other mechanisms SHOULD
be able to be built on top of this mechanism, if at all possible.

### Other Mechanisms
Additional configuration mechanisms SHOULD be provided in whatever
language/format/style is idiomatic for the language of the SDK. The
default SDK should be shipped with as many as these as deemed appropriate
for the language community in question.

## Details (needs a better title)

### General

### Tracing
TODO: link to the tracing configuration options

### Metrics
TODO: link to the metrics configuration options
