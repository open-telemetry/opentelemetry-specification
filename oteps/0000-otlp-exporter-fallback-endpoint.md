# OTLP Exporter Fallback Endpoint

Add optional fallback endpoint configuration to OTLP exporters so that, when export to the primary endpoint fails after retries are exhausted, the exporter can attempt export to a secondary endpoint before reporting failure.

## Motivation

OTLP exporters today support a single export destination per signal. When that destination is unreachable, telemetry is dropped after the exporter's retry policy is exhausted.

The common mitigation is to place a load balancer in front of one or more collectors. That works well in some topologies, but it is not always practical:

- **Operational overhead** — Provisioning, configuring, and monitoring load balancers for every collector endpoint adds cost and complexity, especially at scale (for example, thousands of collector instances serving dedicated workloads).
- **Deployment constraints** — Teams running collectors as sidecars or per-node daemonsets may have no natural place to insert a load balancer without re-architecting the deployment.
- **Simple redundancy requirement** — The desired behavior is often narrow: if this endpoint is unavailable, try another. A load balancer is a heavier solution than necessary for that requirement.

SDK-level fallback is an established pattern in database drivers, HTTP clients, and other network libraries. It complements load balancing rather than replacing it: deployments that already use load balancers can ignore fallback configuration; deployments without load balancers gain a lightweight safety net.

