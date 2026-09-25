# Add zstd as a specified OTLP compression codec

Specify `zstd` as a second compression codec for OTLP/gRPC and OTLP/HTTP, alongside `gzip`. Not a
default; exporters fall back to `gzip` if a receiver rejects `zstd`.

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
the equivalent constructor option, for both transports, exactly as `gzip` works today.

`zstd` MUST NOT be selected as an implementation's default compression value — a user has to
configure it explicitly, same as any other non-default codec. This matters because
[`exporter.md`][exporter-spec] otherwise lets a SIG default to any supported value, and an
unconfigured user would have no way to know their SIG picked a codec their receiver might lack.

If the configured receiver doesn't support `zstd`:

- **gRPC**: per the [gRPC compression spec][grpc-compression-spec], the server returns
  `UNIMPLEMENTED` with its supported encodings in `grpc-accept-encoding`. Existing gRPC behavior.
- **HTTP**: a receiver that doesn't support the request's `Content-Encoding` MUST reject it
  (`415 Unsupported Media Type`) rather than silently treating the body as uncompressed. This MUST
  is new normative text — HTTP has no built-in equivalent of gRPC's `UNIMPLEMENTED`.

Both statuses are non-retryable under OTLP's existing retry semantics — so "fail loud instead of
silently dropping data" isn't actually true as stated: a compliant `zstd` sender talking to a
compliant SHOULD-level non-supporting receiver drops every batch, both sides in spec. To close
that gap: on receiving `UNIMPLEMENTED` or `415` for a `zstd`-compressed export, the exporter MUST
retry that batch once with `gzip` before treating the export as failed, and SHOULD log a warning
when this fallback fires. This is one hardcoded fallback rung, not general negotiation or
capability probing — an exporter may keep trying `zstd` on every subsequent batch (simplest to
implement) or remember the downgrade for the connection's lifetime (fewer wasted round-trips);
this OTEP only requires that no batch is dropped solely because of a codec mismatch.

Receiver support is SHOULD, not MUST — same bar as any newly-added optional codec, and it doesn't
force every minimal/vendor receiver to take on a new dependency to stay compliant. Exporter-side
support is also SHOULD, symmetric with receivers: a conforming OTLP exporter MAY omit `zstd`
entirely (e.g. to avoid the third-party dependency), same as a receiver MAY decline to accept it.
This is a narrow exception to the general rule that a conforming exporter MUST offer every listed
`Compression` value, justified because `zstd`, unlike `gzip`, isn't in most languages' standard
libraries.

## Internal details

- **`specification/protocol/exporter.md`**: add `zstd` alongside `gzip` as a specified value for
  `OTEL_EXPORTER_OTLP_COMPRESSION` and per-signal variants, for both transports. `none` is
  unchanged. Add explicit text that `zstd` MUST NOT be a SIG's default.
