# Semantic Conventions

This document defines reserved attributes that can be used to add operation and
protocol specific information.

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

These span types represent HTTP requests. They can be used for http and https
schemes and various HTTP versions like 1.1, 2 and SPDY.

Given an [RFC 3986](https://tools.ietf.org/html/rfc3986) compliant URI of the form
`scheme:[//host[:port]]path[?query][#fragment]`, the span name of the span SHOULD
be set to the URI path value, unless another value that represents the identity
of the request and has a lower cardinality can be identified.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Denotes the type of the span and needs to be `"http"`. | Yes |
| `http.method` | HTTP request method. E.g. `"GET"`. | Yes |
| `http.url` | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. | Defined later. |
| `http.status_code` | [HTTP response status code][]. E.g. `200` (integer) | No |
| `http.status_text` | [HTTP reason phrase][]. E.g. `"OK"` | No |
| `http.flavor` | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`. |  If not TCP-based (`QUIC`). |

It is recommended to also use the `peer.*` attributes, especially `peer.ip*`.

[HTTP response status code]: https://tools.ietf.org/html/rfc7231#section-6
[HTTP reason phrase]: https://tools.ietf.org/html/rfc7230#section-3.1.2

### HTTP client

This span type represents an outbound HTTP request.

For an HTTP client span, `SpanKind` MUST be `Client`.

`http.url` is required and represents the HTTP URL used to (initially) make this request.

### HTTP server

This span type represents an inbound HTTP request.

For an HTTP server span, `SpanKind` MUST be `Server`.

Given an inbound request for a route (e.g. `"/users/:userID?"` the `name` attribute of the span SHOULD be set to this route. If the route does not include the application root path, it SHOULD be prepended to the span name.

If the route cannot be determined, the `name` attribute MUST be set as defined in the general semantic conventions for HTTP.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `http.target` | The full request target as passed in a [HTTP request line][] or equivalent, e.g. `/path/12314/?q=ddds#123"`. | [1] |
| `http.host` | The value of the [HTTP host header][]. Note that this might be empty or not present. | [1] |
| `http.scheme` | The URI scheme identifying the used protocol: `"http"` or `"https"` | [1] |
| `http.server_name` | The (primary) server name (usually not including a port). This should be obtained via configuration, e.g. the Apache [`ServerName`][ap-sn] or NGINX [`server_name`][nx-sn] directive. If no such configuration can be obtained, this attribute MUST NOT be set ( `host.name` should be used instead). | [1] |
| `host.name` |  Analogous to `peer.hostname` but for the host instead of the peer. | [1] |
| `host.port` | Local port. E.g., `80` (integer). Analogous to `peer.port`. | [1] |
| `http.route` | The matched route (path template). E.g. `"/users/:userID?"`. | No |
| `http.app` | An identifier for the whole HTTP application. E.g. Flask app name, `spring.application.name`, etc. | No |
| `http.app_root` |The path prefix of the URL that identifies this `http.app`. Also known as "context root". If multiple roots exist, the one that was matched for this request should be used. | No |
| `http.client_ip` | The IP address of the original client behind all proxies, if known (e.g. from [X-Forwarded-For][]). | No |

[HTTP request line]: https://tools.ietf.org/html/rfc7230#section-3.1.1
[HTTP host header]: https://tools.ietf.org/html/rfc7230#section-5.4
[X-Forwarded-For]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
[ap-sn]: https://httpd.apache.org/docs/2.4/mod/core.html#servername
[nx-sn]: http://nginx.org/en/docs/http/ngx_http_core_module.html#server_name

**[1]**: `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. <https://github.com/open-telemetry/opentelemetry-python/pull/148>).
It is thus preferred to supply the raw data that *is* available.
Namely, one of the following sets is required (in order of preference, all strings must be non-empty):

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, `host.port`, `http.target`
* `http.scheme`, `host.name`, `host.port`, `http.target`
* `http.url`

Of course, more than the required attributes can be supplied, but this is recommended only if they cannot be inferred from the sent ones.
For example, `http.server_name` has shown great value in practice, as bogus HTTP Host headers occur often in the wild.

It is strongly recommended to set at least one of `http.app` or `http.server_name` to allow associating requests with some logical app or server entity.

As an example, if a browser request for `https://example.com:8080/webshop/articles/4?s=1` is invoked, we may have:

Span name: `/webshop/articles/:article_id` (`app_root` + `route`).

|   Attribute name   |                                       Value                                       |
| :----------------- | :-------------------------------------------------------------------------------- |
| `component`        | `"http"`                                                                          |
| `http.method`      | `"GET"`                                                                           |
| `http.url`         | `"https://example.com:8080/webshop/articles/4?s=1"` (or not set)                  |
| `http.target`      | `"/webshop/articles/4?s=1"`                                                       |
| `http.host`        | `"example.com:8080"`                                                              |
| `http.server_name` | `"example.com"`                                                                   |
| `host.port`        | `8080`                                                                            |
| `http.scheme`      | `"https"`                                                                         |
| `http.route`       | `"/articles/:article_id"` (note that the `app_root` part is missing in this case) |
| `http.status_code` | `200`                                                                             |
| `http.status_text` | `"OK"`                                                                            |
| `http.app`         | E.g., `"My cool WebShop"` or `"com.example.webshop"`                              |
| `http.app_root`    | `"/webshop"`                                                                      |
| `http.client_ip`   | `"192.0.2.4"`                                                                     |
| `peer.ip4`         | `"192.0.2.5"` (the client goes through a proxy)                                   |

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
