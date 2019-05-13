# HTTP Stats

Any particular library might provide only a subset of these measures/views/tags.
Check the language-specific documentation for the list of supported values.

There is no special support for multi-part HTTP requests and responses. These are just treated as a single request.

## Units

As always, units are encoded according to the case-sensitive abbreviations from the [Unified Code for Units of Measure](http://unitsofmeasure.org/ucum.html):

* Latencies are measures in float64 milliseconds, denoted "ms"
* Sizes are measured in bytes, denoted "By"
* Dimensionless values have unit "1"

Buckets for distributions in default views are as follows:

* Size in bytes: 0, 1024, 2048, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216, 67108864, 268435456, 1073741824, 4294967296
* Latency in ms: 0, 1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 30, 40, 50, 65, 80, 100, 130, 160, 200, 250, 300, 400, 500, 650, 800, 1000, 2000, 5000, 10000, 20000, 50000, 100000

## Client

### Measures

Client stats are recorded for each individual HTTP request, including for each individual redirect (followed or not). All stats are recorded after request processing (usually after the response body has been fully read).

| Measure name                                | Unit | Description                                                                                                                                                                                                                                                                                       |
|---------------------------------------------|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| opencensus.io/http/client/sent_bytes        | By   | Total bytes sent in request body (not including headers). This is uncompressed bytes.                                                                                                                                                                                                             |
| opencensus.io/http/client/received_bytes    | By   | Total bytes received in response bodies (not including headers but including error responses with bodies). Should be measured from actual bytes received and read, not the value of the Content-Length header. This is uncompressed bytes. Responses with no body should record 0 for this value. |
| opencensus.io/http/client/roundtrip_latency | ms   | Time between first byte of request headers sent to last byte of response received, or terminal error                                                                                                                                                                                              |

### Tags

All client measures should be tagged with the following.

| Tag name           | Description                                                                                              |
|--------------------|----------------------------------------------------------------------------------------------------------|
| http_client_method | HTTP method, capitalized (i.e. GET, POST, PUT, DELETE, etc.)                                             |
| http_client_path   | URL path (not including query string)                                                                    |
| http_client_status | HTTP status code as an integer (e.g. 200, 404, 500.), or "error" if no response status line was received |
| http_client_host   | Value of the request Host header                                                                         |

`http_client_method`, `http_client_path`, `http_client_host` are set when an outgoing request
starts and are available in the context for the entire outgoing request processing.
`http_client_status` is set when an outgoing request finishes and is only available around the
stats recorded at the end of request processing.

`http_client_path` and `http_client_host` might have high cardinality and you should be careful about using these
in views if your metrics backend cannot tolerate high-cardinality labels.

### Default views

The following set of views are considered minimum required to monitor client side performance:

| View name                                   | Measure                                     | Aggregation  | Tags                                   |
|---------------------------------------------|---------------------------------------------|--------------|----------------------------------------|
| opencensus.io/http/client/sent_bytes        | opencensus.io/http/client/sent_bytes        | distribution | http_client_method, http_client_status                     |
| opencensus.io/http/client/received_bytes    | opencensus.io/http/client/received_bytes    | distribution | http_client_method, http_client_status |
| opencensus.io/http/client/roundtrip_latency | opencensus.io/http/client/roundtrip_latency | distribution | http_client_method, http_client_status |
| opencensus.io/http/client/completed_count   | opencensus.io/http/client/roundtrip_latency | count        | http_client_method, http_client_status |

## Server

Server measures are recorded at the end of request processing.

### Measures

Server stats are recorded for each individual HTTP request handled. They are recorded at the end of request handling.

| Measure name                             | Unit | Description                                                                                                                                                                                                                                                                                   |
|------------------------------------------|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| opencensus.io/http/server/received_bytes | By   | Total bytes received in request body (not including headers). This is uncompressed bytes.                                                                                                                                                                                                     |
| opencensus.io/http/server/sent_bytes     | By   | Total bytes sent in response bodies (not including headers but including error responses with bodies). Should be measured from actual bytes received and read, not the value of the Content-Length header. This is uncompressed bytes. Responses with no body should record 0 for this value. |
| opencensus.io/http/server/server_latency | ms   | Time between first byte of request headers read to last byte of response sent, or terminal error                                                                                                                                                                                              |

### Tags

All server metrics should be tagged with the following.

| Tag name           | Description                                                         |
|--------------------|---------------------------------------------------------------------|
| http_server_method | HTTP method, capitalized (i.e. GET, POST, PUT, DELETE, etc.)        |
| http_server_path   | URL path (not including query string)                               |
| http_server_status | HTTP server status code returned, as an integer e.g. 200, 404, 500. |
| http_server_host   | Value of the request Host header                                    |
| http_server_route  | Logical route of the handler of this request                        |

`http_server_method`, `http_server_path`, `http_server_host` are set when an incoming request
starts and are available in the context for the entire incoming request processing.
`http_server_status` is set when an incoming request finishes and is only available around the stats
recorded at the end of request processing.

`http_server_path` and `http_server_host` are set by the client: you should be careful about using these
in views if your metrics backend cannot tolerate high-cardinality labels.

`http_server_route` should always be a low cardinality string representing the logical route or handler of the
request. A reasonable interpretation of this would be the URL path pattern matched to handle the request,
or an explicitly specified function name. Defaults to the empty string if no other suitable value is
available.

### Default views

The following set of views are considered minimum required to monitor server side performance:

| View name                                 | Measure                                  | Aggregation  | Tags                                                      |
|-------------------------------------------|------------------------------------------|--------------|-----------------------------------------------------------|
| opencensus.io/http/server/received_bytes  | opencensus.io/http/server/received_bytes | distribution | http_server_method, http_server_route, http_server_status |
| opencensus.io/http/server/sent_bytes      | opencensus.io/http/server/sent_bytes     | distribution | http_server_method, http_server_route, http_server_status |
| opencensus.io/http/server/server_latency  | opencensus.io/http/server/server_latency | distribution | http_server_method, http_server_route, http_server_status |
| opencensus.io/http/server/completed_count | opencensus.io/http/server/server_latency | count        | http_server_method, http_server_route, http_server_status |

## FAQ

### Why was the path removed from the default views?

Path can have unbounded cardinality, which causes problems for time-series databases like Prometheus.
This is especially true of public-facing HTTP servers, where this becomes a DoS vector.