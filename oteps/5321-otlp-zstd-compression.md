# Add zstd as a specified OTLP compression codec

Specify `zstd` as a second compression codec for OTLP/gRPC and OTLP/HTTP, alongside `gzip`. Not a
default; exporters fall back to `gzip` if a receiver rejects `zstd`.

## Motivation

The [OTLP exporter spec][exporter-spec] says `gzip` is the only specified compression method.
Zstandard has better compression ratio and faster decompression than gzip at comparable CPU
cost, given pooled encoders — a real cost for CPU- and bandwidth-constrained telemetry pipelines.
The .NET prototype (see Prototypes) measured payloads 11–36% smaller than gzip, with 0.65–1.0x
gzip's compression CPU when encoders are reused and 1.2–1.5x faster decompression.

The ecosystem has already moved here without the spec:

- `opentelemetry-rust`'s `opentelemetry-otlp` crate ships `zstd` today for both transports
  (`zstd-tonic`, `zstd-http` feature flags), opt-in, tested, with the same env-var precedence the
  spec defines for `gzip`. An official SDK already shipped this independent of the spec.
- The Collector's `configgrpc`/`confighttp` support `zstd`/`snappy` alongside `gzip`; several
  `collector-contrib` exporters (file, Pulsar, Azure Blob, STEF, otel-arrow) do too.
- `opentelemetry-java-contrib` ships a [`compressor-zstd`][java-contrib-zstd] module.
- grpc-go's `encoding.RegisterCompressor` already treats compressor choice as pluggable, which is
  what the blocked otel-go PR builds on.
- OTLP profiles dropped its *mandatory* gzip requirement in
  [`opentelemetry-proto#661`][proto-661] for the same reason argued here.

Without a spec, each SDK invents its own shape. Rust and Go already have two independent,
incompatible implementations of the same idea. This OTEP gives them one target to converge on.

## Explanation

SDKs offer `zstd` as a value for `OTEL_EXPORTER_OTLP_COMPRESSION` / the per-signal variants /
the equivalent constructor option, for both transports, exactly as `gzip` works today.

`zstd` MUST NOT be selected as an implementation's default compression value — a user has to
configure it explicitly. `exporter.md` otherwise lets a SIG default to any supported value, and
an unconfigured user would have no way to know their SIG picked a codec their receiver might lack.

If the configured receiver doesn't support `zstd`:

- **gRPC**: per the [gRPC compression spec][grpc-compression-spec], the server returns
  `UNIMPLEMENTED`. That spec also has the server list its supported encodings in
  `grpc-accept-encoding`, but grpc-go's server (and so the Collector) rejects before any handler
  runs and sends no `grpc-accept-encoding` on the response, so OTLP can't rely on the header.
