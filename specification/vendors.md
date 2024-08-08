# Vendors

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Abstract](#abstract)
- [Supports OpenTelemetry](#supports-opentelemetry)
- [Implements OpenTelemetry](#implements-opentelemetry)
- [Qualifications](#qualifications)

<!-- tocstop -->

</details>

## Abstract

The OpenTelemetry project consists of both a
[specification](https://github.com/open-telemetry/opentelemetry-specification)
for the API, SDK, protocol and semantic conventions, as well as an
implementation of each for a number of languages. The default SDK implementation
is [highly configurable](configuration/README.md) and extendable, for example
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

## Supports OpenTelemetry

"Supports OpenTelemetry" means the vendor must accept the output of the default
SDK through one of two mechanisms:

- By providing an exporter for the [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector/) and / or the OpenTelemetry SDKs
- By building a receiver for the [OpenTelemetry protocol](https://github.com/open-telemetry/opentelemetry-proto)

## Implements OpenTelemetry

A vendor with a custom SDK implementation will be listed as "Implements
OpenTelemetry". If the custom SDK is optional then the vendor can be listed as
"Supports OpenTelemetry".

## Qualifications

A vendor can qualify their support for OpenTelemetry with the type of telemetry
they support. For example, a vendor that accepts the OpenTelemetry protocol
exports for metrics only will be listed as "Supports OpenTelemetry Metrics" or
one that implements a custom SDK only for tracing will be listed as "Implements
OpenTelemetry Tracing".
