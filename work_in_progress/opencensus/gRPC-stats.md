# gRPC Stats

Any particular library might provide only a subset of these measures/views/tags.
Check the language-specific documentation for the list of supported values.

## Units

As always, units are encoded according to the case-sensitive abbreviations from the [Unified Code for Units of Measure](http://unitsofmeasure.org/ucum.html):

* Latencies are measures in float64 milliseconds, denoted "ms"
* Sizes are measured in bytes, denoted "By"
* Counts of messages per RPC have unit "1"

Buckets for distributions in default views are as follows:

* Size in bytes: 0, 1024, 2048, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216, 67108864, 268435456, 1073741824, 4294967296
* Latency in ms: 0, 0.01, 0.05, 0.1, 0.3, 0.6, 0.8, 1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 30, 40, 50, 65, 80, 100, 130, 160, 200, 250, 300, 400, 500, 650, 800, 1000, 2000, 5000, 10000, 20000, 50000, 100000
* Counts (no unit): 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536

## Terminology

* **RPC** single call against a gRPC service, either streaming or unary.
* **message** individual message in an RPC. Streaming RPCs can have multiple messages per RPC. Unary RPCs always have only a single message per RPC.
* **status** string (all caps), e.g. CANCELLED, DEADLINE_EXCEEDED. See: https://github.com/grpc/grpc/blob/master/doc/statuscodes.md

## Client

### Measures

Client stats are recorded at the end of each outbound RPC.

| Measure name                              | Unit | Description                                                                                   |
|-------------------------------------------|------|-----------------------------------------------------------------------------------------------|
| grpc.io/client/sent_messages_per_rpc      | 1    | Number of messages sent in the RPC (always 1 for non-streaming RPCs).                         |
| grpc.io/client/sent_bytes_per_rpc         | By   | Total bytes sent across all request messages per RPC.                                         |
| grpc.io/client/received_messages_per_rpc  | 1    | Number of response messages received per RPC (always 1 for non-streaming RPCs).               |
| grpc.io/client/received_bytes_per_rpc     | By   | Total bytes received across all response messages per RPC.                                    |
| grpc.io/client/roundtrip_latency          | ms   | Time between first byte of request sent to last byte of response received, or terminal error. |
| grpc.io/client/server_latency             | ms   | Propagated from the server and should have the same value as "grpc.io/server/latency".        |
| grpc.io/client/started_rpcs               | 1    | The total number of client RPCs ever opened, including those that have not completed.         |
| grpc.io/client/sent_messages_per_method   | 1    | Total messages sent per method.                                    |
| grpc.io/client/received_messages_per_method | 1  | Total messages received per method.                                |
| grpc.io/client/sent_bytes_per_method      | By   | Total bytes sent per method, recorded real-time as bytes are sent. |
| grpc.io/client/received_bytes_per_method  | By   | Total bytes received per method, recorded real-time as bytes are received. |


### Tags

All client metrics should be tagged with the following.

| Tag name           | Description                                                                                                      |
|--------------------|------------------------------------------------------------------------------------------------------------------|
| grpc_client_method | Full gRPC method name, including package, service and method, e.g. google.bigtable.v2.Bigtable/CheckAndMutateRow |
| grpc_client_status | gRPC server status code received, e.g. OK, CANCELLED, DEADLINE_EXCEEDED                                          |

`grpc_client_method` is set when an outgoing request starts and is available in all the recorded
metrics.
`grpc_client_status` is set when an outgoing request finishes and is only available around metrics
recorded at the end of the outgoing request.
Status codes should be stringified according to:
https://github.com/grpc/grpc/blob/master/doc/statuscodes.md

### Default views

The following set of views are considered minimum required to monitor client-side performance:

| View name                                 | Measure                                   | Aggregation  | Tags                                   |
|-------------------------------------------|-------------------------------------------|--------------|----------------------------------------|
| grpc.io/client/sent_bytes_per_rpc         | grpc.io/client/sent_bytes_per_rpc         | distribution | grpc_client_method                     |
| grpc.io/client/received_bytes_per_rpc     | grpc.io/client/received_bytes_per_rpc     | distribution | grpc_client_method                     |
| grpc.io/client/roundtrip_latency          | grpc.io/client/roundtrip_latency          | distribution | grpc_client_method                     |
| grpc.io/client/completed_rpcs             | grpc.io/client/roundtrip_latency          | count        | grpc_client_method, grpc_client_status |
| grpc.io/client/started_rpcs               | grpc.io/client/started_rpcs               | count        | grpc_client_method                     |

### Extra views

The following set of views are considered useful but not mandatory to monitor client side performance:

| View name                                | Measure                                  | Aggregation  | Tags               |
|------------------------------------------|------------------------------------------|--------------|--------------------|
| grpc.io/client/sent_messages_per_rpc     | grpc.io/client/sent_messages_per_rpc     | distribution | grpc_client_method |
| grpc.io/client/received_messages_per_rpc | grpc.io/client/received_messages_per_rpc | distribution | grpc_client_method |
| grpc.io/client/server_latency            | grpc.io/client/server_latency            | distribution | grpc_client_method |
| grpc.io/client/sent_messages_per_method      | grpc.io/client/sent_messages_per_method      | count | grpc_client_method                     |
| grpc.io/client/received_messages_per_method  | grpc.io/client/received_messages_per_method  | count | grpc_client_method                     |
| grpc.io/client/sent_bytes_per_method      | grpc.io/client/sent_bytes_per_method      | sum | grpc_client_method                     |
| grpc.io/client/received_bytes_per_method  | grpc.io/client/received_bytes_per_method  | sum | grpc_client_method                     |

## Server

Server stats are recorded at the end of processing each RPC.

| Measure name                              | Unit | Description                                                                                   |
|-------------------------------------------|------|-----------------------------------------------------------------------------------------------|
| grpc.io/server/received_messages_per_rpc  | 1    | Number of messages received in each RPC. Has value 1 for non-streaming RPCs.                  |
| grpc.io/server/received_bytes_per_rpc     | By   | Total bytes received across all messages per RPC.                                             |
| grpc.io/server/sent_messages_per_rpc      | 1    | Number of messages sent in each RPC. Has value 1 for non-streaming RPCs.                      |
| grpc.io/server/sent_bytes_per_rpc         | By   | Total bytes sent in across all response messages per RPC.                                     |
| grpc.io/server/server_latency             | ms   | Time between first byte of request received to last byte of response sent, or terminal error. |
| grpc.io/server/started_rpcs               | 1    | The total number of server RPCs ever opened, including those that have not completed.         |
| grpc.io/server/sent_messages_per_method   | 1    | Total messages sent per method.                                    |
| grpc.io/server/received_messages_per_method  | 1 | Total messages received per method.                                |
| grpc.io/server/sent_bytes_per_method      | By   | Total bytes sent per method, recorded real-time as bytes are sent. |
| grpc.io/server/received_bytes_per_method  | By   | Total bytes received per method, recorded real-time as bytes are received. |


### Tags

All server metrics should be tagged with the following.

| Tag name           | Description                                                                                                    |
|--------------------|----------------------------------------------------------------------------------------------------------------|
| grpc_server_method | Full gRPC method name, including package, service and method, e.g. com.exampleapi.v4.BookshelfService/Checkout |
| grpc_server_status | gRPC server status code returned, e.g. OK, CANCELLED, DEADLINE_EXCEEDED                                        |

`grpc_server_method` is set when an incoming request starts and is available in the context for
the entire RPC call handling.

`grpc_server_status` is set when an incoming request finishes and is only available around metrics
recorded at the end of the incoming request.
Status codes should be stringified according to:
https://github.com/grpc/grpc/blob/master/doc/statuscodes.md

### Default views

The following set of views are considered minimum required to monitor server side performance:

| View name                                 | Measure                               | Aggregation  | Tags                                   |
|-------------------------------------------|---------------------------------------|--------------|----------------------------------------|
| grpc.io/server/received_bytes_per_rpc     | grpc.io/server/received_bytes_per_rpc | distribution | grpc_server_method                     |
| grpc.io/server/sent_bytes_per_rpc         | grpc.io/server/sent_bytes_per_rpc     | distribution | grpc_server_method                     |
| grpc.io/server/server_latency             | grpc.io/server/server_latency         | distribution | grpc_server_method                     |
| grpc.io/server/completed_rpcs             | grpc.io/server/server_latency         | count        | grpc_server_method, grpc_server_status |
| grpc.io/server/started_rpcs               | grpc.io/server/started_rpcs           | count        | grpc_server_method                     |

### Extra views

The following set of views are considered useful but not mandatory to monitor server side performance:

| View name                                | Measure                                  | Aggregation  | Tag                |
|------------------------------------------|------------------------------------------|--------------|--------------------|
| grpc.io/server/received_messages_per_rpc | grpc.io/server/received_messages_per_rpc | distribution | grpc_server_method |
| grpc.io/server/sent_messages_per_rpc     | grpc.io/server/sent_messages_per_rpc     | distribution | grpc_server_method |
| grpc.io/server/sent_messages_per_method      | grpc.io/server/sent_messages_per_method      | count | grpc_server_method                     |
| grpc.io/server/received_messages_per_method  | grpc.io/server/received_messages_per_method  | count | grpc_server_method                     |
| grpc.io/server/sent_bytes_per_method      | grpc.io/server/sent_bytes_per_method      | sum | grpc_server_method                     |
| grpc.io/server/received_bytes_per_method  | grpc.io/server/received_bytes_per_method  | sum | grpc_server_method                     |

## FAQ

### Why different tag name for server/client method?
This way users can configure views to correlate incoming with outgoing requests. A view example:

| View name                               | Measure                          | Aggregation  | Tag                                    |
|-----------------------------------------|----------------------------------|--------------|----------------------------------------|
| grpc.io/client/latency_by_server_method | grpc.io/client/roundtrip_latency | distribution | grpc_client_method, grpc_server_method |

### How is the server latency on the client recorded (grcp.io/client/server_latency)?
This is TBD, eventually a designated gRPC metadata key will be specified for this purpose.

### Why no error counts?
Error counts can be computed on your metrics backend by totalling the different per-status values.

### Why are ".../completed_rpcs" views defined over latency measures?
They can be defined over any measure recorded once per RPC (since it's just a count aggregation over the measure).
It would be unnecessary to use a separate "count" measure.

### Why are "*_per_method" views not default?

These views are useful for real-time reporting for streaming RPCs. However, for unary calls
they are not particularly useful, and data volume for these views could be huge compared to
default views. Only enable these views if you are using streaming RPCs and want real-time
metrics.