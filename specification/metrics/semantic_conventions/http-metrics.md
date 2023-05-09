<!--- Hugo front matter used to generate the website version of this page:
linkTitle: HTTP
--->

# Semantic Conventions for HTTP Metrics

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**Status**: [Experimental](../../document-status.md)

The conventions described in this section are HTTP specific. When HTTP operations occur,
metric events about those operations will be generated and reported to provide insight into the
operations. By adding HTTP attributes to metric events it allows for finely tuned filtering.

**Disclaimer:** These are initial HTTP metric instruments and attributes but more may be added in the future.

<!-- toc -->

- [HTTP Server](#http-server)
  * [Metric: `http.server.duration`](#metric-httpserverduration)
  * [Metric: `http.server.active_requests`](#metric-httpserveractive_requests)
  * [Metric: `http.server.request.size`](#metric-httpserverrequestsize)
  * [Metric: `http.server.response.size`](#metric-httpserverresponsesize)
- [HTTP Client](#http-client)
  * [Metric: `http.client.duration`](#metric-httpclientduration)
  * [Metric: `http.client.request.size`](#metric-httpclientrequestsize)
  * [Metric: `http.client.response.size`](#metric-httpclientresponsesize)

<!-- tocstop -->

> **Warning**
> Existing HTTP instrumentations that are using
> [v1.20.0 of this document](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.20.0/specification/metrics/semantic_conventions/http-metrics.md)
> (or prior):
>
> * SHOULD NOT change the version of the HTTP or networking attributes that they emit
>   until the HTTP semantic conventions are marked stable (HTTP stabilization will
>   include stabilization of a core set of networking attributes which are also used
>   in HTTP instrumentations).
> * SHOULD introduce an environment variable `OTEL_SEMCONV_STABILITY_OPT_IN`
>   in the existing major version which supports the following values:
>   * `none` - continue emitting whatever version of the old experimental
>     HTTP and networking attributes the instrumentation was emitting previously.
>     This is the default value.
>   * `http` - emit the new, stable HTTP and networking attributes,
>     and stop emitting the old experimental HTTP and networking attributes
>     that the instrumentation emitted previously.
>   * `http/dup` - emit both the old and the stable HTTP and networking attributes,
>     allowing for a seamless transition.
> * SHOULD maintain (security patching at a minimum) the existing major version
>   for at least six months after it starts emitting both sets of attributes.
> * SHOULD drop the environment variable in the next major version (stable
>   next major version SHOULD NOT be released prior to October 1, 2023).

## HTTP Server

### Metric: `http.server.duration`

This metric is required.

This metric SHOULD be specified with
[`ExplicitBucketBoundaries`](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#instrument-advice)
of `[ 0, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10 ]`.

<!-- semconv metric.http.server.duration(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.server.duration` | Histogram | `s` | Measures the duration of inbound HTTP requests. |
<!-- endsemconv -->

<!-- semconv metric.http.server.duration(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.route` | string | The matched route (path template in the format used by the respective server framework). See note below [1] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.response.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`network.protocol.name`](../../trace/semantic_conventions/span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| [`network.protocol.version`](../../trace/semantic_conventions/span-general.md) | string | Version of the application layer protocol used. See note below. [2] | `3.1.1` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [3] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [4] | `80`; `8080`; `443` | Conditionally Required: [5] |
| [`url.scheme`](../../common/url.md) | string | The [URI scheme](https://www.rfc-editor.org/rfc/rfc3986#section-3.1) component identifying the used protocol. | `http`; `https` | Required |

**[1]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](/specification/trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[2]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[3]:** Determined by using the first of the following that applies

- The [primary server name](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[4]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
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
| `http.server.active_requests` | UpDownCounter | `{request}` | Measures the number of concurrent HTTP requests that are currently in-flight. |
<!-- endsemconv -->

<!-- semconv metric.http.server.active_requests(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [1] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [2] | `80`; `8080`; `443` | Conditionally Required: [3] |
| [`url.scheme`](../../common/url.md) | string | The [URI scheme](https://www.rfc-editor.org/rfc/rfc3986#section-3.1) component identifying the used protocol. | `http`; `https` | Required |

**[1]:** Determined by using the first of the following that applies

- The [primary server name](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[2]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[3]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.server.request.size`

This metric is optional.

<!-- semconv metric.http.server.request.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.server.request.size` | Histogram | `By` | Measures the size of HTTP request messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.server.request.size(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.route` | string | The matched route (path template in the format used by the respective server framework). See note below [1] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.response.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`network.protocol.name`](../../trace/semantic_conventions/span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| [`network.protocol.version`](../../trace/semantic_conventions/span-general.md) | string | Version of the application layer protocol used. See note below. [2] | `3.1.1` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [3] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [4] | `80`; `8080`; `443` | Conditionally Required: [5] |
| [`url.scheme`](../../common/url.md) | string | The [URI scheme](https://www.rfc-editor.org/rfc/rfc3986#section-3.1) component identifying the used protocol. | `http`; `https` | Required |

**[1]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](/specification/trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[2]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[3]:** Determined by using the first of the following that applies

- The [primary server name](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[4]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
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

<!-- semconv metric.http.server.response.size(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.route` | string | The matched route (path template in the format used by the respective server framework). See note below [1] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.response.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`network.protocol.name`](../../trace/semantic_conventions/span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| [`network.protocol.version`](../../trace/semantic_conventions/span-general.md) | string | Version of the application layer protocol used. See note below. [2] | `3.1.1` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Name of the local HTTP server that received the request. [3] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port of the local HTTP server that received the request. [4] | `80`; `8080`; `443` | Conditionally Required: [5] |
| [`url.scheme`](../../common/url.md) | string | The [URI scheme](https://www.rfc-editor.org/rfc/rfc3986#section-3.1) component identifying the used protocol. | `http`; `https` | Required |

**[1]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](/specification/trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[2]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[3]:** Determined by using the first of the following that applies

- The [primary server name](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[4]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[5]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

## HTTP Client

### Metric: `http.client.duration`

This metric is required.

This metric SHOULD be specified with
[`ExplicitBucketBoundaries`](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#instrument-advice)
of `[ 0, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10 ]`.

<!-- semconv metric.http.client.duration(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.client.duration` | Histogram | `s` | Measures the duration of outbound HTTP requests. |
<!-- endsemconv -->

<!-- semconv metric.http.client.duration(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.response.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`network.protocol.name`](../../trace/semantic_conventions/span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| [`network.protocol.version`](../../trace/semantic_conventions/span-general.md) | string | Version of the application layer protocol used. See note below. [1] | `3.1.1` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [2] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `80`; `8080`; `443` | Conditionally Required: [4] |
| [`server.socket.address`](../../trace/semantic_conventions/span-general.md) | string | Physical server IP address or Unix socket address. | `10.5.3.2` | Recommended: If different than `server.address`. |

**[1]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[2]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[3]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `server.port` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.client.request.size`

This metric is optional.

<!-- semconv metric.http.client.request.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.client.request.size` | Histogram | `By` | Measures the size of HTTP request messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.client.request.size(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.response.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`network.protocol.name`](../../trace/semantic_conventions/span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| [`network.protocol.version`](../../trace/semantic_conventions/span-general.md) | string | Version of the application layer protocol used. See note below. [1] | `3.1.1` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [2] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `80`; `8080`; `443` | Conditionally Required: [4] |
| [`server.socket.address`](../../trace/semantic_conventions/span-general.md) | string | Physical server IP address or Unix socket address. | `10.5.3.2` | Recommended: If different than `server.address`. |

**[1]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[2]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[3]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `server.port` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->

### Metric: `http.client.response.size`

This metric is optional.

<!-- semconv metric.http.client.response.size(metric_table) -->
| Name     | Instrument Type | Unit (UCUM) | Description    |
| -------- | --------------- | ----------- | -------------- |
| `http.client.response.size` | Histogram | `By` | Measures the size of HTTP response messages (compressed). |
<!-- endsemconv -->

<!-- semconv metric.http.client.response.size(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.request.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.response.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| [`network.protocol.name`](../../trace/semantic_conventions/span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `amqp`; `http`; `mqtt` | Recommended |
| [`network.protocol.version`](../../trace/semantic_conventions/span-general.md) | string | Version of the application layer protocol used. See note below. [1] | `3.1.1` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [2] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `80`; `8080`; `443` | Conditionally Required: [4] |
| [`server.socket.address`](../../trace/semantic_conventions/span-general.md) | string | Physical server IP address or Unix socket address. | `10.5.3.2` | Recommended: If different than `server.address`. |

**[1]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[2]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[3]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `server.port` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[4]:** If not default (`80` for `http` scheme, `443` for `https`).
<!-- endsemconv -->
