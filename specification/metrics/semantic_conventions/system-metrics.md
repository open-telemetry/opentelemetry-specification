# Semantic Conventions for System Metrics

This document describes instruments and labels for common system level
metrics in OpenTelemetry. Also included are general semantic conventions for
system, process, and runtime metrics, which should be considered when
creating instruments not explicitly defined in the specification.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Semantic Conventions](#semantic-conventions)
  * [Instrument Naming](#instrument-naming)
  * [Units](#units)
- [Metric Instruments](#metric-instruments)
  * [Standard System Metrics - `system.`](#standard-system-metrics---system)
    + [`system.cpu.` - Processor metrics](#systemcpu---processor-metrics)
    + [`system.memory.` - Memory metrics](#systemmemory---memory-metrics)
    + [`system.swap.` - Swap/paging metrics](#systemswap---swappaging-metrics)
    + [`system.disk.` - Disk controller metrics](#systemdisk---disk-controller-metrics)
    + [`system.filesystem.` - Filesystem metrics](#systemfilesystem---filesystem-metrics)
    + [`system.network.` - Network metrics](#systemnetwork---network-metrics)
    + [`system.process.` - Aggregate system process metrics](#systemprocess---aggregate-system-process-metrics)
    + [`system.{os}.` - OS Specific System Metrics](#systemos---os-specific-system-metrics)

<!-- tocstop -->

## Semantic Conventions

The following semantic conventions aim to keep naming consistent. They
provide guidelines for most of the cases in this specification and should be
followed for other instruments not explicitly defined in this document.

### Instrument Naming

- **limit** - an instrument that measures the constant, known total amount of
something should be called `entity.limit`. For example, `system.memory.limit`
for the total amount of memory on a system.

- **usage** - an instrument that measures an amount used out of a known total
(**limit**) amount should be called `entity.usage`. For example,
`system.memory.usage` with label `state = used | cached | free | ...` for the
amount of memory in a each state. In many cases, the sum of **usage** over
all label values is equal to the **limit**.

  A measure of the amount of an unlimited resource consumed is differentiated
  from **usage**.

- **utilization** - an instrument that measures the *fraction* of **usage**
out of its **limit** should be called `entity.utilization`. For example,
`system.memory.utilization` for the fraction of memory in use. Utilization
values are in the range `[0, 1]`.

- **time** - an instrument that measures passage of time should be called
`entity.time`. For example, `system.cpu.time` with label `state = idle | user
| system | ...`. **time** measurements are not necessarily wall time and can be less than
  or greater than the real wall time between measurements.

  **time** instruments are a special case of **usage** metrics, where the
  **limit** can usually be calculated as the sum of **time** over all label
  values. **utilization** can also be calculated and useful, for example
  `system.cpu.utilization`.

- **io** - an instrument that measures bidirectional data flow should be
called `entity.io` and have labels for direction. For example,
`system.network.io`.

- Other instruments that do not fit the above descriptions may be named more
freely. For example, `system.swap.page_faults` and `system.network.packets`.
Units do not need to be specified in the names since they are included during
instrument creation, but can be added if there is ambiguity.

### Units

Units should follow the [UCUM](http://unitsofmeasure.org/ucum.html) (need
more clarification in
[#705](https://github.com/open-telemetry/opentelemetry-specification/issues/705)).

- Instruments for **utilization** metrics (that measure the fraction out of a total)
SHOULD use units of `1`.
- Instruments that measure an integer count of something have
["non-units"](https://ucum.org/ucum.html#section-Examples-for-some-Non-Units.)
and SHOULD use [annotations](https://ucum.org/ucum.html#para-curly) with curly
braces. For example `{packets}`, `{errors}`, `{faults}`, etc.

## Metric Instruments

### Standard System Metrics - `system.`

#### `system.cpu.` - Processor metrics

**Description:** System level processor metrics.

| Name                   | Description | Units | Instrument Type | Value Type | Label Key | Label Values                        |
| ---------------------- | ----------- | ----- | --------------- | ---------- | --------- | ----------------------------------- |
| system.cpu.time        |             | s     | SumObserver     | Double     | state     | idle, user, system, interrupt, etc. |
|                        |             |       |                 |            | cpu       | CPU number (0..n)                   |
| system.cpu.utilization |             | 1     | ValueObserver   | Double     | state     | idle, user, system, interrupt, etc. |
|                        |             |       |                 |            | cpu       | CPU number (0..n)                   |

#### `system.memory.` - Memory metrics

**Description:** System level memory metrics. This does not include [paging/swap
memory](#systemswap---swappaging-metrics).

| Name                      | Description | Units | Instrument Type   | Value Type | Label Key | Label Values             |
| ------------------------- | ----------- | ----- | ----------------- | ---------- | --------- | ------------------------ |
| system.memory.usage       |             | By    | UpDownSumObserver | Int64      | state     | used, free, cached, etc. |
| system.memory.utilization |             | 1     | ValueObserver     | Double     | state     | used, free, cached, etc. |

#### `system.swap.` - Swap/paging metrics

**Description:** System level paging/swap memory metrics.
| Name                         | Description                         | Units        | Instrument Type   | Value Type | Label Key | Label Values |
| ---------------------------- | ----------------------------------- | ------------ | ----------------- | ---------- | --------- | ------------ |
| system.swap.usage            | Unix swap or windows pagefile usage | By           | UpDownSumObserver | Int64      | state     | used, free   |
| system.swap.utilization      |                                     | 1            | ValueObserver     | Double     | state     | used, free   |
| system.swap.page\_faults     |                                     | {faults}     | SumObserver       | Int64      | type      | major, minor |
| system.swap.page\_operations |                                     | {operations} | SumObserver       | Int64      | type      | major, minor |
|                              |                                     |              |                   |            | direction | in, out      |

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
| Name                          | Description | Units | Instrument Type   | Value Type | Label Key | Label Values         |
| ----------------------------- | ----------- | ----- | ----------------- | ---------- | --------- | -------------------- |
| system.filesystem.usage       |             | By    | UpDownSumObserver | Int64      | device    | (identifier)         |
|                               |             |       |                   |            | state     | used, free, reserved |
| system.filesystem.utilization |             | 1     | ValueObserver     | Double     | device    | (identifier)         |
|                               |             |       |                   |            | state     | used, free, reserved |

#### `system.network.` - Network metrics

**Description:** System level network metrics.
| Name                            | Description | Units         | Instrument Type   | Value Type | Label Key | Label Values                                                                                   |
| ------------------------------- | ----------- | ------------- | ----------------- | ---------- | --------- | ---------------------------------------------------------------------------------------------- |
| system.network.dropped\_packets |             | {packets}     | SumObserver       | Int64      | device    | (identifier)                                                                                   |
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
and network. This follows the rule of thumb that [aggregations over all the
dimensions of a given metric SHOULD be
meaningful.](https://prometheus.io/docs/practices/naming/#metric-names:~:text=As%20a%20rule%20of%20thumb%2C%20either,be%20meaningful%20(though%20not%20necessarily%20useful).)

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
