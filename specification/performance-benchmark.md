# Performance Benchmark of OpenTelemetry API

This document describes common performance benchmark requirements of OpenTelemetry API implementation in language libriries.

**Status:** Draft

## Events Throughput

### Number of events could be produced per second

For application uses with C/C++/Java library, it can produce 10K events without dropping any event.

### Number of outstanding events in local cache

If the remote end-point is unavailable for OpenTelemetry exporter, the library needs cache 1M events before dropping them.

## Instrumentation Cost

### CPU time

Under extreme workload, the library should not take more than 5% of total CPU time for event tracing, or it should not take more than 1 full logical core in multi-core system.

### Memory consumption

Under extreme workload, the peak working set increase caused by tracing should not exceed 100MB.

## Benchmark Report

The implementation language libraries need add the typical result of above benchmarks in the release page. 