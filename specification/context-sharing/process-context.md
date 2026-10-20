<NEW>

# Process Context Sharing

<NEW>

**Status**: [Development](../document-status.md)

<NEW>

> Annotation legend:
>
> - `<COPIED>`: copied verbatim from OTEP 4719.
> - `<DERIVED>`: based on OTEP 4719, with wording or structure changed for the specification.
> - `<NEW>`: not stated in OTEP 4719 and introduced by this draft.

<NEW>

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

<DERIVED>

## Overview

<DERIVED>

Process Context Sharing allows OpenTelemetry SDKs to publish process-level information for access by out-of-process readers running on the same host, such as the OpenTelemetry eBPF Profiler.

<DERIVED>

External readers operate outside the instrumented process and cannot otherwise access Resource attributes configured within an OpenTelemetry SDK. This can prevent telemetry collected externally from being correlated with telemetry produced by the SDK, particularly when attributes such as `service.instance.id` are generated at runtime.

<DERIVED>

This specification defines Process Context publication and discovery on Linux through a memory mapping that external processes can discover and read. A publisher can make the context available before any reader is running, and readers can access it without requiring the publishing process to be actively emitting telemetry.

<DERIVED>

A reader must have sufficient permissions to inspect the publishing process's memory mappings and read its memory.

<NEW>

For design rationale, alternatives and prototypes, see [OTEP 4719][otep].

<DERIVED>

## Process Context Format

<DERIVED>

The Process Context consists of a fixed header and a payload encoded using [Protocol Buffers][protobuf]. The payload contains the process Resource and additional attributes for external readers.

<DERIVED>

### Header

<DERIVED>

The header has the following format:

<COPIED>

