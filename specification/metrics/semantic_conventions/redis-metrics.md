# Semantic conventions for database metrics

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Redis](#redis)

<!-- tocstop -->

## Redis

The following describes the recommended metric names, instruments and units used to describe Redis server metrics.

| Name                          | Instrument                 | Units        | Description | Attribute Keys | Attributes |
|-------------------------------|----------------------------|--------------|-------------|-|-|
|`redis.uptime`|Asynchronous Counter|seconds|Number of seconds since Redis server start|
|`redis.cpu.time`|Asynchronous Counter|seconds|CPU consumed by the Redis server in seconds since server start| `state` | `system`, `user`, `children`|
|`redis.clients.connected`|Asynchronous UpDownCounter||Number of client connections (excluding connections from replicas)| | |
|`redis.clients.max_input_buffer`|Asynchronous Gauge||Biggest input buffer among current client connections| | |
|`redis.clients.max_output_buffer`|Asynchronous Gauge||Biggest output list among current client connections| | |
|`redis.clients.blocked`|Asynchronous Counter||Number of clients pending on a blocking call| | |
|`redis.keys.expired`|Asynchronous Counter||Total number of key expiration events| | |
|`redis.keys.evicted`|Asynchronous Counter||Total number of evicted keys due to maxmemory limit| | |
|`redis.connections.received`|Asynchronous Counter||Total number of connections accepted by the server| | |
|`redis.connections.rejected`|Asynchronous Counter||Total number of connections rejected because of maxclients limit| | |
|`redis.memory.used`|Asynchronous Gauge|bytes|Total number of bytes allocated by Redis using its allocator| | |
|`redis.memory.peak`|Asynchronous Gauge|bytes|Peak memory consumed| | |
|`redis.memory.rss`|Asynchronous Gauge|bytes|Number of bytes that Redis allocated as seen by the operating system| | |
|`redis.memory.lua`|Asynchronous Gauge|bytes|Number of bytes used by the Lua engine| | |
|`redis.memory.fragmentation_ratio`|Asynchronous Gauge||Ratio between used_memory_rss and used_memory| | |
|`redis.rdb.changes_since_last_save`|Asynchronous UpDownCounter||Number of changes since the last dump| | |
|`redis.commands`|Asynchronous Gauge|operations per second|Number of commands processed per second| | |
|`redis.commands.processed`|Asynchronous Counter||Total number of commands processed by the server| | |
|`redis.net.input`|Asynchronous Counter|bytes|The total number of bytes read from the network| | |
|`redis.net.output`|Asynchronous Counter|bytes|The total number of bytes written to the network| | |
|`redis.keyspace.hits`|Asynchronous Counter||Number of successful lookup of keys in the main dictionary| | |
|`redis.keyspace.misses`|Asynchronous Counter||Number of failed lookup of keys in the main dictionary| | |
|`redis.latest_fork`|Asynchronous Gauge|microseconds|Duration of the latest fork operation| | |
|`redis.slaves.connected`|Asynchronous UpDownCounter||Number of connected replicas| | |
|`redis.replication.backlog_first_byte_offset`|Asynchronous Gauge||The master offset of the replication backlog buffer| | |
|`redis.db.keys`|Asynchronous Gauge||Number of keyspace keys| | |
|`redis.db.expired`|Asynchronous Gauge||Number of keyspace keys with an expiration| | |
|`redis.db.avg_ttl`|Asynchronous Gauge||Average keyspace keys TTL| | |
