# Semantic Conventions for System Metrics

This document describes instruments and labels for common system level
metrics in OpenTelemetry. Also included are general semantic conventions for
system, process, and runtime metrics, which should be considered when
creating instruments not explicitly defined in the specification.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Semantic Conventions](#semantic-conventions)
  * [Instrument Names](#instrument-names)
  * [Units](#units)
- [Metric Instruments](#metric-instruments)
  * [Standard System Metrics - `system.`](#standard-system-metrics---system)
    + [`system.cpu.`](#systemcpu)
    + [`system.memory.`](#systemmemory)
    + [`system.swap.`](#systemswap)
    + [`system.disk.`](#systemdisk)
    + [`system.filesystem.`](#systemfilesystem)
    + [`system.network.`](#systemnetwork)
    + [`system.process.`](#systemprocess)
    + [OS Specific System Metrics - `system.{os}.`](#os-specific-system-metrics---systemos)

<!-- tocstop -->

## Semantic Conventions

The following semantic conventions aim to keep naming consistent. They
provide guidelines for most of the cases in this specification and should be
followed for other instruments not explicitly defined in this document.

### Instrument Names

- **usage** - an instrument that measures an amount used out of a known total
amount should be called `entity.usage`. For example,
`system.filesystem.usage` for the amount of disk spaced used. A measure of
the amount of an unlimited resource consumed is differentiated from
**usage**. This may be time, data, etc.
- **utilization** - an instrument that measures a *value ratio* of usage
(like percent, but in the range `[0, 1]`) should be called
`entity.utilization`. For example, `system.memory.utilization` for the ratio
of memory in use.
- **time** - an instrument that measures passage of time should be called
`entity.time`. For example, `system.cpu.time` with varying values of label
`state` for idle, user, etc.
- **io** - an instrument that measures bidirectional data flow should be
called `entity.io` and have labels for direction. For example,
`system.network.io`.
- Other instruments that do not fit the above descriptions may be named more
freely. For example, `system.swap.page_faults` and `system.network.packets`.
Units do not need to be specified in the names since they are included during
instrument creation, but can be added if there is ambiguity.

### Units

- Instruments for utilization metrics (that measure the ratio out of a total)
SHOULD use units of `1`. Such values represent a *value ratio* and are always
in the range `[0, 1]`.
- Instruments that measure an integer count of something SHOULD use semantic
units like `packets`, `errors`, `faults`, etc.

## Metric Instruments

### Standard System Metrics - `system.`

#### `system.cpu.`

**Description:** System level processor metrics.
| Name                   | Units   | Instrument Type   | Value Type | Label Key | Label Values                        |
| ---------------------- | ------- | ----------------- | ---------- | --------- | ----------------------------------- |
| system.cpu.time        | seconds | SumObserver       | Double     | state     | idle, user, system, interrupt, etc. |
|                        |         |                   |            | cpu       | 1 - #cores                          |
| system.cpu.utilization | 1       | UpDownSumObserver | Double     | state     | idle, user, system, interrupt, etc. |
|                        |         |                   |            | cpu       | 1 - #cores                          |

#### `system.memory.`

**Description:** System level memory metrics.
| Name                      | Units | Instrument Type   | Value Type | Label Key | Label Values             |
| ------------------------- | ----- | ----------------- | ---------- | --------- | ------------------------ |
| system.memory.usage       | bytes | UpDownSumObserver | Int64      | state     | used, free, cached, etc. |
| system.memory.utilization | 1     | ValueObserver     | Double     | state     | used, free, cached, etc. |

#### `system.swap.`

**Description:** System level swap/paging metrics.
| Name                         | Units      | Instrument Type   | Value Type | Label Key | Label Values |
| ---------------------------- | ---------- | ----------------- | ---------- | --------- | ------------ |
| system.swap.usage            | pages      | UpDownSumObserver | Int64      | state     | used, free   |
| system.swap.utilization      | 1          | ValueObserver     | Double     | state     | used, free   |
| system.swap.page\_faults     | faults     | SumObserver       | Int64      | type      | major, minor |
| system.swap.page\_operations | operations | SumObserver       | Int64      | type      | major, minor |
|                              |            |                   |            | direction | in, out      |

#### `system.disk.`

**Description:** System level disk performance metrics.
| Name                         | Units      | Instrument Type | Value Type | Label Key | Label Values |
| ---------------------------- | ---------- | --------------- | ---------- | --------- | ------------ |
| system.disk.io<!--notlink--> | bytes      | SumObserver     | Int64      | device    | (identifier) |
|                              |            |                 |            | direction | read, write  |
| system.disk.operations       | operations | SumObserver     | Int64      | device    | (identifier) |
|                              |            |                 |            | direction | read, write  |
| system.disk.time             | seconds    | SumObserver     | Double     | device    | (identifier) |
|                              |            |                 |            | direction | read, write  |
| system.disk.merged           | 1          | SumObserver     | Int64      | device    | (identifier) |
|                              |            |                 |            | direction | read, write  |

#### `system.filesystem.`

**Description:** System level filesystem metrics.
| Name                          | Units | Instrument Type   | Value Type | Label Key | Label Values         |
| ----------------------------- | ----- | ----------------- | ---------- | --------- | -------------------- |
| system.filesystem.usage       | bytes | UpDownSumObserver | Int64      | device    | (identifier)         |
|                               |       |                   |            | state     | used, free, reserved |
| system.filesystem.utilization | 1     | ValueObserver     | Double     | device    | (identifier)         |
|                               |       |                   |            | state     | used, free, reserved |

#### `system.network.`

**Description:** System level network metrics.
| Name                            | Units       | Instrument Type   | Value Type | Label Key | Label Values                                                                                   |
| ------------------------------- | ----------- | ----------------- | ---------- | --------- | ---------------------------------------------------------------------------------------------- |
| system.network.dropped\_packets | packets     | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |                   |            | direction | transmit, receive                                                                              |
| system.network.packets          | packets     | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |                   |            | direction | transmit, receive                                                                              |
| system.network.errors           | errors      | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |                   |            | direction | transmit, receive                                                                              |
| system<!--notlink-->.network.io | bytes       | SumObserver       | Int64      | device    | (identifier)                                                                                   |
|                                 |             |                   |            | direction | transmit, receive                                                                              |
| system.network.connections      | connections | UpDownSumObserver | Int64      | device    | (identifier)                                                                                   |
|                                 |             |                   |            | protocol  | tcp, udp, [etc.](https://en.wikipedia.org/wiki/Transport_layer#Protocols)                      |
|                                 |             |                   |            | state     | [e.g. for tcp](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Protocol_operation) |

#### `system.process.`

**Description:** System level aggregate process metrics. For metrics at the
individual process level, see [process metrics](process-metrics.md).
| Name                 | Units     | Instrument Type | Value Type | Label Key | Label Values                                                                                   |
| -------------------- | --------- | --------------- | ---------- | --------- | ---------------------------------------------------------------------------------------------- |
| system.process.count | processes | SumObserver     | Int64      | status    | running, sleeping, [etc.](https://man7.org/linux/man-pages/man1/ps.1.html#PROCESS_STATE_CODES) |

#### OS Specific System Metrics - `system.{os}.`

Instrument names for system level metrics that have different and conflicting
meaning across multiple OSes should be prefixed with `system.{os}.` and
follow the hierarchies listed above for different entities like CPU, memory,
and network. For example, an instrument for measuring the load average on
Linux could be named `system.linux.cpu.load`, reusing the `cpu` name proposed
above.