- **HTTP**: a receiver that doesn't support the request's `Content-Encoding` MUST reject it with
  `415 Unsupported Media Type` rather than silently treating the body as uncompressed, and SHOULD
  list the codings it does accept in an `Accept-Encoding` response header
  ([RFC 9110 §15.5.16][rfc9110-415]). `400 Bad Request` is not conformant here: OTLP/HTTP
  reserves `400` for permanently invalid data. The Collector returns `400` today (see
  [Compliance gaps](#compliance-gaps-in-existing-implementations)).

Both statuses are non-retryable under OTLP's existing retry semantics, so a compliant `zstd`
sender talking to a compliant non-supporting receiver would drop every batch. To close that gap,
for a `zstd`-compressed export the exporter MUST retry that batch once with `gzip`, and SHOULD log
a warning, when and only when:

- **gRPC**: the status is `UNIMPLEMENTED` and the response's `grpc-accept-encoding` is absent or
  does not list `zstd`. If it lists `zstd`, the gRPC spec says the error is unrelated to
  compression, and existing non-retryable handling applies.
- **HTTP**: the status is `415`. Every other status keeps its existing OTLP semantics; in
  particular `400` stays non-retryable.

This can still misfire — a `415` for an unsupported `Content-Type`, or a grpc-go `UNIMPLEMENTED`
for an unregistered service — but the cost is bounded: one extra `gzip` request that fails the
same way and is then handled exactly as today. A batch the receiver calls permanently invalid
(`400`) is never resent. This is one hardcoded fallback rung, not negotiation — an exporter may
keep trying `zstd` on later batches or remember the downgrade for the connection's lifetime;
either is fine, as long as no batch is dropped solely for a codec mismatch.

Receiver support is SHOULD, not MUST — same bar as any newly-added optional codec, and it doesn't
force a minimal/vendor receiver to take on a new dependency to stay compliant. Exporter support is
also SHOULD: a conforming exporter MAY omit `zstd` (e.g. to avoid the dependency), same as a
receiver MAY decline it. This is a narrow exception to the general rule that a conforming
exporter MUST offer every listed `Compression` value, justified because `zstd`, unlike `gzip`,
isn't in most languages' standard libraries.

## Internal details

- **`specification/protocol/exporter.md`**: add `zstd` alongside `gzip` as a specified value for
  `OTEL_EXPORTER_OTLP_COMPRESSION` and per-signal variants, for both transports. `none` is
  unchanged. State explicitly that `zstd` MUST NOT be a SIG's default.
- **[`opentelemetry-proto`][proto-spec]**: the actual normative home for receiver behavior and
  wire format — `exporter.md` alone can't establish it. That document today requires server
  support for `none`/`gzip` and defines only `Content-Encoding: gzip` for HTTP. Citing
  [RFC 8878](https://www.rfc-editor.org/rfc/rfc8878) isn't enough either: it leaves window size,
  dictionaries, checksums, and frame concatenation open, so "RFC 8878-compliant" alone doesn't
  guarantee interop. This uses the same streaming shape (`Compress(io.Writer)` /
  `Decompress(io.Reader)`) `gzip` already has, not a new one:
  - **Window size capped at 8 MB**, per [RFC 9659 §3](https://www.rfc-editor.org/rfc/rfc9659#section-3)'s
    HTTP interoperability recommendation — encoders SHOULD NOT exceed it. Single-segment framing
    (`Frame_Content_Size` known up front) is deliberately not required: that field is
    sender-reported and unverified until decompression happens, so it isn't a real
    decompression-bomb defense, and requiring it would mean a different implementation shape than
    every other codec here uses for no compensating benefit.
  - **One frame per payload.** RFC 8878 §3.1.1 permits concatenating frames, but no single OTLP
    request/response body needs more than one.
  - **Standard frame format only.** Magic number `0xFD2FB528` (§3.1.1); no legacy
    pre-standardization formats, no skippable frames (§3.1.2).
  - **No compression dictionaries.** `Dictionary_ID_Flag` MUST be `0`. §6: dictionary use needs
    out-of-band agreement, which is exactly the negotiation surface this OTEP avoids opening.
  - **`Content_Checksum_Flag` is unconstrained** — it's self-describing via the flag, so no prior
    agreement is needed either way.
- **`opentelemetry-configuration`**: adding `zstd` to `Compression` is a config-surface change.
  `CONTRIBUTING.md` requires a schema PR (today's schema documents only `gzip`/`none`) linked from,
  and merged together with, the spec PR that changes SDK configuration — here, the follow-up
  `exporter.md` change this OTEP leads to, not the OTEP itself. That schema PR will be opened
  alongside the spec PR.
- **Mixed-version rollout**: no new policy here. Nothing in `specification/configuration`
  mandates warn-vs-fail-fast for an unrecognized value today; the closest existing guidance is
  [`error-handling.md`](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/error-handling.md#basic-error-handling-principles) —
  MAY fail fast at init, MUST NOT fail at runtime. An SDK predating `zstd` support that sees it in
  a fleet-wide env var just keeps its existing behavior for an unrecognized value.
- **Receiver conformance**: gRPC receivers SHOULD register a `zstd` compressor the same way they
  do `gzip`, and SHOULD include `grpc-accept-encoding` when rejecting an unsupported encoding, as
  the gRPC spec describes. HTTP receivers SHOULD accept `Content-Encoding: zstd`, MUST reject any
  encoding they don't support with `415`, and SHOULD include `Accept-Encoding` in that response.
- **Exporter conformance**: SHOULD, not MUST — see Explanation.
- **Error modes**: `UNIMPLEMENTED` (gRPC) / `415` (HTTP) on a non-supporting receiver, followed
  by the mandatory gzip-retry under the conditions in Explanation. No other new client-side error
  modes, and no change to how any other status is handled.
- **Reference implementation** (non-normative — see Prototypes): [otel-go#8985][otel-go-pr].
  Pooled `zstd.Encoder`/`Decoder` via `klauspost/compress/zstd`, registered as a
  `grpc/encoding.Compressor` for gRPC and wrapping the request body for HTTP, with
  `zstd.WithWindowSize` pinned to the 8 MB cap. Concurrency pinned to 1: OTLP batches are too
  small to benefit from zstd's parallel workers, and it bounds leaked goroutines if a pooled
  decoder is dropped without `Close`.

## Trade-offs and mitigations

- **Uneven receiver support at first.** Mitigated by: `zstd` can't be a default, and a rejected
  batch retries once with `gzip` instead of being dropped.
- **One hardcoded fallback rung, not general negotiation.** A full negotiation mechanism is a
  much bigger spec change, isn't needed for `gzip` today, and would indefinitely block this if
  made a prerequisite. The gzip-retry is the minimum needed to keep "opt into zstd" from silently
  dropping telemetry. Worth its own OTEP if there's appetite for more.
- **New dependency for implementations that add it.** Unlike `gzip`, `zstd` isn't in most
  standard libraries. Rust's Cargo feature flags (`zstd-tonic`/`zstd-http`) are real per-feature
  opt-in — no feature, no dependency. The otel-go prototype matches this with a `nozstd` build
  tag that drops the codec and `klauspost/compress`; a build with the tag fails fast at exporter
  construction if `zstd` is still configured.
- **SHOULD, not MUST, on both sides.** A compliant receiver can still reject `zstd`, a compliant
  exporter can still omit it. Keeps the adoption bar low; a future OTEP could raise either once
  there's adoption data.

## Prior art and alternatives

- **`opentelemetry-rust`**: ships `zstd` for both gRPC and HTTP today (see Motivation) — an
  official SDK already reached this conclusion independent of the spec, which weakens "zstd isn't
  an OpenTelemetry specified protocol" as an objection.
- **Collector `configgrpc`/`confighttp`** and several `collector-contrib` exporters: already
  ahead of the SDK-facing spec text this OTEP changes.
- **`opentelemetry-java-contrib` `compressor-zstd`**: existing out-of-spec Java implementation.
- **grpc-go's `encoding.RegisterCompressor`**: the pluggable-compressor mechanism the blocked
  otel-go PR builds on.
- **OTLP profiles gzip requirement removal** ([proto#629][proto-629] / [#661][proto-661]):
  different requirement (mandatory vs. optional gzip), same underlying argument, already accepted.
- **Rejected: general negotiation/capability-probing**, and **rejected: MUST-level receiver or
  exporter support** — see Trade-offs above. A single gzip-retry-on-rejection fallback is in
  scope; general negotiation is not.
- **Trigger**: [otel-go#8984][otel-go-issue] / [#8985][otel-go-pr] — maintainers correctly
  declined to add `zstd` ahead of spec support and asked for this OTEP as follow-up. That issue
  also flagged that otel-go silently falls back to no compression on an unrecognized
  `WithCompressor` value instead of erroring — a real bug, but a separate, SDK-specific one.

## Compliance gaps in existing implementations

The prior art above mostly shipped before this OTEP's fallback requirement existed, so having a
`zstd` option doesn't make it automatically compliant — checked against
[Internal details](#internal-details):

- **Decoders need no changes.** Every implementation checked here already decodes a windowed
  RFC 8878 frame correctly. The window-size cap is encoder-side only; the gaps below are too.
- **Collector `configgrpc`**: [a streaming `zstd.NewWriter`][collector-configgrpc-zstd] with a
  fixed 512 KB window — already under this OTEP's 8 MB cap, no dictionary use. Compliant on
  framing already. The remaining gap, same as everyone else: no gzip-fallback-on-rejection, a
  requirement that didn't exist before this OTEP. `confighttp` decodes `zstd` by default
  ([`availableDecoders["zstd"]`][collector-confighttp-zstd]), but when it sees an encoding it
  doesn't support (e.g. `zstd` removed from its configured algorithms) it returns a plain-text
  `400` with no `Accept-Encoding` ([`compression.go`][collector-confighttp]), the same status it
  uses for a corrupt body. It needs to return `415` instead; a small change, and only reachable
  when an operator has disabled `zstd`. On gRPC, the Collector inherits grpc-go's `UNIMPLEMENTED`
  with no `grpc-accept-encoding`, which the fallback rule already treats as a codec mismatch.
- **`opentelemetry-rust`**:
  - gRPC (`zstd-tonic`): delegates to `tonic::codec::CompressionEncoding::Zstd`. Window size is
    tonic's implementation detail, not something `opentelemetry-rust` asserts either way.
  - HTTP (`zstd-http`): calls [`zstd::bulk::compress(&body, 0)`][rust-http-zstd]. Likely stays
    under 8 MB for typical OTLP payload sizes given zstd's own size-based heuristics, but nothing
    pins or tests that.
  - No dictionary use, and `zstd` confirmed not defaulted (`resolve_compression` returns `None`
    when unconfigured). No gzip-fallback in `process_body` — same gap as everyone else.
  - Cargo feature gating (opt-in, off by default) already exceeds this OTEP's bar — the otel-go
    prototype only matches this now, via the `nozstd` build tag added in this revision.
- **`opentelemetry-java-contrib` `compressor-zstd`**: [wraps `ZstdOutputStream`][java-zstd] — the
  same streaming shape this OTEP settled on, but no explicit window-size bound; would need one
  (or confirmation `zstd-jni`'s default is already ≤8 MB). No gzip-fallback.

None of this blocks the OTEP — `gzip`'s spec compliance didn't require every ad hoc
implementation to already match it either. The gzip-fallback requirement is new for everyone; the
framing requirement (8 MB window, no dictionary) already matches existing practice more often
than not.

## Open questions

- Does this need to say anything about the profiles signal specifically, or is transport-level,
  signal-agnostic wording sufficient? (Profiles dropped a *mandatory* gzip requirement for its
  on-disk format — a different axis from the transport compression here.)
- Compression level: TC discussion (2026-09-23) raised that configurable zstd level matters
  because it drives memory consumption. This OTEP doesn't propose a level knob — doing so adds
  more config surface, compounding the `opentelemetry-configuration` schema work already required.
  Fold a level option into this OTEP now, or leave it to a fast-follow? If so, there's already
  prior art for a single cross-algorithm surface: the Collector's `confighttp.ClientConfig`
  exposes one generic `compression_params.level` field regardless of codec —
  `configcompression.Type.ValidateParams` validates it against `zlib`'s range for
  gzip/zlib/deflate, while for zstd "supports arbitrary levels: zstd will map any given level to
  the nearest internally supported level." No such knob exists on the SDK/exporter side today —
  checked `opentelemetry-go` (this OTEP's own prototype), `opentelemetry-rust`, and
  `opentelemetry-java`, none of which expose one; all hardcode the compression library's default
  rather than exposing a level parameter. Not an exhaustive survey of every language SDK, but this
  would be new surface for exporters even though
  the Collector's config side already has it.
- Is there appetite to eventually raise `zstd` receiver or exporter support from SHOULD to MUST,
  and what adoption bar would justify that?

## Prototypes

- [otel-go#8985][otel-go-pr] — both transports (`otlptracegrpc`/`otlpmetricgrpc`,
  `otlptracehttp`/`otlpmetrichttp`), implementing the gzip-fallback rule above, with tests for the
  negotiated codec, the fallback, and the cases that must not fall back (HTTP `400`; gRPC
  `UNIMPLEMENTED` whose `grpc-accept-encoding` lists `zstd`). `nozstd` build tag for opt-out.
  Blocked pending this OTEP.
- [martincostello/opentelemetry-dotnet@63674a2][dotnet-proto] — .NET 11 (built-in Zstandard),
  both transports, interop-tested against Collector 0.163.1 including the gzip fallback, with
  benchmarks against gzip ([PR comment][dotnet-bench]). Predates the narrowed trigger above (it
  falls back on `400`).

## Future possibilities

- A general compression-negotiation OTEP, applicable to any codec — out of scope here.
- Same treatment for other modern codecs (e.g. `brotli`) if there's similar demand.
- Revisiting SHOULD vs. MUST for `zstd` receiver/exporter support once adoption data exists.

[exporter-spec]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md
[collector-confighttp]: https://github.com/open-telemetry/opentelemetry-collector/blob/main/config/confighttp/compression.go
[rfc9110-415]: https://www.rfc-editor.org/rfc/rfc9110#section-15.5.16
[dotnet-proto]: https://github.com/martincostello/opentelemetry-dotnet/commit/63674a2d858519f02ecc39536925fd2afd5a5280
[dotnet-bench]: https://github.com/open-telemetry/opentelemetry-specification/pull/5321#issuecomment-6320068725
[proto-spec]: https://github.com/open-telemetry/opentelemetry-proto/blob/main/docs/specification.md
[java-contrib-zstd]: https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/compressors/compressor-zstd/README.md
[proto-629]: https://github.com/open-telemetry/opentelemetry-proto/issues/629
[proto-661]: https://github.com/open-telemetry/opentelemetry-proto/pull/661
[grpc-compression-spec]: https://github.com/grpc/grpc/blob/master/doc/compression.md
[otel-go-issue]: https://github.com/open-telemetry/opentelemetry-go/issues/8984
[otel-go-pr]: https://github.com/open-telemetry/opentelemetry-go/pull/8985
[rust-http-zstd]: https://github.com/open-telemetry/opentelemetry-rust/blob/main/opentelemetry-otlp/src/exporter/http/mod.rs
[java-zstd]: https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/compressors/compressor-zstd/src/main/java/io/opentelemetry/contrib/compressor/zstd/ZstdCompressor.java
[collector-configgrpc-zstd]: https://github.com/open-telemetry/opentelemetry-collector/blob/main/config/configgrpc/internal/grpccompression/zstd/zstd.go
[collector-confighttp-zstd]: https://github.com/open-telemetry/opentelemetry-collector/blob/main/config/confighttp/compression.go
