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

The communication channel between OBI and the profiler is implemented via an eBPF map pinned at `/sys/fs/bpf/obi_ctx`.  

For both programs to access the map, the `/sys/fs/bpf` filesystem (bpffs) must be mounted and accessible.

### Data Model

As described in the [Profiles Data Model](./0239-profiles-data-model.md), the shared eBPF map uses a minimal structure to store correlation data:

- **Key:** `(u64)pid_tgid`
- **Value:**  

```c
struct trace_context {
    u8 trace_id[16];
    u8 span_id[8];
};
