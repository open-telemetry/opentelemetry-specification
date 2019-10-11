# Semantic Conventions

This document defines reserved attributes that can be used to add operation and
protocol specific information.

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

## HTTP client

This span type represents an outbound HTTP request.

For a HTTP client span, `SpanKind` MUST be `Client`.

Given an [RFC 3986](https://www.ietf.org/rfc/rfc3986.txt) compliant URI of the form
`scheme:[//authority]path[?query][#fragment]`, the span name of the span SHOULD
be set to to the URI path value.

If a framework can identify a value that represents the identity of the request
and has a lower cardinality than the URI path, this value MUST be used for the span name instead.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Denotes the type of the span and needs to be `"http"`. | Yes |
| `http.method` | HTTP request method. E.g. `"GET"`. | Yes |
| `http.url` | HTTP URL of this request, represented as `scheme://host:port/path?query#fragment` E.g. `"https://example.com:779/path/12314/?q=ddds#123"`. | Yes |
| `http.status_code` | [HTTP response status code](https://tools.ietf.org/html/rfc7231). E.g. `200` (integer) | No |
| `http.status_text` | [HTTP reason phrase](https://www.ietf.org/rfc/rfc2616.txt). E.g. `"OK"` | No |

## HTTP server

This span type represents an inbound HTTP request.

For a HTTP server span, `SpanKind` MUST be `Server`.

Given an inbound request for a route (e.g. `"/users/:userID?"` the `name`
attribute of the span SHOULD be set to this route.

If the route can not be determined, the `name` attribute MUST be set to the [RFC 3986 URI](https://www.ietf.org/rfc/rfc3986.txt) path value.

If a framework can identify a value that represents the identity of the request
and has a lower cardinality than the URI path or route, this value MUST be used for the span name instead.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Denotes the type of the span and needs to be `"http"`. | Yes |
| `http.method` | HTTP request method. E.g. `"GET"`. | Yes |
| `http.url` | HTTP URL of this request, represented as `scheme://host:port/path?query#fragment` E.g. `"https://example.com:779/path/12314/?q=ddds#123"`. | Yes |
| `http.route` | The matched route. E.g. `"/users/:userID?"`. | No |
| `http.status_code` | [HTTP response status code](https://tools.ietf.org/html/rfc7231). E.g. `200` (integer) | No |
| `http.status_text` | [HTTP reason phrase](https://www.ietf.org/rfc/rfc2616.txt). E.g. `"OK"` | No |

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

# Resource Conventions

This section defines standard labels for [Resources](sdk-resource.md). The 
majority of these labels are inherited from 
[OpenCensus Resource standard](https://github.com/census-instrumentation/opencensus-specs/blob/master/resource/StandardResources.md).

 * [Service](#service)
 * [Compute Unit](#compute-unit)
   * [Container](#container)
 * [Deployment Service](#deployment-service)
   * [Kubernetes](#kubernetes)
 * [Compute Instance](#compute-instance)
   * [Host](#host)
 * [Environment](#environment)
   * [Cloud](#cloud)
   * [Cluster](#cluster)

## TODOs
* Add more compute units: Process, Lambda Function, AppEngine unit, etc.
* Add Device (mobile) and Web Browser.
* Decide if lower case strings only.
* Consider to add optional/required for each label and combination of labels
  (e.g when supplying a k8s resource all k8s may be required).

## Services

**type:** `service`

**Description:** A service instance.

| Label  | Description  | Example  | Required? |
|---|---|---|---|
| service.name | Logical name of the service. <br/> MUST be the same for all instances of horizontally scaled services. | `shoppingcart` | Yes |
| service.instance.uuid | UUID of the service instance (RFC 4122, string representation). <br/>MUST be unique for each instance of the same service and SHOULD be globally unique. | `627cc493-f310-47de-96bd-71410b7dec09` | Yes |


## Compute Unit
Labels defining a compute unit (e.g. Container, Process, Lambda Function).

### Container
**type:** `container`

**Description:** A container instance.

| Label  | Description  | Example  |
|---|---|---|
| container.name | Container name. | `opentelemetry-autoconf` |
| container.image.name | Name of the image the container was built on. | `gcr.io/opentelemetry/operator` |
| container.image.tag | Container image tag. | `0.1` |

## Deployment Service
Labels defining a deployment service (e.g. Kubernetes).

### Kubernetes
**type:** `k8s`

**Description:** A Kubernetes resource.

| Label  | Description  | Example  |
|---|---|---|
| k8s.cluster.name | The name of the cluster that the pod is running in. | `opentelemetry-cluster` |
| k8s.namespace.name | The name of the namespace that the pod is running in. | `default` |
| k8s.pod.name | The name of the pod. | `opentelemetry-pod-autoconf` |
| k8s.deployment.name | The name of the deployment. | `opentelemetry` |

## Compute Instance
Labels defining a computing instance (e.g. host).

### Host
**type:** `host`

**Description:** A host is defined as a general computing instance.

| Label  | Description  | Example  |
|---|---|---|
| host.hostname | Hostname of the host.<br/> It contains what the `hostname` command returns on the host machine. | `opentelemetry-test` |
| host.id | Unique host id.<br/> For Cloud this must be the instance_id assigned by the cloud provider | `opentelemetry-test` |
| host.name | Name of the host.<br/> It may contain what `hostname` returns on Unix systems, the fully qualified, or a name specified by the user. | `opentelemetry-test` |
| host.type | Type of host.<br/> For Cloud this must be the machine type.| `n1-standard-1` |

## Environment
Labels defining a running environment (e.g. Cloud, Data Center).

### Cloud
**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

| Label  | Description  | Example  |
|---|---|---|
| cloud.provider | Name of the cloud provider.<br/> Example values are aws, azure, gcp. | `gcp` |
| cloud.account.id | The cloud account id used to identify different entities. | `opentelemetry` |
| cloud.region | A specific geographical location where different entities can run | `us-central1` |
| cloud.zone | Zones are a sub set of the region connected through low-latency links.<br/> In aws it is called availability-zone. | `us-central1-a` |
