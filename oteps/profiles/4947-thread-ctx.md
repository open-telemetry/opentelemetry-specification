# Thread Context: Sharing Thread-Level Information with External Readers

Introduce a standard mechanism for OpenTelemetry SDKs to publish thread-level attributes for out-of-process readers such as the OpenTelemetry eBPF profiler.
It is related to [OTEP 4719: Process Context](4719-process-ctx.md), which it uses to share initial configuration information with readers.

There is a complete example of the spec as well as example readers and writers in <https://github.com/scottgerring/ctx-sharing-demo>
(possibly to be moved to [open-telemetry/sig-profiling](https://github.com/open-telemetry/sig-profiling)?).

Our work-in-progress implementation of this on the OTel eBPF Profiler side is at <https://github.com/open-telemetry/opentelemetry-ebpf-profiler/pull/1229>.

## Motivation

External readers such as the OpenTelemetry eBPF Profiler operate outside the instrumented process and cannot collect information about active OpenTelemetry traces running within the processes they are observing. This creates two main problems:

* **Inability to correlate observations with context metadata** - Without visibility into context information such as the active span, an external reader cannot attribute its observations to particular HTTP endpoints or other request characteristics.
* **Lack of request metadata for samples collected on threads with un-sampled traces** - in many cases, the active span observed by the external process *may not* be sampled by the OpenTelemetry SDK. In these cases it is useful to make extra metadata available directly to the external process, so that its samples maintain useful context even in the face of sampling on the tracer side.
* **Avoiding duplication** - other out-of-process readers such as [OTel OBI](https://opentelemetry.io/docs/zero-code/obi/) can avoid redundant instrumentation efforts in cases where the OTel SDK is already sharing necessary thread context information, simplifying the user experience and conserving resources.

## Explanation

We propose a mechanism for OpenTelemetry SDKs to publish thread-level information reflecting the context of the active request, if any, through a standard format using a Linux-specific ELF Thread-Local Storage (TLS) variable.

Because this mechanism relies on having a native component and knowing when a runtime switches contexts, we consider it optional for SDKs to support, as some runtimes (or even runtime versions) may not be able to feasibly/efficiently implement it.

The TLS-based publication mechanism and the in-memory **Thread-Local Context Record** format are intentionally separable. Runtimes that cannot efficiently expose context through TLS, or for which OS-thread-local context is not the appropriate execution-context model, are not required to implement this mechanism. However, we highly recommend reusing the same in-memory record format when publishing equivalent context through a runtime-specific discovery mechanism, rather than defining a runtime-specific payload format. Such mechanisms are out of scope for this OTEP, but reusing the record layout where practical allows readers to share parsing logic across runtimes.

When a request context is attached or detached from a thread, the SDK publishes select information including trace ID, span ID, and trace flags in the format described in this document to the appropriate thread-local. When an external reader observes this thread it checks to see if any such TLS data has been attached, and if so, includes it in its telemetry.

### Interaction with other context sources

A valid thread-local context record represents the publishing SDK's view of the active OpenTelemetry context for the observed thread. Readers SHOULD treat this context as authoritative for the OpenTelemetry context fields it provides.

Other context sources, such as OBI-derived information, may still be used to enrich observations or as a fallback when SDK-published thread context is unavailable. If a reader chooses to override or merge conflicting SDK-published context with another source, it SHOULD document that policy explicitly.

### Goals

This mechanism is designed to achieve the following goals:

* **Reader flexibility**: Readers are not limited to eBPF-based implementations; any external reader with sufficient permissions to inspect `/proc/<pid>/maps` for library discovery and to read target process memory should be able to use this mechanism  (nb: [OTEP-4719](4719-process-ctx.md) also requires access to this resource)
* **Runtime compatibility:** This mechanism is an optional extension to an OpenTelemetry SDK for languages that are able to use ELF TLS and have an appropriate threading model. We have tested it with C/C++, Rust, and Java, and intend this to work with other runtimes as well, see "What does this mean in practice for runtimes supported by OTel SDKs?" section below.
* **Low, opt-in overhead**: Context attach/detach is a performance critical path in an OpenTelemetry SDK, and this mechanism is designed to provide fixed, low overhead when serializing thread context
* **Simplicity:** Limit the implementation complexity on both writer and reader sides.

## Internal details

### Process Context: Thread-Local Reference Data

This is process-wide data that the TLS data will reference. It will be stored in the [Process Context introduced by OTEP 4719](4719-process-ctx.md) as entries in the `ProcessContext.attributes` field.

The following values are stored:

* `threadlocal.schema_version` - type and version of the schema - initially `tlsdesc_v1_dev` for experimentation (to be changed to `tls_v1` once the OTEP gets merged)
  * Note: Beyond evolution of the format, having the type of the schema allows the application to e.g. signal that it's a Go application and thus context should be read from [Go pprof labels and not the thread-local](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/tree/main/design-docs/00002-custom-labels) or from a different offset for [Node.js](https://www.polarsignals.com/blog/posts/2025/11/19/custom-labels-for-node-js). (Such alternative schemas would be subject of separate documents)
* `threadlocal.attribute_key_map` - provides a mapping from **key indexes** (uint8 maximum) to **attribute names** (string). The thread-local storage itself will then use these key indexes in place of the **attribute names**.

> **Note:** The `threadlocal.*` keys are defined here rather than as semantic conventions because they are inter-process coordination metadata, not telemetry attributes, and are not expected to appear in OTLP exports.

The exact format used will be the `repeated KeyValue` protobuf structure from the `ProcessContext.attributes` field standardized in OTEP-4719. A stringified representation of this showing the usage of the elements of that schema along with some example values:

```yaml
key: "threadlocal.schema_version"
value:
  string_value: "tlsdesc_v1_dev"

key: "threadlocal.attribute_key_map"
value:
  array_value:
    values:
      - string_value: "http_route"   # index 0
      - string_value: "http_method"  # index 1
      - string_value: "user_id"      # index 2
```

**Why:** this mechanism separates static, process-scoped data from the TLS storage, so that a reader can read it once and not every time it samples a thread.
This reduces the cost of both writing and reading thread samples, while retaining flexibility to store an arbitrary set of extra attributes on samples as required.
By leveraging OTEP 4719 we are also collocating with another feature that is likely to be used by many of the same readers.

#### `attribute_key_map` dictionary semantics

The key map is intended to attach a minimal set of contextual attributes to profiles, so that samples remain useful even when trace data is unavailable. The `attribute_key_map` is append-only: entries are added but never removed or reordered. Existing key indexes remain stable once assigned, so readers can treat previously-seen indexes as valid without re-reading the full map.

Keys do not need to be registered at process startup. New keys may be appended over time as the SDK encounters new attribute names. Updates are expected to be infrequent; in practice, the key set is typically established early in the process lifetime. Prior implementations have shown that a small number of keys is sufficient for the common case.

When a key is appended, the SDK must update the `attribute_key_map` entry in the Process Context. Readers rely on the OTEP 4719 update protocol to read the entire Process Context block free of torn/corrupted reads. The SDK is responsible for ensuring it acts as a single writer to the Process Context, e.g. via a mutex or equivalent internal coordination across its own threads, so that concurrent key appends from multiple application threads do not race with each other or violate the OTEP 4719 update protocol.
As long as writers correctly execute the OTEP 4719 update protocol, the OTEP 4719 reader protocol guarantees that readers will observe a correct and complete process context payload, including the `attribute_key_map`, even when a reader is concurrent/racing with a writer.

The uint8 key index caps the map at 256 entries. This is a conscious trade-off for v1; if it proves limiting, future versions may extend the dictionary or allow inline keys for high-cardinality use cases.

Having read the record, the reader then processes `attrs-data` to resolve each key index against its cached `attribute_key_map`. If it encounters an index it doesn't recognize at that point, it MUST refresh the cached map before continuing.

### Thread-Local Variable Resolution

`otel_thread_ctx_v1` must be exported as an ELF TLS symbol in the dynamic symbol table (`.dynsym`), even for statically linked binaries (e.g. via `--export-dynamic-symbol` or equivalent linker options). The following TLS access models are supported:

- **Global Dynamic / TLSDESC** (recommended): the symbol uses the TLSDESC dialect (e.g. `-mtls-dialect=gnu2` in GCC or Clang), producing TLSDESC relocations in shared libraries. This is the preferred model as it offers the best runtime performance for the writer.
- **Global Dynamic / legacy GNU**: the symbol uses traditional GNU TLS General Dynamic relocations. This is supported but not preferred.
- **Static access (initial-exec or local-exec)**: linkers may relax a Global Dynamic reference to initial-exec or local-exec when the variable's module is known at link time, for example when `otel_thread_ctx_v1` is defined in a main executable. This relaxation is outside the writer's control and readers MUST handle it.

The Local Dynamic model is not supported.

Writers SHOULD use the TLSDESC dialect where practical, as it offers better write-path performance.
Readers MUST support all three models above, see "Reading Protocol" section for details.

### Thread-Local Variable

We introduce a single thread-local - `otel_thread_ctx_v1`. This is a pointer to the active **Thread-Local Context Record** associated with the given thread.

### Thread-Local Context Record

This is the attached thread record itself. SDK-side implementations may choose to hold multiple instances of this for active spans, and attach/detach them by setting the TLS to point to the appropriate entry. We err on the side of simplicity and support string (utf-8 bytes) attributes only.

The record layout is byte-packed exactly as shown, with no implicit compiler padding between fields. Multi-byte fields are in native machine (host) endianness.

| Name            |            | Data type                          | Notes                                                                                                                                                    |
| :-------------- | :--------- | :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| trace-id        |            | uint8[16]                          | In W3C Trace Context format. Zeroes can be used to indicate none active. If either of trace-id/span-id are set, both must be set.                        |
| span-id         |            | uint8[8]                           | In W3C Trace Context format.                                                                                                                             |
| valid           |            | uint8                              | This value is set to 1 when the record is valid. Consumers should ignore this record if any other value is set  when they read. All other values are reserved and treated as invalid. |
| trace-flags     |            | uint8                              | W3C Trace Context trace-flags byte associated with trace-id/span-id above, including the sampled and random-trace-id bits. Zero if trace-id/span-id are unset. Also serves to align attrs-data-size at a two byte boundary.                          |
| attrs-data-size |            | uint16                             | Size of `attrs-data`. This lets the reader know when it has consumed all `attrs-data` records within the TLS buffer. The total record is recommended to stay at or under 640 bytes. |
| attrs-data      |            | uint8[]                            | A byte buffer containing the attributes themselves. Its total length is given by `attrs-data-size`.                                                      |
|                 | [x].key    | uint8 (*See below for alternative) | Index into the key table. Readers MUST ignore entries whose key index is outside `threadlocal.attribute_key_map`.                                        |
|                 | [x].length | uint8 (*See below for alternative) | Length of val string                                                                                                                                     |
|                 | [x].val    | uint8[length] (utf-8 bytes)        | Inline array of the string value itself. Exactly `length` bytes appear here, before the next attribute entry begins.                                     |

Entries in `attrs-data` are packed consecutively with no padding between entries.
Readers MUST stop parsing `attrs-data` if the remaining buffer cannot hold a complete entry.
If the same key index appears more than once in `attrs-data`, readers MUST use the last occurrence. This allows writers to append an updated value for an existing key without rewriting prior entries.

The record MUST start at an address aligned to at least a 2-byte boundary.

This format usually relies on two reads - one to read the required fields up to and including `attrs-data-size` (first 28 bytes), and a second to read any custom attributes.

**Why this layout**: It is scalable; if a writer is configured to publish only the required attributes and no custom fields, it can set `attrs-data-size` to 0; having read the first portion of the structure, the reader stops without having to read the rest.

**Cache Impact:** Likewise, a frugal writer may aim to keep the entire record under 64 bytes (the typical size of a cache line) in which case we might expect the entire record to be in cache after the first read.  This format takes 28 bytes for the lead in, then an overhead of 2 bytes per key-value pair.
For a single pair, we'd have 34 bytes for the value (64b total -28b lead in -1b key -1b length); for two, 32 bytes total (previous value -1b key -1b length).
If we expected to track attributes such as `path` and `method`, this means we'd realistically expect to fit in a single cache line of 64 bytes. We recommend keeping at or under 640 bytes for the total record [to match the limit](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/tree/main/design-docs/00002-custom-labels#proposed-solution) on the OTel eBPF Profiler.

***Possible alternative/request for comments:** Switch one or both of `[x].key` and `[x].length` to being a [protobuf-style variable-length integer](https://protobuf.dev/programming-guides/encoding/#varints). This would allow more than 255 keys or longer value lengths than 255 bytes, if needed. Do we want this?*

### Publication Protocol

The publishing SDK makes thread-local context available to external readers through the following sequence:

#### 1. Process Initialization

At process startup, the SDK:

* Publishes the **Thread-Local Reference Data** to the **Process Context** (per OTEP-4719):
  * `threadlocal.schema_version`: version of the schema for compatibility checking
  * `threadlocal.attribute_key_map`: mapping from key indexes (uint8) to attribute names
* The SDK takes note of the `attribute_key_map` as this is used to prepare the TLS data itself.

#### 2. Context Attachment

When a request context is attached to a thread, the SDK:

1. Obtains a contiguous buffer large enough to store the anticipated record size
2. Constructs a new **Thread-Local Context Record**  within the buffer containing:
   - Trace context (trace ID, span ID, trace flags)
   - Any configured attributes, encoded per the record format
3. Sets the `valid` field to indicate the record is complete
4. Updates the TLS pointer to reference the new record

If reusing storage that may already be visible to readers, the SDK MAY first set the TLS pointer to `NULL` to ensure readers see no record during construction.

Note: the SDK is free to re-use existing buffers to save allocations in this path.

Alternatively, a SDK may choose to leave the TLS pointer pointing to a fixed record, and instead mutate the `valid`
flag during updates only. Assuming the TLS pointer is set once per-thread to point to a fixed record, the update process becomes:

1. Sets the `valid` flag to `false`
2. Updates the **Thread-Local Context Record** for the thread as required
3. Sets the `valid` field to `true` to indicate the record is complete

A SDK should choose to either set/unset the TLS pointer itself, or the `valid` flag, but not both.
The intention of this design is to enable flexibility for the writers. We envision that some writers may choose to keep a fixed record for a given thread and can thus mutate it in-place, and that other writers may instead keep the record associated with some other high-level concept (coroutine, request, etc) and swap out the pointer as needed when they become active on any given thread.

In both cases, all pointer and validity updates use compiler fences (`atomic_signal_fence` or equivalent) and volatile writes to prevent instruction reordering by the compiler. This design assumes signal handler-like semantics, therefore it is unnecessary to guard against CPU reordering.

#### 3. Context Detachment

When a request context is no longer active on a thread, the SDK either sets the TLS pointer to `NULL`, or sets the `valid` flag to `false`.

#### Design Considerations

**Record reuse**: SDKs may implement caching strategies where records for frequently-reattached contexts (e.g., a parent span that is repeatedly entered and exited) are retained rather than reconstructed. The `valid` field can alternatively be used to mark a record as under modification without detaching it entirely.

**Allocation:** Implementations may choose to preallocate storage for some fixed set of **Thread-Local Reference Data** instances. This removes the need to allocate in the hot path.

**Concurrency model**: Unlike the process context (OTEP 4719), where the writer races asynchronously with the reader and CPU memory barriers are mandated, thread context assumes signal handler-like semantics.
In practice, context reads are expected to behave as if the thread whose context is being read is stopped or otherwise interrupted. Since this protocol requires a thread's context record to be updated only by that same thread, there can't be any concurrency hazards between reads and writes.
This means CPU memory ordering is not a concern.
Writers need only use compiler fences (`atomic_signal_fence` or equivalent) and/or volatile writes to prevent compilers from reordering writes to the context with those to `valid` or the TLS pointer.
These fences are expected to carry no runtime cost.
Readers conforming to this specification MUST only read thread context while the target thread is stopped or interrupted (e.g. via eBPF perf events, ptrace-stop, or equivalent mechanisms).

### Reading Protocol

External readers (such as the OpenTelemetry eBPF profiler) discover and read thread-local context as follows. The reading protocol assumes the reader observes each thread while it is stopped or interrupted.

#### 1. Process Initialization

The external reader discovers a new process to observe. It:

1.1 **Locates the process context**

* The reading protocol from OTEP-4719 is followed to obtain the **Thread-Local Reference Data** resources from the **Process Context**
* The reader may choose to retain the information read from the process mappings at this point, as they are immediately needed for TLS resolution
* Note that OTEP-4719 allows for updates to the **Process Context** an thus the **Thread-Local Reference Data** may show up during one of these updates and is not guaranteed to exist from the first published context

1.2. **Check binary and loaded libraries for TLS dynsym**

If the `threadlocal.*` keys are not present in the process context at this point, the reader should defer TLS symbol discovery and re-run step 1.2 when the process context is next updated.
Readers can detect process context updates using the polling or prctl-hook mechanisms described in OTEP-4719.

* Generate a list of dynamic libraries loaded by the process from the process mappings in `/proc/<pid>/maps`
* For each of the process itself and its dynamically loaded libraries:
  * Check if the `dynsym` table contains the TLS symbols listed above
  * If it does, collect them
* Note down the TLS offset for **Thread-Local Reference Data** discovered

Once the `threadlocal.*` keys are present and TLS symbols have been discovered, the reader has everything it needs to begin sampling threads.

For more details omn how to find the offsets of the TLS see [this google doc](https://docs.google.com/document/d/1eatbHpEXXhWZEPrXZpfR58-5RIx-81mUgF69Zpn3Rz4/edit?tab=t.v43rcsc1d6p9).

#### 2. Thread Sampling

The external reader reads the **Thread-Local Reference Data** TLS record for the targeted thread, obtaining a pointer to an instance of a **Thread-Local Context Record.**

If the pointer is null, no context record is attached and the reader is done.

If the pointer is not null, the reader first reads the fixed 28-byte record header from the pointer, obtaining the trace context, validity flag, and `attrs-data-size`. If the record is valid and `attrs-data-size` is non-zero, the reader performs a second read of attrs-data-size bytes starting at offset 28 to obtain the custom attribute data.

This buffer can then be parsed according to the specification above at the reader's leisure.

### Interaction with Existing Functionality

#### OpenTelemetry SDK

This mechanism is additive and does not modify existing OpenTelemetry SDK behaviour.

#### OpenTelemetry - Process Context

The **Thread-Local Reference Data** is to be added to the **Process Context Proposal**:

* The lifecycle of the **Thread-Local Reference Data** is more accurately tied to the process not the thread
* The consumers of the **Process Context** are likely to substantially overlap the consumers of the **Thread Level Context**

## Trade-offs and mitigations

### Host and Permission Requirements

This mechanism requires that the external reader (such as an eBPF profiler) is running on the same host as the instrumented process and has sufficient privileges to access the memory mappings exposed by the process and read target process memory.

External readers such as the OpenTelemetry eBPF Profiler will typically already have these permissions by design. This approach does not support remote or cross-host correlation of process context, and attempts to access the process context mappings without appropriate permissions (e.g., from an unprivileged user) will fail.

### Complexity for SDK Implementers

Exporting a TLS symbol and ensuring it ends up in the process's `dynsym` table adds complexity to SDK implementations.

**Mitigation:** We've created an extension of the existing PolarSignals [custom-labels](https://github.com/polarsignals/custom-labels) work, providing a reference implementation in C and bindings in Rust.

### Complexity for End Users building from source

Ensuring that TLS symbols published by the SDK end up in an application's `dynsym` table, when building native binaries from source (e.g. for Rust) requires some language configuration of the build tools by the end user themselves.

### Protocol Evolution

As requirements evolve, we may need to extend the payload format.

**Mitigation**: The design includes both versioning as well as allowing extension points

1. **Open-ended custom attributes set**: Can be configured by the SDK, user, or both, to expose relevant attributes to thread-local storage. Can also be configured to the empty set to reduce overhead.
2. **Version number**: for incompatible changes (not expected to change frequently)

### Memory Overhead

By separating frequently changing **Thread-Local Context Record** data from static, process-wide **Thread-Local Reference Data**, we ensure that:

* Overhead of repeating attribute key names is minimized with indexing scheme
* Memory overhead of TLS context reads is reduced, minimizing the time a thread must be kept suspended, and reducing the impact on the CPU cache

### Trace Sampling

An out of process reader has no ability to influence the sampling decisions of the in-process tracer; samples collected may therefore reference trace data that was not exported by the SDK, and cannot be used to enrich the sample with request metadata such as `route`. This limits the use of any samples captured under these conditions.

**Mitigation:** by allowing the optional addition of custom key-value pairs to the **Thread-Local Context Record,** an SDK can be configured to ensure core attribute information is shared with the external reader directly. This could be used for instance to attach `route` to each sample.

## What does this mean in practice for runtimes supported by OTel SDKs?

As mentioned above in the document, this mechanism is intended to be optional as not all runtimes and runtime versions are able to feasibly/efficiently implement it.

So far, we've looked at a number of runtimes/languages and we list below what we've learned of their feasibility.
This section is not intended to constrain implementers of the specification (nor to mandate that SDKs adopt this feature if they have no interest in it), but rather to indicate how likely we currently believe this is to fit with those languages/runtimes:

* **C/C++:** Full support
* **Rust**:  Full support. Requires linking against a native library in order to ensure the TLS symbol is exposed correctly (see [here](https://github.com/rust-lang/rust/pull/132480))
* **Java**: Full support. Requires calling into native library (e.g. via JNI or equivalent API)
* **.NET:** Full support via FFI bindings to native library
* **Python:** Full support using native library. Tracers running on Python >= 3.14 can use [PyContext_WatchCallback](https://docs.python.org/3/c-api/contextvars.html#c.PyContext_WatchCallback) to track context activation; older versions must monkey-patch the runtime
* **Ruby:** Full support via native extension. [ruby-profiler gem](https://github.com/socketry/ruby-profiler) shows an example of a very similar approach to doing this in Ruby (from Shopify)

We believe these two runtimes are not going to be supported by this proposal for the foreseeable future (details below):

* **Go:**
* **Node.js**:

### Alternative for Go support

Because of its fine-grained goroutine based concurrency model and relative cost of calling across an FFI, we foresee Go readers will directly read
[pprof labels](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/blob/main/design-docs/00002-custom-labels/README.md).

Go SDKs should publish a **Context Reference Data** with

```yaml
key: "threadlocal.schema_version"
value:
  string_value: "go_pprof_labels_v1"
```

and no (or empty) `threadlocal.attribute_key_map`.

### Alternative for Node.js support

We do not expect Node.js to use the TLS publication mechanism directly, due to the threading model and the performance impact of crossing a Node-API/native FFI boundary on context attach/detach.

Node.js readers are more likely to discover context through Node.js-specific runtime internals, as in
[Polar Signal's profiler](https://www.polarsignals.com/blog/posts/2025/11/19/custom-labels-for-node-js).
However, a separate Node.js-specific proposal is expected to reuse the **Thread-Local Context Record** in-memory format, with only the discovery mechanism being Node.js-specific.

An upcoming proposal will define the details of discovery and the expected `threadlocal.schema_version` that Node.js should use.

## Prior art and alternatives

There are two existing TLS mechanisms we are aware of for sharing similar information that we took inspiration from. In both cases the same mechanism is used for TLS discovery and access as described here, the differences are only in the storage format:

[**Elastic Universal Profiling Integration**](https://github.com/elastic/apm/blob/149cd3e39a77a58002344270ed2ad35357bdd02d/specs/agents/universal-profiling-integration.md#process-storage-layout)**:** Uses a simple, flat memory, fixed-length layout behind a single TLS capturing core trace information (parent, flags, ID, span ID, transaction ID) only. This is simple to implement and fast to read and write.

[**Polar Signals Custom Labels**](https://github.com/polarsignals/custom-labels/blob/master/custom-labels-v1.md#custom_labels_current_set)**:** An alternative to the elastic model, additionally supporting custom key-value pairs.

This proposal attempts to unify the benefits of these two approaches by providing the flexibility of the **Polar Signals** format with the static allocation and read time performance of the **Elastic** format.

**TLS Value Storage**: If we assume that the value of the attributes attached to profiles is from a fixed, but unknown-at-startup set, we could also choose to store these in a shared hashmap outside of the Thread-Local Context Record itself, further reducing the size of the record and the cost associated with reading/writing it. This would be the case if we stored attributes for things like `http_method`, and `http_route`, and not things like `uuid()`. It would also require a process wide hash table implementation with lock-free reads. There is prior art in Datadog's [Java profiler's context sharing mechanism](https://github.com/DataDog/java-profiler/blob/main/ddprof-lib/src/main/java/com/datadoghq/profiler/ContextSetter.java).

### macOS and Windows support

We decided to keep this OTEP Linux-specific as:

* We expect the first consumers of this to be the
  [eBPF Profiler](https://github.com/open-telemetry/opentelemetry-ebpf-profiler) and
  [OBI](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation) both of which are Linux-specific due to their current heavy use of eBPF hooks
* While all modern operating systems provide thread-locals, there is a very different security model across them (especially on macOS),
  and because of that it's not clear that this option would be the best one there
* The proposed mechanism is quite low-level and with very tight efficiency goals.
  We believe it's better to later evaluate how exactly they would map to other operating systems with more care,
  rather than going "everyone has thread locals so this should be fine"

## Open questions

1. Are the current limits on key and value count and length acceptable/the right trade-off?

2. Should there be a way to provide dynamic keys without needing to add them via the `attribute_key_map`?

## Prototypes

* Readers:
  * **[ctx-sharing-demo reader](https://github.com/scottgerring/ctx-sharing-demo/tree/main/context-reader)**: Sample reader, based on PolarSignals' [custom-labels](https://github.com/polarsignals/custom-labels/tree/master) work
  * **[OpenTelemetry eBPF Profiler PR](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/pull/1229)**: Reads thread context information and propagates it with profiles

* Writers:
  * **[ctx-sharing-demo repo](https://github.com/scottgerring/ctx-sharing-demo)**: Multiple writer examples, including in rust and C
  * **[opentelemetry-rust](https://github.com/open-telemetry/opentelemetry-rust/compare/main...scottgerring:opentelemetry-rust:feat/otep-4719)**: Experimental implementation of both process context and thread context for rust SDK
  * **[Node.js thread context](https://github.com/polarsignals/custom-labels/tree/otel-thread-ctx-wip/js)**: Experimental implementation of thread context for Node.js
  * **[libdd-otel-thread-ctx](https://github.com/DataDog/libdatadog/tree/main/libdd-otel-thread-ctx)**: Datadog's open-source implementation of thread context in Rust
  * **[Datadog's dd-trace-java SDK](https://github.com/DataDog/java-profiler/pull/347)**: Shows a high-performance implementation of thread context, and includes adoption of this mechanism by an in-process profiler, demonstrating applicability beyond eBPF-based readers

## Future possibilities

Like OTEP 4719 and the OTel eBPF Profiler before it, this proposal specifies a Linux-only mechanism.
In the future, we may explore similar mechanisms for other operating systems.
