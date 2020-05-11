# Vendors

<details>
<summary>Table of Contents</summary>

* [Abstract](#abstract)
* [What it means to support OpenTelemetry](#what-it-means-to-support-opentelemetry)

</details>

## Abstract

The OpenTelemetry project consists of both a
[specification](https://github.com/open-telemetry/opentelemetry-specification)
for the API, SDK, protocol and semantic conventions, as well as an
implementation of each for a number of languages. The default SDK implementation
is [highly configurable](sdk-configuration.md) and extendable, for example
through [Span Processors](trace/sdk.md#span-processor), to allow for additional
logic needed by particular vendors to be added without having to implement a
custom SDK. By not requiring a custom SDK means for most languages a user will
already find an implementation to use and if not they'll have a well documented
specification to follow for implementing in a new language.

The goal is for users to be able to easily switch between vendors while also
ensuring that any language with an OpenTelemetry SDK implementation is able to
work with any vendor who claims support for OpenTelemetry.

This document will explain what is required of a vendor to be considered to
"Support OpenTelemetry" or "Implements OpenTelemetry".

## What it means to support OpenTelemetry

## Tracing, Metrics and Logging Qualifications

A vendor can qualify their support for OpenTelemetry with the type of telemetry
they support. For example, a vendor that accepts the OpenTelemetry protocol
exports for metrics only will be listed as "Supports OpenTelemetry Metrics".

### Default SDK and the OpenTelemetry Protocol

"Supports OpenTelemetry" means the vendor must accept the output of the default
SDK through the OpenTelemetry Protocol either directly -- meaning the vendor's
endpoint/collector/agent implements the receiver end of the protocol -- or as an
exporter that works with the [OpenTelemetry
Collector](https://github.com/open-telemetry/opentelemetry-collector/).

### Custom SDK

A vendor with a custom SDK implementation will be listed as "Implements
OpenTelemetry". If the custom SDK is optional then the vendor can be listed as
"Supports OpenTelemetry".
