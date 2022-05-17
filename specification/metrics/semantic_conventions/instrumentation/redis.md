# Instrumenting Redis

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Redis.

<!-- toc -->

- [Redis Metrics](#redis-metrics)

<!-- tocstop -->

## Redis Metrics

**Description:** General Redis metrics.

| Name                                           | Instrument    | Value type | Unit         | Unit ([UCUM](../README.md#instrument-units)) | Description                                                           | Attribute Key | Attribute Values |
| ---------------------------------------------- | ------------- | ---------- | ------------ | -------------------------------------------- | --------------------------------------------------------------------- | ------------- | ---------------- |
| db.redis.uptime                                | Counter       | Int64      | seconds      | `{s}`                                        | Number of seconds since Redis server start                            |               |                  |
| db.redis.cpu.time                              | Counter       | Double     | seconds      | `{s}`                                        | System CPU consumed by the Redis server in seconds since server start | `state`       |                  |
| db.redis.clients.connected                     | UpDownCounter | Int64      | clients      | `{clients}`                                  | Number of client connections (excluding connections from replicas)    |               |                  |
| db.redis.clients.max_input_buffer              | Gauge         | Int64      |              |                                              | Biggest input buffer among current client connections                 |               |                  |
| db.redis.clients.max_output_buffer             | Gauge         | Int64      |              |                                              | Longest output list among current client connections                  |               |                  |
| db.redis.clients.blocked                       | UpDownCounter | Int64      | clients      | `{clients}`                                  | Number of clients pending on a blocking call                          |               |                  |
| db.redis.keys.expired                          | Counter       | Int64      | keys         | `{keys}`                                     | Total number of key expiration events                                 |               |                  |
| db.redis.keys.evicted                          | Counter       | Int64      | keys         | `{keys}`                                     | Number of evicted keys due to maxmemory limit                         |               |                  |
| db.redis.connections.received                  | Counter       | Int64      | connections  | `{connections}`                              | Total number of connections accepted by the server                    |               |                  |
| db.redis.connections.rejected                  | Counter       | Int64      | connections  | `{connections}`                              | Number of connections rejected because of maxclients limit            |               |                  |
| db.redis.memory.used                           | Gauge         | Int64      | bytes        | `{by}`                                       | Total number of bytes allocated by Redis using its allocator          |               |                  |
| db.redis.memory.peak                           | Gauge         | Int64      | bytes        | `{by}`                                       | Peak memory consumed by Redis                                         |               |                  |
| db.redis.memory.rss                            | Gauge         | Int64      | bytes        | `{by}`                                       | Number of bytes that Redis allocated as seen by the operating system  |               |                  |
| db.redis.memory.lua                            | Gauge         | Int64      | bytes        | `{by}`                                       | Number of bytes used by the Lua engine                                |               |                  |
| db.redis.memory.fragmentation_ratio            | Gauge         | Double     |              |                                              | Ratio between used_memory_rss and used_memory                         |               |                  |
| db.redis.rdb.changes_since_last_save           | UpDownCounter | Int64      | changes      | `{changes}`                                  | Number of changes since the last dump                                 |               |                  |
| db.redis.commands                              | Gauge         | Int64      | operations   | `{ops}/s`                                    | Number of commands processed per second                               |               |                  |
| db.redis.commands.processed                    | Counter       | Int64      | operations   | `{ops}`                                      | Total number of commands processed by the server                      |               |                  |
| db.redis.net.input                             | Counter       | Int64      | bytes        | `{by}`                                       | The total number of bytes read from the network                       |               |                  |
| db.redis.net.output                            | Counter       | Int64      | bytes        | `{by}`                                       | The total number of bytes written to the network                      |               |                  |
| db.redis.keyspace.hits                         | Counter       | Int64      | operations   | `{ops}`                                      | The total number of successful lookup of keys in the main dictionary  |               |                  |
| db.redis.keyspace.misses                       | Counter       | Int64      | operations   | `{ops}`                                      | The total number of failed lookup of keys in the main dictionary      |               |                  |
| db.redis.latest_fork                           | Gauge         | Int64      | microseconds | `{us}`                                       | Duration of the latest fork operation                                 |               |                  |
| db.redis.replicas.connected                    | Gauge         | Int64      | replicas     | `{replicas}`                                 | Number of connected replicas                                          |               |                  |
| db.redis.replication.backlog_first_byte_offset | Gauge         | Int64      |              |                                              | The master offset of the replication backlog buffer                   |               |                  |
| db.redis.replication.offset                    | Gauge         | Int64      |              |                                              | The server's current replication offset                               |               |                  |
| db.redis.db.keys                               | Gauge         | Int64      | keys         | `{keys}`                                     | Number of keyspace keys                                               | `db`          |                  |
| db.redis.db.expires                            | Gauge         | Int64      | keys         | `{keys}`                                     | Number of keyspace keys with an expiration                            | `db`          |                  |
| db.redis.db.avg_ttl                            | Gauge         | Int64      | milliseconds | `{ms}`                                       | Average keyspace keys TTL                                             |               |  `db`            |
