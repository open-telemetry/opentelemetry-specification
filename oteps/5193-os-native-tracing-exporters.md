# Exporting OpenTelemetry to OS-native tracing facilities (ETW and `user_events`)

Recognize emitting telemetry to OS-native tracing facilities, [Event Tracing for Windows (ETW)](https://learn.microsoft.com/windows/win32/etw/event-tracing-portal) on Windows and [`user_events`](https://docs.kernel.org/trace/user_events.html) on Linux, as a supported OpenTelemetry export path, and define how the OpenTelemetry data model (logs, spans, and metrics) maps onto them.

## Motivation

OpenTelemetry's exporting model today assumes telemetry leaves the process by being sent to an endpoint: OTLP to a collector or a backend, or a pull-based scrape such as Prometheus. Both deliver telemetry across the network to a listening endpoint. This has served the project well.

Getting telemetry out of a process is not unique to OpenTelemetry. Operating systems have offered facilities for it for a long time, built around a different model: ETW on Windows, and kernel tracepoints and the newer `user_events` interface on Linux. These facilities are mature, ubiquitous, and relied upon every day by kernel components, device drivers, and core operating-system services. They are a natural destination for application telemetry too, and one that OpenTelemetry does not yet take advantage of.

Two properties make them compelling as a telemetry destination:

1. Exporting an event is extremely fast: a synchronous, in-memory write to a kernel-backed, per-CPU buffer. There is no network client and no in-process batching. Because the buffers are per-CPU, concurrent emitters do not contend with each other, so throughput scales with CPU count.
2. Enablement is controlled out of band by the consumer. A tracing session started from outside the process decides at runtime whether a producer's telemetry is collected, with no change to and no redeploy of the running application. When nobody is listening, emission costs almost nothing.

Together these change the economics of instrumentation. Dense instrumentation and low telemetry cost stop being in tension. OpenTelemetry has made it easy to instrument applications richly; this model lets that richness be paid for only when the data is actually being collected. The appendix, ["Instrumentation density vs. telemetry cost"](#perspective-instrumentation-density-vs-telemetry-cost), develops this point.

These properties are complementary to OpenTelemetry's existing exporters rather than a replacement for them. OTLP remains the portable default for delivering telemetry across the network. What is missing is a recognized way for an OpenTelemetry SDK to *also* emit into an OS-native tracing facility when the properties above are wanted, and a defined contract for how the data model maps onto those facilities so that the events are interoperable.

Bringing these facilities into OpenTelemetry takes a set of techniques long proven in low-level system diagnostics and makes them available to the same instrumentation an application already has. One body of instrumentation can then serve both continuous, always-on collection and deeper, on-demand investigation.

### What this OTEP proposes

Concretely, this OTEP proposes that OpenTelemetry:

1. Define OS-native tracing exporters (ETW and `user_events`), together with the mapping from the OpenTelemetry data model (logs, spans, and metrics) onto each facility's native event model. This mirrors how OpenTelemetry has previously specified exporters, such as Zipkin (and formerly Jaeger), each paired with a defined data-model mapping. The mapping is largely common across the two facilities, with some differences that are inherent to ETW and `user_events`, and it is the interoperability contract that any consumer decodes against.
2. Specify the SDK pipeline component that emits these events and the emission semantics it must guarantee (synchronous, per-emit), so producer behavior and configuration are uniform across languages.
3. Keep the capability OPTIONAL per language SDK and additive, changing nothing about OTLP, the data model, or existing exporters.

The precise per-field encodings, naming rules, and configuration schema are left to the specification phase. The normative work is expected to proceed signal by signal, beginning with logs, where the enablement gate and the prior art are strongest, then spans, then metrics. This OTEP asks the community to agree that this is a direction worth specifying, and establishes the shape of that specification.

A note on terminology: this document uses "exporter" in the conceptual sense of telemetry leaving the process to a destination. For logs and spans the concrete SDK pipeline component that implements it is a *processor*, for the reasons explained under ["Pipeline modeling: a processor"](#pipeline-modeling-a-processor); metrics use the metric reader and exporter path (see [Metrics](#metrics)).

### Scope

This OTEP's scope is the producer (SDK) side: the exporter that writes telemetry to OS-native tracing facilities, and the mapping from the OpenTelemetry data model onto each facility's native event model. That mapping is the contract.

Once the mapping is established, the reading side follows from it and is out of scope here. Any consumer (native OS tools, the OpenTelemetry Collector, the [OpenTelemetry Arrow `df_engine`](https://github.com/open-telemetry/otel-arrow/tree/main/rust/otap-dataflow), or a vendor's own agent) can decode the events by following the same contract. How those consumers are built and deployed is governed outside this specification.

A few boundaries are worth stating explicitly. This OTEP focuses on ETW and `user_events` because they are mature and already have prior art; the same pattern can extend to other operating systems' facilities (for example macOS `os_log` and `os_signpost`, or DTrace) in later work, and those are out of scope here. It covers the logs, spans, and metrics signals; profiles are out of scope for now. It requires no changes to the OpenTelemetry API and introduces no new semantic conventions for telemetry content: it defines an on-host transport and an encoding of the existing data model, selected per signal through existing SDK extension points and declarative configuration.

## Explanation

### An optional exporter

Support is OPTIONAL per language SDK. This OTEP does not require any SDK to implement it, and it is reasonable for a language never to. Two reasons. Not every language has the performance profile where this matters; many are well served by OTLP. And not every language has convenient bindings to write to ETW or `user_events`. Rust, C++, and .NET already have APIs for these facilities and are the natural first implementations. Where no native support exists, an SDK could reach the facilities through FFI if the benefit justifies the effort. OTLP remains the portable default; OS-native export is an additional capability a language MAY provide.

### What the model provides

Exporting to an OS-native facility differs from network export in a few fundamental ways. Most of these properties are inherent to how the facilities work, not things this OTEP defines.

1. Synchronous local write, for performance and durability. A log or span is serialized and written to the facility on the calling thread, with no SDK-side buffering or batching. The write lands in a kernel-backed, per-CPU buffer, so it is fast and, being per-CPU and contention-free, scales with CPU count. Because a record accepted into that buffer is owned by the operating system, it survives an immediate crash of the application, unlike an in-process batch buffer, and the application can no longer alter or delete it. The buffer is bounded, sized by the consumer that starts the session, and its full behavior (dropping or overwriting) is well defined by the OS facility.
2. Consumer-controlled, out-of-band enablement. A tracing session started externally decides at runtime whether a producer's telemetry is collected, with no restart of the application. The facility exposes a cheap check for whether anyone is listening, so the producer can do almost no work when nobody is. This disabled fast path is strongest for logs today, where the processor can answer the OpenTelemetry logs `Enabled()` check (see ["The disabled fast path for Logs"](#the-disabled-fast-path-for-logs)) so that a disabled log is not constructed. Spans and metrics do not have a standardized equivalent yet; a span sampler can consult the same enablement signal, but that integration is follow-up work and should not be assumed today.
3. Readable by existing OS tooling, and by multiple consumers at once. Events land in a standard OS facility, so they can be read with existing tools ([`perf`](https://perfwiki.github.io/main/) on Linux; [`logman`](https://learn.microsoft.com/windows-server/administration/windows-commands/logman) and [PerfView](https://github.com/microsoft/perfview) on Windows) with no OpenTelemetry pipeline running. The facilities also allow multiple independent consumers on the same events, so an ad-hoc diagnostic session can observe the stream alongside the normal collector.
4. A simpler producer with a smaller attack surface. The application moves networking, TLS, authentication, endpoint configuration, retry, and buffering out of its own process and into the same-host consumer. That cost moves rather than disappears, but the application's telemetry path becomes a thin local write, with no HTTP/gRPC/TLS client, just a small library that formats and emits events. Backend credentials also stay out of the application's address space, held by the same-host consumer instead.
5. Resilience to consumer crashes, on ETW. Because nothing is buffered inside the application, records already written to the facility are not lost if the producer crashes. ETW extends this to the consumer: the session exists independently of the process reading it, so if the consumer crashes and restarts, the kernel keeps buffering meanwhile (within the session's configured buffer) and the reconnecting consumer drains what accumulated. On Linux, `user_events` does not offer this today, because enablement is reference-counted and recording stops when the last consumer detaches.
6. Access to the emitting call stack. Because emission is synchronous, the event is written on the same thread at the point where it originated, so a consumer that supports stack capture can record that thread's exact call stack at that moment (for example when a `FATAL` log is emitted). This is not possible when export happens later on a background thread, by which time the originating stack is gone.

### Usage

A deployment can adopt this in one of a few ways.

#### Full replacement of the local hop

All telemetry that would go from the application to a local collector is emitted through ETW or `user_events` instead, with no change to instrumentation or to the downstream pipeline. It does require running a same-host consumer to pick the events up and forward them onward (typically over OTLP); everything downstream of that consumer is unchanged. Per-event writes land in local memory, and the same-host consumer re-batches before the network hop, so downstream batching and compression are unchanged. A deployment may choose this purely for the higher performance, crash resilience, and lighter application (no in-process buffering, retry, or TLS) that it brings, without leveraging anything else the facility offers.

#### Selective OS-native routing

Only chosen telemetry (for example a subset of logs) is routed through the OS-native path, specifically where its on-demand enablement is wanted, while the rest continues over OTLP. Exporting OpenTelemetry's own SDK internal logs this way (see ["Example: SDK self-logs"](#example-sdk-self-logs)) is one such example.

#### Hybrid

A deployment can run both transports at once: some telemetry over OS-native export and the rest over OTLP. For example, the highest-volume logs and spans take the OS-native local hop for its performance, crash resilience, or future capabilities such as flight recorders, while the remaining telemetry continues directly over OTLP.

#### Configuration and flow

To use it, a developer configures OS-native tracing export for the relevant signal(s), giving it a provider name, the identity under which the OS exposes the events. The example below uses logs for concreteness. Traces are configured analogously as a span processor; metrics, being periodic, are configured as a metric reader and exporter (see [Metrics](#metrics)).

```yaml
# Declarative configuration; logs shown as an example
logger_provider:
  processors:
    - os_native_tracing:
        provider_name: "MyCompany-MyApp-Diagnostics"
```

Once configured (illustrated with logs):

1. When nothing is listening, emission is nearly free. The processor consults the facility's enablement state; if no session has subscribed, `Enabled()` is false and the instrumentation does almost no work.
2. A consumer enables collection out of band. On Windows an operator starts an ETW session (for example with `logman`) on the provider; on Linux an operator records the corresponding `user_events` tracepoint(s) (for example with `perf record`). The exact provider and tracepoint names follow the naming rules to be defined in the specification. The application begins emitting immediately, with no redeploy.
3. A local consumer reads and forwards. A same-host consumer decodes the events and forwards them onward exactly as today, typically over OTLP. Only the application-to-local-consumer hop changes; everything downstream is unchanged.

The common topology is: application -> OS-native tracing facility -> local consumer -> existing pipeline (OTLP, etc.) -> backend.

#### Same-host constraint

The one structural difference from OTLP is listener reachability. OTLP can deliver to a local, remote, or managed backend across the network, whereas OS-native export writes to an on-host facility, so a *collecting* consumer must run on the same node. With no local listener, nothing is collected. Because the facility is also readable by standard OS tools, an operator can additionally attach directly on demand (`perf`, `logman`, PerfView) to inspect a live process with no collector involved at all.

#### Example: SDK self-logs

The capability applies to ordinary application telemetry; nothing about it is specific to any particular source. As one illustration, consider the SDK's own internal logs, where the same mechanism applies unchanged with the SDK as just another producer. SDK internal logs are the classic case of telemetry that is usually noise in steady state but valuable when investigating a problem, and awkward to expose through the normal pipeline (feedback loops, steady-state overhead). Exporting them to an OS-native facility fits well: free while unobserved, and an operator can attach a tool on demand to read them from a live process, with no redeploy. A real example already exists. The OpenTelemetry .NET SDK emits its internal logs through .NET `EventSource` (`OpenTelemetry-Sdk`, ETW-backed on Windows), viewable with PerfView or `dotnet-trace`, as documented in its [troubleshooting guide](https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry/README.md#troubleshooting).

### Pipeline modeling: a processor

For the synchronous, per-event signals (logs and spans), OS-native emission is modeled as an SDK processor that writes directly to the facility on each emit: a `LogRecordProcessor` for logs and a `SpanProcessor` (acting on span end) for spans. These are existing extension points in those pipelines, so this needs no new pipeline concept.

A conventional exporter behind a built-in processor does not fit these two signals. The *batch* processor buffers, which is the opposite of the immediate per-emit write we want. The *simple* processor typically serializes export calls, discarding the per-CPU, contention-free scaling that is a primary reason to use these facilities. Rather than introduce a new "concurrent simple" processor, the write is modeled as the processor itself.

Metrics are different. They are pre-aggregated and exported periodically, so they use the normal metric reader and exporter path rather than a per-emit processor; see [Metrics](#metrics).

### Declarative configuration

Because the component is specified, it can be referenced from OpenTelemetry's declarative (file-based) configuration like any other spec-defined component: a user references it by name and supplies its settings (for example `provider_name`), as in the example above. One structural difference from the common case, for logs and spans, is that this processor does not embed a separate exporter; it performs the export itself as part of processing. Accommodating a processor that is also the terminal sink is concrete schema work (new schema entries, plugin-provider behavior, and validation rules), not a new concept. The exact schema shape is to be finalized in the specification.

### Consumers

The consumer side is out of scope here (see [Scope](#scope)); building consumers for these facilities is left to their implementers.

## Internal details

### The disabled fast path for Logs

The disabled path is cheap because the OS-native log processor implements the OpenTelemetry logs `Enabled()` check, answering it from the facility's live enablement state, so when no consumer is subscribed the `LogRecord` is never constructed. OpenTelemetry Rust contrib benchmarks measure roughly 1-2 ns for a disabled log on this path; absolute numbers vary by language and implementation. This applies to logs today; spans and metrics have no standardized `Enabled()`-style gate yet (see ["What the model provides"](#what-the-model-provides)). When other processors share the pipeline, skipping record construction at the API level depends on pipeline composition (routing a log to a single processor, or a routing processor whose `Enabled()` consults the OS-native side), an implementation detail rather than part of this proposal.

### Per-signal handling and encoding

The three signals are not encoded the same way, because the right encoding depends on what consumers do with the data.

Logs and spans are written in the facility's own event format (ETW TraceLogging fields; EventHeader/`tracefs` fields for `user_events`), not OTLP bytes or an opaque blob, one event per log or per span end. Native encoding is what lets standard OS tools (`perf`, `logman`, PerfView) and pipeline receivers act on events without OpenTelemetry-specific decoding, and it is what makes them triggerable: a consumer (or the facility itself, or an eBPF program) can react to event *content*, for example "when an event named `FOO` arrives, capture a process dump", without first decoding the payload.

This OTEP proposes that there be a defined mapping from the OpenTelemetry log and span data model onto each facility's native fields, covering at a high level: event identity, body, severity number and text (logs), span fields (name, kind, status, start and end time, span/trace/parent IDs, attributes, events, links), timestamps, trace context, and attributes. The precise per-field encoding for each facility is to be finalized in the specification.

An initial, illustrative piece of this already exists. The [ETW mapping in the logs data-model appendix](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model-appendix.md#etw-event-tracing-for-windows) gives a field-by-field ETW-to-logs mapping (including the ETW level to `SeverityNumber` mapping). It is deliberately narrow: a non-normative appendix example for one signal (logs) and one facility (ETW) describing how a *consumer* interprets such events. It serves here as evidence that the mapping is feasible and concrete. Defining these exporters, the producer emission semantics, and the cross-language contract across all signals and facilities is what this OTEP adds on top of it.

#### Event identity (event name)

Each event carries a name. It could be a constant such as `"Span"` or `"Log"`, or, when applicable, derived from `LogRecord.EventName`. Much of the on/off enablement of these facilities keys off this name, so it carries implications; the exact naming rules are to be sorted out in the specification.

#### Metrics

Metrics are pre-aggregated, so emission is periodic rather than per-measurement, and the synchronous, native-format benefits do not apply: there is no per-measurement event to trigger on, and native tools cannot render metrics. Metrics therefore use the normal periodic metric reader and exporter path, not a per-emit processor, and are carried as a binary OTLP/protobuf payload inside an OS-native event. This is how existing Rust and .NET metric exporters to these facilities already work, using the facility purely as on-host transport. This is transport consolidation, not native observability: recovering the metrics still requires an OpenTelemetry-aware same-host consumer, and standard OS tools cannot render them.

The reason to include metrics at all, despite the limited per-signal benefit, is consolidation. Once logs and spans leave the process through the OS facility, requiring the application to *also* maintain a full HTTP/gRPC client stack solely to ship metrics would give back much of the reduced dependency and network surface the on-host model otherwise provides. Routing metrics over the same on-host facility lets a deployment carry all telemetry off the process through a single channel.

#### Resource and instrumentation scope

This differs from OTLP, which carries `Resource` and `InstrumentationScope` once per batch and shares them across the records in it. Events here are independent, with no batch to attach shared context to, so both must instead be associated with each event. The two differ in where they can come from. Many `Resource` attributes describe the host or process and can be filled in by the local consumer, and some context (such as process and thread ID) comes for free from the kernel write. `InstrumentationScope`, by contrast, identifies the emitting instrumentation and is known only to the producer, so it must be carried on each event and cannot be inferred by the consumer. The exact producer/consumer split for `Resource`, and how `InstrumentationScope` is encoded per event, are to be finalized in the specification.

## Security and trust boundary

- Privilege asymmetry. On both ETW and `user_events`, *emitting* events requires minimal privilege (almost any process can write), while *subscribing* to them requires elevated privilege. Enabling collection is therefore an inherently privileged, deliberate act performed from outside the producing process. This is a reasonable default posture: an unprivileged application cannot cause its own telemetry to be collected, and turning collection on is gated by OS permissions.
- Local readability. Once a privileged consumer subscribes, the events are readable by that consumer, and potentially by any other sufficiently privileged process on the same host, including standard OS tools. Telemetry exported this way inherits the access-control model of the underlying OS facility. Any sensitive data (PII, secrets) present in telemetry is exposed to local tracing consumers under that model, exactly as it would be for any other use of these facilities. This is a property operators must account for when deciding what to emit.
- Multi-tenant and container visibility. In shared environments, a consumer running on the host may be able to observe events from multiple workloads sharing a node (for example several pods on one node). Whether that is acceptable, and how to scope or isolate it, depends on the deployment and is primarily a consumer-side concern, governed by who is permitted to run a subscribing session. As this OTEP covers only the producer side, it does not attempt to solve consumer-side isolation; it notes the consideration so that consumer designs and deployment guidance can address it.
- Practical guidance. Treat any emitted payload as readable by local administrators, tracing-privileged users, and host or node-level agents, potentially across containers or pods on the same node. Do not emit secrets, and apply the same redaction and attribute policies used for any telemetry, while assuming a host-local privileged reader can see past application-level intent. The specific controls differ by platform: on Windows, collection is governed by ETW session permissions and administrative or trace privileges; on Linux, it depends on the kernel version and on `tracefs` and perf permissions and capabilities as configured by the distribution. Container isolation of these facilities is not guaranteed by this OTEP.

## Trade-offs and mitigations

- Requires a same-host collecting consumer. A listener must run on the same node, or nothing is collected. This is inherent to writing to an on-host facility; it is by design and not mitigated (see [Same-host constraint](#same-host-constraint)).
- Linux requires kernel 6.4 or newer for `user_events`. There is no mitigation; deployments on older kernels cannot use the Linux path. (ETW has no equivalent version floor.) Even on a 6.4+ kernel, `user_events` needs `tracefs` access, which containerized and managed environments often do not expose, so the Linux path may be unavailable there regardless of kernel version, unless the operator chooses to expose `tracefs` to the workload.
- Per-event size cap (about 64 KB). Individual events rarely approach this in practice. The common exception is a long exception stack trace; where the log is emitted at the throw or catch site, the synchronous model lets a listener capture the emitting thread's live stack out of band instead of embedding it in the payload. This does not help when the stack trace belongs to an exception originating elsewhere, so it is a partial mitigation, not a general one.
- Per-event `Resource` and `InstrumentationScope`, where OTLP carries them once per batch (see [Resource and instrumentation scope](#resource-and-instrumentation-scope)). Much of `Resource` can be filled in by the local consumer rather than emitted per event. `InstrumentationScope` is known only to the producer and must be carried on each event, which duplicates it across events; there is no established way to avoid this today, and reducing it is left to the specification phase.
- Telemetry is readable by privileged host-local consumers, potentially across containers on the same node. This is inherent to using a shared OS facility and is governed by the platform's access-control model rather than mitigated here; operators account for it when deciding what to emit (see [Security and trust boundary](#security-and-trust-boundary)).

## Prior art and alternatives

- ETW and `user_events` exporters already exist in OpenTelemetry contrib for three languages (Rust, .NET, C++); for example, Rust `opentelemetry-etw-logs` and `opentelemetry-user-events-logs`. They encode payloads using Microsoft Common Schema; this proposal instead defines an OpenTelemetry-standard encoding, but the existing exporters are proven prior art for the mechanism and its feasibility. The standard encoding is additive; existing encoders can continue to exist and nothing here forces a migration.
- On the consumer side, the OpenTelemetry Arrow `df_engine` (`otap-dataflow`) `etw_receiver` and `user_events_receiver` already read these facilities and produce OpenTelemetry data.
- The OpenTelemetry .NET SDK already exposes its own internal logs over ETW via `EventSource` (`OpenTelemetry-Sdk`), demonstrating the "free until observed" self-diagnostics pattern (see [Troubleshooting](https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry/README.md#troubleshooting)).
- The approach was presented in the talk ["Beyond OTLP: Unlocking the Potential of OS-native Tracing"](https://youtu.be/Ej-z2WwWWak) (Cijo Thomas and Chris Gray, OpenTelemetry Community Day 2025, Denver).

Alternatives considered:

- OTLP over a local IPC transport (UNIX domain socket, named pipe, or shared memory). This can make the local hop cheaper and is a reasonable option on its own, but it still delivers to a single listening endpoint, so it provides none of the out-of-band, consumer-controlled enablement, readability by standard OS tools, multi-consumer fan-out, kernel-backed durability, or content-based triggering that motivate this proposal. Those properties come from the OS facility, not merely from staying on-host.
- Writing OTLP to a file or stdout and shipping it externally. Same reason: it provides neither out-of-band, near-zero-cost enablement nor kernel-backed durability, and the producer pays full cost regardless of whether anyone reads.

## Frequently asked questions

- OpenTelemetry is consolidating on OTLP and retiring Jaeger and Zipkin. Why add new exporters?

  Jaeger and Zipkin are being retired because they are alternative *network wire protocols* for the job OTLP already does: carrying telemetry across the network to a backend. Maintaining parallel protocols for the same job is redundant. OS-native export is not another network protocol competing with OTLP; it is a different *transport* with properties OTLP does not offer: out-of-band, consumer-controlled enablement, near-zero cost when nobody is listening, kernel-backed durability, readability by standard OS tools, and content-based triggering. It is also where telemetry already lives on a host: the kernel, drivers, and system services all emit into these facilities, and there is no way to ask them to send OTLP to a collector instead. OTLP remains the portable default and the usual downstream path (a local consumer typically forwards over OTLP); this complements it rather than competing with it.

- Exporters for these facilities already exist in contrib. Why standardize in the spec?

  Today's contrib exporters (Rust, .NET, C++) each encode with Microsoft Common Schema, so producers and consumers only interoperate if built against the same encoding. The spec defines one vendor-neutral OpenTelemetry mapping, so any conforming producer and consumer work together across languages and vendors.

- Does the synchronous write block the application's hot path?

  No. Emitting is a write to an in-memory, kernel-backed buffer on the calling thread. There is no disk I/O and no network call, so there is no I/O wait. When nothing is listening the producer returns without building the record.

- What happens when the buffer is full?

  There is no backpressure to the application. The kernel drops the event and increments its own lost-event counter for the session; the producer is never stalled. Reading and reporting that counter is a consumer-side concern, out of scope here.

- OpenTelemetry already has eBPF-based projects. How does this relate?

  They solve opposite directions of the same problem and compose well. OpenTelemetry's eBPF work (zero-code instrumentation and profiling) observes a program from the outside, producing telemetry about an application that was not instrumented for it. This proposal is the inbound direction: an explicit emit path for an application already instrumented with the OpenTelemetry SDK, writing its own telemetry out through `user_events`. It requires no eBPF. The two are complementary, and even composable, because `user_events` surfaces through the standard kernel tracing infrastructure, so an eBPF-based consumer can subscribe to these events if desired.

## Open questions

These are expected to be resolved during the specification phase, not in this OTEP:

- Per-field encoding of the log and span data model onto ETW and `user_events` fields.
- Fallback rules for event identity when `LogRecord.EventName` is absent.
- The producer/consumer split for `Resource`, and how `InstrumentationScope` is carried per event.
- The declarative-configuration schema for a processor that is also the terminal sink.
- Ordering and correlation across independent, per-CPU events.
- Stable, collision-resistant provider and event naming.

## Prototypes

Feasibility is already demonstrated across producers, consumers, and the mapping itself:

- Producers: the Rust, .NET, and C++ contrib exporters for ETW and `user_events` listed under [Prior art and alternatives](#prior-art-and-alternatives). The Rust crates are [`opentelemetry-etw-logs`](https://github.com/open-telemetry/opentelemetry-rust-contrib/tree/main/opentelemetry-etw-logs) and [`opentelemetry-user-events-logs`](https://github.com/open-telemetry/opentelemetry-rust-contrib/tree/main/opentelemetry-user-events-logs).
- Consumers: the [`etw_receiver`](https://github.com/open-telemetry/otel-arrow/tree/main/rust/otap-dataflow/crates/contrib-nodes/src/receivers/etw_receiver) and [`user_events_receiver`](https://github.com/open-telemetry/otel-arrow/tree/main/rust/otap-dataflow/crates/contrib-nodes/src/receivers/user_events_receiver) in the [`otap-dataflow`](https://github.com/open-telemetry/otel-arrow/tree/main/rust/otap-dataflow) project.
- Mapping: the [ETW-to-logs field mapping](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model-appendix.md#etw-event-tracing-for-windows) already merged into the logs data-model appendix.

## Future possibilities

1. Higher-level diagnostic capabilities built on out-of-band enablement and kernel-backed buffering, pursued in separate proposals. A prime example is a flight recorder: because these facilities can maintain a bounded, always-on ring buffer of recent events in the kernel, a consumer can continuously record at low cost and snapshot the buffer only when a trigger fires (for example a `FATAL` log or a crash), capturing the events leading up to an incident without shipping everything all the time.
2. A built-in SDK capability. Further out, OS-native export could become a core property of the SDK itself on platforms that support it, always present rather than wired up as an opt-in exporter or processor. Because it costs effectively nothing until a consumer subscribes, the SDK could always be ready to emit to the OS facility, so the OpenTelemetry data is simply there whenever an operator needs it, with no configuration and no redeploy.
3. Raw measurements as triggerable events. If OpenTelemetry introduces a `MeasurementProcessor`-style concept (access to individual measurements before aggregation), those raw measurements could be written to the OS facility like logs and spans, synchronously and in native event format, rather than as aggregated binary metrics. Modeled this way, a measurement becomes a triggerable event: for example, a histogram recording `req_size` could drive a trigger such as "if `req_size` > 3 MB, capture and dump the packet for analysis." This is explicitly out of scope for this OTEP (it depends on a concept that does not yet exist) but motivates keeping the per-signal model open.
4. Reference blueprint and demo. A reference blueprint for the end-to-end pattern, and inclusion in the OpenTelemetry Demo so the model can be exercised and evaluated by the community.
5. Dynamic control via OpAMP. With telemetry flowing through OS-native facilities whose enablement is controlled out of band, a control plane such as OpAMP could enable and disable sources dynamically and remotely across a fleet. This is a natural extension of the out-of-band enablement property, and is being pursued separately.

## Appendix: background on the OS-native facilities

### Perspective: instrumentation density vs. telemetry cost

Telemetry volume, and its cost, is a well-recognized and growing concern across the OpenTelemetry community. It is worth noting that this concern is not fundamental to *having* instrumentation; it is a consequence of *always emitting* it. A single ordinary machine already contains an enormous amount of instrumentation: hundreds of thousands of trace points across the kernel, drivers, and system services, capable of producing millions of events per second. Yet nobody worries about the cost of all that instrumentation, because it emits nothing unless a consumer explicitly turns it on. The volume exists only when, where, and for as long as someone is actually collecting it.

This is the property the OTEP borrows. Instrumentation can be dense and pervasive without being expensive, provided enablement is controlled out of band by the consumer rather than paid for continuously by the producer. It lets an application be instrumented liberally, with the cost incurred only when the data is genuinely wanted.

### Event Tracing for Windows (ETW)

ETW is the built-in, high-performance tracing facility of the Windows operating system, present since Windows 2000 and central to Windows diagnostics for over two decades. Providers register and emit events; sessions (started by tools such as `logman`, or analyzed with PerfView) subscribe out of band; and events cost effectively nothing when no session is enabled.

- ETW overview: <https://learn.microsoft.com/windows/win32/etw/event-tracing-portal>
- TraceLogging (the self-describing event schema used by the dynamic-provider model): <https://learn.microsoft.com/windows/win32/tracelogging/trace-logging-portal>

### Linux tracepoints and `user_events`

Linux tracepoints have existed for well over a decade (since kernel 2.6.x, 2008), providing low-overhead static instrumentation points in kernel code, observable via ftrace and `perf`. Historically only kernel code could define and emit tracepoints.

`user_events` is the newer facility that lets user-mode applications register and write to this same tracepoint/`tracefs` infrastructure, so user-space events are observable with the standard kernel tooling. It became generally available in Linux 6.4 (2023) and should be treated as requiring kernel 6.4+ in practice.

References:

- Kernel documentation: <https://docs.kernel.org/trace/user_events.html>
- Initial implementation commit (`7f5a08c79df3`, adds `kernel/trace/trace_events_user.c`): <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7f5a08c79df35e68f1a43033450c5050f12bc155>
- LWN overview, "User-space event tracing" (2022): <https://lwn.net/Articles/889607/>
