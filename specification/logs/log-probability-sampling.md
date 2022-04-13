# Log Probability Sampling

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
  * [References](#references)
  * [Definitions](#definitions)
- [Requirements](#requirements)
  * [Deterministic sampling source](#deterministic-sampling-source)

<!-- tocstop -->

</details>

## Overview

This specification defines how logs are sampled with OpenTelemetry.

Log sampling inherits from the logic defined in tracing sampling. By default, a log will use its trace ID to determine
whether it should be sampled, in a similar manner as [Trace state probability sampling](../trace/tracestate-probability-sampling.md).

In particular, log sampling borrows and reuses the notion of a hash seed that can be explicitly set on the sampler
to guarantee sampling is consistent with a series of collectors.

Trace ID sampling may be explicitly disabled.

Log sampling can consider another attribute as the source of its sampling. In that case, the attribute must be explicitly defined.
When the attribute is not set, the trace ID will be used instead if present.

If no explicit attribute is set or no attribute has been defined, and no trace ID is present or trace ID sampling is disabled,
the log is not considered as part of the sampling process and must be collected.

Additionally, the log record may define an attribute to be considered as a sampling priority in a similar manner to how
traces rely on a `sampling.priority` field to set the priority of the trace sampling.

### References

* [Trace state probability sampling](../trace/tracestate-probability-sampling.md)

### Definitions

* Sampling source: an attribute representing the source of sampling.
* Sampling priority: an attribute representing the priority of the log to be sampled. It is represented as percentage points, with 100 to always sample the log record, 0 to never sample the log record.  

## Requirements

### Deterministic sampling source

The log record must use a deterministic sampling source to represent the log record while sampling.
This is necessary to address the case where logs are sampled by multiple collectors, either as part of a highly-available setup where multiple collectors ingest a log source,
or when collectors are placed in sequence.
