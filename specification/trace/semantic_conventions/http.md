# Semantic conventions for HTTP spans

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for HTTP client and server Spans.
They can be used for http and https schemes
and various HTTP versions like 1.1, 2 and SPDY.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Semantic conventions for HTTP spans](#semantic-conventions-for-http-spans)
  - [Name](#name)
  - [Status](#status)
  - [Common Attributes](#common-attributes)
  - [HTTP client](#http-client)
  - [HTTP server](#http-server)
    - [HTTP server definitions](#http-server-definitions)
    - [HTTP Server semantic conventions](#http-server-semantic-conventions)
  - [HTTP client-server example](#http-client-server-example)

<!-- tocstop -->

## Name

HTTP spans MUST follow the overall [guidelines for span names](../api.md#span).
Many REST APIs encode parameters into URI path, e.g. `/api/users/123` where `123`
is a user id, which creates high cardinality value space not suitable for span
names. In case of HTTP servers, these endpoints are often mapped by the server
frameworks to more concise _HTTP routes_, e.g. `/api/users/{user_id}`, which are
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

For HTTP status codes in the 4xx and 5xx ranges, as well as any other code the client
failed to interpret, status MUST be set to `Error`.

Don't set the span status description if the reason can be inferred from `http.status_code`.

## Common Attributes

<!-- semconv http -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `http.method` | string | HTTP request method. | `GET`; `POST`; `HEAD` | Yes |
| `http.url` | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [1] | `https://www.foo.bar/search?q=OpenTelemetry#SemConv` | No |
| `http.target` | string | The full request target as passed in a HTTP request line or equivalent. | `/path/12314/?q=ddds#123` | No |
| `http.host` | string | The value of the [HTTP host header](https://tools.ietf.org/html/rfc7230#section-5.4). When the header is empty or not present, this attribute should be the same. | `www.example.org` | No |
| `http.scheme` | string | The URI scheme identifying the used protocol. | `http`; `https` | No |
| `http.status_code` | int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | If and only if one was received/sent. |
| `http.flavor` | string | Kind of HTTP protocol used. [2] | `1.0` | No |
| `http.user_agent` | string | Value of the [HTTP User-Agent](https://tools.ietf.org/html/rfc7231#section-5.5.3) header sent by the client. | `CERN-LineMode/2.15 libwww/2.17b3` | No |
| `http.request_content_length` | int | The size of the request payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://tools.ietf.org/html/rfc7230#section-3.3.2) header. For requests using transport encoding, this should be the compressed size. | `3495` | No |
| `http.request_content_length_uncompressed` | int | The size of the uncompressed request payload body after transport decoding. Not set if transport encoding not used. | `5493` | No |
| `http.response_content_length` | int | The size of the response payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://tools.ietf.org/html/rfc7230#section-3.3.2) header. For requests using transport encoding, this should be the compressed size. | `3495` | No |
| `http.response_content_length_uncompressed` | int | The size of the uncompressed response payload body after transport decoding. Not set if transport encoding not used. | `5493` | No |

**[1]:** `http.url` MUST NOT contain credentials passed via URL in form of `https://username:password@www.example.com/`. In such case the attribute's value should be `https://www.example.com/`.

**[2]:** If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

`http.flavor` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `1.0` | HTTP 1.0 |
| `1.1` | HTTP 1.1 |
| `2.0` | HTTP 2 |
| `SPDY` | SPDY protocol. |
| `QUIC` | QUIC protocol. |
<!-- endsemconv -->

It is recommended to also use the general [network attributes][], especially `net.peer.ip`. If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

[network attributes]: span-general.md#general-network-connection-attributes

## HTTP client

This span type represents an outbound HTTP request.

For an HTTP client span, `SpanKind` MUST be `Client`.

If set, `http.url` must be the originally requested URL,
before any HTTP-redirects that may happen when executing the request.

<!-- semconv http.client -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `http.url`
* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, [`net.peer.name`](span-general.md), [`net.peer.port`](span-general.md), `http.target`
* `http.scheme`, [`net.peer.ip`](span-general.md), [`net.peer.port`](span-general.md), `http.target`
<!-- endsemconv -->

Note that in some cases `http.host` might be different
from the `net.peer.name`
used to look up the `net.peer.ip` that is actually connected to.
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
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `http.server_name` | string | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `net.host.name` should be used instead). [1] | `example.com` | See below |
| `http.route` | string | The matched route (path template). | `/users/:userID?` | No |
| `http.client_ip` | string | The IP address of the original client behind all proxies, if known (e.g. from [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)). [2] | `83.164.160.102` | No |

**[1]:** `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. open-telemetry/opentelemetry-python/pull/148). It is thus preferred to supply the raw data that is available.

**[2]:** This is not necessarily the same as `net.peer.ip`, which would identify the network-level peer, which may be a proxy.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, [`net.host.port`](span-general.md), `http.target`
* `http.scheme`, [`net.host.name`](span-general.md), [`net.host.port`](span-general.md), `http.target`
* `http.url`
<!-- endsemconv -->

Of course, more than the required attributes can be supplied, but this is recommended only if they cannot be inferred from the sent ones.
For example, `http.server_name` has shown great value in practice, as bogus HTTP Host headers occur often in the wild.

It is strongly recommended to set `http.server_name` to allow associating requests with some logical server entity.

## HTTP client-server example

As an example, if a browser request for `https://example.com:8080/webshop/articles/4?s=1` is invoked from a host with IP 192.0.2.4, we may have the following Span on the client side:

Span name: `/webshop/articles/4` (NOTE: This is subject to change, see [open-telemetry/opentelemetry-specification#270][].)

[open-telemetry/opentelemetry-specification#270]: https://github.com/open-telemetry/opentelemetry-specification/issues/270

|   Attribute name   |                                       Value             |
| :----------------- | :-------------------------------------------------------|
| `http.method`      | `"GET"`                                                 |
| `http.flavor`      | `"1.1"`                                                 |
| `http.url`         | `"https://example.com:8080/webshop/articles/4?s=1"`     |
| `net.peer.ip`      | `"192.0.2.5"`                                           |
| `http.status_code` | `200`                                                   |

The corresponding server Span may look like this:

Span name: `/webshop/articles/:article_id`.

|   Attribute name   |                      Value                      |
| :----------------- | :---------------------------------------------- |
| `http.method`      | `"GET"`                                         |
| `http.flavor`      | `"1.1"`                                         |
| `http.target`      | `"/webshop/articles/4?s=1"`                     |
| `http.host`        | `"example.com:8080"`                            |
| `http.server_name` | `"example.com"`                                 |
| `net.host.port`    | `8080`                                          |
| `http.scheme`      | `"https"`                                       |
| `http.route`       | `"/webshop/articles/:article_id"`               |
| `http.status_code` | `200`                                           |
| `http.client_ip`   | `"192.0.2.4"`                                   |
| `net.peer.ip`      | `"192.0.2.5"` (the client goes through a proxy) |
| `http.user_agent`  | `"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"`                               |

Note that following the recommendations above, `http.url` is not set in the above example.
If set, it would be
`"https://example.com:8080/webshop/articles/4?s=1"`
but due to `http.scheme`, `http.host` and `http.target` being set, it would be redundant.
As explained above, these separate values are preferred but if for some reason the URL is available but the other values are not,
URL can replace `http.scheme`, `http.host` and `http.target`.
