# Performance Benchmark of OpenTelemetry API

This document describes common performance benchmark guidelines for
OpenTelemetry API implementation in language libraries.

**Status:** Draft

## Benchmark Configuration

### Span Configuration

Spans for the tests in this spec should have empty resource, no parent `Span` and
`SpanContext`. The `AlwaysOn` sampler should be enabled.

## Throughput

### Create Spans

Number of spans which could be created and exported via OTLP exporter in 1
second per logical core and average number over all logical cores, with each
span containing 10 attributes, and each attribute containing two 20 characters
strings, one as attribute name the other as value.

## Instrumentation Cost

### CPU Usage

With given number of span throughput specified by user, or 10,000 spans per
second as default if user does not input the number, measure and report the CPU
usage for SDK with both simple and batching span processors together with OTLP
exporter. The benchmark should create an OTLP receiver which listens on the
exporting target in the same process, responds with success immediately and
drops the data, so it does not incur significant CPU overhead on the measured
result. Because the benchmark doesn't include user processing logic, the total
CPU consumption of benchmark program could be considered as approximation of
SDK's CPU consumption.  
The total running time for one test iteration is suggested to be 15 seconds. The
average and peak CPU usage should be reported.  

### Memory Usage

Measure dynamic memory consumption, e.g. heap, for the same scenario as above
CPU Usage section with 15 seconds duration.

## Report

### Report Format

All the numbers above should be measured by multiple times (suggest 10 times at
least) and reported with below statistic values:  

- Mean   : Arithmetic mean of all measurements.
- StdDev : Standard deviation of all measurements.
