# Semantic conventions for Azure SDK

**Status**: [Experimental](../../../document-status.md)

This document describes tracing semantic conventions adopted by Azure SDK. Instrumentations live in Azure SDK repos and are shipped along with Azure SDK artifacts. Instrumentations cover all modern (track 2) Azure client libraries.

- [Java](https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/core/azure-core-tracing-opentelemetry)
- [JavaScript](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/core/core-tracing)
- [Python](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry)
- [.NET](https://github.com/Azure/azure-sdk-for-net/blob/5ce907df6490e68c2e632d97048a6b6ee95c01f0/sdk/core/Azure.Core/samples/Diagnostics.md#activitysource-support)

Azure SDK produces spans for public API calls and nested HTTP client spans. Non-HTTP transport-level calls (AMQP, CosmosDB TCP-based protocol) are not traced.

## Versioning

Azure SDK semantic conventions pin specific versions of OpenTelemetry semantic conventions (where applicable) and are not updated regularly to the latest OpenTelemetry semantic conventions version. However OpenTelemetry-compatible changes should be expected.

Azure SDK plans to fully adopt OpenTelemetry semantic conventions once they reach `Stable` status.

## Common Attributes

All Azure SDKs spans have `az.namespace` attribute to uniquely identify *Azure SDK* request is made *from*, usually the value matches the destination Azure service, but in some cases client library can support multiple services.

<!-- semconv azure -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `az.namespace` | string | [Namespace](https://docs.microsoft.com/azure/azure-resource-manager/management/azure-services-resource-providers) of Azure service that the request is made against. | `Microsoft.Storage`; `Microsoft.KeyVault`; `Microsoft.ServiceBus` | Yes |

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* `az.namespace`
<!-- endsemconv -->

## Public API calls

Azure SDKs create a span for public API call (that involves communication with Azure services).

- Spans representing public APIs have names following `client.method` pattern, which is language-specific.
- For HTTP-based SDKs, public API spans have `INTERNAL` kind.

[Messaging](#messaging-sdks) and [CosmosDb](#cosmosdb) sections below describe non-HTTP semantics.

## HTTP Client

Azure SDK implements a valid subset of [OpenTelemetry HTTP conventions v1.8.0](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.8.0/specification/trace/semantic_conventions/http.md) and create a span per HTTP call (try).

<!-- semconv azure.sdk.http -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `request_id` | string | Value of the [x-ms-client-request-id] header (or other request-id header, depending on the service) sent by the client. | `eb178587-c05a-418c-a695-ae9466c5303c` | Yes |
| `service_request_id` | string | Value of the [x-ms-request-id]  header (or other request-id header, depending on the service) sent by the server in response. | `3f828ae5-ecb9-40ab-88d9-db0420af30c6` | Yes |
| [`http.method`](../http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Yes |
| [`http.status_code`](../http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Yes |
| [`http.url`](../http.md) | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [1] | `https://www.foo.bar/search?q=OpenTelemetry#SemConv` | Yes |
| [`http.user_agent`](../http.md) | string | Value of the [HTTP User-Agent](https://tools.ietf.org/html/rfc7231#section-5.5.3) or X-MS-UserAgent header sent by the client. | `CERN-LineMode/2.15 libwww/2.17b3` | Yes |

**[1]:** `http.url` MUST NOT contain credentials passed via URL in form of `https://username:password@www.example.com/`. In such case the attribute's value should be `https://www.example.com/`.

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* [`http.method`](../http.md)
* [`http.url`](../http.md)
* [`http.user_agent`](../http.md)
<!-- endsemconv -->

Instrumentation supports [W3C Trace context](https://w3c.github.io/trace-context/) propagation and Azure legacy correlation protocols. Propagator configuration is not supported.

## Messaging SDKs

Messaging span semantics apply to Azure Event Hubs and Service Bus SDKs.

Attribute names predate OpenTelemetry and originate from [OpenTracing semantic conventions](https://opentracing.io/specification/conventions/)

Messaging SDKs produce three kinds of spans:

- `PRODUCER` - describes message creation and associates unique context with the message to trace them when they are sent in batches.
  - Producer spans name follows `<client>.message` pattern (e.g. `EventHubs.message`)

- `CLIENT` - describes message (or batch) publishing.
  - It has links pointing to each message being sent.
  - Links don't have attributes.
  - Send spans name follows `<client>.send` pattern (e.g. `EventHubs.send`)

- `CONSUMER` - describes message (or batch) processing.
  - It is created when user leverages handler APIs that wrap message or batch processing.
  - Processing span has links to each message being processed (when context is present).
  - Each link has `enqueued_time` attribute with `long` value with unix epoch time (with milliseconds precision) representing when message was enqueued on the broker.

### Messaging attributes

<!-- semconv azure.sdk.messaging -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `message_bus.destination` | string | Name of the messaging entity within namespace: e.g EventHubs name, ServiceBus queue or topic name. | `myqueue`; `myhub` | Yes |
| `peer.address` | string | Fully qualified messaging service name. | `myEventHubNamespace.servicebus.windows.net` | Yes |
<!-- endsemconv -->

## CosmosDB

CosmosDB SDK in [Direct mode](https://docs.microsoft.com/azure/cosmos-db/sql/sql-sdk-connection-modes#available-connectivity-modes) uses TCP-based protocol and traces public API calls only.
CosmosDB semantic conventions are pinned to OpenTelemetry [Semantic Conventions v0.5.0](https://github.com/open-telemetry/opentelemetry-specification/blob/v0.5.0/specification/trace/semantic_conventions/database.md) version.

Spans have `CLIENT` kind and the name matches `db.statement` value. When CosmosDB detects an error or long operation (with configurable threshold), it adds a span event with extended `CosmosDiagnostics` information.

### CosmosDB attributes

<!-- semconv azure.sdk.cosmos -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `db.url` | string | Cosmos DB URI | `https://my-cosmos.documents.azure.com:443/` | Yes |
| `db.instance` | string | Database name | `mydb` | Yes |
| `db.type` | string | Database type | `Cosmos` | Yes |
| [`db.statement`](../database.md) | string | The database statement being executed. [1] | `createContainerIfNotExists.myContainer` | Yes |

**[1]:** The value may be sanitized to exclude sensitive information.
<!-- endsemconv -->