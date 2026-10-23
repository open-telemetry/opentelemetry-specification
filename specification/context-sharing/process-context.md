# Process Context Sharing

**Status**: [Alpha](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- START doctoc -->

- [Overview](#overview)
- [Process Context Format](#process-context-format)
  * [Header](#header)
  * [Payload](#payload)
- [Publication Protocol](#publication-protocol)
- [Reading Protocol](#reading-protocol)
- [Updating Protocol](#updating-protocol)
- [Interaction with Existing Functionality](#interaction-with-existing-functionality)

<!-- END doctoc -->

</details>

## Overview

Process Context Sharing allows OpenTelemetry SDKs to publish process-level information for access by out-of-process readers, such as the OpenTelemetry eBPF Profiler.

SDK support for Process Context Sharing is OPTIONAL.

This mechanism relies on Linux-specific features (`mmap`, `prctl`, `/proc`) and requires external readers to run on the same host as the instrumented process with sufficient privileges to access the process's memory mappings and read target process memory.

External readers like the OpenTelemetry eBPF Profiler operate outside the instrumented process and cannot access resource attributes configured within OpenTelemetry SDKs. This can prevent telemetry collected externally from being correlated with telemetry produced by the SDK, particularly when attributes such as `service.instance.id` are generated at runtime.

A publisher can make the context available before any reader is running, and readers can access it without requiring the publishing process to be actively emitting telemetry.

For design rationale, alternatives and prototypes, see [OTEP 4719][otep].

## Process Context Format

The Process Context consists of a fixed header and a payload encoded using [Protocol Buffers][protobuf]. The payload contains the process Resource and additional attributes for external readers.

### Header

The header is stored in a memory mapping with the following format:

| Field                       | Type      | Description                                                                                               |
|-----------------------------|-----------|-----------------------------------------------------------------------------------------------------------|
| `signature`                 | `char[8]` | Always set to the 8-byte sequence `"OTEL_CTX"` (not NUL-terminated; readers MUST compare exactly 8 bytes) |
| `version`                   | `uint32`  | Format version. Currently `2` (`1` can be used for development)                                           |
| `payload_size`              | `uint32`  | Number of bytes of the encoded payload                                                                    |
| `monotonic_published_at_ns` | `uint64`  | Monotonic clock timestamp from `CLOCK_BOOTTIME` of when the context was published, in nanoseconds         |
| `payload`                   | `uint64`  | Pointer to payload (in the publishing process' address space), in protobuf format, cast to uint64         |

The `payload` can optionally be placed after the header (with the `payload` pointer field correctly pointing at it) or elsewhere in the process memory.

The `monotonic_published_at_ns` SHOULD use a timestamp from the `CLOCK_BOOTTIME` system clock.
This timestamp is used for detecting if the context is consistent/during updates and thus:

* `monotonic_published_at_ns` being zero is reserved to indicate the context is being mutated and is not yet ready for reading.
* Every update to `monotonic_published_at_ns` MUST provide a different value for this timestamp.

### Payload

The payload uses protobuf with the [`ProcessContext` message][process-context-proto].

`ProcessContext` contains:

- `resource`, containing the [Resource](../resource/README.md) attributes describing this process.

  Attribute keys MUST be unique (it is not allowed to have more than one attribute with the same key). The behavior of software that receives duplicated keys can be unpredictable.
- `attributes`, containing additional attributes to share with external readers that are not part of the standard Resource.

Whenever applicable, attributes SHOULD follow the existing OpenTelemetry [semantic conventions][semantic-conventions].

## Publication Protocol

Publishing the context SHOULD follow these steps:

1. **Check for existing mapping**: If a previous context was published, follow the "[Updating Protocol](#updating-protocol)" instead.
2. **Allocate new memfd and size it**: Create a new memfd using `memfd_create("OTEL_CTX", MFD_CLOEXEC | MFD_ALLOW_SEALING | MFD_NOEXEC_SEAL)`, size it with `ftruncate`.
   Note that `MFD_NOEXEC_SEAL` is a newer Linux feature so if you get a failure creating the memfd, you probably want to try again with just `MFD_CLOEXEC | MFD_ALLOW_SEALING`.
3. **Allocate a new mmap from the memfd then close the memfd**: Setup an mmap using `mmap(..., PROT_READ | PROT_WRITE, MAP_PRIVATE, memfd, 0)`. This makes the memfd show up in `/proc/<pid>/maps`; afterwards the file descriptor can be closed.
4. **If memfd is not available (step 2)**: If system security restrictions disallow memfd, fall back to creating a new anonymous mapping using `mmap(..., PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0)` and use that instead.
5. **Prevent fork inheritance**: Apply `madvise(..., MADV_DONTFORK)` to prevent child processes from inheriting stale data.
6. **Encode payload**: Serialize the payload message using protobuf (storing it either following the header OR in a separate memory allocation).
7. **Write header fields**: Populate `signature`, `version`, `payload_size`, `payload` but not yet `monotonic_published_at_ns`.
8. **Memory barrier**: Use language/compiler-specific techniques to ensure all previous writes complete before proceeding (`atomic_thread_fence(memory_order_seq_cst)` or equivalent).
9. **Write timestamp**: Write `monotonic_published_at_ns` last. This field is used to detect that the context is ready for use by the reader.
10. **Name mapping**: Use `prctl(PR_SET_VMA, PR_SET_VMA_ANON_NAME, ..., "OTEL_CTX")` to name the mapping. This step SHOULD be done unconditionally, although naming mappings is not always supported by the kernel.

The `monotonic_published_at_ns` MUST be written last to ensure readers never observe incomplete or invalid data. Once this field is non-zero (and thus all fields are also non-zero), the entire mapping is considered valid.

If attributes are updated during the process lifetime, the "[Updating Protocol](#updating-protocol)" SHOULD be followed.

If any of the steps above fail (other than naming or allocating a new memfd), publication is considered to have failed, and the process context will not be available.
Finally, if both `memfd_create` fails (step 2, thus requiring falling back to step 4) and naming the mapping fails (step 10), then the process context will not be available either.

The process context is treated as a singleton: there MUST NOT be more than one process context active for the same process.

In a situation where multiple resources exist as per <https://github.com/open-telemetry/opentelemetry-specification/pull/4665>, the process context SHOULD contain the default SDK resource.
We expect future work to enable more granular attribution of work to specific resources, e.g. [the thread context sharing specification](../../oteps/profiles/4947-thread-ctx.md)
will enable identifying which threads are working on what (e.g. in a multi-tenant scenario).

The context MAY be dropped during SDK shutdown, or kept around until the process itself terminates and the OS takes care of cleaning the process memory.

Naming the mapping is only available on Linux 5.17+ when the `CONFIG_ANON_VMA_NAME` feature on the kernel is enabled. Many Linux distributions such as Ubuntu and Arch enable it. On earlier kernel versions or kernels without the feature, the `prctl` call will return an error which SHOULD be ignored. The reading protocol specified below is able to work regardless of `CONFIG_ANON_VMA_NAME` being available.

Note that on legacy kernels and those without `CONFIG_ANON_VMA_NAME` it's still possible, using eBPF, to optionally hook on `prctl` naming attempts as a way of detecting new mappings being published. For this reason, this step SHOULD always be done even if the publisher somehow is aware that naming will not be successful on the current system.

## Reading Protocol

External readers (such as the OpenTelemetry eBPF Profiler) discover and read process context as follows:

1. **Locate mapping**: Parse `/proc/<pid>/maps` and search for entries with name **starting with** `[anon_shmem:OTEL_CTX]`, `[anon:OTEL_CTX]` or `/memfd:OTEL_CTX`.

2. **Validate signature and version**:
   - Read the first 8 bytes of the header and verify they match `OTEL_CTX`.
   - Read the version field and verify it is supported (currently `2`).
   - If both of these checks succeed, the reader SHOULD consider the mapping established and MAY optionally cache the mapping address for that process for subsequent process context reads.
   - If either check fails, skip this mapping.

3. **Verify the rest of the header**:
   - Verify that `monotonic_published_at_ns` is non-zero (zero indicates the context is currently being mutated).
   - If this fails, restart at 2 (MAY skip signature and version validation after mapping is considered established).

4. **Memory barrier**: Ensure previous reads terminate before proceeding (`atomic_thread_fence(memory_order_seq_cst)` or equivalent).

5. **Read payload**: Read the `payload` and `payload_size` fields. Copy `payload_size` bytes from the `payload` pointer into reader-local memory.

6. **Memory barrier**: Ensure previous reads terminate before proceeding (`atomic_thread_fence(memory_order_seq_cst)` or equivalent).

7. **Re-verify header**: Read `monotonic_published_at_ns` again. If it has not changed, the read of header + payload is consistent. This ensures there were no concurrent changes to the process context.
If `monotonic_published_at_ns` is different from the value read in step 3, restart at 2 (MAY skip signature and version validation after mapping is considered established).

8. **Decode payload**: Deserialize the bytes as a Protocol Buffer payload message.

9. **Apply attributes**: Use the decoded resource attributes to enrich telemetry collected from this process.

Readers SHOULD gracefully handle missing, incomplete, or invalid mappings. If a process does not publish context or if decoding fails, readers SHOULD fall back to default resource detection mechanisms.
We recommend the use of APIs such as `process_vm_readv` or equivalent to read data, as they allow gracefully handling of issues inherent to racy cross-process memory access.

After the first successful read, if using polling to check for updates, readers can assume that if `monotonic_published_at_ns` has not changed, then the read payload is still consistent.
That is, the `monotonic_published_at_ns` can be used as a "cache invalidation key" for parsing the payload.

The different names in `/proc/<pid>/maps` are caused by the fallback options the writer goes through to setup and name the mapping: `[anon_shmem:OTEL_CTX]` means both `memfd_create` and `prctl` succeeded; `[anon:OTEL_CTX]` means `memfd_create` failed but `prctl` succeeded; `/memfd:OTEL_CTX` means `memfd_create` succeeded but `prctl` failed.
The remaining option where both `memfd_create` and `prctl` failed does not establish a valid context and is treated as an error in the writer.

## Updating Protocol

When the attributes change, the process context mapping SHOULD be updated following these steps:

1. **Prepare new payload**: Serialize the new payload message.
2. **Signal update start**: Write `0` to the `monotonic_published_at_ns` field. This signals to readers that an update is in progress (readers verify this field is non-zero).
3. **Memory barrier**: Ensure the write to `monotonic_published_at_ns` is visible before proceeding (`atomic_thread_fence(memory_order_seq_cst)` or equivalent).
4. **Update payload fields**: Update the `payload` pointer and `payload_size` fields to point to the new payload.
5. **Memory barrier**: Ensure the payload fields are updated before finalizing the timestamp (`atomic_thread_fence(memory_order_seq_cst)` or equivalent).
6. **Signal update complete**: Write the new timestamp to `monotonic_published_at_ns`; this is an aligned 64-bit write and thus expected to be atomic.
   The new `monotonic_published_at_ns` MUST be different (and after) the value present before the update started.
7. **Name mapping**: Re-issue the `prctl(PR_SET_VMA, ...)` call to name the mapping. This step MUST be done unconditionally, although naming mappings is not always supported by the kernel.

As the reader checks `monotonic_published_at_ns` before and after reading the payload, it will detect concurrent updates and avoid concurrency issues.

## Interaction with Existing Functionality

This mechanism is additive and does not modify existing OpenTelemetry SDK behavior:

- Resource attributes continue to work as before for exporters within the process.
- The mapping is process-scoped and does not affect thread-local context propagation.

SDKs that do not implement this feature continue to function normally; external readers simply will not have access to their runtime-generated resource attributes.

[otep]: ../../oteps/profiles/4719-process-ctx.md
[process-context-proto]: https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/processcontext/v1development/process_context.proto
[protobuf]: https://protobuf.dev/
[semantic-conventions]: https://opentelemetry.io/docs/specs/semconv/
