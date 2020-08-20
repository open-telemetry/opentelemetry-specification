# Metrics SDK

Note: This document assumes you are familiar with the (Metrics
API)[api.md] specification.

TODO: TOC

## Purpose

This document describes a model implementation of the OpenTelemetry
Metrics SDK.  The architectural details of the model SDK described
here are meant to offer guidance to implementors, not to mandate an
exact reproduction of the model architecture across languages.

## Expectations

The SDK implementors are expected to follow the best practices for the
language and runtime environment when implementing the OpenTelemetry
API.  Implementors SHOULD follow the general prescriptions on safety
and performance given in [OpenTelemetry library
guidelines](../library-guidelines.md).

## Export Pipeline Terminology

**Export Pipeline** is used to describe a whole assembly of SDK parts.
There are three major components of the Metrics SDK that data flows
through, in order:

1. **Accumulator**: Receives metric events from the API, computes one Accumulation per active Instrument and Label Set pair
2. **Processor**: Receives Accumulations from the Accumulator, transforms into ExportRecordSet
3. **Exporter**: Receives ExportRecordSet, transforms into some protocol and sends it somewhere.

These terms are defined in the Metrics API specification:

- **Metric Instrument**: the API object used by a developer for instrumentation
- **Synchronous Instrument**: a metric instrument called by the user with application context
- **Asynchronous Instrument**: a metric instrument invoked through a callback from the SDK
- **Metric Descriptor**: describes a metric instrument
- **Metric Event**: a single recorded or observed (Instrument, Label Set, Measurement)
- **Collection Interval**: the period between calls to Accumulator.Collect()
- **Label**: a key-value describing a property of the metric event
- **Label Set**: a set of key-values with unique keys
- **Measurement**: an integer or floating point number.

Defined in the [Resource SDK](../resource/sdk.md) specification:

- **Resource**: a set of key-values with unique keys describing the process.

These are the significant Key data types used in the model architecture

- **Aggregator**: aggregates one or more measurements in a useful way
- **AggregatorSelector**: chooses which Aggregator to assign to a metric instrument
- **Aggregation**: the result of aggregating one or more events by a specific aggregator
- **AggregationKind**: describes the kind of read API the Aggregation supports (e.g., Sum)
- **Accumulation**: consists of Instrument, Label Set, Resource, and Aggregator snapshot
- **ExportRecordSet**: a set of export records
- **Controller**: coordinates the Accumulator, Processor, and Exporter components in an export pipeline
- **Export Record**: consists of Instrument, Label Set, Resource, Timestamp(s), and Aggregation
- **ExportKind**: one of Delta, Cumulative, or Pass-Through
- **ExportKindSelector**: chooses which ExportKind to use for a metric instrument.

## Dataflow Diagram

![Metrics SDK Design Diagram](img/metrics-sdk.png)

## Accumulator Detail

## Controller Detail

## Basic Processor Detail

## Reducing Processor Detail

## Aggregator Implementations
