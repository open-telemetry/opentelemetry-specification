# Pluggable Authentication Interface for OTLP Exporters

Introduce a pluggable authentication mechanism for OTLP exporters (traces, metrics, logs) in OpenTelemetry SDKs, enabling users to inject custom authenticators.

## Motivation

As OpenTelemetry adoption grows, many vendors—including cloud providers—now expose OTLP endpoints for traces, logs, and metrics. These endpoints often require authenticated requests, using methods ranging from simple OAuth2 bearer tokens to complex schemes like AWS SigV4.

While the OpenTelemetry Collector supports pluggable `auth` extensions (e.g., [sigv4auth](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/sigv4authextension), [oauth2clientauth](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/oauth2clientauthextension)), the SDKs do not offer a standardized way to add authentication to OTLP exporters. Today, SDK users resort to authentication workarounds available within some SDKs (like [header supplier in Java](https://opentelemetry.io/docs/languages/java/sdk/#authentication), and [custom requests session in Python](https://github.com/open-telemetry/opentelemetry-python/issues/4459#issuecomment-2711675191)) but these are limited in capabilities and are not standard across all languages. Otherwise SDK users must either fork exporter implementations or build custom wrappers to inject authentication logic—leading to fragmentation and duplicated effort.

This OTEP proposes adding a standard pluggable authentication interface to OTLP exporters in SDKs. It enables users to inject custom authenticators (e.g., for SigV4 or OAuth2) without altering exporter internals. This improves portability, simplifies integration with secured backends, and brings SDKs closer to feature parity with the Collector—empowering secure, direct export from applications without requiring a Collector.

This requirement has been brought up in the past via multiple issues in defferent forms:

* [Limited OTLP exporter request authentication methods](https://github.com/open-telemetry/opentelemetry-specification/issues/4390)
* [Exporter authentication](https://github.com/open-telemetry/opentelemetry-specification/issues/1344)
* [Sigv4 Authentication in OtlpHttp{Signal}Exporter](https://github.com/open-telemetry/opentelemetry-java/issues/7002)
* [Improved support to enable Authentication on otlp exporters (or any exporter?)](https://github.com/open-telemetry/opentelemetry-java/issues/4590)
* [Better support for OTLP header authentication](https://github.com/open-telemetry/opentelemetry-java/issues/4292)

## Explanation

Each OTLP exporter (for traces, metrics, and logs) exposes a new optional configuration parameter `authenticator` which allows users to plug in a custom authenticator implementation.

An authenticator is a user-defined component that modifies outgoing requests to add the appropriate authentication metadata, such as headers or tokens. This plugin model is conceptually similar to the `auth` extensions used in the OpenTelemetry Collector, but scoped for SDK usage.

For example, in Python:

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from my.auth import MyCustomAuthenticator  # Custom implementation

exporter = OTLPSpanExporter(
    endpoint="https://my-otlp.com/v1/traces",
    authenticator=MyCustomAuthenticator(region="us-west-2")
)
```

In this example, the `MyCustomAuthenticator` injects the necessary authentication headers into each OTLP request before it is sent.

The authenticator interface is transport-agnostic: exporters that send data over HTTP or gRPC both invoke the authenticator at the appropriate time, just before dispatching the request. For HTTP, this might involve mutating headers; for gRPC, it may involve setting metadata or using per-RPC credentials.

## Internal details

This proposal introduces an Authenticator interface that can be optionally passed to OTLP exporters in OpenTelemetry SDKs. The core idea is to allow users to inject authentication logic into outbound requests (both HTTP and gRPC) without altering the behavior of existing exporter implementations.

### Impact on Existing Functionality

- Backward Compatibility: Existing OTLP exporters remain unchanged for users who do not specify an authenticator. The new interface is optional and defaults to a no-op.

- Minimal Invasiveness: Changes are localized to the request dispatch paths of the OTLP exporters, specifically just before sending data.

- Cross-signal Applicability: The change can be implemented in the common OTLP exporter infrastructure shared across signal types (trace, metrics, logs), avoiding duplication.

### Proposed Authenticator Interface

Each SDK would define an Authenticator interface (or class, depending on the language and the exporter client), such as:

```python
class Authenticator:
    def authenticate(self, request: requests.PreparedRequest) -> None:
        """Mutate the request to add auth headers, tokens, etc."""
```

### Likely Error Modes

- Authenticator Failures: If the authenticator raises an error (e.g., token fetch failed), the exporter should surface this as an export failure. Exporter retry logic should apply as it does for network errors.

- Misconfiguration: If an authenticator is provided but incompatible with the transport (e.g., HTTP-style auth on gRPC), the exporter should log an error and fail fast.

- Invalid Auth Data: If the authenticator produces invalid headers or credentials, the exporter may receive 4xx responses. These are already surfaced as part of OTLP exporter diagnostics.

### Corner Cases

- Concurrent Auth Use: Exporters may be shared across threads. Authenticator implementations must be thread-safe or instantiated per-exporter.

- Multiple Signals, One Authenticator: If users share a single authenticator across trace, log, and metric exporters, SDKs must not cache or mutate state inside the exporters in ways that interfere with this usage.

### Implementation Suggestion

The initial implementation can be language-specific and start with HTTP-based exporters, which are simpler to modify. For example, in Python, the OTLP HTTP exporter can accept a new authenticator parameter, and modify its send() method to invoke `authenticator.authenticate(request)` before dispatch.

A similar pattern can be applied in Java using a decorator for OkHttpClient, though it could be a more complicated in Java since there are multiple [Sender](https://opentelemetry.io/docs/languages/java/sdk/#senders) possible with different HTTP client in each.

## Trade-offs and mitigations

The following trade-offs are mostly concerning increased surface area for complexity, misconfiguration and errors on both the SDK side and the user side.

**Added Complexity in Exporter Configuration:**
Introducing an authentication plugin system adds a new layer of complexity. SDKs must support a pluggable authenticator model, and users must understand and correctly implement authenticators suitable for their telemetry destination.

Mitigation:

- Provide well-documented built-in authenticators or vendor-maintained libraries.
- Offer clear examples and quickstarts in official OpenTelemetry SDK docs.

**Potential for Misconfiguration:**
Users may attach an incompatible authenticator to an exporter (e.g., using an HTTP authenticator with a gRPC exporter), leading to failed exports.

Mitigation:

- SDKs should validate the compatibility between exporter type and authenticator type during exporter construction.
- Emit clear errors or warnings during initialization when mismatches are detected.

**Increased Surface Area for Errors:**
Authenticator implementations may fail in complex ways—e.g., expired tokens, failed credential resolution, or transient network errors. This can degrade telemetry delivery reliability.

Mitigation:

- Exporters should treat authentication failures as transient errors and apply standard retry logic.
- Encourage authenticators to expose metrics or logs to help users diagnose failures.

## Prior art and alternatives

- OpenTelemetry Collector supports pluggable authentication via [extensions](https://opentelemetry.io/docs/collector/building/authenticator-extension/). Some examples:
  - [sigv4authextension](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/sigv4authextension)
  - [oauth2client](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/oauth2clientauthextension)
- OpenTelemetry [Python](https://github.com/open-telemetry/opentelemetry-python/blob/037e9cb100a78ee2b50d297aaa381b1097708041/exporter/opentelemetry-exporter-otlp-proto-http/src/opentelemetry/exporter/otlp/proto/http/trace_exporter/__init__.py#L76) and [Go](https://github.com/open-telemetry/opentelemetry-go/pull/6688) have mechanisms to let users provide custom `Session` or `Client` respectivelt to the exporter. This provides grounds for expanding the capabilities of these exporters beyond authentication if that's something we are interested in.

## Open questions

1. How would this work with auto-instrumentations? Most auto-instrumentations configure exporters internally using well-defined environment variables, so we need to explore how to expose and inject authenticators cleanly in those flows.

2. If a single application exports traces, metrics, and logs to the same backend, can or should it share a common authenticator instance?

3. What is the expected lifecycle of an authenticator? Should authenticators be tied to the exporter lifecycle (init/shutdown), and how should credential caching or rotation be handled?

## Future possibilities

Cloud providers and SaaS vendors could publish and maintain authenticators for their services (e.g., AWS SigV4, GCP OAuth, Azure MSI), making it easier for users to export telemetry securely without writing custom logic.
