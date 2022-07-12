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
  * [HTTP request retries and redirects](#http-request-retries-and-redirects)
- [HTTP client](#http-client)
- [HTTP server](#http-server)
  * [HTTP server definitions](#http-server-definitions)
  * [HTTP Server semantic conventions](#http-server-semantic-conventions)
- [HTTP client-server example](#http-client-server-example)
- [HTTP retries examples](#http-retries-examples)
- [HTTP redirects examples](#http-redirects-examples)

<!-- tocstop -->

## Name

HTTP spans MUST follow the overall [guidelines for span names](../api.md#span).
Many REST APIs encode parameters into URI path, e.g. `/api/users/123` where `123`
is a user id, which creates high cardinality value space not suitable for span
names. In case of HTTP servers, these endpoints are often mapped by the server
frameworks to more concise *HTTP routes*, e.g. `/api/users/{user_id}`, which are
recommended as the low cardinality span names. However, the same approach usually
does not work for HTTP client spans, especially when instrumentation is provided
by a lower-level middleware that is not aware of the specifics of how the URIs
are formed. Therefore, HTTP client spans SHOULD be using conservative, low
cardinality names formed from the available parameters of an HTTP request,
such as `"HTTP {METHOD_NAME}"`. Instrumentation MUST NOT default to using URI
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

<!-- semconv http -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `http.url` | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [1] | `https://www.foo.bar/search?q=OpenTelemetry#SemConv` | Recommended |
| `http.target` | string | The full request target as passed in a HTTP request line or equivalent. | `/path/12314/?q=ddds#123` | Recommended |
| `http.host` | string | The value of the [HTTP host header](https://tools.ietf.org/html/rfc7230#section-5.4). An empty Host header should also be reported, see note. [2] | `www.example.org` | Recommended |
| `http.scheme` | string | The URI scheme identifying the used protocol. | `http`; `https` | Recommended |
| `http.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| `http.flavor` | string | Kind of HTTP protocol used. [3] | `1.0` | Recommended |
| `http.user_agent` | string | Value of the [HTTP User-Agent](https://tools.ietf.org/html/rfc7231#section-5.5.3) header sent by the client. | `CERN-LineMode/2.15 libwww/2.17b3` | Recommended |
| `http.request_content_length` | int | The size of the request payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://tools.ietf.org/html/rfc7230#section-3.3.2) header. For requests using transport encoding, this should be the compressed size. | `3495` | Recommended |
| `http.request_content_length_uncompressed` | int | The size of the uncompressed request payload body after transport decoding. Not set if transport encoding not used. | `5493` | Recommended |
| `http.response_content_length` | int | The size of the response payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://tools.ietf.org/html/rfc7230#section-3.3.2) header. For requests using transport encoding, this should be the compressed size. | `3495` | Recommended |
| `http.response_content_length_uncompressed` | int | The size of the uncompressed response payload body after transport decoding. Not set if transport encoding not used. | `5493` | Recommended |
| `http.retry_count` | int | The ordinal number of request re-sending attempt. | `3` | Recommended: If and only if a request was retried. |
| [`net.sock.family`](span-general.md) | string | Protocol [address family](https://man7.org/linux/man-pages/man7/address_families.7.html) which is used for communication. | `inet6`; `bluetooth` | Conditionally Required: [4] |
| [`net.sock.peer.addr`](span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | Recommended |
| [`net.sock.peer.name`](span-general.md) | string | Remote socket peer name. | `proxy.example.com` | Recommended: [5] |
| [`net.sock.peer.port`](span-general.md) | int | Remote socket peer port. | `16456` | Recommended: [6] |

**[1]:** `http.url` MUST NOT contain credentials passed via URL in form of `https://username:password@www.example.com/`. In such case the attribute's value should be `https://www.example.com/`.

**[2]:** When the header is present but empty the attribute SHOULD be set to the empty string. Note that this is a valid situation that is expected in certain cases, according the aforementioned [section of RFC 7230](https://tools.ietf.org/html/rfc7230#section-5.4). When the header is not set the attribute MUST NOT be set.

**[3]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

**[4]:** If different than `inet` and if any of `net.sock.peer.addr` or `net.sock.host.addr` are set. Consumers of telemetry SHOULD expect to receive IPv6 address in `net.sock.peer.addr` without `net.sock.family` coming from instrumentations that follow previous versions of this document.

**[5]:** If available and different than `net.peer.name` and if `net.sock.peer.addr` is set.

**[6]:** If defined for the address family and if different than `net.peer.port` and if `net.sock.peer.addr` is set.

`http.flavor` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `1.0` | HTTP/1.0 |
| `1.1` | HTTP/1.1 |
| `2.0` | HTTP/2 |
| `3.0` | HTTP/3 |
| `SPDY` | SPDY protocol. |
| `QUIC` | QUIC protocol. |

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* `http.method`
* `http.url`
* `http.target`
* `http.host`
* `http.scheme`
<!-- endsemconv -->

It is recommended to also use the general [socket-level attributes][] - `net.sock.peer.addr` when available,  `net.sock.peer.name` and `net.sock.peer.port` when don't match `net.peer.name` and `net.peer.port` (if [intermediary](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.7) is detected).

### HTTP request and response headers

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.request.header.<key>` | string[] | HTTP request headers, `<key>` being the normalized HTTP Header name (lowercase, with `-` characters replaced by `_`), the value being the header values. [1] [2] | `http.request.header.content_type=["application/json"]`; `http.request.header.x_forwarded_for=["1.2.3.4", "1.2.3.5"]` | Optional |
| `http.response.header.<key>` | string[] | HTTP response headers, `<key>` being the normalized HTTP Header name (lowercase, with `-` characters replaced by `_`), the value being the header values. [1] [2] | `http.response.header.content_type=["application/json"]`; `http.response.header.my_custom_header=["abc", "def"]` | Optional |

**[1]:** Instrumentations SHOULD require an explicit configuration of which headers are to be captured.
Including all request/response headers can be a security risk - explicit configuration helps avoid leaking sensitive information.

Some HTTP headers - `Host` and `User-Agent` - are already captured in the `http.host` and `http.user_agent` attributes.
Users MAY explicitly configure instrumentations to capture them even though it is not recommended.

**[2]:** The attribute value MUST consist of either multiple header values as an array of strings or a single-item array containing a possibly comma-concatenated string, depending on the way the HTTP library provides access to headers.

[socket-level attributes]: span-general.md#netsock-attributes

### HTTP request retries and redirects

Retries and redirects cause more than one physical HTTP request to be sent.
A CLIENT span SHOULD be created for each one of these physical requests.
No span is created corresponding to the "logical" (encompassing) request.

For retries, `http.retry_count` attribute SHOULD be added to each retry span
with the value that reflects the ordinal number of request retry attempt.

See [examples](#http-retries-examples) for more details.

## HTTP client

This span type represents an outbound HTTP request.

For an HTTP client span, `SpanKind` MUST be `Client`.

If set, `http.url` must be the originally requested URL,
before any HTTP-redirects that may happen when executing the request.

<!-- semconv http.client -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`net.peer.name`](span-general.md) | string | Host component of the ["origin"](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.6) server HTTP request is sent to. [1] | `example.com` | See below |
| [`net.peer.port`](span-general.md) | int | Port identifier of the ["origin"](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.6) server HTTP request is sent to. [2] | `80`; `8080`; `443` | Conditionally Required: if not default for request scheme. |

**[1]:** When host component is an IP address, instrumentations SHOULD NOT do a reverse proxy lookup to obtain DNS name and SHOULD set `net.peer.name` to the provided host component. When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.peer.name` SHOULD match URI host component, otherwise `Host` header host component SHOULD be used.

**[2]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.peer.name` MUST match URI port component, otherwise it MUST match `Host` header port component.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `http.url`
* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, [`net.peer.name`](span-general.md), [`net.peer.port`](span-general.md), `http.target`
* `http.scheme`, [`net.sock.peer.addr`](span-general.md), [`net.sock.peer.port`](span-general.md), `http.target`

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* [`net.peer.name`](span-general.md)
* [`net.peer.port`](span-general.md)
<!-- endsemconv -->

It is recommended to also use the general [socket-level attributes][] - `net.sock.host.addr` when available, `net.sock.host.port` when it doesn't match `net.host.port` (if [intermediary](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.7) is detected).

Note that in some cases `http.host` might be different
from the `net.peer.name`
used to look up the `net.sock.peer.addr` that is actually connected to.
In that case it is strongly recommended to set the `net.peer.name` attribute in addition to `http.host`.

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

An application can be "mounted" under some **application root**
(also know as *[context root][]* *[context prefix][]*, or *[document base][]*)
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
If the route does not include the application root, it SHOULD be prepended to the span name.

If the route cannot be determined, the `name` attribute MUST be set as defined in the general semantic conventions for HTTP.

<!-- semconv http.server -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `http.server_name` | string | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `net.host.name` should be used instead). [1] | `example.com` | See below |
| `http.route` | string | The matched route (path template). | `/users/:userID?` | Recommended |
| `http.client_ip` | string | The IP address of the original client behind all proxies, if known (e.g. from [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)). [2] | `83.164.160.102` | Recommended |
| [`net.host.name`](span-general.md) | string | Host component of the ["origin"](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.6) server HTTP request is sent to. [3] | `localhost` | See below |
| [`net.host.port`](span-general.md) | int | Port component of the ["origin"](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.6) server HTTP request is sent to. [4] | `8080` | See below |
| [`net.sock.host.addr`](span-general.md) | string | Local socket address. Useful in case of a multi-IP host.' | `192.168.0.1` | Recommended |
| [`net.sock.host.port`](span-general.md) | int | Local socket port number. | `35555` | Recommended: [5] |

**[1]:** `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. open-telemetry/opentelemetry-python/pull/148). It is thus preferred to supply the raw data that is available.

**[2]:** This is not necessarily the same as `net.sock.peer.addr`, which would
identify the network-level peer, which may be a proxy.

This attribute should be set when a source of information different
from the one used for `net.sock.peer.addr`, is available even if that other
source just confirms the same value as `net.sock.peer.addr`.
Rationale: For `net.sock.peer.addr`, one typically does not know if it
comes from a proxy, reverse proxy, or the actual client. Setting
`http.client_ip` when it's the same as `net.sock.peer.addr` means that
one is at least somewhat confident that the address is not that of
the closest proxy.

**[3]:** When host component is an IP address, instrumentations SHOULD NOT do a reverse proxy lookup to obtain DNS name and SHOULD set `net.host.name` to the IP address provided in the host component. When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.host.name` SHOULD match URI host component, otherwise `Host` header host component SHOULD be used.

**[4]:** When [request target](https://www.rfc-editor.org/rfc/rfc9110.html#target.resource) is absolute URI, `net.host.port` SHOULD match URI port component, otherwise `Host` header port component SHOULD be used.

**[5]:** If defined for the address family and if different than `net.host.port` and if `net.sock.host.addr` is set.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, [`net.host.port`](span-general.md), `http.target`
* `http.scheme`, [`net.host.name`](span-general.md), [`net.host.port`](span-general.md), `http.target`
* `http.url`

Following attributes MUST be provided **at span creation time** (when provided at all), so they can be considered for sampling decisions:

* [`net.host.name`](span-general.md)
* [`net.host.port`](span-general.md)
<!-- endsemconv -->

Of course, more than the required attributes can be supplied, but this is recommended only if they cannot be inferred from the sent ones.
For example, `http.server_name` has shown great value in practice, as bogus HTTP Host headers occur often in the wild.

It is strongly recommended to set `http.server_name` to allow associating requests with some logical server entity.

## HTTP client-server example

As an example, if a browser request for `https://example.com:8080/webshop/articles/4?s=1` is invoked from a host with IP 192.0.2.4, we may have the following Span on the client side:

Span name: `HTTP GET`

|   Attribute name     |                                       Value             |
| :------------------- | :-------------------------------------------------------|
| `http.method`        | `"GET"`                                                 |
| `http.flavor`        | `"1.1"`                                                 |
| `http.url`           | `"https://example.com:8080/webshop/articles/4?s=1"`     |
| `net.sock.peer.addr` | `"192.0.2.5"`                                           |
| `http.status_code`   | `200`                                                   |

The corresponding server Span may look like this:

Span name: `/webshop/articles/:article_id`.

|   Attribute name     |                      Value                      |
| :------------------- | :---------------------------------------------- |
| `http.method`        | `"GET"`                                         |
| `http.flavor`        | `"1.1"`                                         |
| `http.target`        | `"/webshop/articles/4?s=1"`                     |
| `http.host`          | `"example.com:8080"`                            |
| `http.server_name`   | `"example.com"`                                 |
| `net.host.port`      | `8080`                                          |
| `http.scheme`        | `"https"`                                       |
| `http.route`         | `"/webshop/articles/:article_id"`               |
| `http.status_code`   | `200`                                           |
| `http.client_ip`     | `"192.0.2.4"`                                   |
| `net.sock.peer.addr` | `"192.0.2.5"` (the client goes through a proxy) |
| `http.user_agent`    | `"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"`                               |

Note that following the recommendations above, `http.url` is not set in the above example.
If set, it would be
`"https://example.com:8080/webshop/articles/4?s=1"`
but due to `http.scheme`, `http.host` and `http.target` being set, it would be redundant.
As explained above, these separate values are preferred but if for some reason the URL is available but the other values are not,
URL can replace `http.scheme`, `http.host` and `http.target`.

## HTTP retries examples

Example of retries in the presence of a trace started by an inbound request:

```
request (SERVER, trace=t1, span=s1)
  |
  -- GET / - 500 (CLIENT, trace=t1, span=s2)
  |   |
  |   --- server (SERVER, trace=t1, span=s3)
  |
  -- GET / - 500 (CLIENT, trace=t1, span=s4, http.retry_count=1)
  |   |
  |   --- server (SERVER, trace=t1, span=s5)
  |
  -- GET / - 200 (CLIENT, trace=t1, span=s6, http.retry_count=2)
      |
      --- server (SERVER, trace=t1, span=s7)
```

Example of retries with no trace started upfront:

```
GET / - 500 (CLIENT, trace=t1, span=s1)
 |
 --- server (SERVER, trace=t1, span=s2)

GET / - 500 (CLIENT, trace=t2, span=s1, http.retry_count=1)
 |
 --- server (SERVER, trace=t2, span=s2)

GET / - 200 (CLIENT, trace=t3, span=s1, http.retry_count=2)
 |
 --- server (SERVER, trace=t3, span=s1)
```

## HTTP redirects examples

Example of redirects in the presence of a trace started by an inbound request:

```
request (SERVER, trace=t1, span=s1)
  |
  -- GET / - 302 (CLIENT, trace=t1, span=s2)
  |   |
  |   --- server (SERVER, trace=t1, span=s3)
  |
  -- GET /hello - 200 (CLIENT, trace=t1, span=s4)
      |
      --- server (SERVER, trace=t1, span=s5)
```

Example of redirects with no trace started upfront:

```
GET / - 302 (CLIENT, trace=t1, span=s1)
 |
 --- server (SERVER, trace=t1, span=s2)

GET /hello - 200 (CLIENT, trace=t2, span=s1)
 |
 --- server (SERVER, trace=t2, span=s2)
```
