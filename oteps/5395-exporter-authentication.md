# OTLP Exporter Authentication

Introduce an `Authenticator` SDK plugin component for dynamic client
authentication in exporters (with initial support on `otlp/http` and `otlp/grpc`
across traces, metrics, and logs).

## Motivation

OpenTelemetry SDKs increasingly export telemetry directly over OTLP to remote
Collector gateways, managed cloud ingestion endpoints, and observability
backends that require dynamic, short-lived credentials rather than static API
keys:

* **OAuth 2.0 / OIDC (`oauth2client`)**: Enterprise Collector gateways and SaaS
  backends authenticating via OAuth 2.0 Client Credentials grants or OpenID
  Connect tokens that must be refreshed before expiry.
* **Cloud Provider IAM & Managed Identity (`azureauth`, `googleclientauth`, `sigv4auth`)**:
  Managed OTLP endpoints requiring short-lived cloud credentials—such as
  Microsoft Entra ID (Azure Managed Identity) tokens, Google Cloud Application
  Default Credentials (ADC) or Workload Identity tokens, and AWS IAM STS
  credentials or (in SDKs using HTTP transport/request wrappers) SigV4 request
  signing.
* **Rotating Bearer Token Files & Custom Schemes (`bearertokenauth`, `basicauth`, `asapclient`)**:
  Workloads authenticating with bearer tokens loaded from mounted secret/token
  files that are periodically rotated on disk (watched by the Collector's
  `bearertokenauth` `filename` option), or service-to-service JWT schemes.

Today, the OpenTelemetry Specification only defines static headers
(`OTEL_EXPORTER_OTLP_HEADERS` and Declarative Configuration `headers` /
`headers_list`), which are evaluated once at SDK startup and cannot refresh
expired credentials.