Related specification issue: [#4973](https://github.com/open-telemetry/opentelemetry-specification/issues/4973).

## Explanation

When a fallback endpoint is configured, OTLP exporters behave as follows for each export attempt:

1. Send telemetry to the **primary** endpoint using the configured protocol, applying the existing retry policy for transient errors.
2. If export to the primary endpoint **succeeds**, the export completes successfully.
3. If export to the primary endpoint **fails after retries are exhausted** due to a [transient error](#failover-trigger), attempt export to the **fallback** endpoint using the same protocol and retry policy.
4. If export to the fallback endpoint succeeds, the export completes successfully.
5. If both endpoints fail, the export fails in the same way as today (for example, the exporter returns failure to the SDK, which applies its configured export error handling).

When no fallback endpoint is configured, exporter behavior is unchanged from today.

### Configuration

Fallback endpoint configuration follows the same naming and precedence conventions as existing OTLP endpoint configuration.

Environment variables:

| Scope | Environment variable |
|-------|---------------------|
| All signals | `OTEL_EXPORTER_OTLP_FALLBACK_ENDPOINT` |
| Traces | `OTEL_EXPORTER_OTLP_TRACES_FALLBACK_ENDPOINT` |
| Metrics | `OTEL_EXPORTER_OTLP_METRICS_FALLBACK_ENDPOINT` |
| Logs | `OTEL_EXPORTER_OTLP_LOGS_FALLBACK_ENDPOINT` |

Signal-specific variables override the generic variable for that signal, matching the precedence of `OTEL_EXPORTER_OTLP_<signal>_ENDPOINT` over `OTEL_EXPORTER_OTLP_ENDPOINT`.

Implementations MUST also expose a programmatic configuration option on OTLP exporter builders (for example, `setFallbackEndpoint(String)` in Java) to set the fallback endpoint for that exporter instance.

The fallback endpoint MUST NOT be configured to the same resolved destination as the primary endpoint. If it is, implementations SHOULD log a warning and MAY treat the fallback as unset.

### Example

A service sends all signals to a local sidecar collector, with a regional collector as fallback:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_FALLBACK_ENDPOINT=https://collector.example.com:4318
```

If the local sidecar is down, traces are sent to `https://collector.example.com:4318/v1/traces`, metrics to `https://collector.example.com:4318/v1/metrics`, and logs to `https://collector.example.com:4318/v1/logs`, using the same URL construction rules as the primary endpoint.

Traces can override only their fallback:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_TRACES_FALLBACK_ENDPOINT=https://traces-backup.example.com/v1/traces
export OTEL_EXPORTER_OTLP_FALLBACK_ENDPOINT=https://collector.example.com:4318
```

Traces use the traces-specific fallback; metrics and logs use the generic fallback.

### Relationship to other configuration

Unless specified otherwise in a future change, the fallback endpoint shares all non-endpoint OTLP exporter settings with the primary endpoint, including:

- Protocol (`grpc`, `http/protobuf`, `http/json`)
- Timeout
- Compression
- Headers
- TLS / mTLS settings (`certificate`, `client key`, `client certificate`, `insecure`)

Only the destination differs between primary and fallback. This keeps configuration predictable and avoids duplicating every exporter option for a secondary destination in the initial version of this feature.

### Export flow

```text
┌─────────────┐
│ Export batch│
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ Send to primary endpoint│◄── each export attempt starts here
└──────────┬──────────────┘
           │
     success? ──yes──► Done
           │
          no
           │
     transient error
     after retries
     exhausted?
           │
          no ──► Fail export
           │
          yes
           │
     fallback
     configured?
           │
          no ──► Fail export
           │
          yes
           ▼
┌──────────────────────────┐
│ Send to fallback endpoint│
└──────────┬───────────────┘
           │
     success? ──yes──► Done
           │
          no ──► Fail export
```

Each export attempt independently tries the primary endpoint first. Implementations MUST NOT permanently "stick" to the fallback endpoint after a successful failover. This ensures traffic returns to the primary endpoint automatically when it recovers.

## Internal details

### Failover trigger

Failover to the fallback endpoint MUST occur only when **both** of the following are true:

1. Export to the primary endpoint failed after the exporter's retry policy for transient errors was exhausted.
2. The failure is classified as a **transient error** as defined in the [OTLP Protocol Exporter retry section](../specification/protocol/exporter.md#retry) and the [OTLP protocol specification](https://github.com/open-telemetry/opentelemetry-proto/blob/main/docs/specification.md).

Transient errors include connection failures, timeouts, and retryable HTTP/gRPC status codes defined by OTLP.

Export failures caused by **non-transient** errors (for example, `400 Bad Request` indicating invalid payload) MUST NOT trigger failover. Sending the same payload to a fallback endpoint would not address the underlying problem.

### Retry behavior on fallback

The fallback endpoint MUST be subject to the same retry policy as the primary endpoint. Retries on the primary endpoint MUST be exhausted before attempting the fallback endpoint. Retries on the fallback endpoint MUST be exhausted before the overall export is considered failed.

Implementations MUST NOT duplicate retry attempts across endpoints in a way that multiplies total retry latency beyond what would occur for two sequential export attempts, each with the configured retry policy.

### Endpoint URL construction (OTLP/HTTP)

For OTLP/HTTP, fallback endpoint URLs MUST be constructed using the same rules as primary endpoint URLs described in [Endpoint URLs for OTLP/HTTP](../specification/protocol/exporter.md#endpoint-urls-for-otlphttp):

- Per-signal fallback variables (`OTEL_EXPORTER_OTLP_<signal>_FALLBACK_ENDPOINT`) MUST be used as-is, except that a URL with no path uses `/` as the path.
- The generic fallback variable (`OTEL_EXPORTER_OTLP_FALLBACK_ENDPOINT`) MUST be combined with per-signal paths (`v1/traces`, `v1/metrics`, `v1/logs`) for signals that do not have a signal-specific fallback configured.

For OTLP/gRPC, fallback endpoint values MUST accept the same forms as primary gRPC endpoints.

### Interaction with existing functionality

- **Batching** — Failover is per export operation (per batch), not per signal item within a batch.
- **Multiple exporters** — Fallback applies within a single OTLP exporter instance. Composing multiple exporters (for example, via a multi-exporter wrapper) remains a valid user-level pattern and is not replaced by this feature.
- **Collector** — This OTEP specifies SDK OTLP exporter behavior. OpenTelemetry Collector pipeline failover is out of scope.
- **Declarative configuration** — The [OpenTelemetry configuration schema](https://github.com/open-telemetry/opentelemetry-configuration) MUST be updated to include fallback endpoint settings when this change is integrated into the specification.

### Suggested implementation approach

Implementations may model the fallback endpoint as a second internal client/sender that shares connection settings with the primary client and is invoked only on qualifying primary failures. The Java proof-of-concept follows this approach in `HttpExporter` and `GrpcExporter`.

## Trade-offs and mitigations

### Duplication of telemetry during partial outages

If the primary endpoint accepts a request but the client times out before receiving a response, a retry or fallback attempt could result in duplicate telemetry at the backend.

**Mitigation:** This is an existing concern for OTLP retry behavior, not introduced uniquely by fallback. Backends should tolerate at-least-once delivery. Fallback does not change idempotency expectations beyond what retries already impose.

### Load balancing remains the preferred approach for many deployments

Spec maintainers have noted that a single endpoint fronted by a load balancer, combined with retry, may address failover by routing retries to healthy backends.

**Mitigation:** Fallback is optional. Teams with load balancers need not configure it. This feature targets deployments where load balancing is impractical or disproportionately costly.

### User-composed multi-exporter wrappers

Applications can already compose failover behavior by wrapping multiple OTLP exporters and attempting the next exporter when the first returns a retryable failure (as noted in [opentelemetry-java#8197](https://github.com/open-telemetry/opentelemetry-java/pull/8197)).

**Mitigation:** A specification-level fallback endpoint standardizes configuration (environment variables, autoconfigure, documentation) and ensures consistent behavior across languages. User wrappers remain valid for advanced cases (for example, different headers or protocols per destination).

### Increased export latency during outages

When the primary endpoint is down, export latency includes primary retries plus fallback retries.

**Mitigation:** This is expected during failure scenarios. Implementations SHOULD NOT add additional retry rounds beyond the configured policy. Operators can tune timeout and retry settings with the understanding that fallback adds a second export attempt.

### Shared TLS and headers may be insufficient for some failover topologies

Some deployments may require different credentials or headers on the fallback destination (for example, a disaster-recovery region with distinct mTLS certificates).

**Mitigation:** Defer separate per-endpoint TLS/header configuration to a future change if needed. Users with heterogeneous destinations can use a multi-exporter wrapper until then.

## Prior art and alternatives

### Load balancer in front of collectors

The most common production approach today. Provides health checking, traffic distribution, and transparent failover.

**Why not rely on this alone:** Operational cost, topology constraints, and cases where only a simple primary/secondary pair is needed.

### DNS-based failover

Rotate or resolve multiple collector addresses via DNS.

**Why not chosen:** Slow propagation, limited health awareness, and inconsistent behavior across runtimes make this a poor fit as a specification requirement.

### OpenTelemetry Collector routing and redundancy

Collectors support pipeline configuration, extensions, and operational patterns for high availability. SDK fallback does not replace collector-side redundancy.

**Why not chosen for this OTEP:** The motivating use case is SDK-to-collector export when the first collector destination is unreachable from the application.

### Application-level delegating exporter

Wrap multiple configured OTLP exporters and delegate on failure.

**Why not chosen as the only solution:** Works today but lacks cross-language configuration standards, autoconfigure integration, and consistent semantics. This OTEP standardizes the common two-endpoint case.

### Database / HTTP client failover patterns

Many network clients support primary and secondary connection strings or endpoint lists.

**Relevance:** Provides precedent for optional SDK-level failover without requiring external infrastructure.

## Open questions

1. **Should failover apply to partial batch failures?** This OTEP assumes failover is per export call (batch). If a batch partially succeeds on the primary endpoint, should the exporter attempt fallback for the remainder? (Initial proposal: no — treat export as atomic per batch attempt.)

2. **Observability of failover events** — Should exporters emit a standard log message, internal metric, or diagnostic event when failover occurs? (Initial proposal: implementations SHOULD log at warning level when failover is attempted; standard metrics may be a follow-up OTEP.)

3. **Maximum number of fallback endpoints** — This OTEP proposes a single fallback endpoint. Should the specification eventually support an ordered list?

4. **Collector exporter parity** — Should the Collector's OTLP exporter gain equivalent fallback configuration, or is SDK-only scope sufficient?

5. **Stability level** — Should fallback endpoint configuration be introduced at Development maturity alongside other new OTLP exporter options, or remain experimental until multiple language implementations exist?

## Prototypes

- **Specification issue:** [#4973](https://github.com/open-telemetry/opentelemetry-specification/issues/4973)
- **Java proof-of-concept:** [opentelemetry-java#8197](https://github.com/open-telemetry/opentelemetry-java/pull/8197)
  - Adds `setFallbackEndpoint(String)` to OTLP exporter builders
  - Implements failover in shared HTTP and gRPC exporter internals on transport errors after retries
  - Wires environment-variable configuration through autoconfigure providers

Additional language prototypes may be required before spec integration, depending on reviewer feedback and the scope of the integrating PR.

## Future possibilities

- Support for an ordered list of fallback endpoints beyond a single secondary destination.
- Per-endpoint TLS, header, and compression overrides when primary and fallback destinations differ in authentication requirements.
- Health-aware or latency-aware endpoint selection among multiple configured destinations.
- Integration with remote configuration mechanisms (for example, OpAMP) to update fallback endpoints at runtime.
- Standard metrics for failover attempts, successes, and failures to aid operations.
