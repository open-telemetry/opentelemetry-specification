# Semantic Conventions

_TODO: Remove rule `exclude_rule 'MD025'` from `.mdlstyle.rb` once this document is split and we no longer need 2 top-level headers._

These documents define standard names and values of Resource labels and
Span attributes.

* [Resource Conventions](data-resource-semantic-conventions.md)
* [Span Conventions](#span-conventions)

# Span Conventions

In OpenTelemetry spans can be created freely and it’s up to the implementor to
annotate them with attributes specific to the represented operation. Spans
represent specific operations in and between systems. Some of these operations
represent calls that use well-known protocols like HTTP or database calls.
Depending on the protocol and the type of operation, additional information
is needed to represent and analyze a span correctly in monitoring systems. It is
also important to unify how this attribution is made in different languages.
This way, the operator will not need to learn specifics of a language and
telemetry collected from multi-language micro-service can still be easily
correlated and cross-analyzed.

## HTTP

This section defines semantic conventions for HTTP client and server Spans.
They can be used for http and https schemes
and various HTTP versions like 1.1, 2 and SPDY.

### Name

Given an [RFC 3986](https://tools.ietf.org/html/rfc3986) compliant URI of the form `scheme:[//host[:port]]path[?query][#fragment]`,
the span name of the span SHOULD be set to the URI path value,
unless another value that represents the identity of the request and has a lower cardinality can be identified
(e.g. the route for server spans; see below).

### Status

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
| Other 5xx code          | `InternalError` [1]   |
| Any status code the client fails to interpret (e.g., 093 or 573) | `UnknownError` |

Note that the items marked with [1] are different from the mapping defined in the [OpenCensus semantic conventions][oc-http-status].

[oc-http-status]: https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/HTTP.md#mapping-from-http-status-codes-to-trace-status-codes
[rfc-unauthorized]: https://tools.ietf.org/html/rfc7235#section-3.1

### Common Attributes

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

It is recommended to also use the `peer.*` attributes, especially `peer.ip*`.

[HTTP response status code]: https://tools.ietf.org/html/rfc7231#section-6
[HTTP reason phrase]: https://tools.ietf.org/html/rfc7230#section-3.1.2

### HTTP client

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
| DNS resolution failed       | `UnknownError`     |
| Request cancelled by caller | `Cancelled`        |
| URL cannot be parsed        | `InvalidArgument`  |
| Request timed out           | `DeadlineExceeded` |

This is not meant to be an exhaustive list
but if there is no clear mapping for some error conditions,
instrumentation developers are encouraged to use `UnknownError`
and open a PR or issue in the specification repository.

### HTTP server

To understand the attributes defined in this section, it is helpful to read the "Definitions" subsection.

#### Definitions

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

#### Semantic conventions

This span type represents an inbound HTTP request.

For an HTTP server span, `SpanKind` MUST be `Server`.

Given an inbound request for a route (e.g. `"/users/:userID?"`) the `name` attribute of the span SHOULD be set to this route.
If the route does not include the application root, it SHOULD be prepended to the span name.

If the route cannot be determined, the `name` attribute MUST be set as defined in the general semantic conventions for HTTP.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `http.server_name` | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `host.name` should be used instead). | [1] |
| `host.name` | Analogous to `peer.hostname` but for the host instead of the peer. | [1] |
| `host.port` | Local port. E.g., `80` (integer). Analogous to `peer.port`. | [1] |
| `http.route` | The matched route (path template). (TODO: Define whether to prepend application root) E.g. `"/users/:userID?"`. | No |
| `http.client_ip` | The IP address of the original client behind all proxies, if known (e.g. from [X-Forwarded-For][]). Note that this is not necessarily the same as `peer.ip*`, which would identify the network-level peer, which may be a proxy. | No |

[HTTP request line]: https://tools.ietf.org/html/rfc7230#section-3.1.1
[HTTP host header]: https://tools.ietf.org/html/rfc7230#section-5.4
[X-Forwarded-For]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For

**[1]**: `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. <https://github.com/open-telemetry/opentelemetry-python/pull/148>).
It is thus preferred to supply the raw data that *is* available.
Namely, one of the following sets is required (in order of usual preference unless for a particular web server/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, `host.port`, `http.target`
* `http.scheme`, `host.name`, `host.port`, `http.target`
* `http.url`

Of course, more than the required attributes can be supplied, but this is recommended only if they cannot be inferred from the sent ones.
For example, `http.server_name` has shown great value in practice, as bogus HTTP Host headers occur often in the wild.

It is strongly recommended to set `http.server_name` to allow associating requests with some logical server entity.

### Example

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
| `peer.ip4`         | `"192.0.2.5"` (the client goes through a proxy) |

Note that following the recommendations above, `http.url` is not set in the above example.
If set, it would be
`"https://example.com:8080/webshop/articles/4?s=1"`
but due to `http.scheme`, `http.host` and `http.target` being set, it would be redundant.
As explained above, these separate values are preferred but if for some reason the URL is available but the other values are not,
URL can replace `http.scheme`, `http.host` and `http.target`.

## Databases client calls

For database client call the `SpanKind` MUST be `Client`.

Span `name` should be set to low cardinality value representing the statement
executed on the database. It may be stored procedure name (without argument), sql
statement without variable arguments, etc. When it's impossible to get any
meaningful representation of the span `name`, it can be populated using the same
value as `db.instance`.

Note, Redis, Cassandra, HBase and other storage systems may reuse the same
attribute names.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Database driver name or database name (when known) `"JDBI"`, `"jdbc"`, `"odbc"`, `"postgreSQL"`. | Yes       |
| `db.type`      | Database type. For any SQL database, `"sql"`. For others, the lower-case database category, e.g. `"cassandra"`, `"hbase"`, or `"redis"`. | Yes       |
| `db.instance`  | Database instance name. E.g., In java, if the jdbc.url=`"jdbc:mysql://db.example.com:3306/customers"`, the instance name is `"customers"`. | Yes       |
| `db.statement` | A database statement for the given database type. Note, that the value may be sanitized to exclude sensitive information. E.g., for `db.type="sql"`, `"SELECT * FROM wuser_table"`; for `db.type="redis"`, `"SET mykey 'WuValue'"`. | Yes       |
| `db.user`      | Username for accessing database. E.g., `"readonly_user"` or `"reporting_user"` | No        |

For database client calls, peer information can be populated and interpreted as
follows:

| Attribute name  | Notes and examples                                           | Required |
| :-------------- | :----------------------------------------------------------- | -------- |
| `peer.address`  | JDBC substring like `"mysql://db.example.com:3306"`          | Yes      |
| `peer.hostname` | Remote hostname. `"db.example.com"`                          | Yes      |
| `peer.ipv4`     | Remote IPv4 address as a `.`-separated tuple. E.g., `"127.0.0.1"` | No       |
| `peer.ipv6`     | Remote IPv6 address as a string of colon-separated 4-char hex tuples. E.g., `"2001:0db8:85a3:0000:0000:8a2e:0370:7334"` | No       |
| `peer.port`     | Remote port. E.g., `80` (integer)                            | No       |
| `peer.service`  | Remote service name. Can be database friendly name or `"db.instance"` | No       |

## gRPC

Implementations MUST create a span, when the gRPC call starts, one for
client-side and one for server-side. Outgoing requests should be a span `kind`
of `CLIENT` and incoming requests should be a span `kind` of `SERVER`.

Span `name` MUST be full gRPC method name formatted as:

```
$package.$service/$method
```

Examples of span name: `grpc.test.EchoService/Echo`.

### Attributes

| Attribute name | Notes and examples                                           | Required? |
| -------------- | ------------------------------------------------------------ | --------- |
| `component`    | Declares that this is a grpc component. Value MUST be `"grpc"` | Yes       |

`peer.*` attributes MUST define service name as `peer.service`, host as
`peer.hostname` and port as `peer.port`.

### Status

Implementations MUST set status which MUST be the same as the gRPC client/server
status. The mapping between gRPC canonical codes and OpenTelemetry status codes
is 1:1 as OpenTelemetry canonical codes is just a snapshot of grpc codes which
can be found [here](https://github.com/grpc/grpc-go/blob/master/codes/codes.go).

### Events

In the lifetime of a gRPC stream, an event for each message sent/received on
client and server spans SHOULD be created with the following attributes:

```
-> [time],
    "name" = "message",
    "message.type" = "SENT",
    "message.id" = id
    "message.compressed_size" = <compressed size in bytes>,
    "message.uncompressed_size" = <uncompressed size in bytes>
```

```
-> [time],
    "name" = "message",
    "message.type" = "RECEIVED",
    "message.id" = id
    "message.compressed_size" = <compressed size in bytes>,
    "message.uncompressed_size" = <uncompressed size in bytes>
```

The `message.id` MUST be calculated as two different counters starting from `1`
one for sent messages and one for received message. This way we guarantee that
the values will be consistent between different implementations. In case of
unary calls only one sent and one received message will be recorded for both
client and server spans.
