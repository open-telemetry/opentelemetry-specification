# Process Context: Sharing Resource Attributes with External Readers

Introduce a standard mechanism for OpenTelemetry SDKs to publish resource attributes for access by out-of-process readers such as the OpenTelemetry eBPF Profiler.

## Motivation

External readers like the OpenTelemetry eBPF Profiler operate outside the instrumented process and cannot access resource attributes configured within OpenTelemetry SDKs. This creates several problems:

- **Missing cross-signal correlation identifiers**: Runtime-generated attributes ([`service.instance.id`](https://opentelemetry.io/docs/specs/semconv/registry/attributes/service/#service-instance-id) being a key example) are often inaccessible to external readers, making it hard to correlate various signals with each other (especially in runtimes that employ multiple processes).

- **Inconsistent resource attributes across signals**: Running in different scopes, configuration such as `service.name`, `deployment.environment.name`, and `service.version` are not always available or resolve consistently between the OpenTelemetry SDKs and external readers, leading to configuration drift and inconsistent tagging.

- **Correlation is dependent on process activity**: If a service is blocked (such as when doing slow I/O, or threads are actually deadlocked) and not emitting other signals, external readers have difficulty identifying it, since resource attributes or identifiers are only sent along when signals are reported.

## Explanation

We propose a mechanism for OpenTelemetry SDKs to publish process-level resource attributes, through a standard format based on Linux memory mappings.

When an SDK initializes (or updates its attributes) it publishes this information to a small memory region that external processes can discover and read.

This mechanism is designed to support loose coordination between the publishing process and external readers:

- **Publisher-first deployment**: The publishing process can start and publish its context before any readers are running, with readers discovering it later
- **Reader flexibility**: Readers are not limited to eBPF-based implementations; any external process with sufficient system permissions to read `/proc/<pid>/maps` and read target process memory can access this information
- **Runtime compatibility**: The mechanism works even in environments where eBPF function hooking is unavailable or restricted
- **Independent of process activity**: The context can be read at any time, including while the application is deadlocked, blocked on I/O, or otherwise idle, without relying on active hook points or the process emitting signals

External readers such as the OpenTelemetry eBPF Profiler will, upon observing a previously-unseen process, probe and read this information, associating it with any profiling samples or other telemetry collected from that process.

## Internal details

The process context is split between a header (stored in an anonymous mapping) and a payload.

### Header Structure

The header is stored in a memory mapping with the following format:

| Field             | Type      | Description                                                          |
|-------------------|-----------|----------------------------------------------------------------------|
| `signature`       | `char[8]` | Always set to `"OTEL_CTX"`                                           |
| `version`         | `uint32`  | Format version. Currently `2` (`1` can be used for development)      |
| `payload_size`    | `uint32`  | Number of bytes of the encoded payload                               |
| `published_at_ns` | `uint64`  | Timestamp when the context was published, in nanoseconds since epoch |
| `payload`         | `uint64`  | Pointer to payload (in the publishing process' address space), in protobuf format, cast to uint64 |

The `payload` can optionally be placed after the header (with the `payload` pointer field correctly pointing at it) or elsewhere in the process memory.

### Payload Format

The payload uses protobuf with the `ProcessContext` message:

```protobuf
// Copyright 2019, OpenTelemetry Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

syntax = "proto3";

// TODO: Is this in the right namespace? Since this is not only for profiling,
// `opentelemetry.proto.profiles` doesn't seem the right place, but perhaps common ain't
// it either? Feedback very welcome!
package opentelemetry.proto.common.v1;

import "opentelemetry/proto/common/v1/common.proto";
import "opentelemetry/proto/resource/v1/resource.proto";

option csharp_namespace = "OpenTelemetry.Proto.Common.V1";
option java_multiple_files = true;
option java_package = "io.opentelemetry.proto.common.v1";
option java_outer_classname = "ProcessContextProto";
option go_package = "go.opentelemetry.io/proto/otlp/common/v1";

// ProcessContext represents the payload for the process context sharing mechanism.
//
// This message is designed to be published by OpenTelemetry SDKs via a memory-mapped
// region, allowing external readers (such as the OpenTelemetry eBPF Profiler) to
// discover and read resource attributes from instrumented processes without requiring
// direct integration or process activity.
message ProcessContext {
  // The resource attributes describing this process.
  //
  // Attribute keys MUST be unique (it is not allowed to have more than one
  // attribute with the same key). The behavior of software that receives
  // duplicated keys can be unpredictable.
  //
  // Attributes SHOULD follow OpenTelemetry semantic conventions where applicable.
  // See: https://opentelemetry.io/docs/specs/semconv/
  opentelemetry.proto.resource.v1.Resource resource = 1;

  // Additional attributes to share with external readers that are not part of
  // the standard Resource. [Optional]
  //
  // This field allows publishers to include supplementary key-value pairs that
  // may be useful for external readers but are not part of the SDK's configured
  // Resource.
  //
  // Consider adding any keys here to the profiles semantic conventions in
  // https://opentelemetry.io/docs/specs/semconv/general/profiles/
  repeated opentelemetry.proto.common.v1.KeyValue extra_attributes = 2;
}

```

Whenever applicable, attributes should follow [existing semantic conventions](https://opentelemetry.io/docs/specs/semconv/).

We expect that once converted to an OTEP, the `threadlocal.`-prefixed keys from the proposed
[thread context sharing specification](https://docs.google.com/document/d/1eatbHpEXXhWZEPrXZpfR58-5RIx-81mUgF69Zpn3Rz4/edit?tab=t.bmgoq3yor67o)
will be the first users of `extra_attributes` section.

### Publication Protocol

Publishing the context should follow these steps:

1. **Check for existing mapping**: If a previous context was published, follow the "Updating Protocol" instead
2. **Allocate new memfd and size it**: Create a new memfd using `memfd_create("OTEL_CTX", ...)`, size it with `ftruncate`
3. **Allocate a new mmap from the memfd then close the memfd**: Setup an mmap using `mmap(..., PROT_READ | PROT_WRITE, MAP_PRIVATE, memfd, 0)`. This makes the memfd show up in `/proc/<pid>/maps`; afterwards the file descriptor can be closed
4. **If memfd is not available (step 2)**: If system security restrictions disallow memfd, fall back to creating a new anonymous mapping using `mmap(..., PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0)` and use that instead
5. **Prevent fork inheritance**: Apply `madvise(..., MADV_DONTFORK)` to prevent child processes from inheriting stale data
6. **Encode payload**: Serialize the payload message using protobuf (storing it either following the header OR in a separate memory allocation)
7. **Write header fields**: Populate `version`, `published_at_ns`, `payload_size`, `payload`
8. **Memory barrier**: Use language/compiler-specific techniques to ensure all previous writes complete before proceeding
9. **Write signature**: Write `"OTEL_CTX"` to the signature field last
10. **Name mapping**: Use `prctl(PR_SET_VMA, PR_SET_VMA_ANON_NAME, ..., "OTEL_CTX")` to name the mapping. This step should be done unconditionally, although naming mappings is not always supported by the kernel.

The signature MUST be written last to ensure readers never observe incomplete or invalid data. Once the signature is present (and thus all fields are non-zero), the entire mapping is considered valid.

If attributes are updated during the process lifetime, the "Updating Protocol" should be followed.

If any of the steps above fail (other than naming or allocating a new memfd), publication is considered to have failed, and the process context will not be available.
Finally, if both `memfd_create` fails (step 2, thus requiring falling back to step 4) and naming the mapping fails (step 10), then the process context will not be available either.

The process context is treated as a singleton: there SHOULD NOT be more than one process context active for the same process.

The context MAY be dropped during SDK shutdown, or kept around until the process itself terminates and the OS takes care of cleaning the process memory.

Naming the mapping is only available on Linux 5.17+ when the `CONFIG_ANON_VMA_NAME` feature on the kernel is enabled. Many Linux distributions such as Ubuntu and Arch enable it. On earlier kernel versions or kernels without the feature, the `prctl` call will return an error which should be ignored. The reading protocol specified below is able to work regardless of `CONFIG_ANON_VMA_NAME` being available.

Note that on legacy kernels and those without `CONFIG_ANON_VMA_NAME` it's still possible, using eBPF, [to optionally hook on `prctl`](https://github.com/ivoanjo/proc-level-demo/tree/main/ebpf-program) naming attempts as a way of detecting new mappings being published. For this reason, this step should always be done even if the publisher somehow is aware that naming will not be successful on the current system.

### Reading Protocol

External readers (such as the OpenTelemetry eBPF Profiler) discover and read process context as follows:

1. **Locate mapping**: Parse `/proc/<pid>/maps` and search for entries with name starting with `[anon_shmem:OTEL_CTX]` or `/memfd:OTEL_CTX`

2. **Validate signature and version**:
   - Read the header and verify first 8 bytes matches `OTEL_CTX`
   - Read the version field and verify it is supported (currently `2`)
   - If both of these checks succeed, the reader SHOULD consider the mapping established and MAY optionally cache the mapping address for that process for subsequent process context reads.
   - If either check fails, skip this mapping.

3. **Verify the rest of the header**:
   - Verify that `published_at_ns` is non-zero (zero indicates the context is currently being written)
   - If this fails, restart at 2 (MAY skip signature and version validation after mapping is considered established).

4. **Read payload**: Read `payload_size` bytes from `payload` pointer

5. **Re-read header**: If `published_at_ns` has not changed, the read of header + payload is consistent. This ensures there were no concurrent changes to the process context. If `published_at_ns` changed, restart at 2 (MAY skip signature and version validation after mapping is considered established).

6. **Decode payload**: Deserialize the bytes as a Protocol Buffer payload message

7. **Apply attributes**: Use the decoded resource attributes to enrich telemetry collected from this process

Readers SHOULD gracefully handle missing, incomplete, or invalid mappings. If a process does not publish context or if decoding fails, readers SHOULD fall back to default resource detection mechanisms.

### Updating Protocol

When the attributes change, the process context mapping should be updated following these steps:

1. **Prepare new payload**: Serialize the new payload message
2. **Signal update start**: Write `0` to the `published_at_ns` field. This signals to readers that an update is in progress (readers verify this field is non-zero).
3. **Memory barrier**: Ensure the write to `published_at_ns` is visible before proceeding.
4. **Update payload fields**: Update the `payload` pointer and `payload_size` fields to point to the new payload.
5. **Memory barrier**: Ensure the payload fields are updated before finalizing the timestamp.
6. **Signal update complete**: Write the new timestamp to `published_at_ns`, this is an aligned word-size write and thus expected to be atomic.
7. **Name mapping**: Re-issue the `prctl(PR_SET_VMA, ...)` call to name the mapping. This step MUST be done unconditionally, although naming mappings is not always supported by the kernel.

As the reader checks `published_at_ns` before and after reading the payload, it will detect concurrent updates and avoid concurrency issues.

### Interaction with Existing Functionality

This mechanism is additive and does not modify existing OpenTelemetry SDK behavior:

- Resource attributes continue to work as before for exporters within the process
- The mapping is process-scoped and does not affect thread-local context propagation

SDKs that do not implement this feature continue to function normally; external readers simply will not have access to their runtime-generated resource attributes.

## Trade-offs and mitigations

### Host and Permission Requirements

This mechanism requires that the external reader (such as an eBPF profiler) is running on the same host as the instrumented process and has sufficient privileges to both access the memory mappings exposed by the process and read target process memory.

The OpenTelemetry eBPF profiler, by design, has the necessary permissions and operates on the same machine to read this metadata. This approach does **not** support remote or cross-host correlation of process context, and attempts to access the process context mappings without appropriate permissions (e.g., from an unprivileged user) will fail.

### Process Forking

When a process forks, child processes do not inherit the parent's process context mapping. This is accomplished through the `madvise(MADV_DONTFORK)` flag, which explicitly marks the memory region as non-inheritable across `fork()`.

**Why this matters**: Without this protection, child processes would inherit stale resource attributes from the parent. For example, if a parent process has `service.instance.id=uuid-parent` and forks a child that initializes its own OpenTelemetry SDK with `service.instance.id=uuid-child`, the child would initially expose the parent's UUID until it publishes its own context. This could lead to misattribution of telemetry in backend systems.

**Behavior**:

- Child processes that initialize their own OpenTelemetry SDK will publish their own process context mapping with their own resource attributes
- Child processes that do not initialize an OpenTelemetry SDK will simply not have a process context mapping, which readers handle gracefully

### Complexity for SDK Implementers

Creating memory mappings and managing them adds complexity to SDK implementations.

**Mitigation**: We've created a reference implementation in [C/C++](https://github.com/open-telemetry/sig-profiling/tree/main/process-context/c-and-cpp), as well as a [demo OTEL Java SDK extension](https://github.com/ivoanjo/proc-level-demo/tree/main/otel-java-extension-demo) and a [Go port as well](https://github.com/DataDog/dd-trace-go/pull/3937).

For Go as well as modern versions of Java it's possible to create an implementation that doesn't rely on third-party libraries or native code (e.g. by directly calling into the OS or libc). Older versions of Java will need to rely on building the C/C++ code into a Java native library.

### Platform Limitations

This mechanism relies on Linux-specific features (`mmap`, `prctl`, `/proc`).

**Mitigation**: The feature is optional. SDKs on other platforms or environments where these features are unavailable can simply not implement it. In the future, we may explore similar mechanisms for other operating systems.

### Protocol Evolution

As requirements evolve, we may need to extend the payload format.

**Mitigation**: The design includes both versioning as well as allowing extension points

1. **Additional `extra_attributes` keys**: The `ProcessContext` message can carry custom attributes
2. **Use of `ProcessContext` protobuf format**: The `ProcessContext` can be expanded in backwards-compatible ways by following usual protobuf evolution guidelines
3. **Version number**: For incompatible changes (not expected to change frequently)

### Memory Overhead

Each process publishes a small (typically one memory page) mapping + the amount of memory needed for the payload, expected to also be in the KB range.

### Payload Format Choice

The proposal uses protobuf. Not all SDKs may want to carry a protobuf encoder dependency.

**Mitigation**: Our reference implementations optionally include a limited protobuf implementation that implements only the feature set needed to emit a minimal payload message in < 500 LoC (C/C++ and Java). Alternatively, existing protobuf encoders can be used.

Aside from protobuf, msgpack was also trialed; similarly to protobuf, it's possible to provide a small msgpack encoder with low complexity. We're hoping that the community can make the final choice during specification review.

### Trace Correlation

The proposed mechanism only supports sharing process-level resource attributes.

In particular, it does not support carrying trace and span ids, which would be required to provide finer-grained correlation. Prior art by Elastic and Polar Signals (see below) provide such thread-level context sharing, and there's a working doc [for supporting thread-level context sharing in the OTEL eBPF Profiler](https://docs.google.com/document/d/1eatbHpEXXhWZEPrXZpfR58-5RIx-81mUgF69Zpn3Rz4/edit?tab=t.0#heading=h.fvztn3xtjxxm) under development for this. We expect that in the future, such correlation would be proposed as a separate OTEP.

Process-level and thread-level context are complementary: The process-level mechanism proposed in this OTEP can be generically adopted by SDKs, and allows for flexibility in publishing metadata and in parsing it. Thread-level mechanisms, in contrast, may need specific support for individual languages/runtimes, and because they would be updated for every span, will need careful performance work.

### Applicability to OpenTelemetry eBPF Instrumentation

The [OpenTelemetry eBPF Instrumentation (OBI)](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation) auto-instrumentation tool, when used in the application observability mode, uses a combination of Linux uprobes and [userspace writes](https://opentelemetry.io/docs/zero-code/obi/security/) to emit traces and metrics from otherwise unmodified applications.

The protocol proposed by this specification requires the ability to, inside the target application, allocate (small amounts of) memory, as well as invoking system calls to set up the naming and the inheritance permissions. This is not something that can currently be done with an eBPF-based approach and thus this spec can't currently be implemented using OBI.

**Mitigation**: For OBI-to-OTEL eBPF Profiler communication, we can separately introduce an out-of-band channel using the existing kernel eBPF primitives, given both tools operate in kernel space.

## Prior art and alternatives

### Prior Art

**Elastic apmint**: Elastic's apmint, described in <https://www.elastic.co/observability-labs/blog/continuous-profiling-distributed-tracing-correlation> and <https://github.com/elastic/apm/blob/main/specs/agents/universal-profiling-integration.md> uses global variables to share process-level data. This is currently used by the Elastic Java trace agent.

**Polar Signals Custom Labels**: Parca uses a [global variable](https://github.com/polarsignals/custom-labels/blob/master/custom-labels-v1.md#custom_labels_abi_version) to share ABI version information.

Both approaches demonstrate the need for process-level data sharing and validate the use case, but they rely on ELF symbols which have some limitations (discussed below).

### Alternatives Considered and Rejected

1. Global Variables (Current Approach in OTEL eBPF Profiler)

   Use global variables with well-known symbol names to store process context.

   **Pros**: Low overhead, straightforward access
   **Cons**:

   - Symbols may not be accessible in stripped binaries
   - Difficult to expose in managed languages (Java, Python) without native libraries
   - Static linking can hide symbols
   - Child processes inherit the parent's global variables after `fork()`, potentially exposing stale resource attributes until overwritten
   - Requires polling to detect context publishing and changes

   **Why rejected**: The mapping approach is more universally accessible across languages and build configurations.

2. Environment Variables

   Share resource attributes via environment variables using `setenv()`.

   **Cons**:

   - `/proc/<pid>/environ` is not updated by `setenv()` at runtime
   - `setenv()` is not thread-safe and can cause crashes in multithreaded applications
   - Some runtimes (e.g., Java) don't expose APIs to modify environment variables
   - Difficult to guarantee safe timing in managed runtimes with background threads
   - Child processes inherit the parent's environment, potentially exposing stale resource attributes until overwritten
   - Requires polling to detect context publishing and changes

   **Why rejected**: Technical limitations make this approach non-viable.

3. Collector-Based Enrichment

   Have the OpenTelemetry Collector correlate resource attributes across signals.

   **Cons**:

   - Adds significant complexity and statefulness to the Collector
   - Conflicts with the Collector's stateless design philosophy
   - Would require tracking resource attributes for each signal and correlating by process/container IDs

   **Why rejected**: Wide impact on collector for all OTEL signals.

4. Custom ELF Sections

   Use custom ELF sections (via section attribute in C/C++ or link_section in Rust).

   **Pros**: Fast lookup without searching all mappings
   **Cons**:

   - Not supported in all languages (e.g., Go, Java)
   - Requires build-time configuration
   - Still faces challenges with stripped binaries
   - Requires polling to detect context publishing and changes

   **Why rejected**: Limited language support and similar limitations to global variables.

5. Dynamic Symbol Export

   Ensure symbols are preserved with `-Wl,--export-dynamic` linker flags.

   **Pros**: Similar to Custom ELF sections.
   **Cons**:

   - Similar to Custom ELF sections
   - Requires users to modify build configurations

   **Why rejected**: Creates adoption barriers and doesn't work for key languages.

6. File/Socket-Based Communication

   Write resource attributes to a file or socket.

   **Pros**: Can use regular file/socket based APIs
   **Cons**:

   - File/socket lifecycle management (creation, cleanup, permissions)
   - Also needs to deal with `fork()` and how child processes inherit the parent's open files/sockets
   - Requires polling to detect context publishing and changes
   - File-based not compatible with services deployed on read-only filesystems

   **Why rejected**: The technical and operational complexities (especially regarding lifecycle, `fork()` and access control) outweigh the benefits over memory mappings.

## Open questions

1. **Protobuf vs. msgpack vs. other**: Should the payload use protobuf or msgpack, or something else entirely (such as [Type, Length, Value](https://docs.google.com/document/d/1Ij6SYfv0lHOhTNsXNGVFpra3ZCfz-WC7QBXdB_OaoYc/edit?tab=t.0#heading=h.llbgke6lmlbd))? In our experiments, they all work well, the choice is primarily about ease of implementation in the ecosystem and standardization.

2. **SDK implementation requirements**: Should SDKs publish this information by default whenever possible, or be opt-in?

## Prototypes

The following proof-of-concept implementations demonstrate feasibility across multiple languages:

- **[process-context-c-and-cpp](https://github.com/open-telemetry/sig-profiling/tree/main/process-context/c-and-cpp)**: Complete reference implementation in C/C++ with protobuf payload
- **[otel-java-extension-demo](https://github.com/ivoanjo/proc-level-demo/tree/main/otel-java-extension-demo)**: OTEL Java SDK extension for automatic publication
- **[anonmapping-java](https://github.com/ivoanjo/proc-level-demo/tree/main/anonmapping-java)**: Pure Java implementation using FFM (no dependencies)
- **[ebpf-program](https://github.com/ivoanjo/proc-level-demo/tree/main/ebpf-program)**: Example eBPF program demonstrating event-driven publishing detection
- **[OpenTelemetry eBPF Profiler PR](https://github.com/DataDog/dd-otel-host-profiler/pull/210)**: Integration in Datadog's experimental fork

Additional implementations have been tested with:

- [Datadog Java SDK](https://github.com/DataDog/java-profiler/pull/266)
- [Datadog Ruby SDK](https://github.com/DataDog/dd-trace-rb/pull/4865)
- [Datadog Go SDK](https://github.com/DataDog/dd-trace-go/pull/3937)

These prototypes validate that the approach works across different languages and runtimes.

## Future possibilities

Supporting thread-level context sharing, to enable correlation of outside activity (e.g. profiles) with traces/spans is highly desired.

The process context could also be used for entity detection as detailed in [OTEP 264](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/entities/0264-resource-and-entities.md).
