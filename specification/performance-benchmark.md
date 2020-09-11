# Performance Benchmark of OpenTelemetry API

This document describes common performance benchmark guidelines for
OpenTelemetry API implementation in language libraries.

**Status:** Draft

## Throughput

### Create Spans

Number of spans which could be created and exported to OTLP exporter in 1 second
per logical core and average number over all logical cores, with each span
containing 10 attributes with random string data with 20 random characters.

## Instrumentation Cost

### CPU Usage

With given number of span throughput specified by user, or specify 10,000 spans
per second as default if user doesn't input the number, measure and report the
CPU usage for SDK with simple processor and OTLP exporter. The benchmark should
listen on the exporting target in-process and return success immediately, so it
does incur significant CPU overhead on the measurement. Because the benchmark
doesn't contain user processing logic, the total CPU consumption of benchmark
program could be used to approximate SDK CPU comsumption.  
The total running time should be more than 1 minute, and the average and peak
CPU usage should be reported.

### Memory Usage

Measure dynamic memory comsumption, e.g. heap, for the same scenario as [CPU
Usage](#CPU-Usage) section with 1 miniute during.

## Report

### Report Format

All the numbers above should be measured by multiple times (suggest 10 times at
least) and reported with below statistic values:

- Mean   : Arithmetic mean of all measurements.
- StdDev : Standard deviation of all measurements.