As a result, SDKs have evolved fragmented, incompatible approaches (see
[Prior art](#prior-art-and-alternatives)), and Declarative Configuration has no
way to configure dynamic exporter authentication
([spec#1344](https://github.com/open-telemetry/opentelemetry-specification/issues/1344),
[opentelemetry-configuration#257](https://github.com/open-telemetry/opentelemetry-configuration/issues/257)).
For example, migrating existing autoconfiguration auth extensions to
Declarative Configuration is blocked because mutating the configuration model at
startup only fetches the token once at parse time
([opentelemetry-java-contrib#2020](https://github.com/open-telemetry/opentelemetry-java-contrib/pull/2020)).

## Example usage

This proposal introduces an **`Authenticator`** SDK plugin component that can be
attached to HTTP and gRPC exporters programmatically or via Declarative
Configuration.

### Programmatic configuration (Go and Java)

SDKs expose an `Authenticator` option following their language conventions:

```go
// Go example with otlptracehttp / otlptracegrpc and an OAuth2 authenticator
// implementing HTTP RoundTripper wrapping and gRPC credentials.PerRPCCredentials
auth, err := oauth2.New(
    oauth2.WithTokenURL("https://idp.example.com/oauth/token"),
    oauth2.WithClientCredentials(clientID, clientSecret),
)
httpExporter, err := otlptracehttp.New(ctx,
    otlptracehttp.WithEndpointURL("https://telemetry.example.com/v1/traces"),
    otlpauth.WithTraceHTTPAuthenticator(auth),
)
grpcExporter, err := otlptracegrpc.New(ctx,
    otlptracegrpc.WithEndpoint("telemetry.example.com:4317"),
    otlpauth.WithTraceGRPCAuthenticator(auth),
)
```

```java
// Java example with OtlpHttpSpanExporter and an OAuth2 authenticator
Authenticator auth = OAuth2ClientCredentialsAuthenticator.builder()
    .setTokenUrl("https://idp.example.com/oauth/token")
    .setClientId(clientId)
    .setClientSecret(clientSecret)
    .build();
OtlpHttpSpanExporterBuilder builder = OtlpHttpSpanExporter.builder()
    .setEndpoint("https://telemetry.example.com/v1/traces");
OtlpExporterUtil.setAuthenticator(builder, auth);
OtlpHttpSpanExporter exporter = builder.build();
```

### Declarative Configuration

`ExperimentalAuthenticator` (stabilizing to `Authenticator`) is defined as an
open SDK extension plugin (`isSdkExtensionPlugin: true`, accepting any single
plugin name key mapped to its `ConfigProperties` object or `null`) in
`schema/common.yaml`. Any custom, contrib, or vendor authenticator registered
via [`PluginComponentProvider`](../specification/configuration/sdk.md#plugincomponentprovider)
(such as `oauth2`, `bearertokenauth`, or a user-defined
`my_custom_authenticator`) can be configured by its registered plugin name.
`OtlpHttpExporter` and `OtlpGrpcExporter` (`schema/common.yaml`, shared by trace
and log exporters) and `OtlpHttpMetricExporter` and `OtlpGrpcMetricExporter`
(`schema/meter_provider.yaml`) gain an optional `authenticator/development`
property referencing `ExperimentalAuthenticator`:

```yaml
file_format: "1.0"
tracer_provider:
  processors:
    - batch:
        exporter:
          otlp_http:
            endpoint: https://telemetry.example.com/v1/traces
            authenticator/development:
              oauth2:
                token_url: https://idp.example.com/oauth/token
                client_id: ${OAUTH_CLIENT_ID}
                client_secret: ${OAUTH_CLIENT_SECRET}
                scopes: ["otel.export"]
```

```yaml
file_format: "1.0"
meter_provider:
  readers:
    - periodic:
        exporter:
          otlp_grpc:
            endpoint: https://telemetry.example.com:4317
            authenticator/development:
              bearertokenauth:
                filename: /var/run/secrets/tokens/otel-token
```

```yaml
file_format: "1.0"
logger_provider:
  processors:
    - batch:
        exporter:
          otlp_http:
            endpoint: https://telemetry.example.com/v1/logs
            authenticator/development:
              my_custom_authenticator:
                custom_option: value
```

## Proposal

Previous attempts to standardize exporter authentication stalled because
languages have very different HTTP/gRPC transport stacks and concurrency models.
This proposal draws a boundary between **cross-language behavioral
requirements** (which are specified) and **language-idiomatic transport
interfaces** (which are left to each SDK).

### What the Specification WILL specify

1. **New Common SDK `Authenticator` Specification (`specification/auth/sdk.md`, indexed under `SDK Specification` in `specification/README.md`)**:
   * **General Exporter Scope**: Defines `Authenticator` in a standalone SDK
     specification document for HTTP and gRPC exporters rather than coupling it
     exclusively to OTLP. SDKs SHOULD define the `Authenticator` interface in a
     common SDK or shared exporter-transport package so that authentication
     plugins do not need to depend on the OTLP exporter package, non-OTLP
     HTTP/gRPC exporters can reuse them, and separate per-signal/per-protocol
     exporter modules share a common contract.
   * **What the `Authenticator` mechanism SHOULD support**:
     * Dynamically attaching per-request HTTP headers or gRPC request metadata
       (including multiple headers per request, such as `Authorization` and
       tenant/routing headers), or wrapping/configuring the underlying HTTP
       transport (`http.RoundTripper`) or gRPC per-RPC credentials
       (`credentials.PerRPCCredentials` / `CallCredentials`) where idiomatic.
     * Bounding authentication operations so that credential acquisition MUST
       NOT block indefinitely, with a reasonable upper limit after which the
       operation times out with an error (matching the existing exporter
       `Export` timeout model; OpenTelemetry SDK authors can decide if they want
       to make the timeout configurable or pass a timeout, deadline, or
       cancellation signal).
     * An optional `Shutdown` lifecycle operation to release background
       resources (such as token-exchange HTTP clients or file watchers).
       `Shutdown` SHOULD NOT block indefinitely, and OpenTelemetry SDK authors
       can decide if they want to make the shutdown timeout configurable.
   * **What the `Authenticator` mechanism MUST NOT require**:
     * MUST NOT require the exporter to materialize or pass the full serialized
       request payload (`byte[]`) in memory, preserving streaming serialization
       (e.g., Java's `OkHttpHttpSender`). Consequently, payload-signing schemes
       like AWS SigV4 (which hash the compressed HTTP request body alongside the
       request URI and headers) are supported in SDKs whose `Authenticator`
       wraps the HTTP transport or request (e.g., Go `http.RoundTripper` or
       Python `requests.Session` / `requests.auth.AuthBase`), whereas SDKs that
       use a header-only supplier (`getHeaders()`) support payload-independent
       credentials (such as bearer tokens, OAuth 2.0/OIDC, and API keys) and
       rely on transport-level hooks or dedicated exporter wrappers for
       full-payload signing.
     * MUST NOT require access to in-memory telemetry items (spans, metrics, or
       log records), keeping authentication strictly at the transport layer.
   * **Required documentation for plugin authors**:
     * SDKs MUST document—on the `Authenticator` interface or on the exporter
       configuration option that accepts it—that `Authenticator` implementations
       must not block indefinitely (honoring any provided timeout, deadline, or
       cancellation signal), must be safe to invoke concurrently, and must not
       log sensitive credential or header values.
2. **OTLP Exporter Specification (`specification/protocol/exporter.md` — new `## Authentication` section)**:
   * **Support on OTLP Exporters**: OTLP HTTP and gRPC exporters across traces,
     metrics, and logs SHOULD support configuring an `Authenticator`.
   * **Exporter Behavior with Header/Metadata Suppliers**: When the SDK's
     `Authenticator` produces dynamic headers or metadata that the exporter
     attaches:
     * The exporter MUST invoke the `Authenticator` for each outgoing export
       request attempt (including retry attempts) rather than only at
       initialization.
     * The exporter MUST merge its configured headers with the dynamic headers
       or metadata returned by the `Authenticator` for each export attempt. If
       the same header or metadata key is defined in multiple places (compared
       case-insensitively), the `Authenticator`-supplied value MUST take
       precedence over any dynamic header callback (where supported by the SDK)
       and static `Headers` (`OTEL_EXPORTER_OTLP_*_HEADERS` or Declarative
       Configuration `headers` / `headers_list`) for that request, without
       mutating the static `Headers`.
   * **Exporter Behavior with Transport/Credential Wrappers**: When the SDK's
     `Authenticator` wraps the HTTP transport (e.g., Go `http.RoundTripper` or
     .NET `DelegatingHandler`) or provides gRPC per-RPC credentials (e.g., Go
     `credentials.PerRPCCredentials` or `CallCredentials`):
     * The exporter MUST still attach its configured static `Headers` to each
       outgoing request or RPC (for HTTP transport wrappers, before the wrapper
       executes so that wrapper-supplied headers override colliding static
       headers without mutating the static `Headers`).
     * The exporter MUST wire the `Authenticator` onto its transport, channel,
       or RPC call options such that the exporter's configured TLS/mTLS
       (`Certificate File`, `Client key file`, `Client certificate file`),
       `Compression`, and `Timeout` settings are preserved rather than
       overwritten, and so that per-RPC credentials apply on each RPC attempt
       (including when a user-supplied gRPC connection is used).
   * **Suppressing Recursive Telemetry, Diagnostics & Lifecycle**:
     * In SDKs that provide an in-band `Context` mechanism for suppressing
       instrumentation (see
       [Avoiding telemetry-induced-telemetry loops](../specification/self-observability-supplementary-guidelines.md#avoiding-telemetry-induced-telemetry-loops)),
       the exporter SHOULD invoke the `Authenticator` within a
       suppressed-instrumentation context so that outbound network requests made
       during credential refresh do not trigger recursive telemetry export loops.
     * If invoking the `Authenticator` fails or raises an error during an export
       attempt, the exporter MUST handle the error in accordance with
       [Error handling](../specification/error-handling.md) rather than throwing
       an unhandled exception, and complete the export attempt with a failure
       result.
     * The exporter MUST NOT log dynamic header or metadata values returned by
       the `Authenticator`, and MUST invoke the `Authenticator`'s `Shutdown`
       operation (if present) when the exporter's `Shutdown` is called.
3. **Declarative Configuration (`specification/configuration/sdk.md` & `opentelemetry-configuration`)**:
   * Add `[exporter authenticator]` (`ExperimentalAuthenticator`, with
     `Missing provider behavior: error`) to the
     [Supported SDK plugin components](../specification/configuration/sdk.md#supported-sdk-plugin-components)
     table.
   * In `opentelemetry-configuration`, define `ExperimentalAuthenticator`
     (`isSdkExtensionPlugin: true`, with `additionalProperties` accepting any
     plugin name mapped to an object or `null`, `minProperties: 1`,
     `maxProperties: 1`) in `schema/common.yaml` and add optional
     `authenticator/development` (`defaultBehavior: no authenticator is used`)
     to `OtlpHttpExporter`, `OtlpGrpcExporter`, `OtlpHttpMetricExporter`, and
     `OtlpGrpcMetricExporter`.

### What the Specification WILL NOT specify

1. **Exact Language-Level Method Signatures (Header Supplier vs. Transport/Credential Hooks)**:
   * The specification will **not** mandate a single low-level function
     signature across languages. Each language SDK defines the idiomatic
     interface (or pair of HTTP and gRPC interfaces) that its
     `PluginComponentProvider` for `ExperimentalAuthenticator` produces:
     * **Language-native transport and per-RPC credential hooks**: For example,
       in Go (matching the Collector's `extensionauth.HTTPClient` and
       `extensionauth.GRPCClient`), wrapping a base `http.RoundTripper` for HTTP
       and returning `credentials.PerRPCCredentials` for gRPC so existing
       ecosystem libraries (`golang.org/x/oauth2`, `google.golang.org/grpc/credentials/oauth`)
       plug in directly.
     * **Per-request header/metadata supplier**: For example, in Java (where
       OTLP exporters use an SDK-owned `HttpSender`/`GrpcSender` abstraction
       whose default OkHttp gRPC sender does not depend on `io.grpc`), Python
       (where HTTP exporters span `RequestsHTTPTransport` and
       `Urllib3HTTPTransport`), and JS/TS (`OTLPExporterBase`), returning
       dynamic key-value header/metadata maps per export attempt.
2. **Built-in Vendor or Protocol Implementations and Schemas**:
   * This proposal does not define fixed YAML schemas or require SDKs to bundle
     concrete authentication implementations (such as `oauth2`, `aws`, `azure`,
     or `gcp`); like vendor exporters or cloud resource detectors, these are
     provided as contrib or third-party plugin packages configured via the
     `ExperimentalAuthenticator` extension point. Promoting common protocol
     authenticators (such as `oauth2`) to built-in types is left as a
     [future extension](#future-possibilities).
3. **New Environment Variables**:
   * This proposal does not introduce `OTEL_EXPORTER_OTLP_AUTHENTICATOR`
     environment variables. Authentication plugins typically require structured
     parameters (such as token endpoints, scopes, audiences, or file paths) that
     fit Declarative Configuration rather than flat environment variables.

## Prior art and alternatives

### Current support across all 12 OpenTelemetry SDKs and the Collector

| Implementation | HTTP OTLP Auth | gRPC OTLP Auth | Declarative Config (SDK) |
| --- | --- | --- | --- |
| **Collector** | `extensionauth.HTTPClient` (wraps base `http.RoundTripper`) | `extensionauth.GRPCClient` (`PerRPCCredentials`) | `auth: { authenticator: <id> }` |
| **Go** | `WithHTTPClient(*http.Client)` ([opentelemetry-go#6688](https://github.com/open-telemetry/opentelemetry-go/pull/6688)) | `WithDialOption(grpc.WithPerRPCCredentials(...))` | Static `headers` only |
| **Java** | `setHeaders(Supplier<Map<String, String>>)` | `setHeaders(Supplier<Map<String, String>>)` | Static `headers` only (blocks [opentelemetry-java-contrib#2020](https://github.com/open-telemetry/opentelemetry-java-contrib/pull/2020)) |
| **JS / TS** | Async `HeadersFactory` (`() => Promise<Record<string, string>>`) | `credentials` (`ChannelCredentials` with `CallCredentials` metadata generator) | Static `headers` only |
| **Python** | `session: requests.Session` (+ experimental entry point in [opentelemetry-python#4689](https://github.com/open-telemetry/opentelemetry-python/pull/4689)) | `credentials: grpc.ChannelCredentials` (with `grpc.metadata_call_credentials`) | Static `headers` only |
| **.NET** | `HttpClientFactory` (`Func<HttpClient>`) | `GrpcChannelOptions` (`CallCredentials`) | N/A (schema has static `headers` only) |
| **Rust** | Custom `HttpClient` trait | `tonic` `Interceptor` ([opentelemetry-rust#2881](https://github.com/open-telemetry/opentelemetry-rust/issues/2881)) | N/A (schema has static `headers` only) |
| **C++** | Static `http_headers` only | `grpc::ChannelCredentials` (via `CompositeChannelCredentials` + `MetadataCredentialsFromPlugin` `CallCredentials`) | N/A |
| **Swift** | `headersProvider: () -> [(String, String)]?` or custom `HTTPClient` | `headersProvider` on `OtlpConfiguration` | N/A |
| **Kotlin** | Custom `HttpClient` / `HttpClientEngine` or static `headers` | N/A | N/A |
| **PHP** | Custom PSR-18 `ClientInterface` (programmatic) or static `headers` | Static `headers` only | Static `headers` only |
| **Ruby** | Static `headers` (`Hash` / `String`) only | N/A | N/A |
| **Erlang / Elixir** | Static `headers` list in `init/1` only | Static `headers` / `grpc_metadata` in `init/1` only | N/A |

### Alternatives considered

1. **Requiring all SDKs to pass the serialized request body (`byte[]`) to a
   signing callback
   ([spec#4390](https://github.com/open-telemetry/opentelemetry-specification/issues/4390),
   [spec#4500](https://github.com/open-telemetry/opentelemetry-specification/pull/4500))**:
   Rejected as a cross-language requirement because streaming exporters (such as
   Java's `OkHttpHttpSender`) write protobuf directly to an `OutputStream`
   without allocating a contiguous `byte[]` buffer. Because AWS OTLP endpoints
   (such as X-Ray and CloudWatch) require a SHA-256 hash of the compressed HTTP
   payload (`x-amz-content-sha256`) and do not accept S3's `UNSIGNED-PAYLOAD`,
   AWS SigV4 works directly with `Authenticator` in SDKs whose interface wraps
   the HTTP transport or request (e.g., Go `http.RoundTripper` matching the
   Collector's `sigv4authextension`, .NET `DelegatingHandler`, or Python
   `requests.Session` / `requests.auth.AuthBase`), while SDKs that choose a
   header-only supplier (`getHeaders()`) omit built-in payload signing to
   preserve zero-copy streaming serialization.
2. **Dynamic `${secret:TOKEN}` placeholder syntax inside `headers`
   ([opentelemetry-configuration#257](https://github.com/open-telemetry/opentelemetry-configuration/issues/257))**:
   Rejected because `${...}` substitution in Declarative Configuration happens
   once at YAML parse time, cannot inject multiple dynamic headers from a single
   credential, and cannot pass structured configuration (`token_url`, `scopes`,
   `audience`) to the plugin.
3. **Relying only on programmatic `DeclarativeConfigCustomizer` hooks
   ([spec#4777](https://github.com/open-telemetry/opentelemetry-specification/pull/4777))**:
   Rejected as a standalone solution because users cannot select or configure
   an authenticator in the YAML file itself, nor can they easily attach
   different authenticators to different OTLP exporters in the same config file.
4. **Top-level shared `authenticators:` map (Collector `extensions` style)**:
   Deferred in favor of inline `authenticator/development:` on each exporter,
   which matches all other SDK extension plugins in `opentelemetry-configuration`
   (`sampler`, `span_exporter`, `resource_detector`) and avoids cross-tree ID
   references.

## Future possibilities

* Promoting common authenticators (such as `oauth2` / `oauth2client` or
  `bearertokenauth`) to built-in types in `opentelemetry-configuration` and
  standardizing their configuration fields.
  Reference prototypes in Go, Java, Python, and JS/TS demonstrated that an
  RFC 6749 `client_credentials` `oauth2` authenticator can be implemented using
  only standard-library dependencies across all four languages with a uniform
  configuration schema (`token_url`, `client_id`, `client_secret`, `scopes`,
  `audience`).
* Reusing `Authenticator` for non-exporter SDK components that make outbound
  network requests (such as remote samplers or OpAMP clients).
