<!--- Hugo front matter used to generate the website version of this page:
linkTitle: HTTP
--->

# Semantic Conventions for HTTP Metrics

**Status**: [Experimental](../../document-status.md)

The conventions described in this section are HTTP specific. When HTTP operations occur,
metric events about those operations will be generated and reported to provide insight into the
operations. By adding HTTP attributes to metric events it allows for finely tuned filtering.

**Disclaimer:** These are initial HTTP metric instruments and attributes but more may be added in the future.

## Metric Instruments

The following metric instruments MUST be used to describe HTTP operations. They MUST be of the specified
type and units.

### HTTP Server

Below is a table of HTTP server metric instruments.

| Name                          | Instrument Type ([*](README.md#instrument-types)) | Unit         | Unit ([UCUM](README.md#instrument-units)) | Description                                                                  |
|-------------------------------|---------------------------------------------------|--------------|-------------------------------------------|------------------------------------------------------------------------------|
| `http.server.duration`        | Histogram                                         | milliseconds | `ms`                                      | measures the duration inbound HTTP requests                                  |
| `http.server.request.size`    | Histogram                                         | bytes        | `By`                                      | measures the size of HTTP request messages (compressed)                      |
| `http.server.response.size`   | Histogram                                         | bytes        | `By`                                      | measures the size of HTTP response messages (compressed)                     |
| `http.server.active_requests` | UpDownCounter                                     | requests     | `{requests}`                              | measures the number of concurrent HTTP requests that are currently in-flight |

### HTTP Client

Below is a table of HTTP client metric instruments.

| Name                        | Instrument Type ([*](README.md#instrument-types)) | Unit         | Unit ([UCUM](README.md#instrument-units)) | Description                                              |
|-----------------------------|---------------------------------------------------|--------------|-------------------------------------------|----------------------------------------------------------|
| `http.client.duration`      | Histogram                                         | milliseconds | `ms`                                      | measures the duration outbound HTTP requests             |
| `http.client.request.size`  | Histogram                                         | bytes        | `By`                                      | measures the size of HTTP request messages (compressed)  |
| `http.client.response.size` | Histogram                                         | bytes        | `By`                                      | measures the size of HTTP response messages (compressed) |

## Attributes

Below is a table of the attributes that SHOULD be included on `duration` and `size` metric events
and whether they should be on server, client, or both types of HTTP metric events:

| Name                 | Type                | Requirement Level                                                            | Notes and examples                                                                                                                      |
|----------------------|---------------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `http.method`        | `client` & `server` | Required                                                                     | The HTTP request method. E.g. `"GET"`                                                                                                   |
| `http.scheme`        | `server`            | Required                                                                     | The URI scheme identifying the used protocol in lowercase: `"http"` or `"https"`                                                        |
| `http.route`         | `server`            | Conditionally Required: If and only if it's available                        | The matched route (path template in the format used by the respective server framework). See note below [1]. E.g. `"/path/{id}/?q={}"`. |
| `http.status_code`   | `client` & `server` | Conditionally Required: if and only if one was received/sent.                | [HTTP response status code][]. E.g. `200` (String)                                                                                      |
| `http.flavor`        | `client` & `server` | Recommended                                                                  | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`.                                                              |
| `net.peer.name`      | `client`            | Required                                                                     | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to.             |
| `net.peer.port`      | `client`            | Conditionally Required: If not default (`80` for `http`, `443` for `https`). | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to.             |
| `net.sock.peer.addr` | `client`            | Recommended                                                                  | See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes)     |
| `net.host.name`      | `server`            | Required                                                                     | Host of the local HTTP server that received the request.                                                                                |
| `net.host.port`      | `server`            | Conditionally Required: If not default (`80` for `http`, `443` for `https`). | Port of the local HTTP server that received the request.                                                                                |

**[1]:** 'http.route' MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.

The following attributes SHOULD be included in the `http.server.active_requests` observation:

| Name               | Requirement Level | Notes and examples                                                               |
|--------------------|-------------------|----------------------------------------------------------------------------------|
| `http.method`      | Required          | The HTTP request method. E.g. `"GET"`                                            |
| `http.scheme`      | Required          | The URI scheme identifying the used protocol in lowercase: `"http"` or `"https"` |
| `http.flavor`      | Recommended       | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`        |
| `net.host.name`    | Required          | Host component of the ["origin"](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.6) server HTTP request is sent to. |

[HTTP host header]: https://www.rfc-editor.org/rfc/rfc9110.html#name-host-and-authority
[HTTP response status code]: https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes
[HTTP reason phrase]: https://www.rfc-editor.org/rfc/rfc9110.html#section-15.1
