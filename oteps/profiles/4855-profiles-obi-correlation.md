# Correlating Profiles to OBI Traces

This OTEP introduces a standard communication channel and a specification for correlating profiles to [opentelemetry-ebpf-instrumentation (OBI)](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation) traces.

<!-- toc -->
* [Motivation](#motivation)
* [Design Notes](#design-notes)
  * [Communication Channel](#communication-channel)
  * [Data Model](#data-model)
<!-- toc -->

## Motivation

Currently, OBI traces and profiles operate independently, making it difficult to attribute profiling data to specific traces or spans. By establishing a standard kernel-resident communication channel, this OTEP enables:

- Correlating profiles with their corresponding traces or spans  
- End-to-end observability workflows without requiring application-level instrumentation  

## Design Notes

### Communication Channel

The communication channel between OBI and the profiler is implemented via an eBPF map pinned at `$PINPATH/otel_traces_ctx_v1`.

$PINPATH will default to bpffs (`/sys/fs/bpf`) but there must be options to specify an alternative location. If set, the user-configured

location in OBI must match the one set in the profiler.

On startup, both OBI and the profiler, will create the map and pin it if it doesn't exist. OBI will expose an helper function for the profiler

to do so.

### Data Model

As described in the [Profiles Data Model](./0239-profiles-data-model.md), the shared eBPF map uses a minimal structure to store correlation data.

#### eBPF Map Specification

```c
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, u64);
    __type(value, struct trace_context);
    __uint(max_entries, 1 << 14);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} otel_traces_ctx_v1 SEC(".maps");
```

- **Key:** `(u64)pid_tgid`
- **Value:**  

```c
struct trace_context {
    u8 trace_id[16];
    u8 span_id[8];
};
```
