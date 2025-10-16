<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/profiles/_index.md
  to: profiles/README.md
--->

# OpenTelemetry Profiles

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Known values](#known-values)

<!-- tocstop -->

</details>

## Overview

Profiles are emerging as the fourth essential signal of observability, alongside
logs, metrics, and traces. They offer unparalleled insights into system and
application behavior, often uncovering performance bottlenecks overlooked by
other signals.

Profiles provide granular, time-based views of resource consumption and
code execution, encompassing:

* **Application-level profiling**: Reveals how software functions consume CPU,
memory, and other resources, highlighting slow or inefficient code.

* **System-level profiling**: Offers a holistic view of the infrastructure,
pinpointing issues in operating system calls, kernel operations, and I/O.

This performance picture can lead to:

* **Faster Root Cause Analysis**: Quickly identifies the exact cause of
performance degradation.
* **Proactive Optimization**: Identifies potential issues before user impact.
* **Improved Resource Utilization**: Optimizes infrastructure for cost savings
and efficiency.
* **Enhanced Developer Productivity**: Helps developers validate code performance
and prevent regressions.

In essence, while logs, metrics, and traces show "what" and "how much/where,"
profiles explain "why" and "how efficiently," making them indispensable in modern
observability.

## Known values

[OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
are vital for profiles to correlate with other OpenTelemetry signals, enabling
unified analysis of traces, metrics, logs, and profiling data for a holistic
system understanding.

To enhance the compatibility of OpenTelemetry Profiles with existing profiling
tools, known values are utilized.

| Profile field | Known values |
| -------------- | ------------ |
  | original_payload_format  | [pprof](https://github.com/google/pprof/tree/main/proto), [jfr](https://en.wikipedia.org/wiki/JDK_Flight_Recorder) or [linux_perf](https://perfwiki.github.io/) |
