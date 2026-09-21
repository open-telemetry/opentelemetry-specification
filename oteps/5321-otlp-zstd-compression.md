# Add zstd as a specified OTLP compression codec

Specify `zstd` as a second compression codec for OTLP/gRPC and OTLP/HTTP, alongside `gzip`. No
default change, no negotiation mechanism.

## Motivation

The [OTLP exporter spec][exporter-spec] says `gzip` is the only specified compression method.
Zstandard has better compression ratio and several-times-faster decompression than gzip at
comparable CPU cost — a real cost for CPU- and bandwidth-constrained telemetry pipelines.

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
the equivalent constructor option, for both transports, exactly as `gzip` works today. It's
opt-in only — no auto-detection, no negotiation. If the receiver doesn't support it:

- **gRPC**: per the [gRPC compression spec][grpc-compression-spec], the server returns
  `UNIMPLEMENTED` with supported encodings in `grpc-accept-encoding`. Existing gRPC behavior,
  nothing new needed.
- **HTTP**: a receiver that doesn't support the request's `Content-Encoding` MUST reject it
  (`415 Unsupported Media Type`) rather than silently treating the body as uncompressed. This MUST
  is new normative text — HTTP has no built-in equivalent of gRPC's `UNIMPLEMENTED`.

Either way the failure is a normal export error through the SDK's existing retry path — same
failure mode as a bad endpoint, not silent data loss. Silent fallback to no compression was the
objection raised against the otel-go PR; this makes misconfiguration loud instead.

Receiver support is SHOULD, not MUST — same bar as any newly-added optional codec, and it doesn't
force every minimal/vendor receiver to take on a new dependency to stay compliant.

## Internal details

- **`specification/protocol/exporter.md`**: add `zstd` alongside `gzip` as a specified value for
  `OTEL_EXPORTER_OTLP_COMPRESSION` and per-signal variants, for both transports. `none` is
  unchanged.
- **Wire format**: unchanged. This adds a second recognized codec value, not new protocol surface.
- **Receiver conformance**: gRPC receivers SHOULD register a `zstd` compressor the same way they
  do `gzip`. HTTP receivers SHOULD accept `Content-Encoding: zstd` and MUST return `415` for any
  encoding they don't support.
- **Error modes**: `UNIMPLEMENTED` (gRPC) / `415` (HTTP) on a receiver that doesn't support `zstd`.
  No new client-side error modes.
- **Reference implementation** (non-normative): [otel-go#8985][otel-go-pr], blocked pending this
  OTEP — pooled `zstd.Encoder`/`Decoder` via `klauspost/compress/zstd`, registered as a
  `grpc/encoding.Compressor`. Concurrency pinned to 1: OTLP batches are too small to benefit from
  zstd's parallel workers, and it bounds leaked goroutines if a pooled decoder is dropped without
  `Close`.

## Trade-offs and mitigations

- **Uneven receiver support at first.** Mitigated by opt-in + SHOULD: nothing breaks for anyone
  who doesn't configure it, and a mismatch fails loudly rather than dropping data silently.
- **No negotiation mechanism.** Deliberate — negotiation is a much bigger spec change than adding
  a codec, isn't needed for `gzip` today, and would indefinitely block this if made a prerequisite.
  Worth its own OTEP if there's appetite, independent of which codecs exist.
- **New dependency for implementations that add it.** Unlike `gzip`, `zstd` isn't in most standard
  libraries. Mitigated by keeping it opt-in at the package/feature level (as Rust's Cargo features
  and the otel-go prototype both already do), so SDK users who don't want it don't pay for it.
- **SHOULD not MUST** means a compliant receiver can still reject `zstd`. Intentional, to keep the
  adoption bar low; a future OTEP could raise it once there's adoption data.

## Prior art and alternatives

- **`opentelemetry-rust`**: ships `zstd` for both gRPC and HTTP today (see Motivation). The
  strongest argument here — an official SDK already reached this conclusion independent of the
  spec, which weakens "zstd isn't an OpenTelemetry specified protocol" as an objection.
- **Collector `configgrpc`/`confighttp`** and several `collector-contrib` exporters: already
  ahead of the SDK-facing spec text this OTEP changes.
- **`opentelemetry-java-contrib` `compressor-zstd`**: existing out-of-spec Java implementation.
- **grpc-go's `encoding.RegisterCompressor`**: the pluggable-compressor mechanism the blocked
  otel-go PR builds on.
- **OTLP profiles gzip requirement removal** ([proto#629][proto-629] / [#661][proto-661]):
  different requirement (mandatory vs. optional gzip), same underlying argument, already accepted.
- **Rejected: auto-negotiation/fallback** and **rejected: MUST-level receiver support** — see
  Trade-offs above.
- **Trigger**: [otel-go#8984][otel-go-issue] / [#8985][otel-go-pr] — maintainers correctly
  declined to add `zstd` ahead of spec support and asked for this OTEP as follow-up. That issue
  also flagged that otel-go silently falls back to no compression on an unrecognized
  `WithCompressor` value instead of erroring — a real bug, but a separate, SDK-specific one.

## Open questions

- Does this need to say anything about the profiles signal specifically, or is transport-level,
  signal-agnostic wording sufficient? (Profiles dropped a *mandatory* gzip requirement for its
  on-disk format — a different axis from the transport compression here.)
- Is `415` the right required HTTP status, or should `400` also be conformant?
- Should the spec recommend a zstd compression level, or leave it to implementations as with
  `gzip`?
- Is there appetite to eventually raise `zstd` receiver support from SHOULD to MUST, and what
  adoption bar would justify that?

## Prototypes

- [otel-go#8985][otel-go-pr] — full implementation for `otlptracegrpc`/`otlpmetricgrpc`, with
  wire-level tests asserting the negotiated codec. Blocked pending this OTEP.

## Future possibilities

- A general compression-negotiation OTEP, applicable to any codec — out of scope here.
- Same treatment for other modern codecs (e.g. `brotli`) if there's similar demand.
- Revisiting SHOULD vs. MUST for `zstd` receiver support once adoption data exists.

[exporter-spec]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md
[java-contrib-zstd]: https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/compressors/compressor-zstd/README.md
[proto-629]: https://github.com/open-telemetry/opentelemetry-proto/issues/629
[proto-661]: https://github.com/open-telemetry/opentelemetry-proto/pull/661
[grpc-compression-spec]: https://github.com/grpc/grpc/blob/master/doc/compression.md
[otel-go-issue]: https://github.com/open-telemetry/opentelemetry-go/issues/8984
[otel-go-pr]: https://github.com/open-telemetry/opentelemetry-go/pull/8985
