# Performance Benchmark of OpenTelemetry API

This document describes common performance benchmark guidelines on how to
measure and report the performance of OpenTelemetry SDKs.

**Status:** Draft

## Benchmark Configuration

### Span Configuration

- No parent `Span` and `SpanContext`.
- Associated to a [resource](overview.md#resources) with attributes
  `service.name`, `service.version`, `name`, and 10 characters string value for
  each attribute.
- The `AlwaysOn` sampler should be enabled.

## Throughput Measurement

### Create Spans

Number of spans which could be created and exported via OTLP exporter in 1
second per logical core and average number over all logical cores, with each
span containing 10 attributes, and each attribute containing two 20 characters
strings, one as attribute name the other as value.

## Instrumentation Cost

### CPU Usage Measurement

With given number of span throughput specified by user, or 10,000 spans per
second as default if user does not input the number, measure and report the CPU
usage for SDK with both simple and batching span processors together with OTLP
exporter. The benchmark should create an OTLP receiver which listens on the
exporting target in the same process or adopts existing OTLP exporter which runs
out of process, responds with success status immediately and drops the data. The
collector should not add significant CPU overhead to the measurement. Because
the benchmark does not include user processing logic, the total CPU consumption
of benchmark program could be considered as approximation of SDK's CPU
consumption.

The total running time for one test iteration is suggested to be at least 15
seconds. The average and peak CPU usage should be reported.

### Memory Usage Measurement

Measure dynamic memory consumption, e.g. heap, for the same scenario as above
CPU Usage section with 15 seconds duration.

## Report

### Report Format

All the numbers above should be measured multiple times (suggest 10 times at
least) and reported.