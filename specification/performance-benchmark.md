# Performance Benchmark of OpenTelemetry API

This document describes common performance benchmark guidelines for
OpenTelemetry API implementation in language libraries.

**Status:** Draft

## Events Throughput

### Create Span

Number of spans which could be created in 1 second per logical core and over all
logical cores.

## Instrumentation Cost

### CPU Usage

With given number of events throughput specified by user, e.g. 1000 spans per
second, measure and report the CPU usage of SDK. As the benchmark doesn't
contain user processing logic, the total CPU consumption of benchmark program
could be used to approximate SDK CPU comsumption.

### Memory Usage

Measure dynamic memory comsumption, e.g. heap, for above scenario as memory cost
at given event throughput.

## Latency

### OTLP Exporting Latency

Measure and report the latency of sending events to a local OTLP collector via
OTLP exporter.

## Report

### Report Format

All the numbers above should be measured by multiple times and report below
aggregated metrics:

- Mean   : Arithmetic mean of all measurements.
- StdDev : Standard deviation of all measurements.