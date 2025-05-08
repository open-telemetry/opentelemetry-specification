# Pluggable Authentication Interface for OTLP Exporters

Introduce a pluggable authentication mechanism for OTLP exporters (traces, metrics, logs) in OpenTelemetry SDKs, enabling users to inject custom authenticators.

## Motivation

As OpenTelemetry adoption grows, many vendors—including cloud providers—now expose OTLP endpoints for traces, logs, and metrics. These endpoints often require authenticated requests, using methods ranging from simple OAuth2 bearer tokens to complex schemes like AWS SigV4.

While the OpenTelemetry Collector supports pluggable `auth` extensions (e.g., [sigv4auth](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/sigv4authextension), [oauth2clientauth](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/oauth2clientauthextension)), the SDKs do not offer a standardized way to add authentication to OTLP exporters. Today, SDK users resort to authentication workarounds available within some SDKs (like header supplier in Java, and custom requests session in Python) but these are limited in capabilities and are not standard across all languages. Otherwise SDK users must either fork exporter implementations or build custom wrappers to inject authentication logic—leading to fragmentation and duplicated effort.

This OTEP proposes adding a standard pluggable authentication interface to OTLP exporters in SDKs. It enables users to inject custom authenticators (e.g., for SigV4 or OAuth2) without altering exporter internals. This improves portability, simplifies integration with secured backends, and brings SDKs closer to feature parity with the Collector—empowering secure, direct export from applications without requiring a Collector.

*[TODO] Call out the other gh issues and PRs that are opened in relation to this.*

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
In this example, the MyCustomAuthenticator injects the necessary authentication headers into each OTLP request before it is sent.

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
    def authenticate(self, request: requests.Request) -> None:
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

A similar pattern can be applied in Java using a decorator for OkHttpClient, though it could be a more complicated in Java since there are multiple Sender possible.

## Trade-offs and mitigations [TODO]

What are some (known!) drawbacks? What are some ways that they might be mitigated?

Note that mitigations do not need to be complete *solutions*, and that they do not need to be accomplished directly through your proposal. A suggested mitigation may even warrant its own OTEP!

## Prior art and alternatives [TODO]

What are some prior and/or alternative approaches? For instance, is there a corresponding feature in OpenTracing or OpenCensus? What are some ideas that you have rejected?

## Open questions [TODO]

What are some questions that you know aren't resolved yet by the OTEP? These may be questions that could be answered through further discussion, implementation experiments, or anything else that the future may bring.

- How would this work with auto-instrumentations??

## Future possibilities [TODO]

What are some future changes that this proposal would enable?
