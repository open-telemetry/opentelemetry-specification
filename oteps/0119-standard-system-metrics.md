# Standard names for system/runtime metric instruments

This OTEP proposes a set of standard names, labels, and semantic conventions for common system/runtime metric instruments in OpenTelemetry. The instrument names proposed here are common across the supported operating systems and runtime environments. Also included are general semantic conventions for system/runtime metrics including those not specific to a particular OS or runtime.

This OTEP is largely based on the existing implementation in the OpenTelemetry Collector's [Host Metrics Receiver](https://github.com/open-telemetry/opentelemetry-collector/tree/1ad767e62f3dff6f62f32c7360b6fefe0fbf32ff/receiver/hostmetricsreceiver). The proposed names aim to make system/runtime metrics unambiguous and easily discoverable. See [OTEP #108](https://github.com/open-telemetry/oteps/pull/108/files) for additional motivation.

## Trade-offs and mitigations

When naming a metric instrument, there is a trade off between discoverability and ambiguity. For example, a metric called `system.cpu.load_average` is very discoverable, but the meaning of this metric is ambiguous. [Load average](https://en.wikipedia.org/wiki/Load_(computing)) is well defined on UNIX, but is not a standard metric on Windows. While discoverability is important, names must be unambiguous.

## Prior art

There are already a few implementations of system and/or runtime metric collection in OpenTelemetry:

- **[OTEP #108](https://github.com/open-telemetry/oteps/pull/108/files)**
  * Provides high level guidelines around naming metric instruments.
  * Came out of a [prior proposal](https://docs.google.com/spreadsheets/d/1WlStcUe2eQoN1y_UF7TOd6Sw7aV_U0lFcLk5kBNxPsY/edit#gid=0) for system metrics?
- **Collector**
  * [Host Metrics Receiver](https://github.com/open-telemetry/opentelemetry-collector/tree/1ad767e62f3dff6f62f32c7360b6fefe0fbf32ff/receiver/hostmetricsreceiver) generates metrics about the host system when run as an agent.
  * Currently is the most comprehensive implementation.
  * Collects system metrics for CPU, memory, swap, disks, filesystems, network, and load.
  * There are plans to collect process metrics for CPU, memory, and disk I/O.
  * Makes good use of labels rather than defining individual metrics.
  * [Overview of collected metrics](https://docs.google.com/spreadsheets/d/11qSmzD9e7PnzaJPYRFdkkKbjTLrAKmvyQpjBjpJsR2s/edit).

- **Go**
  * Go [has instrumentation](https://github.com/open-telemetry/opentelemetry-go-contrib/tree/main/instrumentation/runtime) to collect runtime metrics for GC, heap use, and goroutines.
  * This package does not export metrics with labels, instead exporting individual metrics.
  * [Overview of collected metrics](https://docs.google.com/spreadsheets/d/1r50cC9ass0A8SZIg2ZpLdvZf6HmQJsUSXFOu-rl4yaY/edit#gid=0).
- **Python**
  * Python [has instrumentation](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-system-metrics) to collect some system and runtime metrics.
  * Collects system CPU, memory, and network metrics.
  * Collects runtime CPU, memory, and GC metrics.
  * Makes use of labels, similar to the Collector.
  * [Overview of collected metrics](https://docs.google.com/spreadsheets/d/1r50cC9ass0A8SZIg2ZpLdvZf6HmQJsUSXFOu-rl4yaY/edit#gid=0).

## Semantic Conventions

The following semantic conventions aim to keep naming consistent. Not all possible metrics are covered by these conventions, but they provide guidelines for most of the cases in this proposal:

- **usage** - an instrument that measures an amount used out of a known total amount should be called `entity.usage`. For example, `system.filesystem.usage` for the amount of disk spaced used. A measure of the amount of an unlimited resource consumed is differentiated from **usage**. This may be time, data, etc.
- **utilization** - an instrument that measures a *value ratio* of usage (like percent, but in the range `[0, 1]`) should be called `entity.utilization`. For example, `system.memory.utilization` for the ratio of memory in use.
- **time** - an instrument that measures passage of time should be called `entity.time`. For example, `system.cpu.time` with varying values of label `state` for idle, user, etc.
- **io** - an instrument that measures bidirectional data flow should be called `entity.io` and have labels for direction. For example, `system.network.io`.
- Other instruments that do not fit the above descriptions may be named more freely. For example, `system.swap.page_faults` and `system.network.packets`. Units do not need to be specified in the names since they are included during instrument creation, but can be added if there is ambiguity.

## Internal details

The following standard metric instruments should be used in libraries instrumenting system/runtime metrics (here is a [spreadsheet](https://docs.google.com/spreadsheets/d/1r50cC9ass0A8SZIg2ZpLdvZf6HmQJsUSXFOu-rl4yaY/edit#gid=973941697) of the tables below).

In the tables below, units of `1` refer to a ratio value that is always in the range `[0, 1]`. Instruments that measure an integer count of something use semantic units like `packets`, `errors`, `faults`, etc.

### Standard System Metrics - `system.`

---

#### `system.cpu.`

**Description:** System level processor metrics.

|Name                  |Units  |Instrument Type  |Value Type|Label Key|Label Values                       |
|----------------------|-------|-----------------|----------|---------|-----------------------------------|
|system.cpu.time       |seconds|SumObserver      |Double    |state    |idle, user, system, interrupt, etc.|
|                      |       |                 |          |cpu      |1 - #cores                         |
|system.cpu.utilization|1      |UpDownSumObserver|Double    |state    |idle, user, system, interrupt, etc.|
|                      |       |                 |          |cpu      |1 - #cores                         |

#### `system.memory.`

**Description:** System level memory metrics.

|Name                     |Units|Instrument Type  |Value Type|Label Key|Label Values            |
|-------------------------|-----|-----------------|----------|---------|------------------------|
|system.memory.usage      |bytes|UpDownSumObserver|Int64     |state    |used, free, cached, etc.|
|system.memory.utilization|1    |UpDownSumObserver|Double    |state    |used, free, cached, etc.|

#### `system.swap.`

**Description:** System level swap/paging metrics.

|Name                        |Units     |Instrument Type  |Value Type|Label Key|Label Values|
|----------------------------|----------|-----------------|----------|---------|------------|
|system.swap.usage           |pages     |UpDownSumObserver|Int64     |state    |used, free  |
|system.swap.utilization     |1         |UpDownSumObserver|Double    |state    |used, free  |
|system.swap.page\_faults    |faults    |SumObserver      |Int64     |type     |major, minor|
|system.swap.page\_operations|operations|SumObserver      |Int64     |type     |major, minor|
|                            |          |                 |          |direction|in, out     |

#### `system.disk.`

**Description:** System level disk performance metrics.

|Name                        |Units     |Instrument Type|Value Type|Label Key|Label Values|
|----------------------------|----------|---------------|----------|---------|------------|
|system.disk.io<!--notlink-->|bytes     |SumObserver    |Int64     |device   |(identifier)|
|                            |          |               |          |direction|read, write |
|system.disk.operations      |operations|SumObserver    |Int64     |device   |(identifier)|
|                            |          |               |          |direction|read, write |
|system.disk.time            |seconds   |SumObserver    |Double    |device   |(identifier)|
|                            |          |               |          |direction|read, write |
|system.disk.merged          |1         |SumObserver    |Int64     |device   |(identifier)|
|                            |          |               |          |direction|read, write |

#### `system.filesystem.`

**Description:** System level filesystem metrics.

|Name                         |Units|Instrument Type  |Value Type|Label Key|Label Values        |
|-----------------------------|-----|-----------------|----------|---------|--------------------|
|system.filesystem.usage      |bytes|UpDownSumObserver|Int64     |device   |(identifier)        |
|                             |     |                 |          |state    |used, free, reserved|
|system.filesystem.utilization|1    |UpDownSumObserver|Double    |device   |(identifier)        |
|                             |     |                 |          |state    |used, free, reserved|

#### `system.network.`

**Description:** System level network metrics.

|Name                           |Units      |Instrument Type  |Value Type|Label Key|Label Values                                                                                  |
|-------------------------------|-----------|-----------------|----------|---------|----------------------------------------------------------------------------------------------|
|system.network.dropped\_packets|packets    |SumObserver      |Int64     |device   |(identifier)                                                                                  |
|                               |           |                 |          |direction|transmit, receive                                                                             |
|system.network.packets         |packets    |SumObserver      |Int64     |device   |(identifier)                                                                                  |
|                               |           |                 |          |direction|transmit, receive                                                                             |
|system.network.errors          |errors     |SumObserver      |Int64     |device   |(identifier)                                                                                  |
|                               |           |                 |          |direction|transmit, receive                                                                             |
|system<!--notlink-->.network.io|bytes      |SumObserver      |Int64     |device   |(identifier)                                                                                  |
|                               |           |                 |          |direction|transmit, receive                                                                             |
|system.network.connections     |connections|UpDownSumObserver|Int64     |device   |(identifier)                                                                                  |
|                               |           |                 |          |protocol |tcp, udp, [others](https://en.wikipedia.org/wiki/Transport_layer#Protocols)                   |
|                               |           |                 |          |state    |[e.g. for tcp](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Protocol_operation)|

#### OS Specific System Metrics - `system.{os}.`

Instrument names for system level metrics specific to a certain operating system should be prefixed with `system.{os}.` and follow the hierarchies listed above for different entities like CPU, memory, and network. For example, an instrument for counting the number of Linux merged disk operations (see [here](https://unix.stackexchange.com/questions/462704/iostat-what-is-exactly-the-concept-of-merge) and [here](https://man7.org/linux/man-pages/man1/iostat.1.html)) could be named `system.linux.disk.merged_operations`, reusing the `disk` name proposed above.

### Standard Runtime Metrics - `runtime.`

---

Runtime environments vary widely in their terminology, implementation, and relative values for a given metric. For example, Go and Python are both garbage collected languages, but comparing heap usage between the two runtimes directly is not meaningful. For this reason, this OTEP does not propose any standard top-level runtime metric instruments. See [OTEP #108](https://github.com/open-telemetry/oteps/pull/108/files) for additional discussion.

#### Runtime Specific Metrics - `runtime.{environment}.`

Runtime level metrics specific to a certain runtime environment should be prefixed with `runtime.{environment}.` and follow the semantic conventions outlined in [Semantic Conventions](#semantic-conventions). For example, Go runtime metrics use `runtime.go.` as a prefix.

Some programming languages have multiple runtime environments that vary significantly in their implementation, for example [Python has many implementations](https://wiki.python.org/moin/PythonImplementations). For these languages, consider using specific `environment` prefixes to avoid ambiguity, like `runtime.cpython.` and `runtime.pypy.`.

## Open questions

- Should the individual runtimes have their specific naming conventions in the spec?
- Is it ok to include instruments specific to an OS (or OS family) under a top-level prefix, as long as they are unambiguous? For example, naming inode related instruments, which of the below is preferred?
  1. Top level: `system.filesystem.inodes.*`
  2. UNIX family level: `system.unix.filesystem.inodes.*`
  3. One for each UNIX OS: `system.linux.filesystem.inodes.*`, `system.freebsd.filesystem.inodes.*`, `system.netbsd.filesystem.inodes.*`, etc.
