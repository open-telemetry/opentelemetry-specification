<!--- Hugo front matter used to generate the website version of this page:
linkTitle: HTTP
--->

# Semantic Conventions for HTTP Metrics

**Status**: [Experimental](../../document-status.md)

The conventions described in this section are HTTP specific. When HTTP operations occur,
metric events about those operations will be generated and reported to provide insight into the
operations. By adding HTTP attributes to metric events it allows for finely tuned filtering.

**Disclaimer:** These are initial HTTP metric instruments and attributes but more may be added in the future.

## HTTP Server

### Metric: `http.server.duration`

This metric is required.

<!-- semconv metric.http.server.duration(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.server.duration` | Histogram | `ms` | Measures the duration of inbound HTTP requests. |
<!-- endsemconv -->

<!-- semconv metric.http.server.duration -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.route`](../../trace/semantic_conventions/http.md) | string | The matched route (path template in the format used by the respective server framework). See note below [2] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| [`http.scheme`](../../trace/semantic_conventions/http.md) | string | The URI scheme identifying the used protocol. | `http`; `https` | Required |
| [`http.status_code`](../../trace/semantic_conventions/http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`net.host.name`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [3] | `localhost` | Required |
| [`net.host.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [4] | `8080` | Conditionally Required: [5] |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](../../trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[3]:** Determined by using the first of the following that applies

- The [primary server name](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[4]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[5]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.server.active_requests`

This metric is optional.

<!-- semconv metric.http.server.active_requests(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.server.active_requests` | UpDownCounter | `{requests}` | Measures the number of concurrent HTTP requests that are currently in-flight. |
<!-- endsemconv -->

<!-- semconv metric.http.server.active_requests -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.scheme`](../../trace/semantic_conventions/http.md) | string | The URI scheme identifying the used protocol. | `http`; `https` | Required |
| [`net.host.name`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [2] | `localhost` | Required |
| [`net.host.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [3] | `8080` | Conditionally Required: [4] |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** Determined by using the first of the following that applies

- The [primary server name](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[3]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.server.request.size`

This metric is optional.

<!-- semconv metric.http.server.request.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.server.request.size` | Histogram | `By` | Measures the size of HTTP request messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.server.request.size -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.route`](../../trace/semantic_conventions/http.md) | string | The matched route (path template in the format used by the respective server framework). See note below [2] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| [`http.scheme`](../../trace/semantic_conventions/http.md) | string | The URI scheme identifying the used protocol. | `http`; `https` | Required |
| [`http.status_code`](../../trace/semantic_conventions/http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`net.host.name`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [3] | `localhost` | Required |
| [`net.host.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [4] | `8080` | Conditionally Required: [5] |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](../../trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[3]:** Determined by using the first of the following that applies

- The [primary server name](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[4]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[5]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.server.response.size`

This metric is optional.

<!-- semconv metric.http.server.response.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.server.response.size` | Histogram | `By` | Measures the size of HTTP response messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.server.response.size -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.route`](../../trace/semantic_conventions/http.md) | string | The matched route (path template in the format used by the respective server framework). See note below [2] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| [`http.scheme`](../../trace/semantic_conventions/http.md) | string | The URI scheme identifying the used protocol. | `http`; `https` | Required |
| [`http.status_code`](../../trace/semantic_conventions/http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`net.host.name`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [3] | `localhost` | Required |
| [`net.host.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [4] | `8080` | Conditionally Required: [5] |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](../../trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[3]:** Determined by using the first of the following that applies

- The [primary server name](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[4]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](../../trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[5]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

## HTTP Client

### Metric: `http.client.duration`

This metric is required.

<!-- semconv metric.http.client.duration(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.client.duration` | Histogram | `ms` | Measures the duration of outbound HTTP requests. |
<!-- endsemconv -->

<!-- semconv metric.http.client.duration -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.status_code`](../../trace/semantic_conventions/http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`net.peer.name`](../../trace/semantic_conventions/span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [2] | `example.com` | Required |
| [`net.peer.port`](../../trace/semantic_conventions/span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `80`; `8080`; `443` | Conditionally Required: [4] |
| [`net.sock.peer.addr`](../../trace/semantic_conventions/span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | Recommended |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[3]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.peer.name` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.client.request.size`

This metric is optional.

<!-- semconv metric.http.client.request.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.client.request.size` | Histogram | `By` | Measures the size of HTTP request messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.client.request.size -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.status_code`](../../trace/semantic_conventions/http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`net.peer.name`](../../trace/semantic_conventions/span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [2] | `example.com` | Required |
| [`net.peer.port`](../../trace/semantic_conventions/span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `80`; `8080`; `443` | Conditionally Required: [4] |
| [`net.sock.peer.addr`](../../trace/semantic_conventions/span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | Recommended |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[3]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.peer.name` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.client.response.size`

This metric is optional.

<!-- semconv metric.http.client.response.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.client.response.size` | Histogram | `By` | Measures the size of HTTP response messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.client.response.size -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`http.flavor`](../../trace/semantic_conventions/http.md) | string | Kind of HTTP protocol used. [1] | `1.0` | Recommended |
| [`http.method`](../../trace/semantic_conventions/http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`http.status_code`](../../trace/semantic_conventions/http.md) | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`net.peer.name`](../../trace/semantic_conventions/span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [2] | `example.com` | Required |
| [`net.peer.port`](../../trace/semantic_conventions/span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `80`; `8080`; `443` | Conditionally Required: [4] |
| [`net.sock.peer.addr`](../../trace/semantic_conventions/span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | Recommended |

**[1]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[2]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[3]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.peer.name` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->