- **[`opentelemetry-proto`][proto-spec]**: the actual normative home for receiver behavior and
  wire format is here, not `exporter.md` alone — that document currently requires server support
  for `none`/`gzip` and defines only `Content-Encoding: gzip` for HTTP. This OTEP needs a
  corresponding proto-spec change, not just an SDK-spec one. That change should:
  - Identify [RFC 8878](https://www.rfc-editor.org/rfc/rfc8878) as the zstd frame format.
  - Forbid compression dictionaries (RFC 8878 §6): dictionary use requires out-of-band agreement,
    which is exactly the negotiation surface this OTEP avoids opening. OTLP `zstd` frames are
    always independent, dictionary-free frames.
  - Cap window size at 8 MB per [RFC 9659 §3](https://www.rfc-editor.org/rfc/rfc9659#section-3)'s
    HTTP interoperability limit — encoders MUST NOT exceed an 8 MB window, so any RFC 8878
    decoder can decode OTLP `zstd` payloads without pre-negotiating window size.
- **`opentelemetry-configuration`**: adding `zstd` to `Compression` is a config-surface change;
  per `CONTRIBUTING.md`, a corresponding schema PR (today's schema documents only `gzip`/`none`)
  is required and must merge together with this OTEP. **Not yet written — this is a hard blocker
  to merging this OTEP**, tracked here rather than solved in this round.
- **Mixed-version rollout**: this OTEP does not introduce a new unknown-enum-value policy.
  Nothing in `specification/configuration` mandates warn-vs-fail-fast for an unrecognized config
  value today; the closest existing guidance is
  [`error-handling.md`](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/error-handling.md#basic-error-handling-principles):
  implementations MAY fail fast at init on bad config but MUST NOT fail at runtime. An SDK
  predating `zstd` support that sees `zstd` in a fleet-wide env var keeps behaving however it
  already behaves on an unrecognized `Compression` value — this OTEP doesn't change that, it only
  adds one more value implementations need to recognize going forward.
- **Receiver conformance**: gRPC receivers SHOULD register a `zstd` compressor the same way they
  do `gzip`. HTTP receivers SHOULD accept `Content-Encoding: zstd` and MUST return `415` for any
  encoding they don't support.
- **Exporter conformance**: SHOULD, not MUST — see Explanation.
- **Error modes**: `UNIMPLEMENTED` (gRPC) / `415` (HTTP) on a receiver that doesn't support
  `zstd`, followed by the mandatory gzip-retry described in Explanation. No other new client-side
  error modes.
- **Reference implementation** (non-normative, gRPC only — see Prototypes): [otel-go#8985][otel-go-pr].
  Pooled `zstd.Encoder`/`Decoder` via `klauspost/compress/zstd`, registered as a
  `grpc/encoding.Compressor`. Concurrency pinned to 1: OTLP batches are too small to benefit from
  zstd's parallel workers, and it bounds leaked goroutines if a pooled decoder is dropped without
  `Close`. The gzip-retry-on-rejection behavior above isn't implemented there yet — that prototype
  predates this revision.

## Trade-offs and mitigations

- **Uneven receiver support at first.** Mitigated by: `zstd` can't be a default (explicit opt-in
  only), and a rejected batch retries once with `gzip` rather than being dropped — see Explanation.
- **One hardcoded fallback rung, not general negotiation.** Deliberate — a full negotiation or
  capability-probing mechanism is a much bigger spec change, isn't needed for `gzip` today, and
  would indefinitely block this if made a prerequisite. The gzip-retry-on-rejection requirement is
  the minimum needed to keep "opt into zstd" from silently dropping telemetry; it doesn't attempt
  to solve negotiation generally. Worth its own OTEP if there's appetite for more, independent of
  which codecs exist.
- **New dependency for implementations that add it.** Unlike `gzip`, `zstd` isn't in most standard
  libraries. Rust's Cargo feature flags (`zstd-tonic`/`zstd-http`) demonstrate real per-feature
  opt-in — a user who doesn't enable the feature doesn't get the dependency at all. The otel-go
  prototype does **not** yet do this: `klauspost/compress` and the `init()`-time registration are
  unconditional for anyone importing the gRPC exporter packages, whether or not they configure
  `zstd`. That's a gap in the prototype, not a property of this proposal — flagging it rather than
  claiming it's solved.
- **SHOULD not MUST**, on both receivers and exporters. A compliant receiver can still reject
  `zstd`, and a compliant exporter can still omit it. Intentional, to keep the adoption bar low; a
  future OTEP could raise either once there's adoption data.

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
- **Rejected: general negotiation/capability-probing**, and **rejected: MUST-level receiver or
  exporter support** — see Trade-offs above. (A single gzip-retry-on-rejection fallback is in
  scope; general negotiation is not.)
- **Trigger**: [otel-go#8984][otel-go-issue] / [#8985][otel-go-pr] — maintainers correctly
  declined to add `zstd` ahead of spec support and asked for this OTEP as follow-up. That issue
  also flagged that otel-go silently falls back to no compression on an unrecognized
  `WithCompressor` value instead of erroring — a real bug, but a separate, SDK-specific one.

## Open questions

- Does this need to say anything about the profiles signal specifically, or is transport-level,
  signal-agnostic wording sufficient? (Profiles dropped a *mandatory* gzip requirement for its
  on-disk format — a different axis from the transport compression here.)
- Is `415` the right required HTTP status, or should `400` also be conformant?
- Compression level: TC discussion (2026-09-23) raised that configurable zstd level matters
  because it drives memory consumption. This OTEP doesn't propose a level knob — doing so adds
  more config surface, compounding the `opentelemetry-configuration` schema work already required
  (see Internal details). Fold a level option into this OTEP now, or leave it to a fast-follow
  once the base codec is approved?
- Is there appetite to eventually raise `zstd` receiver or exporter support from SHOULD to MUST,
  and what adoption bar would justify that?

## Prototypes

- [otel-go#8985][otel-go-pr] — gRPC only (`otlptracegrpc`/`otlpmetricgrpc`), with wire-level tests
  asserting the negotiated codec. Blocked pending this OTEP, and predates the gzip-retry-on-
  rejection requirement above.
- **No working HTTP prototype exists.** That same PR extends the HTTP exporters' compression enum
  and env-var parsing to accept `zstd`, but their request builders only handle `none`/`gzip` —
  selecting `zstd` leaves the body reader nil and the first export panics. This OTEP proposes
  `zstd` for both transports; only one has been proven out. A working, tested HTTP prototype is
  needed before this can be considered validated for that transport.

## Future possibilities

- A general compression-negotiation OTEP, applicable to any codec — out of scope here.
- Same treatment for other modern codecs (e.g. `brotli`) if there's similar demand.
- Revisiting SHOULD vs. MUST for `zstd` receiver/exporter support once adoption data exists.

[exporter-spec]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md
[proto-spec]: https://github.com/open-telemetry/opentelemetry-proto/blob/main/docs/specification.md
[java-contrib-zstd]: https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/compressors/compressor-zstd/README.md
[proto-629]: https://github.com/open-telemetry/opentelemetry-proto/issues/629
[proto-661]: https://github.com/open-telemetry/opentelemetry-proto/pull/661
[grpc-compression-spec]: https://github.com/grpc/grpc/blob/master/doc/compression.md
[otel-go-issue]: https://github.com/open-telemetry/opentelemetry-go/issues/8984
[otel-go-pr]: https://github.com/open-telemetry/opentelemetry-go/pull/8985
