# Semantic conventions for HTTP spans

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for HTTP client and server Spans.
They can be used for http and https schemes
and various HTTP versions like 1.1, 2 and SPDY.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Name](#name)
- [Status](#status)
- [Common Attributes](#common-attributes)
  * [HTTP request and response headers](#http-request-and-response-headers)
- [HTTP client](#http-client)
  * [HTTP request retries and redirects](#http-request-retries-and-redirects)
- [HTTP server](#http-server)
  * [HTTP server definitions](#http-server-definitions)
  * [HTTP Server semantic conventions](#http-server-semantic-conventions)
- [Examples](#examples)
  * [HTTP client-server example](#http-client-server-example)
  * [HTTP client retries examples](#http-client-retries-examples)
  * [HTTP client authorization retry examples](#http-client-authorization-retry-examples)
  * [HTTP client redirects examples](#http-client-redirects-examples)

<!-- tocstop -->

> **Warning**
> Existing HTTP instrumentations that are using
> [v1.20.0 of this document](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.20.0/specification/trace/semantic_conventions/http.md)
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

## Name

HTTP spans MUST follow the overall [guidelines for span names](../api.md#span).
HTTP server span names SHOULD be `{http.method} {http.route}` if there is a
(low-cardinality) `http.route` available.
HTTP server span names SHOULD be `{http.method}` if there is no (low-cardinality)
`http.route` available.
HTTP client spans have no `http.route` attribute since client-side instrumentation
is not generally aware of the "route", and therefore HTTP client spans SHOULD use
`{http.method}`.
Instrumentation MUST NOT default to using URI
path as span name, but MAY provide hooks to allow custom logic to override the
default span name.

## Status

[Span Status](../api.md#set-status) MUST be left unset if HTTP status code was in the
1xx, 2xx or 3xx ranges, unless there was another error (e.g., network error receiving
the response body; or 3xx codes with max redirects exceeded), in which case status
MUST be set to `Error`.

For HTTP status codes in the 4xx range span status MUST be left unset in case of `SpanKind.SERVER`
and MUST be set to `Error` in case of `SpanKind.CLIENT`.

For HTTP status codes in the 5xx range, as well as any other code the client
failed to interpret, span status MUST be set to `Error`.

Don't set the span status description if the reason can be inferred from `http.status_code`.

## Common Attributes

The common attributes listed in this section apply to both HTTP clients and servers in addition to
the specific attributes listed in the [HTTP client](#http-client) and [HTTP server](#http-server)
sections below.

<!-- semconv trace.http.common(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| `http.request_content_length` | int | The size of the request payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://www.rfc-editor.org/rfc/rfc9110.html#field.content-length) header. For requests using transport encoding, this should be the compressed size. | `3495` | Recommended |
| `http.response_content_length` | int | The size of the response payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://www.rfc-editor.org/rfc/rfc9110.html#field.content-length) header. For requests using transport encoding, this should be the compressed size. | `3495` | Recommended |
| `http.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| [`network.protocol.name`](span-general.md) | string | [OSI Application Layer](https://osi-model.com/application-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `http`; `spdy` | Recommended: if not default (`http`). |
| [`network.protocol.version`](span-general.md) | string | Version of the application layer protocol used. See note below. [1] | `1.0`; `1.1`; `2.0` | Recommended |
| [`network.transport`](span-general.md) | string | [OSI Transport Layer](https://osi-model.com/transport-layer/) or [Inter-process Communication method](https://en.wikipedia.org/wiki/Inter-process_communication). The value SHOULD be normalized to lowercase. | `tcp`; `udp` | Conditionally Required: [2] |
| [`network.type`](span-general.md) | string | [OSI Network Layer](https://osi-model.com/network-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `ipv4`; `ipv6` | Recommended |
| `user_agent.original` | string | Value of the [HTTP User-Agent](https://www.rfc-editor.org/rfc/rfc9110.html#field.user-agent) header sent by the client. | `CERN-LineMode/2.15 libwww/2.17b3` | Recommended |

**[1]:** `network.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[2]:** If not default (`tcp` for `HTTP/1.1` and `HTTP/2`, `udp` for `HTTP/3`).

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* `http.method`

`network.transport` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `tcp` | TCP |
| `udp` | UDP |
| `pipe` | Named or anonymous pipe. See note below. |
| `unix` | Unix domain socket |

`network.type` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `ipv4` | IPv4 |
| `ipv6` | IPv6 |
<!-- endsemconv -->

### HTTP request and response headers

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|-------------------|
| `http.request.header.<key>` | string[] | HTTP request headers, `<key>` being the normalized HTTP Header name (lowercase, with `-` characters replaced by `_`), the value being the header values. [1] [2] | `http.request.header.content_type=["application/json"]`; `http.request.header.x_forwarded_for=["1.2.3.4", "1.2.3.5"]` | Opt-In            |
| `http.response.header.<key>` | string[] | HTTP response headers, `<key>` being the normalized HTTP Header name (lowercase, with `-` characters replaced by `_`), the value being the header values. [1] [2] | `http.response.header.content_type=["application/json"]`; `http.response.header.my_custom_header=["abc", "def"]` | Opt-In            |

**[1]:** Instrumentations SHOULD require an explicit configuration of which headers are to be captured.
Including all request/response headers can be a security risk - explicit configuration helps avoid leaking sensitive information.

The `User-Agent` header is already captured in the `http.user_agent` attribute.
Users MAY explicitly configure instrumentations to capture them even though it is not recommended.

**[2]:** The attribute value MUST consist of either multiple header values as an array of strings or a single-item array containing a possibly comma-concatenated string, depending on the way the HTTP library provides access to headers.

## HTTP client

This span type represents an outbound HTTP request. There are two ways this can be achieved in an instrumentation:

1. Instrumentations SHOULD create an HTTP span for each attempt to send an HTTP request over the wire.
   In case the request is resent, the resend attempts MUST follow the [HTTP resend spec](#http-request-retries-and-redirects).
   In this case, instrumentations SHOULD NOT (also) emit a logical encompassing HTTP client span.

2. If for some reason it is not possible to emit a span for each send attempt (because e.g. the instrumented library does not expose hooks that would allow this),
   instrumentations MAY create an HTTP span for the top-most operation of the HTTP client.
   In this case, the `http.url` MUST be the originally requested URL, before any HTTP-redirects that may happen when executing the request.

For an HTTP client span, `SpanKind` MUST be `Client`.

<!-- semconv trace.http.client(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.url` | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [1] | `https://www.foo.bar/search?q=OpenTelemetry#SemConv` | Required |
| `http.resend_count` | int | The ordinal number of request resending attempt (for any reason, including redirects). [2] | `3` | Recommended: if and only if request was retried. |
| [`server.address`](span-general.md) | string | Host identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [3] | `example.com` | Required |
| [`server.port`](span-general.md) | int | Port identifier of the ["URI origin"](https://www.rfc-editor.org/rfc/rfc9110.html#name-uri-origin) HTTP request is sent to. [4] | `80`; `8080`; `443` | Conditionally Required: [5] |
| [`server.socket.address`](span-general.md) | string | Physical server IP address or Unix socket address. | `10.5.3.2` | Recommended: If different than `server.address`. |
| [`server.socket.domain`](span-general.md) | string | The domain name of an immediate peer. [6] | `proxy.example.com` | Recommended |
| [`server.socket.port`](span-general.md) | int | Physical server port. | `16456` | Recommended: If different than `server.port`. |

**[1]:** `http.url` MUST NOT contain credentials passed via URL in form of `https://username:password@www.example.com/`. In such case the attribute's value should be `https://www.example.com/`.

**[2]:** The resend count SHOULD be updated each time an HTTP request gets resent by the client, regardless of what was the cause of the resending (e.g. redirection, authorization failure, 503 Server Unavailable, network issues, or any other).

**[3]:** Determined by using the first of the following that applies

- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form
- Host identifier of the `Host` header

If an HTTP client request is explicitly made to an IP address, e.g. `http://x.x.x.x:8080`, then
`server.address` SHOULD be the IP address `x.x.x.x`. A DNS lookup SHOULD NOT be used.

**[4]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `server.port` MUST match URI port identifier, otherwise it MUST match `Host` header port identifier.

**[5]:** If not default (`80` for `http` scheme, `443` for `https`).

**[6]:** Typically observed from the client side, and represents a proxy or other intermediary domain name.

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* `http.url`
* [`server.address`](span-general.md)
* [`server.port`](span-general.md)
<!-- endsemconv -->

Note that in some cases host and port identifiers in the `Host` header might be different from the `server.address` and `server.port`, in this case instrumentation MAY populate `Host` header on `http.request.header.host` attribute even if it's not enabled by user.

### HTTP request retries and redirects

Retries and redirects cause more than one physical HTTP request to be sent.
A request is resent when an HTTP client library sends more than one HTTP request to satisfy the same API call.
This may happen due to following redirects, authorization challenges, 503 Server Unavailable, network issues, or any other.

Each time an HTTP request is resent, the `http.resend_count` attribute SHOULD be added to each repeated span and set to the ordinal number of the request resend attempt.

See the examples for more details about:

* [retrying a server error](#http-client-retries-examples),
* [redirects](#http-client-redirects-examples),
* [authorization](#http-client-authorization-retry-examples).

## HTTP server

To understand the attributes defined in this section, it is helpful to read the "Definitions" subsection.

### HTTP server definitions

This section gives a short summary of some concepts
in web server configuration and web app deployment
that are relevant to tracing.

Usually, on a physical host, reachable by one or multiple IP addresses, a single HTTP listener process runs.
If multiple processes are running, they must listen on distinct TCP/UDP ports so that the OS can route incoming TCP/UDP packets to the right one.

Within a single server process, there can be multiple **virtual hosts**.
The [HTTP host header][] (in combination with a port number) is normally used to determine to which of them to route incoming HTTP requests.

The host header value that matches some virtual host is called the virtual hosts's **server name**. If there are multiple aliases for the virtual host, one of them (often the first one listed in the configuration) is called the **primary server name**. See for example, the Apache [`ServerName`][ap-sn] or NGINX [`server_name`][nx-sn] directive or the CGI specification on `SERVER_NAME` ([RFC 3875][rfc-servername]).
In practice the HTTP host header is often ignored when just a single virtual host is configured for the IP.

Within a single virtual host, some servers support the concepts of an **HTTP application**
(for example in Java, the Servlet JSR defines an application as
"a collection of servlets, HTML pages, classes, and other resources that make up a complete application on a Web server"
-- SRV.9 in [JSR 53][];
in a deployment of a Python application to Apache, the application would be the [PEP 3333][] conformant callable that is configured using the
[`WSGIScriptAlias` directive][modwsgisetup] of `mod_wsgi`).

An application can be "mounted" under an **application root**
(also known as a *[context root][]*, *[context prefix][]*, or *[document base][]*)
which is a fixed path prefix of the URL that determines to which application a request is routed
(e.g., the server could be configured to route all requests that go to an URL path starting with `/webshop/`
at a particular virtual host
to the `com.example.webshop` web application).

Some servers allow to bind the same HTTP application to multiple `(virtual host, application root)` pairs.

> TODO: Find way to trace HTTP application and application root ([opentelemetry/opentelementry-specification#335][])

[HTTP host header]: https://tools.ietf.org/html/rfc7230#section-5.4
[PEP 3333]: https://www.python.org/dev/peps/pep-3333/
[modwsgisetup]: https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html
[context root]: https://docs.jboss.org/jbossas/guides/webguide/r2/en/html/ch06.html
[context prefix]: https://marc.info/?l=apache-cvs&m=130928191414740
[document base]: http://tomcat.apache.org/tomcat-5.5-doc/config/context.html
[rfc-servername]: https://tools.ietf.org/html/rfc3875#section-4.1.14
[ap-sn]: https://httpd.apache.org/docs/2.4/mod/core.html#servername
[nx-sn]: http://nginx.org/en/docs/http/ngx_http_core_module.html#server_name
[JSR 53]: https://jcp.org/aboutJava/communityprocess/maintenance/jsr053/index2.html
[opentelemetry/opentelementry-specification#335]: https://github.com/open-telemetry/opentelemetry-specification/issues/335

### HTTP Server semantic conventions

This span type represents an inbound HTTP request.

For an HTTP server span, `SpanKind` MUST be `Server`.

Given an inbound request for a route (e.g. `"/users/:userID?"`) the `name` attribute of the span SHOULD be set to this route.

If the route cannot be determined, the `name` attribute MUST be set as defined in the general semantic conventions for HTTP.

<!-- semconv trace.http.server(full) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.route` | string | The matched route (path template in the format used by the respective server framework). See note below [1] | `/users/:userID?`; `{controller}/{action}/{id?}` | Conditionally Required: If and only if it's available |
| `http.target` | string | The full request target as passed in a HTTP request line or equivalent. | `/users/12314/?q=ddds` | Required |
| [`client.address`](span-general.md) | string | Client address - unix domain socket name, IPv4 or IPv6 address. [2] | `83.164.160.102` | Recommended |
| [`client.port`](span-general.md) | int | The port of the original client behind all proxies, if known (e.g. from [Forwarded](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Forwarded) or a similar header). Otherwise, the immediate client peer port. [3] | `65123` | Recommended |
| [`client.socket.address`](span-general.md) | string | Immediate client peer address - unix domain socket name, IPv4 or IPv6 address. | `/tmp/my.sock`; `127.0.0.1` | Recommended: If different than `client.address`. |
| [`client.socket.port`](span-general.md) | int | Immediate client peer port number | `35555` | Recommended: If different than `client.port`. |
| `http.scheme` | string | The URI scheme identifying the used protocol. | `http`; `https` | Required |
| [`server.address`](span-general.md) | string | Name of the local HTTP server that received the request. [4] | `example.com` | Required |
| [`server.port`](span-general.md) | int | Port of the local HTTP server that received the request. [5] | `80`; `8080`; `443` | Conditionally Required: [6] |
| [`server.socket.address`](span-general.md) | string | Local socket address. Useful in case of a multi-IP host. | `10.5.3.2` | Opt-In |
| [`server.socket.port`](span-general.md) | int | Local socket port. Useful in case of a multi-port host. | `16456` | Opt-In |

**[1]:** MUST NOT be populated when this is not supported by the HTTP server framework as the route attribute should have low-cardinality and the URI path can NOT substitute it.
SHOULD include the [application root](/specification/trace/semantic_conventions/http.md#http-server-definitions) if there is one.

**[2]:** The IP address of the original client behind all proxies, if known (e.g. from [Forwarded](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Forwarded), [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For), or a similar header). Otherwise, the immediate client peer address.

**[3]:** When observed from the server side, and when communicating through an intermediary, `client.port` SHOULD represent client port behind any intermediaries (e.g. proxies) if it's available.

**[4]:** Determined by using the first of the following that applies

- The [primary server name](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host. MUST only
  include host identifier.
- Host identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Host identifier of the `Host` header

SHOULD NOT be set if only IP address is available and capturing name would require a reverse DNS lookup.

**[5]:** Determined by using the first of the following that applies

- Port identifier of the [primary server host](/specification/trace/semantic_conventions/http.md#http-server-definitions) of the matched virtual host.
- Port identifier of the [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource)
  if it's sent in absolute-form.
- Port identifier of the `Host` header

**[6]:** If not default (`80` for `http` scheme, `443` for `https`).

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* `http.target`
* `http.scheme`
* [`server.address`](span-general.md)
* [`server.port`](span-general.md)
<!-- endsemconv -->

`http.route` MUST be provided at span creation time if and only if it's already available. If it becomes available after span starts, instrumentation MUST populate it anytime before span ends.

Note that in some cases host and port identifiers in the `Host` header might be different from the `server.address` and `server.port`, in this case instrumentation MAY populate `Host` header on `http.request.header.host` attribute even if it's not enabled by user.

## Examples

### HTTP client-server example

As an example, if a browser request for `https://example.com:8080/webshop/articles/4?s=1` is invoked from a host with IP 192.0.2.4, we may have the following Span on the client side:

Span name: `GET`

|   Attribute name     |                                       Value             |
| :------------------- | :-------------------------------------------------------|
| `http.method`        | `"GET"`                                                 |
| `http.flavor`        | `"1.1"`                                                 |
| `http.url`           | `"https://example.com:8080/webshop/articles/4?s=1"`     |
| `server.address`     | `example.com`                                           |
| `server.port`        | 8080                                                    |
| `server.socket.address` | `"192.0.2.5"`                                        |
| `http.status_code`   | `200`                                                   |

The corresponding server Span may look like this:

Span name: `GET /webshop/articles/:article_id`.

|   Attribute name     |                      Value                      |
| :------------------- | :---------------------------------------------- |
| `http.method`        | `"GET"`                                         |
| `http.flavor`        | `"1.1"`                                         |
| `http.target`        | `"/webshop/articles/4?s=1"`                     |
| `server.address`     | `"example.com"`                                 |
| `server.port`        | `8080`                                          |
| `http.scheme`        | `"https"`                                       |
| `http.route`         | `"/webshop/articles/:article_id"`               |
| `http.status_code`   | `200`                                           |
| `client.address`     | `"192.0.2.4"`                                   |
| `client.socket.address` | `"192.0.2.5"` (the client goes through a proxy) |
| `http.user_agent`    | `"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"` |

### HTTP client retries examples

Example of retries in the presence of a trace started by an inbound request:

```
request (SERVER, trace=t1, span=s1)
  |
  -- GET / - 500 (CLIENT, trace=t1, span=s2)
  |   |
  |   --- server (SERVER, trace=t1, span=s3)
  |
  -- GET / - 500 (CLIENT, trace=t1, span=s4, http.resend_count=1)
  |   |
  |   --- server (SERVER, trace=t1, span=s5)
  |
  -- GET / - 200 (CLIENT, trace=t1, span=s6, http.resend_count=2)
      |
      --- server (SERVER, trace=t1, span=s7)
```

Example of retries with no trace started upfront:

```
GET / - 500 (CLIENT, trace=t1, span=s1)
 |
 --- server (SERVER, trace=t1, span=s2)

GET / - 500 (CLIENT, trace=t2, span=s1, http.resend_count=1)
 |
 --- server (SERVER, trace=t2, span=s2)

GET / - 200 (CLIENT, trace=t3, span=s1, http.resend_count=2)
 |
 --- server (SERVER, trace=t3, span=s1)
```

### HTTP client authorization retry examples

Example of retries in the presence of a trace started by an inbound request:

```
request (SERVER, trace=t1, span=s1)
  |
  -- GET /hello - 401 (CLIENT, trace=t1, span=s2)
  |   |
  |   --- server (SERVER, trace=t1, span=s3)
  |
  -- GET /hello - 200 (CLIENT, trace=t1, span=s4, http.resend_count=1)
      |
      --- server (SERVER, trace=t1, span=s5)
```

Example of retries with no trace started upfront:

```
GET /hello - 401 (CLIENT, trace=t1, span=s1)
 |
 --- server (SERVER, trace=t1, span=s2)

GET /hello - 200 (CLIENT, trace=t2, span=s1, http.resend_count=1)
 |
 --- server (SERVER, trace=t2, span=s2)
```

### HTTP client redirects examples

Example of redirects in the presence of a trace started by an inbound request:

```
request (SERVER, trace=t1, span=s1)
  |
  -- GET / - 302 (CLIENT, trace=t1, span=s2)
  |   |
  |   --- server (SERVER, trace=t1, span=s3)
  |
  -- GET /hello - 200 (CLIENT, trace=t1, span=s4, http.resend_count=1)
      |
      --- server (SERVER, trace=t1, span=s5)
```

Example of redirects with no trace started upfront:

```
GET / - 302 (CLIENT, trace=t1, span=s1)
 |
 --- server (SERVER, trace=t1, span=s2)

GET /hello - 200 (CLIENT, trace=t2, span=s1, http.resend_count=1)
 |
 --- server (SERVER, trace=t2, span=s2)
```
