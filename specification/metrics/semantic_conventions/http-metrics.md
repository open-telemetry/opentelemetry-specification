# General

The conventions described in this section are HTTP specific. HTTP calls are
generally fully described by Spans so a lot of the data below can be derived
from them. By adding HTTP labels to metric events it allows for finely tuned filtering.

**Discaimer:** These are initial HTTP metric instruments and labels but more may be added in the future.

### Metric Instruments

Below is a table of the metric instruments that MUST be used for HTTP spans. They MUST be of the specified
type and units.

| Name                   | Type            | Instrument    | Units        | Description |
|------------------------|-----------------|---------------|--------------|-------------|
| `http.{type}.duration` | Client & Server | ValueRecorder | milliseconds | measure a request duration |
| `http.{type}.request`  | Client & Server | Count         | requests     | measure number of requests |

### Labels

When creating metric events, the following labels SHOULD be added:

#### Included labels

Below is a table of the labels that SHOULD be included on metric events
and whether they should be on server, client, or both types of HTTP metric events:

| Label name         | Type            | Recommended       | Notes and examples |
|--------------------|-----------------|-------------------|--------------------|
| `http.method`      | Client & Server | Yes               | The HTTP request method. E.g. `"GET"` |
| `http.host`        | Client & Server | see [label substitution](#label-substitution) | The value of the [HTTP host header][]. When the header is empty or not present, this label should be the same. |
| `http.scheme`      | Client & Server | see [label substitution](#label-substitution) | The URI scheme identifying the used protocol: `"http"` or `"https"` |
| `http.status_code` | Client & Server | Optional          | [HTTP response status code][]. E.g. `200` (integer) |
| `http.status_text` | Client & Server | Optional          | [HTTP reason phrase][]. E.g. `"OK"` |
| `http.flavor`      | Client & Server | Optional          | Kind of HTTP protocol used: `"1.0"`, `"1.1"`, `"2"`, `"SPDY"` or `"QUIC"`. |
| `net.peer.name`    | Client          | see [1] in [label substitution](#label-substitution) | The name of the service the request is going to. |
| `net.peer.port`    | Client          | see [1] in [label substitution](#label-substitution) | The port of the service the request is going to. E.g. `8080` |
| `net.peer.ip`      | Client          | see [1] in [label substitution](#label-substitution) | The IP address of the service the request is going to. E.g. `255.255.255.0` |
| `http.server_name` | Server          | see [2] in [label substitution](#label-substitution) | The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this label MUST NOT be set ( `net.host.name` should be used instead). |
| `net.host.name`    | Server          | see [2] in [label substitution](#label-substitution) | The name of the host. |
| `net.host.port`    | Server          | see [2] in [label substitution](#label-substitution) | The port of the host. |
| `http.route`       | Server          | Optional          | The matched route (path template). (TODO: Define whether to prepend application root) E.g. `"/users/:userID?"`. |

[HTTP host header]: https://tools.ietf.org/html/rfc7230#section-5.4
[HTTP response status code]: https://tools.ietf.org/html/rfc7231#section-6
[HTTP reason phrase]: https://tools.ietf.org/html/rfc7230#section-3.1.2

#### Parameterized labels

To avoid high cardinality the following labels SHOULD substitute any parameters when added as labels to http metric events as described below:

| Label name        | Type            | Recommended |  Notes and examples |
|-------------------|-----------------|-------------|---------------------|
|`http.url`         | Client & Server | see [label substitution](#label-substitution) | The originally requested URL |
|`http.target`      | Client & Server | see [label substitution](#label-substitution) | The full request target as passed in a [HTTP request line][] or equivalent, e.g. `"/path/{id}/?q={}"`. |

[HTTP request line]: https://tools.ietf.org/html/rfc7230#section-3.1.1

Many REST APIs encode parameters into URI path, e.g. `/api/users/123` where `123`
is a user id, which creates high cardinality value space not suitable for labels on metric events.
In case of HTTP servers, these endpoints are often mapped by the server
frameworks to more concise _HTTP routes_, e.g. `/api/users/{user_id}`, which are
recommended as the low cardinality label values. However, the same approach usually
does not work for HTTP client labels, especially when instrumentation is provided
by a lower-level middleware that is not aware of the specifics of how the URIs
are formed. Therefore, HTTP client labels SHOULD be using conservative, low
cardinality names formed from the available parameters of an HTTP request,
such as `"HTTP {METHOD_NAME}"`. These labels MUST NOT default to using URI
path.

#### Label substitution

**[1]** For client metric labels, one of the following sets of labels is RECOMMENDED (in order of usual preference unless for a particular web client/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.url`
* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `net.peer.name`, `net.peer.port`, `http.target`
* `http.scheme`, `net.peer.ip`, `net.peer.port`, `http.target`

**[2]** For server metric labels, `http.url` is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. <https://github.com/open-telemetry/opentelemetry-python/pull/148>).
It is thus preferred to supply the raw data that *is* available.
Namely, one of the following sets is RECOMMENDED (in order of usual preference unless for a particular web server/framework it is known that some other set is preferable for some reason; all strings must be non-empty):

* `http.scheme`, `http.host`, `http.target`
* `http.scheme`, `http.server_name`, `net.host.port`, `http.target`
* `http.scheme`, `net.host.name`, `net.host.port`, `http.target`
* `http.url`