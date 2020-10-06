# Semantic Conventions for System Metrics

This document describes instruments and labels for common system level
metrics in OpenTelemetry. Consider the [general metric semantic
conventions](README.md#general-metric-semantic-conventions) when creating
instruments not explicitly defined in the specification.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [Standard System Metrics - `system.`](#standard-system-metrics---system)
    + [`system.cpu.` - Processor metrics](#systemcpu---processor-metrics)
    + [`system.memory.` - Memory metrics](#systemmemory---memory-metrics)
    + [`system.paging.` - Paging/swap metrics](#systempaging---pagingswap-metrics)
    + [`system.disk.` - Disk controller metrics](#systemdisk---disk-controller-metrics)
    + [`system.filesystem.` - Filesystem metrics](#systemfilesystem---filesystem-metrics)
    + [`system.network.` - Network metrics](#systemnetwork---network-metrics)
    + [`system.process.` - Aggregate system process metrics](#systemprocess---aggregate-system-process-metrics)
    + [`system.{os}.` - OS Specific System Metrics](#systemos---os-specific-system-metrics)

<!-- tocstop -->

## Metric Instruments

### Standard System Metrics - `system.`

#### `system.cpu.` - Processor metrics

**Description:** System level processor metrics.

| Name                   | Description | Units | Instrument Type | Value Type | Label Key(s) | Label Values                        |
| ---------------------- | ----------- | ----- | --------------- | ---------- | --------- | ----------------------------------- |
| system.cpu.time        |             | s     | SumObserver     | Double     | state     | idle, user, system, interrupt, etc. |
|                        |             |       |                 |            | cpu       | CPU number [0..n-1]                   |
| system.cpu.utilization |             | 1     | ValueObserver   | Double     | state     | idle, user, system, interrupt, etc. |
|                        |             |       |                 |            | cpu       | CPU number (0..n)                   |

#### `system.memory.` - Memory metrics

**Description:** System level memory metrics. This does not include [paging/swap
memory](#systempaging---pagingswap-metrics).

| Name                      | Description | Units | Instrument Type   | Value Type | Label Key | Label Values             |
| ------------------------- | ----------- | ----- | ----------------- | ---------- | --------- | ------------------------ |
| system.memory.usage       |             | By    | UpDownSumObserver | Int64      | state     | used, free, cached, etc. |
| system.memory.utilization |             | 1     | ValueObserver     | Double     | state     | used, free, cached, etc. |

#### `system.paging.` - Paging/swap metrics

**Description:** System level paging/swap memory metrics.
| Name                      | Description                         | Units        | Instrument Type   | Value Type | Label Key | Label Values |
| ------------------------- | ----------------------------------- | ------------ | ----------------- | ---------- | --------- | ------------ |
| system.paging.usage       | Unix swap or windows pagefile usage | By           | UpDownSumObserver | Int64      | state     | used, free   |
| system.paging.utilization |                                     | 1            | ValueObserver     | Double     | state     | used, free   |
| system.paging.faults      |                                     | {faults}     | SumObserver       | Int64      | type      | major, minor |
| system.paging.operations  |                                     | {operations} | SumObserver       | Int64      | type      | major, minor |
|                           |                                     |              |                   |            | direction | in, out      |

#### `system.disk.` - Disk controller metrics

**Description:** System level disk performance metrics.
| Name                         | Description | Units        | Instrument Type | Value Type | Label Key | Label Values |
| ---------------------------- | ----------- | ------------ | --------------- | ---------- | --------- | ------------ |
| system.disk.io<!--notlink--> |             | By           | SumObserver     | Int64      | device    | (identifier) |
|                              |             |              |                 |            | direction | read, write  |
| system.disk.operations       |             | {operations} | SumObserver     | Int64      | device    | (identifier) |
|                              |             |              |                 |            | direction | read, write  |
| system.disk.time             |             | s            | SumObserver     | Double     | device    | (identifier) |
|                              |             |              |                 |            | direction | read, write  |
| system.disk.merged           |             | {operations} | SumObserver     | Int64      | device    | (identifier) |
|                              |             |              |                 |            | direction | read, write  |

#### `system.filesystem.` - Filesystem metrics

**Description:** System level filesystem metrics.
| Name                          | Description | Units | Instrument Type   | Value Type | Label Key  | Label Values         |
| ----------------------------- | ----------- | ----- | ----------------- | ---------- | ---------- | -------------------- |
| system.filesystem.usage       |             | By    | UpDownSumObserver | Int64      | device     | (identifier)         |
|                               |             |       |                   |            | state      | used, free, reserved |
|                               |             |       |                   |            | type       | ext4, tmpfs, etc.    |
|                               |             |       |                   |            | mode       | rw, ro, etc.         |
|                               |             |       |                   |            | mountpoint | (path)               |
| system.filesystem.utilization |             | 1     | ValueObserver     | Double     | device     | (identifier)         |
|                               |             |       |                   |            | state      | used, free, reserved |
|                               |             |       |                   |            | type       | ext4, tmpfs, etc.    |
|                               |             |       |                   |            | mode       | rw, ro, etc.         |
|                               |             |       |                   |            | mountpoint | (path)               |

#### `system.network.` - Network metrics

**Description:** System level network metrics.
| Name                            | Description | Units         | Instrument Type   | Value Type | Label Key | Label Values                                                                                   |
| ------------------------------- | ----------- | ------------- | ----------------- | ---------- | --------- | ---------------------------------------------------------------------------------------------- |
| system.network.dropped_packets  |             | {packets}     | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |               |                   |            | direction | transmit, receive                                                                              |
| system.network.packets          |             | {packets}     | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |               |                   |            | direction | transmit, receive                                                                              |
| system.network.errors           |             | {errors}      | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |               |                   |            | direction | transmit, receive                                                                              |
| system<!--notlink-->.network.io |             | By            | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |               |                   |            | direction | transmit, receive                                                                              |
| system.network.connections      |             | {connections} | UpDownSumObserver | Int64      | device    | (identifier)                                                                                   |
|                                 |             |               |                   |            | protocol  | tcp, udp, [etc.](https://en.wikipedia.org/wiki/Transport_layer#Protocols)                      |
|                                 |             |               |                   |            | state     | [e.g. for tcp](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Protocol_operation) |

#### `system.process.` - Aggregate system process metrics

**Description:** System level aggregate process metrics. For metrics at the
individual process level, see [process metrics](process-metrics.md).
| Name                 | Description                             | Units       | Instrument Type   | Value Type | Label Key | Label Values                                                                                   |
| -------------------- | --------------------------------------- | ----------- | ----------------- | ---------- | --------- | ---------------------------------------------------------------------------------------------- |
| system.process.count | Total number of processes in each state | {processes} | UpDownSumObserver | Int64      | status    | running, sleeping, [etc.](https://man7.org/linux/man-pages/man1/ps.1.html#PROCESS_STATE_CODES) |

#### `system.{os}.` - OS Specific System Metrics

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
