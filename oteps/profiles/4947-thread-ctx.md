# Thread Context: Sharing Thread-Level Information with the OpenTelemetry eBPF Profiler

Introduce a standard mechanism for OpenTelemetry SDKs to publish thread-level attributes for out-of-process readers such as the OpenTelemetry eBPF profilers.
It is related to [OTEP 4719: Process Context](https://github.com/open-telemetry/opentelemetry-specification/pull/4719).

There is a complete example of the spec as well as example readers and writers in <https://github.com/scottgerring/ctx-sharing-demo>(possibly to be moved to [open-telemetry/sig-profiling](https://github.com/open-telemetry/sig-profiling)?).

Our work-in-progress implementation of this on the OTel eBPF Profiler side is at [https://github.com/open-telemetry/opentelemetry-ebpf-profiler/pull/1229](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/pull/1229).

## Motivation

External readers like the OpenTelemetry eBPF Profiler operate outside the instrumented process and cannot collect information about active OpenTelemetry traces running within the process they are sampling. This creates two main problems:

* **Inability to correlate samples with context metadata** - For instance, the OpenTelemetry eBPF profiler collects stack samples from observed processes; without visibility into context information - for instance, the span active on each sample - a user cannot attribute the performance characteristics of their service to particular HTTP endpoints or other request characteristics
* **Lack of request metadata for samples collected on threads with un-sampled traces** - in many cases, the active span observed by the external process *may not* be sampled by the OpenTelemetry SDK. In these cases it is useful to make extra metadata available directly to the external process, so that its samples maintain useful context even in the face of sampling on the tracer side.

## Explanation

We propose a mechanism for OpenTelemetry SDKs to publish thread-level information reflecting the context of the active request, if any, through a standard format based on the ELF Thread Local Storage (TLS) TLSDESC dialect.

Because this mechanism relies on having a native component and knowing when a runtime switches contexts, we consider it optional for SDKs to support, as some runtimes (or even runtime versions) may not be able to feasibly/efficiently implement it.

When a request context is attached or detached from a thread, the SDK publishes select information including trace ID, span ID in the format described in this document to the appropriate thread local. When an external reader such as the OpenTelemetry eBPF profiler samples this thread it checks to see if any such TLS data has been attached, and if so, includes it in its sample.

This mechanism is designed to achieve the following goals:

* **Reader flexibility**: Readers are not limited to eBPF-based implementations; any external process with sufficient system permissions to read `/proc/<pid>/maps` to identify loaded libraries, as well as sufficient permission to read from process memory should be able to use this mechanism  (nb: OTEP-4719 also requires access to this resource)
* **Runtime compatibility:** This mechanism is an optional extension to an OpenTelemetry SDK for languages that are able to use TLSDESC and have an appropriate threading model. We have tested it with C/C++, Rust, and Java, and intend this to work with other runtimes as well, see "What does this mean in practice for runtimes supported by OTel SDKs?" section below.
* **Low, opt-in overhead**: Context attach/detach is a performance critical path in an OpenTelemetry SDK, and this mechanism is designed to provide fixed, low overhead when serializing thread context
* **Simplicity:** Limit the implementation complexity on both writer and reader sides.

## Internal details

### Process Context: Thread Local Reference Data

This is immutable, process-wide data that the TLS data will reference. It will be stored in the [Process Context introduced by OTEP 4719](https://github.com/open-telemetry/opentelemetry-specification/pull/4719) under two resources which will be set once at process startup and are subsequently considered immutable.

The following values are stored:

* `threadlocal.schema_version` - type and version of the schema - initially "tlsdesc\_v1\_dev" for experimentation (to be changed to "tlsdesc\_v1" once the OTEP gets merged)
  * Note: Beyond evolution of the format, having the type of the schema allows the application to e.g. signal that it's a go application and thus context should be read from [go pprof labels and not the thread-local](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/tree/main/design-docs/00002-custom-labels) or from a different offset for [node.js](https://www.polarsignals.com/blog/posts/2025/11/19/custom-labels-for-node-js). (Such alternative schemas would be subject of separate documents)
* `threadlocal.attribute_key_map` - provides a mapping from **key indexes** (uint8 maximum) to **attribute names** (string). The thread local storage itself will then use these key indexes in place of the **attribute names**.

The exact format used will be the protobuf structure standardized in OTEP-4719. A stringified representation of this showing the usage of the elements of that schema along with some example values:

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
By leveraging OTEP 4719 we are also co-locating with another feature that is likely to be used by many of the same readers.

### Thread Local Variable Resolution

TLS are stored in the **dynamic symbols** table of the process binary itself or of any shared library loaded by the process using the TLSDESC dialect. [TLSDESC](https://www.fsfla.org/~lxoliva/writeups/TLS/RFC-TLSDESC-x86.txt) was created to allow for highly efficient thread local accesses, significantly reducing overhead compared to traditional TLS models.

### Thread Local Variable

We introduce a single thread local - `custom_labels_current_set_v2` (working name). This is a pointer to the active **Thread Local Context Record** associated with the given thread.

### Thread Local Context Record

This is the attached thread record itself. SDK-side implementations may choose to hold multiple instances of this for active spans, and attach/detach them by setting the TLS to point to the appropriate entry. We err on the side of simplicity and support stringy (utf-8 bytes) attributes only.

| Name            |            | Data type                          | Notes                                                                                                                                                    |
| :-------------- | :--------- | :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| trace-id        |            | uint8[16]                          | In W3C Trace Context format. Zeroes can be used to indicate none active. If either of trace-id/span-id are set, both must be set.                        |
| span-id         |            | uint8[8]                           | In W3C Trace Context format.                                                                                                                             |
| valid           |            | uint8                              | This value is set to 1 when the record is valid. Consumers should ignore this record if any other value is set  when they read.                          |
| _reserved       |            | uint8                              | One spare byte here to align attrs-data-size at two byte boundary.                                                                                       |
| attrs-data-size |            | uint16                             | Size of `attr-data`. This lets the reader know when it has consumed all `attr-data` records within the TLS buffer.                                       |
| attrs-data      |            | uint8[]                            | A byte buffer containing the attributes themselves. Its total length can be derived from max-record-size of the parent minus the lead in of this record. |
|                 | [x].key    | uint8 (*See below for alternative) | Index into the key table                                                                                                                                 |
|                 | [x].length | uint8 (*See below for alternative) | Length of val string                                                                                                                                     |
|                 | [x].val    | uint8[length] (utf-8 bytes)        | Inline array of the string value itself. Exactly 'length' bytes appear here, before the next record begins.                                              |

This format usually relies on two reads - one to read the required fields up to and including `attrs-data-size` (first 28 bytes), and a second to read any custom attributes.

**Why this layout**: It is scalable; if a writer is configured to publish only the required attributes and no custom fields, it can set `attrs-data-size` to 0; having read the first portion of the structure, the reader stops without having to read the rest.

**Cache Impact:** Likewise, a frugal writer may aim to keep the entire record under 64 bytes (the typical size of a cache line) in which case we might expect the entire record is in cache after the first read.  This format takes 28 bytes for the lead in, then an overhead of 2 bytes per key-value pair.  For a single pair, we'd have 28 bytes for the value; for two, 26 bytes total. If we expected to track attributes such as `path` and `method`, this means we'd realistically expect to fit in a single cache line of 64 bytes. We recommend keeping at or under 640 bytes for the total record [to match the limit](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/tree/main/design-docs/00002-custom-labels#proposed-solution) on the OTel eBPF Profiler.

***Possible alternative/request for comments:** Switch one or both of `[x].key` and `[x].length` to being a [protobuf-style variable-length integer](https://protobuf.dev/programming-guides/encoding/#varints). This would allow more than 256 keys or longer value lengths than 256 bytes, if needed. Do we want this?*

### Publication Protocol

The publishing SDK makes thread local context available to external readers through the following sequence:

#### 1. Process Initialization

At process startup, the SDK:

* Publishes the **Thread Local Reference Data** to the **Process Context** (per OTEP-4719):
  * `threadlocal.schema_version`: version of the schema for compatibility checking
  * `threadlocal.attribute_key_map`: mapping from key indexes (uint8) to attribute names
* The SDK takes note of the `attribute_key_map` as this is used to prepare the TLS data itself.

#### 2. Context Attachment

When a request context is attached to a thread, the SDK:

1. Sets the TLS pointer to 0 to ensure readers see no record during construction
2. Obtains a contiguous buffer large enough to store the anticipated record size
3. Constructs a new **Thread Local Context Record**  within the buffer containing:
   - Trace context (trace ID, span ID, root span ID)
   - Any configured attributes, encoded per the record format
4. Sets the `valid` field to indicate the record is complete
5. Updates the TLS pointer to reference the new record

All pointer and validity updates are protected by memory barriers to ensure readers in other processes observe consistent state.

Note: the SDK is free to re-use existing buffers to save allocations in this path.

#### 3. Context Detachment

When a request context is no longer active on a thread, the SDK:

1. Sets the TLS pointer to `NULL`

#### Design Considerations

**Consistency during updates**: By setting the TLS pointer to `NULL` before constructing a new record, the SDK ensures readers never observe partially-written data. Readers that sample a thread during this window simply see no active context.

**Record reuse**: SDKs may implement caching strategies where records for frequently-reattached contexts (e.g., a parent span that is repeatedly entered and exited) are retained rather than reconstructed. The `valid` field can alternatively be used to mark a record as under modification without detaching it entirely.

**Allocation:** Implementations may choose to preallocate storage for some fixed set of **Thread Local Reference Data** instances. This removes the need to allocate in the hot path.

**Memory barriers**: Updates to the TLS pointer and `valid` field must use appropriate memory ordering to ensure visibility to readers accessing thread memory from another process.

### Reading Protocol

External readers (such as the OpenTelemetry eBPF profiler) discover and read thread local context as follows:

#### 1. Process Initialization

The external reader discovers a new process to observe. It:

1.1 **Locates the process context**

* The reading protocol from OTEP-4719 is followed to obtain the **Thread Local Reference Data** resources from the **Process Context**
* The reader may choose to retain the information read from the process mappings at this point, as they are immediately needed for TLS resolution

1.2. **Check binary and loaded libraries for TLS dynsym**

* Generate a list of dynamic libraries loaded by the process from the process mappings in `/proc/<pid>/maps`
* For each of the process itself and its dynamically loaded libraries:
  * Check if the `dynsym` table contains the TLS symbols listed above
  * If it does, collect them
* Note down the TL offset for **Thread Local Reference Data** discovered

At this point the reader has everything it needs to begin sampling threads.

#### 2. Thread Sampling

The external reader reads the **Thread Local Reference Data** TLS record for the targeted thread, obtaining a pointer to an instance of a **Thread Local Context Record.**

If the pointer is null, no context record is attached and the reader is done.

If the pointer is not null, the reader first reads the fixed 28-byte record header from the pointer, obtaining the trace context, validity flag, and `attrs-data-size`. If the record is valid and `attrs-data-size` is non-zero, the reader performs a second read of attrs-data-size bytes starting at offset 28 to obtain the custom attribute data.

This buffer can then be parsed according to the specification above at the reader's leisure.

### Interaction with Existing Functionality

#### OpenTelemetry SDK

This mechanism is additive and does not modify existing OpenTelemetry SDK behaviour.

#### OpenTelemetry - Process Context Proposal

The **Thread Local Reference Data** is to be added to the **Process Context Proposal**:

* The lifecycle of the **Context Reference Data** is more accurately tied to the process not the thread
* The consumers of the **Process Context** are likely to substantially overlap the consumers of the **Thread Level Context**

## Trade-offs and mitigations

### Host and Permission Requirements

This mechanism requires that the external reader (such as an eBPF profiler) is running on the same host as the instrumented process and has sufficient privileges to access the memory mappings exposed by the process and read target process memory.

The OpenTelemetry eBPF profiler, by design, has the necessary permissions and operates on the same machine to read this metadata. This approach does not support remote or cross-host correlation of process context, and attempts to access the process context mappings without appropriate permissions (e.g., from an unprivileged user) will fail.

### Complexity for SDK Implementers

Creating TLSDESC variables and ensuring they end up in the processes `dynsym` table adds complexity to SDK implementations.

**Mitigation:** We've created an extension of the existing PolarSignals [custom-labels](https://github.com/polarsignals/custom-labels) work, providing a reference implementation in C and bindings in Rust.

### Complexity for End Users building from source

Ensuring that TLSDESC variables published by the SDK end up in an application's `dynsym` table, when building native binaries from source (e.g. for Rust) requires some language configuration of the build tools by the end user themselves.

### Protocol Evolution

As requirements evolve, we may need to extend the payload format.

**Mitigation**: The design includes both versioning as well as allowing extension points

1. **Open-ended custom attributes set**: Can be configured by the SDK, user, or both, to expose relevant attributes to thread local storage. Can also be configured to the empty set to reduce overhead.
2. **Version number**: for incompatible changes (not expected to change frequently)

### Memory Overhead

By separating frequently changing **Thread Local Context Record** data from static, process-wide **Context Reference Data**, we ensure that:

* Overhead of repeating attribute key names is minimized with indexing scheme
* Memory overhead of TLS context reads is reduced, minimizing the time a thread must be kept suspended, and reducing the impact on the CPU cache

### Trace Sampling

An out of process reader has no ability to influence the sampling decisions of the in-process tracer; samples collected may therefore reference trace data that was not exported by the SDK, and cannot be used to enrich the sample with request metadata such as `route`. This limits the use of any samples captured under these conditions.

**Mitigation:** by allowing the optional addition of custom key-value pairs to the **Thread Local Context Record,** an SDK can be configured to ensure core attribute information is shared with the external reader directly. This could be used for instance to attach `route` to each sample.

## What does this mean in practice for runtimes supported by OTel SDKs?

As mentioned above in the document, this mechanism is intended to be optional as not all runtimes and runtime versions are able to feasibly/efficiently implement it.

So far, we've looked at a number of runtimes/languages and we list below what we've learned of their feasibility.
This section is not intended to constrain implementers of the specification (nor to mandate that SDKs adopt this feature if they have no interest on it), but rather to indicate how likely we currently believe this is to fit with those languages/runtimes:

* **C/C++:** Full support
* **Rust**:  Full support. Requires linking against a native library in order to ensure the TLS symbol is exposed correctly (see [here](https://github.com/rust-lang/rust/pull/132480))
* **Java**: Full support. Requires calling into native library (e.g. via JNI or equivalent API)
* **Dotnet:** Full support via FFI bindings to native library
* **Python:** Full support using native library. Tracers running on Python >= 3.14 can use [PyContext_WatchCallback](https://docs.python.org/3/c-api/contextvars.html#c.PyContext_WatchCallback) to track context activation; older versions must monkey-patch the runtime
* **Ruby:** Full support via native extension. [ruby-profiler gem](https://github.com/socketry/ruby-profiler) shows an example of a very similar approach to doing this in Ruby (from Shopify)

We believe these two runtimes are not going to be supported by this proposal:

* **Golang:** We foresee golang readers will continue to use the [pprof labels](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/blob/main/design-docs/00002-custom-labels/README.md) due to its fine-grained goroutine based concurrency model and relative cost of calling across an FFI
* **NodeJS**: We expect nodeJS readers are more likely to read the NodeJS runtime internals directly due to the threading model and performance impact of using a Node-API/native TLS approach.This adds complexity to the reader but reduces the performance impact, and is already the approached used in [Polarsignal's profiler](https://www.polarsignals.com/blog/posts/2025/11/19/custom-labels-for-node-js).

## Prior art and alternatives

There are two existing TLS mechanisms we are aware of for sharing similar information that we took inspiration from. In both cases the same mechanism is used for TLS discovery and access as described here, the differences are only in the storage format:

[**Elastic Universal Profiling Integration**](https://github.com/elastic/apm/blob/149cd3e39a77a58002344270ed2ad35357bdd02d/specs/agents/universal-profiling-integration.md#process-storage-layout)**:** Uses a simple, flat memory, fixed-length layout behind a single TLS capturing core trace information (parent, flags, id, span ID, transaction ID) only. This is simple to implement and fast to read and write.

[**Polar Signals Custom Labels**](https://github.com/polarsignals/custom-labels/blob/master/custom-labels-v1.md#custom_labels_current_set)**:** An alternative to the elastic model, additionally supporting custom key/value pairs.

This proposal attempts to unify the benefits of these two approaches by providing the flexibility of the **polar signals** format with the static allocation and read time performance of the **elastic** format.

**TLS Value Storage**: If we assume that the value of the attributes attached to profiles is from a fixed, but unknown-at-startup set, we could also choose to store these in a shared hashmap outside of the Thread Local Context Record itself, further reducing the size of the record and the cost associated with reading/writing it. This would be the case if we stored attributes for things like `http_method`, and `http_route`, and not things like `uuid()`. It would also require a process wide hash table implementation with lock-free reads. There is prior art in Datadog's [java-profiler's context sharing mechanism](https://github.com/DataDog/java-profiler/blob/main/ddprof-lib/src/main/java/com/datadoghq/profiler/ContextSetter.java).

## Open questions

1. Are the current limits on key and value count and length acceptable/the right trade-off?

2. Should there be a way to provide dynamic keys without needing to add them via the `attribute_key_map`?

## Prototypes

- **[OpenTelemetry eBPF Profiler PR](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/pull/1229)**: Work-in-progress integration adding thread context support to the OpenTelemetry eBPF Profiler
- **[ctx-sharing-demo](https://github.com/scottgerring/ctx-sharing-demo)**: Sample writers and readers, based on PolarSignals' [custom-labels](https://github.com/polarsignals/custom-labels/tree/master) work
- **[Datadog java-profiler PR](https://github.com/DataDog/java-profiler/pull/347)**: Adoption of this mechanism by an in-process profiler, demonstrating applicability beyond eBPF-based readers

## Future possibilities

Like OTEP 4719 and the OTel eBPF Profiler before it, this PR proposes a Linux-only mechanism.
In the future, we may explore similar mechanisms for other operating systems.