| Field                       | Type      | Description                                                                                               |
|-----------------------------|-----------|-----------------------------------------------------------------------------------------------------------|
| `signature`                 | `char[8]` | Always set to the 8-byte sequence `"OTEL_CTX"` (not NUL-terminated; readers MUST compare exactly 8 bytes) |
| `version`                   | `uint32`  | Format version. Currently `2` (`1` can be used for development)                                           |
| `payload_size`              | `uint32`  | Number of bytes of the encoded payload                                                                    |
| `monotonic_published_at_ns` | `uint64`  | Monotonic clock timestamp from `CLOCK_BOOTTIME` of when the context was published, in nanoseconds         |
| `payload`                   | `uint64`  | Pointer to payload (in the publishing process' address space), in protobuf format, cast to uint64         |

<DERIVED>

The payload MAY be placed directly after the header or elsewhere in the publishing process's memory. The `payload` field MUST point to its location in the publishing process's address space.

<DERIVED>

`monotonic_published_at_ns` SHOULD use the `CLOCK_BOOTTIME` system clock.

<DERIVED>

This timestamp is used to detect whether the Process Context is consistent during updates:

- `monotonic_published_at_ns` being zero is reserved to indicate that the context is being mutated and is not yet ready for reading.
- Every update to `monotonic_published_at_ns` MUST provide a different value.

<DERIVED>

### Payload

<DERIVED>

The payload uses Protocol Buffers with the [`ProcessContext` message][process-context-proto].

<DERIVED>

`ProcessContext` contains:

- `resource`, containing the [Resource](../resource/README.md) associated with the process.
- `attributes`, containing additional information for external readers that is not part of the Resource.

<DERIVED>

Resource attribute keys MUST be unique. Software receiving duplicate Resource attribute keys may behave unpredictably.

<DERIVED>

Attributes SHOULD follow the OpenTelemetry [semantic conventions][semantic-conventions] where applicable.

<COPIED>

## Publication Protocol

<COPIED>

Publishing the context follows these steps:

1. **Check for existing mapping**: If a previous context was published, follow the [Updating Protocol](#updating-protocol) instead.
2. **Allocate new memfd and size it**: Create a new memfd using `memfd_create("OTEL_CTX", MFD_CLOEXEC | MFD_ALLOW_SEALING | MFD_NOEXEC_SEAL)`, size it with `ftruncate`. Note that `MFD_NOEXEC_SEAL` is a newer Linux feature, so if creating the memfd fails, retry with just `MFD_CLOEXEC | MFD_ALLOW_SEALING`.
3. **Allocate a new mmap from the memfd then close the memfd**: Set up an mmap using `mmap(..., PROT_READ | PROT_WRITE, MAP_PRIVATE, memfd, 0)`. This makes the memfd show up in `/proc/<pid>/maps`; afterwards the file descriptor can be closed.
4. **If memfd is not available (step 2)**: If system security restrictions disallow memfd, fall back to creating a new anonymous mapping using `mmap(..., PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0)` and use that instead.
5. **Prevent fork inheritance**: Apply `madvise(..., MADV_DONTFORK)` to prevent child processes from inheriting stale data.
6. **Encode payload**: Serialize the payload message using protobuf, storing it either following the header or in a separate memory allocation.
7. **Write header fields**: Populate `signature`, `version`, `payload_size`, and `payload`, but not yet `monotonic_published_at_ns`.
8. **Memory barrier**: Use language/compiler-specific techniques to ensure all previous writes complete before proceeding, such as `atomic_thread_fence(memory_order_seq_cst)` or equivalent.
9. **Write timestamp**: Write `monotonic_published_at_ns` last. This field is used to indicate that the context is ready for use by the reader.
10. **Name mapping**: Use `prctl(PR_SET_VMA, PR_SET_VMA_ANON_NAME, ..., "OTEL_CTX")` to name the mapping. This step MUST be performed unconditionally, although naming mappings is not always supported by the kernel.

<COPIED>

The `monotonic_published_at_ns` field MUST be written last to ensure readers never observe incomplete or invalid data. Once this field is non-zero, the entire mapping is considered valid.

<COPIED>

If attributes are updated during the process lifetime, the [Updating Protocol](#updating-protocol) is followed.

<COPIED>

If any of the steps above fail, other than naming or allocating a new memfd, publication has failed and the Process Context is not available. If both `memfd_create` and naming the mapping fail, the Process Context is also not available.

<COPIED>

The Process Context is treated as a singleton: there MUST NOT be more than one active Process Context for the same process.

<COPIED>

When multiple Resources exist, as described by [OTEP 4665](../../oteps/entities/4665-multiple-resource-in-sdk.md), the Process Context SHOULD contain the default SDK Resource. Future work may enable more granular attribution of work to specific Resources. For example, [OTEP 4947](../../oteps/profiles/4947-thread-ctx.md) enables identifying which threads are working on which Resources.

<COPIED>

The Process Context MAY be dropped during SDK shutdown or kept until the process terminates and the operating system cleans up the process memory.

<COPIED>

Naming the mapping is available on Linux 5.17 and later when the `CONFIG_ANON_VMA_NAME` kernel feature is enabled. On earlier kernels or kernels without this feature, the `prctl` call returns an error which is ignored. The [Reading Protocol](#reading-protocol) works regardless of whether `CONFIG_ANON_VMA_NAME` is available.

<COPIED>

On legacy kernels and kernels without `CONFIG_ANON_VMA_NAME`, readers using eBPF can optionally hook `prctl` naming attempts to detect new mappings. For this reason, the naming step is always performed even if the publisher expects it to fail.

<COPIED>

## Reading Protocol

<COPIED>

External readers discover and read Process Context as follows:

1. **Locate mapping**: Parse `/proc/<pid>/maps` and search for entries with names starting with `[anon_shmem:OTEL_CTX]`, `[anon:OTEL_CTX]`, or `/memfd:OTEL_CTX`.
2. **Validate signature and version**:
   - Read the first 8 bytes of the header and verify they match `OTEL_CTX`.
   - Read the version field and verify it is supported, currently `2`.
   - If both checks succeed, the reader SHOULD consider the mapping established and MAY cache the mapping address for subsequent Process Context reads.
   - If either check fails, skip this mapping.
3. **Verify the rest of the header**:
   - Verify that `monotonic_published_at_ns` is non-zero. Zero indicates that the context is currently being mutated.
   - If this check fails, restart at step 2. The reader MAY skip signature and version validation after the mapping is considered established.
4. **Memory barrier**: Ensure previous reads complete before proceeding, using `atomic_thread_fence(memory_order_seq_cst)` or equivalent.
5. **Read payload**: Read `payload` and `payload_size`. Copy `payload_size` bytes from the `payload` pointer into reader-local memory.
6. **Memory barrier**: Ensure previous reads complete before proceeding, using `atomic_thread_fence(memory_order_seq_cst)` or equivalent.
7. **Re-verify header**: Read `monotonic_published_at_ns` again. If it has not changed, the header and payload read is consistent. If it differs from the value read in step 3, restart at step 2. The reader MAY skip signature and version validation after the mapping is considered established.
8. **Decode payload**: Deserialize the bytes as a Protocol Buffer payload message.
9. **Apply attributes**: Use the decoded Resource attributes to enrich telemetry collected from this process.

<COPIED>

Readers SHOULD gracefully handle missing, incomplete, or invalid mappings. If a process does not publish Process Context or decoding fails, readers SHOULD fall back to default Resource detection mechanisms.

<COPIED>

Readers are encouraged to use APIs such as `process_vm_readv` or equivalent to read data, as they allow graceful handling of failures inherent in racy cross-process memory access.

<COPIED>

After the first successful read, readers polling for updates can assume that the payload remains consistent while `monotonic_published_at_ns` remains unchanged. The timestamp can be used as a cache invalidation key for parsing the payload.

<COPIED>

The different names in `/proc/<pid>/maps` result from the fallback options used to set up and name the mapping:

- `[anon_shmem:OTEL_CTX]` means that both `memfd_create` and `prctl` succeeded.
- `[anon:OTEL_CTX]` means that `memfd_create` failed but `prctl` succeeded.
- `/memfd:OTEL_CTX` means that `memfd_create` succeeded but `prctl` failed.

<COPIED>

If both `memfd_create` and `prctl` fail, no valid Process Context is established.

<DERIVED>

## Updating Protocol

<DERIVED>

When the published information changes, the publisher MUST update the existing Process Context mapping as follows:

1. Encode the new `ProcessContext` payload.
2. Write zero to `monotonic_published_at_ns` to indicate that an update is in progress.
3. Use a sequentially consistent memory barrier to ensure the zero value is visible before modifying the payload fields.
4. Update `payload` and `payload_size` to refer to the new payload.
5. Use another sequentially consistent memory barrier to ensure the payload fields are visible before completing the update.
6. Write a new value to `monotonic_published_at_ns`. The value MUST be different from the value used for the previous completed publication.
7. Reissue the `prctl(PR_SET_VMA, PR_SET_VMA_ANON_NAME, ...)` call to name the mapping `OTEL_CTX`.

<DERIVED>

The final write to `monotonic_published_at_ns` is an aligned 64-bit write and is expected to be atomic.

<DERIVED>

Because readers compare `monotonic_published_at_ns` before and after reading the payload, they can detect concurrent updates and discard inconsistent reads.

<NEW>

The publisher is responsible for retaining each published payload allocation for as long as a reader may still be accessing it.

<DERIVED>

## Interaction with Existing Functionality

<DERIVED>

Process Context Sharing is additive and does not change existing OpenTelemetry SDK behaviour:

- Resource attributes continue to be associated with telemetry exported by the SDK.
- The Process Context mapping is process-scoped and does not affect thread-local context propagation.
- SDKs that do not implement Process Context Sharing continue to function normally.
- External readers continue to use their existing Resource detection mechanisms when Process Context is unavailable.

<NEW>

[otep]: ../../oteps/profiles/4719-process-ctx.md
[process-context-proto]: https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/processcontext/v1development/process_context.proto
[protobuf]: https://protobuf.dev/
[semantic-conventions]: https://opentelemetry.io/docs/specs/semconv/
