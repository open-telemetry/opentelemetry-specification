# Semantic conventions for HTTP spans

This document defines semantic conventions for HTTP client and server Spans.
They can be used for http and https schemes
and various HTTP versions like 1.1, 2 and SPDY.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Name](#name)
- [Status](#status)
- [Common Attributes](#common-attributes)
- [HTTP client](#http-client)
- [HTTP server](#http-server)
  * [HTTP server definitions](#http-server-definitions)
  * [HTTP Server semantic conventions](#http-server-semantic-conventions)
- [HTTP client-server example](#http-client-server-example)

<!-- tocstop -->

## Name

Given an [RFC 3986](https://tools.ietf.org/html/rfc3986) compliant URI of the form `scheme:[//host[:port]]path[?query][#fragment]`,
the span name of the span SHOULD be set to the URI path value,
unless another value that represents the identity of the request and has a lower cardinality can be identified
(e.g. the route for server spans; see below).

## Status

Implementations MUST set status if the HTTP communication failed
or an HTTP error status code is returned (e.g. above 3xx).

In the case of an HTTP redirect, the request should normally be considered successful,
unless the client aborts following redirects due to hitting some limit (redirect loop).
If following a (chain of) redirect(s) successfully, the Status should be set according to the result of the final HTTP request.

Don't set a status message if the reason can be inferred from `http.status_code` and `http.status_text` already.

| HTTP code               | Span status code      |
|-------------------------|-----------------------|
| 100...299               | `Ok`                  |
| 3xx redirect codes      | `DeadlineExceeded` in case of loop (see above) [1], otherwise `Ok` |
| 401 Unauthorized ⚠      | `Unauthenticated` ⚠ (Unauthorized actually means unauthenticated according to [RFC 7235][rfc-unauthorized])  |
| 403 Forbidden           | `PermissionDenied`    |
| 404 Not Found           | `NotFound`            |
| 429 Too Many Requests   | `ResourceExhausted`   |
| Other 4xx code          | `InvalidArgument` [1] |
| 501 Not Implemented     | `Unimplemented`       |
| 503 Service Unavailable | `Unavailable`         |
| 504 Gateway Timeout     | `DeadlineExceeded`    |
| Other 5xx code          | `Internal` [1]   |
| Any status code the client fails to interpret (e.g., 093 or 573) | `Unknown` |

Note that the items marked with [1] are different from the mapping defined in the [OpenCensus semantic conventions][oc-http-status].

[oc-http-status]: https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/HTTP.md#mapping-from-http-status-codes-to-trace-status-codes
[rfc-unauthorized]: https://tools.ietf.org/html/rfc7235#section-3.1

## Common Attributes

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Denotes the type of the span and needs to be `"http"`. | Yes |
| `http.method` | HTTP request method. E.g. `"GET"`. | Yes |
| `http.url` | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. | Defined later. |
| `http.target` | The full request target as passed in a [HTTP request line][] or equivalent, e.g. `/path/12314/?q=ddds#123"`. | Defined later. |
| `http.host` | The value of the [HTTP host header][]. When the header is empty or not present, this attribute should be the same. | Defined later. |
| `http.scheme` | The URI scheme identifying the used protocol: `"http"` or `"https"` | Defined later. |
| `http.status_code` | [HTTP response status code][]. E.g. `200` (integer) | If and only if one was received/sent. |
| `http.status_text` | [HTTP reason phrase][]. E.g. `"OK"` | No |
| `http.flavor` | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`. |  No |

It is recommended to also use the general [network attributes][], especially `net.peer.ip`. If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.

[network attributes]: data-span-general.md#general-network-connection-attributes
[HTTP response status code]: https://tools.ietf.org/html/rfc7231#section-6
[HTTP reason phrase]: https://tools.ietf.org/html/rfc7230#section-3.1.2

## HTTP client

This span type represents an outbound HTTP request.

For an HTTP client span, `SpanKind` MUST be `Client`.

If set, `http.url` must be the originally requested URL,
before any HTTP-redirects that may happen when executing the request.

One of the following sets of attributes is required (in order of usual preference unless for a particular web client/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.url`
* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `peer.hostname`, `peer.port`, `http.target`
* `http.scheme`, `peer.ip`, `peer.port`, `http.target`

Note that in some cases `http.host` might be different
from the `peer.hostname`
used to look up the `peer.ip` that is actually connected to.
In that case it is strongly recommended to set the `peer.hostname` attribute in addition to `http.host`.

For status, the following special cases have canonical error codes assigned:

| Client error                | Trace status code  |
|-----------------------------|--------------------|
| DNS resolution failed       | `Unknown`     |
| Request cancelled by caller | `Cancelled`        |
| URL cannot be parsed        | `InvalidArgument`  |
| Request timed out           | `DeadlineExceeded` |

This is not meant to be an exhaustive list
but if there is no clear mapping for some error conditions,
instrumentation developers are encouraged to use `Unknown`
and open a PR or issue in the specification repository.

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

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `http.server_name` | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `net.host.name` should be used instead). | [1] |
| `http.route` | The matched route (path template). (TODO: Define whether to prepend application root) E.g. `"/users/:userID?"`. | No |
| `http.client_ip` | The IP address of the original client behind all proxies, if known (e.g. from [X-Forwarded-For][]). Note that this is not necessarily the same as `net.peer.ip`, which would identify the network-level peer, which may be a proxy. | No |

[HTTP request line]: https://tools.ietf.org/html/rfc7230#section-3.1.1
[HTTP host header]: https://tools.ietf.org/html/rfc7230#section-5.4
[X-Forwarded-For]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For

**[1]**: `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. <https://github.com/open-telemetry/opentelemetry-python/pull/148>).
It is thus preferred to supply the raw data that *is* available.
Namely, one of the following sets is required (in order of usual preference unless for a particular web server/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, `net.host.port`, `http.target`
* `http.scheme`, `net.host.name`, `net.host.port`, `http.target`
* `http.url`

Of course, more than the required attributes can be supplied, but this is recommended only if they cannot be inferred from the sent ones.
For example, `http.server_name` has shown great value in practice, as bogus HTTP Host headers occur often in the wild.

It is strongly recommended to set `http.server_name` to allow associating requests with some logical server entity.

## HTTP client-server example

As an example, if a browser request for `https://example.com:8080/webshop/articles/4?s=1` is invoked from a host with IP 192.0.2.4, we may have the following Span on the client side:

Span name: `/webshop/articles/4` (NOTE: This is subject to change, see [open-telemetry/opentelemetry-specification#270][].)

[open-telemetry/opentelemetry-specification#270]: https://github.com/open-telemetry/opentelemetry-specification/issues/270

|   Attribute name   |                                       Value             |
| :----------------- | :-------------------------------------------------------|
| `component`        | `"http"`                                                |
| `http.method`      | `"GET"`                                                 |
| `http.flavor`      | `"1.1"`                                                 |
| `http.url`         | `"https://example.com:8080/webshop/articles/4?s=1"`     |
| `peer.ip4`         | `"192.0.2.5"`                                           |
| `http.status_code` | `200`                                                   |
| `http.status_text` | `"OK"`                                                  |

The corresponding server Span may look like this:

Span name: `/webshop/articles/:article_id`.

|   Attribute name   |                      Value                      |
| :----------------- | :---------------------------------------------- |
| `component`        | `"http"`                                        |
| `http.method`      | `"GET"`                                         |
| `http.flavor`      | `"1.1"`                                         |
| `http.target`      | `"/webshop/articles/4?s=1"`                     |
| `http.host`        | `"example.com:8080"`                            |
| `http.server_name` | `"example.com"`                                 |
| `host.port`        | `8080`                                          |
| `http.scheme`      | `"https"`                                       |
| `http.route`       | `"/webshop/articles/:article_id"`               |
| `http.status_code` | `200`                                           |
| `http.status_text` | `"OK"`                                          |
| `http.client_ip`   | `"192.0.2.4"`                                   |
| `net.peer.ip`      | `"192.0.2.5"` (the client goes through a proxy) |

Note that following the recommendations above, `http.url` is not set in the above example.
If set, it would be
`"https://example.com:8080/webshop/articles/4?s=1"`
but due to `http.scheme`, `http.host` and `http.target` being set, it would be redundant.
As explained above, these separate values are preferred but if for some reason the URL is available but the other values are not,
URL can replace `http.scheme`, `http.host` and `http.target`.
