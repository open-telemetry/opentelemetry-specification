# General

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

| Name                          | Instrument    | Units        | Description                                                                  |
| ----------------------------- | ------------- | ------------ | ---------------------------------------------------------------------------- |
| `http.server.duration`        | Histogram     | milliseconds | measures the duration of the inbound HTTP request                            |
| `http.server.active_requests` | UpDownCounter | requests     | measures the number of concurrent HTTP requests that are currently in-flight |

### HTTP Client

Below is a table of HTTP client metric instruments.

| Name                   | Instrument | Units        | Description                                       |
| ---------------------- | ---------- | ------------ | ------------------------------------------------- |
| `http.client.duration` | Histogram  | milliseconds | measure the duration of the outbound HTTP request |

## Attributes

Below is a table of the attributes that SHOULD be included on `duration` metric events
and whether they should be on server, client, or both types of HTTP metric events:

| Name               | Type                | Recommended                                                  | Notes and examples                                                                                                                                                                                                  |
| ------------------ | ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `http.method`      | `client` & `server` | Yes                                                          | The HTTP request method. E.g. `"GET"`                                                                                                                                                                               |
| `http.host`        | `client` & `server` | see [attribute alternatives](#attribute-alternatives)        | The value of the [HTTP host header][]. When the header is empty or not present, this attribute should be the same.                                                                                                  |
| `http.scheme`      | `client` & `server` | see [attribute alternatives](#attribute-alternatives)        | The URI scheme identifying the used protocol in lowercase: `"http"` or `"https"`                                                                                                                                    |
| `http.status_code` | `client` & `server` | Optional                                                     | [HTTP response status code][]. E.g. `200` (String)                                                                                                                                                                  |
| `http.flavor`      | `client` & `server` | Optional                                                     | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`.                                                                                                                                          |
| `net.peer.name`    | `client`            | see [1] in [attribute alternatives](#attribute-alternatives) | See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes)                                                                                 |
| `net.peer.port`    | `client`            | see [1] in [attribute alternatives](#attribute-alternatives) | See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes)                                                                                 |
| `net.peer.ip`      | `client`            | see [1] in [attribute alternatives](#attribute-alternatives) | See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes)                                                                                 |
| `http.server_name` | `server`            | see [2] in [attribute alternatives](#attribute-alternatives) | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `net.host.name` should be used instead). |
| `net.host.name`    | `server`            | see [2] in [attribute alternatives](#attribute-alternatives) | See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes)                                                                                 |
| `net.host.port`    | `server`            | see [2] in [attribute alternatives](#attribute-alternatives) | See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes)                                                                                 |

The following attributes SHOULD be included in the `http.server.active_requests` observation:

| Name               | Recommended                                                  | Notes and examples                                                                                                                                                                                                  |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `http.method`      | Yes                                                          | The HTTP request method. E.g. `"GET"`                                                                                                                                                                               |
| `http.host`        | see [attribute alternatives](#attribute-alternatives)        | The value of the [HTTP host header][]. When the header is empty or not present, this attribute should be the same                                                                                                   |
| `http.scheme`      | see [attribute alternatives](#attribute-alternatives)        | The URI scheme identifying the used protocol in lowercase: `"http"` or `"https"`                                                                                                                                    |
| `http.flavor`      | Optional                                                     | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`                                                                                                                                           |
| `http.server_name` | see [2] in [attribute alternatives](#attribute-alternatives) | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `net.host.name` should be used instead). |

[HTTP host header]: https://tools.ietf.org/html/rfc7230#section-5.4
[HTTP response status code]: https://tools.ietf.org/html/rfc7231#section-6
[HTTP reason phrase]: https://tools.ietf.org/html/rfc7230#section-3.1.2

### Parameterized attributes

To avoid high cardinality the following attributes SHOULD substitute any parameters when added as attributes to http metric events as described below:

| Attribute name | Type                | Recommended                                           | Notes and examples                                                                                     |
| -------------- | ------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `http.url`     | `client` & `server` | see [attribute alternatives](#attribute-alternatives) | The originally requested URL                                                                           |
| `http.target`  | `client` & `server` | see [attribute alternatives](#attribute-alternatives) | The full request target as passed in a [HTTP request line][] or equivalent, e.g. `"/path/{id}/?q={}"`. |

[HTTP request line]: https://tools.ietf.org/html/rfc7230#section-3.1.1

Many REST APIs encode parameters into the URI path, e.g. `/api/users/123` where `123`
is a user id, which creates high cardinality value space not suitable for attributes on metric events.
In case of HTTP servers, these endpoints are often mapped by the server
frameworks to more concise _HTTP routes_, e.g. `/api/users/{user_id}`, which are
recommended as the low cardinality attribute values. However, the same approach usually
does not work for HTTP client attributes, especially when instrumentation is provided
by a lower-level middleware that is not aware of the specifics of how the URIs
are formed. Therefore, HTTP client attributes SHOULD be using conservative, low
cardinality names formed from the available parameters of an HTTP request,
such as `"HTTP {METHOD_NAME}"`. These attributes MUST NOT default to using URI
path.

### Attribute alternatives

**[1]** For client metric attributes, one of the following sets of attributes is RECOMMENDED (in order of usual preference unless for a particular web client/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.url`
* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `net.peer.name`, `net.peer.port`, `http.target`
* `http.scheme`, `net.peer.ip`, `net.peer.port`, `http.target`

**[2]** For server metric attributes, `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. <https://github.com/open-telemetry/opentelemetry-python/pull/148>).
It is thus preferred to supply the raw data that *is* available.
Namely, one of the following sets is RECOMMENDED (in order of usual preference unless for a particular web server/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, `net.host.port`, `http.target`
* `http.scheme`, `net.host.name`, `net.host.port`, `http.target`
* `http.url`
