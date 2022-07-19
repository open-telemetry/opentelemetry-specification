<!--- Hugo front matter used to generate the website version of this page:
linkTitle: System
--->

# Semantic Conventions for System Metrics

**Status**: [Experimental](../../document-status.md)

This document describes instruments and attributes for common system level
metrics in OpenTelemetry. Consider the [general metric semantic
conventions](README.md#general-metric-semantic-conventions) when creating
instruments not explicitly defined in the specification.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [`system.cpu.` - Processor metrics](#systemcpu---processor-metrics)
  * [`system.memory.` - Memory metrics](#systemmemory---memory-metrics)
  * [`system.paging.` - Paging/swap metrics](#systempaging---pagingswap-metrics)
  * [`system.disk.` - Disk controller metrics](#systemdisk---disk-controller-metrics)
  * [`system.filesystem.` - Filesystem metrics](#systemfilesystem---filesystem-metrics)
  * [`system.network.` - Network metrics](#systemnetwork---network-metrics)
  * [`system.processes.` - Aggregate system process metrics](#systemprocesses---aggregate-system-process-metrics)
  * [`system.{os}.` - OS Specific System Metrics](#systemos---os-specific-system-metrics)

<!-- tocstop -->

## Metric Instruments

### `system.cpu.` - Processor metrics

**Description:** System level processor metrics.

| Name                   | Description                                                                                              | Units | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key(s) | Attribute Values                    |
| ---------------------- | -------------------------------------------------------------------------------------------------------- | ----- | ------------------------------------------------- | ---------- | ---------------- | ----------------------------------- |
| system.cpu.time        |                                                                                                          | s     | Counter                                           | Double     | state            | idle, user, system, interrupt, etc. |
|                        |                                                                                                          |       |                                                   |            | cpu              | CPU number [0..n-1]                 |
| system.cpu.utilization | Difference in system.cpu.time since the last measurement, divided by the elapsed time and number of CPUs | 1     | Gauge                                             | Double     | state            | idle, user, system, interrupt, etc. |
|                        |                                                                                                          |       |                                                   |            | cpu              | CPU number (0..n)                   |

### `system.memory.` - Memory metrics

**Description:** System level memory metrics. This does not include [paging/swap
memory](#systempaging---pagingswap-metrics).

| Name                      | Description | Units | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values         |
| ------------------------- | ----------- | ----- | ------------------------------------------------- | ---------- | ------------- | ------------------------ |
| system.memory.usage       |             | By    | UpDownCounter                                     | Int64      | state         | used, free, cached, etc. |
| system.memory.utilization |             | 1     | Gauge                                             | Double     | state         | used, free, cached, etc. |

### `system.paging.` - Paging/swap metrics

**Description:** System level paging/swap memory metrics.

| Name                                  | Description                         | Units        | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values |
| ------------------------------------- | ----------------------------------- | ------------ | ------------------------------------------------- | ---------- | ------------- | ---------------- |
| system.paging.usage                   | Unix swap or windows pagefile usage | By           | UpDownCounter                                     | Int64      | state         | used, free       |
| system.paging.utilization             |                                     | 1            | Gauge                                             | Double     | state         | used, free       |
| system.paging.faults                  |                                     | {faults}     | Counter                                           | Int64      | type          | major, minor     |
| system.paging.operations (deprecated) |                                     | {operations} | Counter                                           | Int64      | type          | major, minor     |
|                                       |                                     |              |                                                   |            | direction     | in, out          |
| system.paging.operations.in           |                                     | {operations} | Counter                                           | Int64      | type          | major, minor     |
| system.paging.operations.out          |                                     | {operations} | Counter                                           | Int64      | type          | major, minor     |

### `system.disk.` - Disk controller metrics

**Description:** System level disk performance metrics.

| Name                                             | Description                                     | Units        | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values |
| ------------------------------------------------ | ----------------------------------------------- | ------------ | ------------------------------------------------- | ---------- | ------------- | ---------------- |
| system.disk.io<!--notlink--> (deprecated)        |                                                 | By           | Counter                                           | Int64      | device        | (identifier)     |
|                                                  |                                                 |              |                                                   |            | direction     | read, write      |
| system.disk.io.read                              |                                                 | By           | Counter                                           | Int64      | device        | (identifier)     |
| system.disk.io.write                             |                                                 | By           | Counter                                           | Int64      | device        | (identifier)     |
| system.disk.operations (deprecated)              |                                                 | {operations} | Counter                                           | Int64      | device        | (identifier)     |
|                                                  |                                                 |              |                                                   |            | direction     | read, write      |
| system.disk.operations.read                      |                                                 | {operations} | Counter                                           | Int64      | device        | (identifier)     |
| system.disk.operations.write                     |                                                 | {operations} | Counter                                           | Int64      | device        | (identifier)     |
| system.disk.io_time<sup>\[1\]</sup>              | Time disk spent activated                       | s            | Counter                                           | Double     | device        | (identifier)     |
| system.disk.operation_time (deprecated)          | Sum of the time each operation took to complete | s            | Counter                                           | Double     | device        | (identifier)     |
|                                                  |                                                 |              |                                                   |            | direction     | read, write      |
| system.disk.operation_time.read<sup>\[2\]</sup>  | Sum of the time each operation took to complete | s            | Counter                                           | Double     | device        | (identifier)     |
| system.disk.operation_time.write<sup>\[2\]</sup> | Sum of the time each operation took to complete | s            | Counter                                           | Double     | device        | (identifier)     |
| system.disk.merged (deprecated)                  |                                                 | {operations} | Counter                                           | Int64      | device        | (identifier)     |
|                                                  |                                                 |              |                                                   |            | direction     | read, write      |
| system.disk.merged.read                          |                                                 | {operations} | Counter                                           | Int64      | device        | (identifier)     |
| system.disk.merged.write                         |                                                 | {operations} | Counter                                           | Int64      | device        | (identifier)     |

<sup>1</sup> The real elapsed time ("wall clock")
used in the I/O path (time from operations running in parallel are not
counted). Measured as:

- Linux: Field 13 from
[procfs-diskstats](https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats)
- Windows: The complement of ["Disk\% Idle
Time"](https://docs.microsoft.com/en-us/archive/blogs/askcore/windows-performance-monitor-disk-counters-explained#windows-performance-monitor-disk-counters-explained:~:text=%25%20Idle%20Time,Idle\)%20to%200%20(meaning%20always%20busy).)
performance counter: `uptime * (100 - "Disk\% Idle Time") / 100`

<sup>2</sup> Because it is the sum of time each
request took, parallel-issued requests each contribute to make the count
grow. Measured as:

- Linux: Fields 7 & 11 from
[procfs-diskstats](https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats)
- Windows: "Avg. Disk sec/Read" perf counter multiplied by "Disk Reads/sec"
perf counter (similar for Writes)

### `system.filesystem.` - Filesystem metrics

**Description:** System level filesystem metrics.

| Name                          | Description | Units | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values     |
| ----------------------------- | ----------- | ----- | ------------------------------------------------- | ---------- | ------------- | -------------------- |
| system.filesystem.usage       |             | By    | UpDownCounter                                     | Int64      | device        | (identifier)         |
|                               |             |       |                                                   |            | state         | used, free, reserved |
|                               |             |       |                                                   |            | type          | ext4, tmpfs, etc.    |
|                               |             |       |                                                   |            | mode          | rw, ro, etc.         |
|                               |             |       |                                                   |            | mountain      | (path)               |
| system.filesystem.utilization |             | 1     | Gauge                                             | Double     | device        | (identifier)         |
|                               |             |       |                                                   |            | state         | used, free, reserved |
|                               |             |       |                                                   |            | type          | ext4, tmpfs, etc.    |
|                               |             |       |                                                   |            | mode          | rw, ro, etc.         |
|                               |             |       |                                                   |            | mountpoint    | (path)               |

### `system.network.` - Network metrics

**Description:** System level network metrics.

| Name                                            | Description                                                                               | Units         | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values                                                                               |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------- | ---------- | ------------- | ---------------------------------------------------------------------------------------------- |
| system.network.dropped (deprecated)             | Count of packets that are dropped or discarded even though there was no error             | {packets}     | Counter                                           | Int64      | device        | (identifier)                                                                                   |
|                                                 |                                                                                           |               |                                                   |            | direction     | transmit, receive                                                                              |
| system.network.dropped.transmit<sup>\[1\]</sup> | Count of packets that are dropped or discarded on transmit even though there was no error | {packets}     | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system.network.dropped.receive<sup>\[1\]</sup>  | Count of packets that are dropped or discarded on receive even though there was no error  | {packets}     | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system.network.packets (deprecated)             |                                                                                           | {packets}     | Counter                                           | Int64      | device        | (identifier)                                                                                   |
|                                                 |                                                                                           |               |                                                   |            | direction     | transmit, receive                                                                              |
| system.network.packets.transmit                 | Count of packets transmitted                                                              | {packets}     | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system.network.packets.receive                  | Count of packets received                                                                 | {packets}     | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system.network.errors (deprecated)              | Count of network errors detected                                                          | {errors}      | Counter                                           | Int64      | device        | (identifier)                                                                                   |
|                                                 |                                                                                           |               |                                                   |            | direction     | transmit, receive                                                                              |
| system.network.errors.transmit<sup>\[2\]</sup>  | Count of network errors detected on transmit                                              | {errors}      | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system.network.errors.receive<sup>\[2\]</sup>   | Count of network errors detected on receive                                               | {errors}      | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system<!--notlink-->.network.io (deprecated)    |                                                                                           | By            | Counter                                           | Int64      | device        | (identifier)                                                                                   |
|                                                 |                                                                                           |               |                                                   |            | direction     | transmit, receive                                                                              |
| system<!--notlink-->.network.io.transmit        | Bytes sent                                                                                | By            | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system<!--notlink-->.network.io.receive         | Bytes received                                                                            | By            | Counter                                           | Int64      | device        | (identifier)                                                                                   |
| system.network.connections                      |                                                                                           | {connections} | UpDownCounter                                     | Int64      | device        | (identifier)                                                                                   |
|                                                 |                                                                                           |               |                                                   |            | protocol      | tcp, udp, [etc.](https://en.wikipedia.org/wiki/Transport_layer#Protocols)                      |
|                                                 |                                                                                           |               |                                                   |            | state         | If specified, SHOULD be one of: close, close_wait, closing, delete, established, fin_wait_1, fin_wait_2, last_ack, listen, syn_recv, syn_sent, time_wait. A stateless protocol MUST NOT set this attribute. |

<sup>1</sup> Measured as:

- Linux: the `drop` column in `/proc/dev/net`
([source](https://web.archive.org/web/20180321091318/http://www.onlamp.com/pub/a/linux/2000/11/16/LinuxAdmin.html)).
- Windows:
[`InDiscards`/`OutDiscards`](https://docs.microsoft.com/en-us/windows/win32/api/netioapi/ns-netioapi-mib_if_row2)
from
[`GetIfEntry2`](https://docs.microsoft.com/en-us/windows/win32/api/netioapi/nf-netioapi-getifentry2).

<sup>2</sup> Measured as:

- Linux: the `errs` column in `/proc/dev/net`
([source](https://web.archive.org/web/20180321091318/http://www.onlamp.com/pub/a/linux/2000/11/16/LinuxAdmin.html)).
- Windows:
[`InErrors`/`OutErrors`](https://docs.microsoft.com/en-us/windows/win32/api/netioapi/ns-netioapi-mib_if_row2)
from
[`GetIfEntry2`](https://docs.microsoft.com/en-us/windows/win32/api/netioapi/nf-netioapi-getifentry2).

### `system.processes.` - Aggregate system process metrics

**Description:** System level aggregate process metrics. For metrics at the
individual process level, see [process metrics](process-metrics.md).

| Name                     | Description                                               | Units       | Instrument Type ([*](README.md#instrument-types)) | Value Type | Attribute Key | Attribute Values                                                                               |
| ------------------------ | --------------------------------------------------------- | ----------- | ------------------------------------------------- | ---------- | ------------- | ---------------------------------------------------------------------------------------------- |
| system.processes.count   | Total number of processes in each state                   | {processes} | UpDownCounter                                     | Int64      | status        | running, sleeping, [etc.](https://man7.org/linux/man-pages/man1/ps.1.html#PROCESS_STATE_CODES) |
| system.processes.created | Total number of processes created over uptime of the host | {processes} | Counter                                           | Int64      | -             | -                                                                                              |

### `system.{os}.` - OS Specific System Metrics

Instrument names for system level metrics that have different and conflicting
meaning across multiple OSes should be prefixed with `system.{os}.` and
follow the hierarchies listed above for different entities like CPU, memory,
and network.

For example, [UNIX load
average](https://en.wikipedia.org/wiki/Load_(computing)) over a given
interval is not well standardized and its value across different UNIX like
OSes may vary despite being under similar load:

> Without getting into the vagaries of every Unix-like operating system in
existence, the load average more or less represents the average number of
processes that are in the running (using the CPU) or runnable (waiting for
the CPU) states. One notable exception exists: Linux includes processes in
uninterruptible sleep states, typically waiting for some I/O activity to
complete. This can markedly increase the load average on Linux systems.

([source of
quote](https://github.com/torvalds/linux/blob/e4cbce4d131753eca271d9d67f58c6377f27ad21/kernel/sched/loadavg.c#L11-L18),
[linux source
code](https://github.com/torvalds/linux/blob/e4cbce4d131753eca271d9d67f58c6377f27ad21/kernel/sched/loadavg.c#L11-L18))

An instrument for load average over 1 minute on Linux could be named
`system.linux.cpu.load_1m`, reusing the `cpu` name proposed above and having
an `{os}` prefix to split this metric across OSes.
