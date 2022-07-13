<!--- Hugo front matter used to generate the website version of this page:
linkTitle: API
--->

# Metrics API

**Status**: [Stable](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [MeterProvider](#meterprovider)
  * [MeterProvider operations](#meterprovider-operations)
    + [Get a Meter](#get-a-meter)
- [Meter](#meter)
  * [Meter operations](#meter-operations)
- [Instrument](#instrument)
  * [General characteristics](#general-characteristics)
    + [Instrument type conflict detection](#instrument-type-conflict-detection)
    + [Instrument namespace](#instrument-namespace)
    + [Instrument naming rule](#instrument-naming-rule)
    + [Instrument unit](#instrument-unit)
    + [Instrument description](#instrument-description)
    + [Synchronous and Asynchronous instruments](#synchronous-and-asynchronous-instruments)
    + [Synchronous Instrument API](#synchronous-instrument-api)
    + [Asynchronous Instrument API](#asynchronous-instrument-api)
  * [Counter](#counter)
    + [Counter creation](#counter-creation)
    + [Counter operations](#counter-operations)
      - [Add](#add)
  * [Asynchronous Counter](#asynchronous-counter)
    + [Asynchronous Counter creation](#asynchronous-counter-creation)
    + [Asynchronous Counter operations](#asynchronous-counter-operations)
  * [Histogram](#histogram)
    + [Histogram creation](#histogram-creation)
    + [Histogram operations](#histogram-operations)
      - [Record](#record)
  * [Asynchronous Gauge](#asynchronous-gauge)
    + [Asynchronous Gauge creation](#asynchronous-gauge-creation)
    + [Asynchronous Gauge operations](#asynchronous-gauge-operations)
  * [UpDownCounter](#updowncounter)
    + [UpDownCounter creation](#updowncounter-creation)
    + [UpDownCounter operations](#updowncounter-operations)
      - [Add](#add-1)
  * [Asynchronous UpDownCounter](#asynchronous-updowncounter)
    + [Asynchronous UpDownCounter creation](#asynchronous-updowncounter-creation)
    + [Asynchronous UpDownCounter operations](#asynchronous-updowncounter-operations)
- [Measurement](#measurement)
  * [Multiple-instrument callbacks](#multiple-instrument-callbacks)
- [Compatibility requirements](#compatibility-requirements)
- [Concurrency requirements](#concurrency-requirements)

<!-- tocstop -->

</details>

## Overview

The Metrics API consists of these main components:

* [MeterProvider](#meterprovider) is the entry point of the API. It provides
  access to `Meters`.
* [Meter](#meter) is the class responsible for creating `Instruments`.
* [Instrument](#instrument) is responsible for reporting
  [Measurements](#measurement).

Here is an example of the object hierarchy inside a process instrumented with
the metrics API:

```text
+-- MeterProvider(default)
    |
    +-- Meter(name='io.opentelemetry.runtime', version='1.0.0')
    |   |
    |   +-- Instrument<Asynchronous Gauge, int>(name='cpython.gc', attributes=['generation'], unit='kB')
    |   |
    |   +-- instruments...
    |
    +-- Meter(name='io.opentelemetry.contrib.mongodb.client', version='2.3.0')
        |
        +-- Instrument<Counter, int>(name='client.exception', attributes=['type'], unit='1')
        |
        +-- Instrument<Histogram, double>(name='client.duration', attributes=['net.peer.host', 'net.peer.port'], unit='ms')
        |
        +-- instruments...

+-- MeterProvider(custom)
    |
    +-- Meter(name='bank.payment', version='23.3.5')
        |
        +-- instruments...
```

## MeterProvider

`Meter`s can be accessed with a `MeterProvider`.

In implementations of the API, the `MeterProvider` is expected to be the
stateful object that holds any configuration.

Normally, the `MeterProvider` is expected to be accessed from a central place.
Thus, the API SHOULD provide a way to set/register and access a global default
`MeterProvider`.

Notwithstanding any global `MeterProvider`, some applications may want to or
have to use multiple `MeterProvider` instances, e.g. to have different
configuration for each, or because its easier with dependency injection
frameworks. Thus, implementations of `MeterProvider` SHOULD allow creating an
arbitrary number of `MeterProvider` instances.

### MeterProvider operations

The `MeterProvider` MUST provide the following functions:

* Get a `Meter`

#### Get a Meter

This API MUST accept the following parameters:

* `name` (required): This name SHOULD uniquely identify the [instrumentation
  scope](../glossary.md#instrumentation-scope), such as the
  [instrumentation library](../glossary.md#instrumentation-library) (e.g.
  `io.opentelemetry.contrib.mongodb`), package,
  module or class name. If an application or library has built-in OpenTelemetry
  instrumentation, both [Instrumented
  library](../glossary.md#instrumented-library) and [Instrumentation
  library](../glossary.md#instrumentation-library) may refer to the same
  library. In that scenario, the `name` denotes a module name or component name
  within that library or application. In case an invalid name (null or empty
  string) is specified, a working Meter implementation MUST be returned as a
  fallback rather than returning null or throwing an exception, its `name`
  property SHOULD keep the original invalid value, and a message reporting that
  the specified value is invalid SHOULD be logged. A library, implementing the
  OpenTelemetry API *may* also ignore this name and return a default instance
  for all calls, if it does not support "named" functionality (e.g. an
  implementation which is not even observability-related). A MeterProvider could
  also return a no-op Meter here if application owners configure the SDK to
  suppress telemetry produced by this library.
* `version` (optional): Specifies the version of the instrumentation scope if the scope
  has a version (e.g. a library version). Example value: `1.0.0`.
* [since 1.4.0] `schema_url` (optional): Specifies the Schema URL that should be
  recorded in the emitted telemetry.
* [since 1.13.0] `attributes` (optional): Specifies the instrumentation scope attributes
    to associate with emitted telemetry.

Meters are identified by all of these parameters.

Implementations MUST return different `Meter` instances when called repeatedly
with different values of parameters. Note that always returning a new `Meter` instance
is a valid implementation. The only exception to this rule is the no-op `Meter`:
implementations MAY return the same instance regardless of parameter values.

It is unspecified whether or under which conditions the same or different
`Meter` instances are returned from this function when the same
(name,version,schema_url,attributes) parameters are used.

The term *identical* applied to Meters describes instances where all identifying fields
are equal. The term *distinct* applied to Meters describes instances where at
least one identifying field has a different value.

Implementations MUST NOT require users to repeatedly obtain a `Meter` with
the same identity to pick up configuration changes. This can be
achieved either by allowing to work with an outdated configuration or by
ensuring that new configuration applies also to previously returned `Meter`s.

Note: This could, for example, be implemented by storing any mutable
configuration in the `MeterProvider` and having `Meter` implementation objects
have a reference to the `MeterProvider` from which they were obtained. If
configuration must be stored per-meter (such as disabling a certain meter), the
meter could, for example, do a look-up with its identity in a map
in the `MeterProvider`, or the `MeterProvider` could maintain a registry of all
returned `Meter`s and actively update their configuration if it changes.

The effect of associating a Schema URL with a `Meter` MUST be that the telemetry
emitted using the `Meter` will be associated with the Schema URL, provided that
the emitted data format is capable of representing such association.

## Meter

The meter is responsible for creating [Instruments](#instrument).

Note: `Meter` SHOULD NOT be responsible for the configuration. This should be
the responsibility of the `MeterProvider` instead.

### Meter operations

The `Meter` MUST provide functions to create new [Instruments](#instrument):

* [Create a new Counter](#counter-creation)
* [Create a new Asynchronous Counter](#asynchronous-counter-creation)
* [Create a new Histogram](#histogram-creation)
* [Create a new Asynchronous Gauge](#asynchronous-gauge-creation)
* [Create a new UpDownCounter](#updowncounter-creation)
* [Create a new Asynchronous UpDownCounter](#asynchronous-updowncounter-creation)

Also see the respective sections below for more information on instrument creation.

## Instrument

Instruments are used to report [Measurements](#measurement). Each Instrument
will have the following fields:

* The `name` of the Instrument
* The `kind` of the Instrument - whether it is a [Counter](#counter) or
  one of the other kinds, whether it is synchronous or asynchronous
* An optional `unit` of measure
* An optional `description`

Instruments are associated with the Meter during creation. Instruments
are identified by all of these fields.

Language-level features such as the distinction between integer and
floating point numbers SHOULD be considered as identifying.

### General characteristics

#### Instrument type conflict detection

When more than one Instrument of the same `name` is created for
identical Meters, denoted *duplicate instrument registration*, the
implementation MUST create a valid Instrument in every case.  Here,
"valid" means an instrument that is functional and can be expected to
export data, despite potentially creating a [semantic error in the
data
model](data-model.md#opentelemetry-protocol-data-model-producer-recommendations).

It is unspecified whether or under which conditions the same or
different Instrument instance will be returned as a result of
duplicate instrument registration.  The term *identical* applied to
Instruments describes instances where all identifying fields are
equal.  The term *distinct* applied to Instruments describes instances
where at least one field value is different.

When more than one distinct Instrument is registered with the same
`name` for identical Meters, the implementation SHOULD emit a warning
to the user informing them of duplicate registration conflict(s).
The warning helps to avoid the semantic error state described in the
[OpenTelemetry Metrics data
model](data-model.md#opentelemetry-protocol-data-model-producer-recommendations)
when more than one `Metric` is written for a given instrument `name`
and Meter identity by the same MeterProvider.

#### Instrument namespace

Distinct Meters MUST be treated as separate namespaces for the
purposes of detecting [duplicate instrument registration
conflicts](#instrument-type-conflict-detection).

#### Instrument naming rule

Instrument names MUST conform to the following syntax (described using the
[Augmented Backus-Naur Form](https://tools.ietf.org/html/rfc5234)):

```abnf
instrument-name = ALPHA 0*62 ("_" / "." / "-" / ALPHA / DIGIT)

ALPHA = %x41-5A / %x61-7A; A-Z / a-z
DIGIT = %x30-39 ; 0-9
```

* They are not null or empty strings.
* They are case-insensitive, ASCII strings.
* The first character must be an alphabetic character.
* Subsequent characters must belong to the alphanumeric characters, '_', '.',
  and '-'.
* They can have a maximum length of 63 characters.

#### Instrument unit

The `unit` is an optional string provided by the author of the Instrument. It
SHOULD be treated as an opaque string from the API and SDK (e.g. the SDK is not
expected to validate the unit of measurement, or perform the unit conversion).

* If the `unit` is not provided or the `unit` is null, the API and SDK MUST make
  sure that the behavior is the same as an empty `unit` string.
* It MUST be case-sensitive (e.g. `kb` and `kB` are different units), ASCII
  string.
* It can have a maximum length of 63 characters. The number 63 is chosen to
  allow the unit strings (including the `\0` terminator on certain language
  runtimes) to be stored and compared as fixed size array/struct when
  performance is critical.

#### Instrument description

The `description` is an optional free-form text provided by the author of the
instrument. It MUST be treated as an opaque string from the API and SDK.

* If the `description` is not provided or the `description` is null, the API and
  SDK MUST make sure that the behavior is the same as an empty `description`
  string.
* It MUST support [BMP (Unicode Plane
  0)](https://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane),
  which is basically only the first three bytes of UTF-8 (or `utf8mb3`).
  [OpenTelemetry API](../overview.md#api) authors MAY decide if they want to
  support more Unicode [Planes](https://en.wikipedia.org/wiki/Plane_(Unicode)).
* It MUST support at least 1023 characters. [OpenTelemetry
  API](../overview.md#api) authors MAY decide if they want to support more.

Instruments are categorized on whether they are synchronous or
asynchronous:

#### Synchronous and Asynchronous instruments

* Synchronous instruments (e.g. [Counter](#counter)) are meant to be invoked
  inline with application/business processing logic. For example, an HTTP client
  could use a Counter to record the number of bytes it has received.
  [Measurements](#measurement) recorded by synchronous instruments can be
  associated with the [Context](../context/README.md).

* Asynchronous instruments (e.g. [Asynchronous Gauge](#asynchronous-gauge)) give
  the user a way to register callback function, and the callback function will
  be invoked only on demand (see SDK [collection](sdk.md#collect) for reference). For example, a piece of embedded software
  could use an asynchronous gauge to collect the temperature from a sensor every
  15 seconds, which means the callback function will only be invoked every 15
  seconds. [Measurements](#measurement) recorded by asynchronous instruments
  cannot be associated with the [Context](../context/README.md).

Please note that the term *synchronous* and *asynchronous* have nothing to do
with the [asynchronous
pattern](https://en.wikipedia.org/wiki/Asynchronous_method_invocation).

#### Synchronous Instrument API

The API to construct synchronous instruments MUST accept the following parameters:

* The `name` of the Instrument, following the [instrument naming
  rule](#instrument-naming-rule).
* An optional `unit` of measure, following the [instrument unit
  rule](#instrument-unit).
* An optional `description`, following the [instrument description
  rule](#instrument-description).

#### Asynchronous Instrument API

Asynchronous instruments have associated `callback` functions which
are responsible for reporting [Measurement](#measurement)s. Callback
functions will be called only when the Meter is being observed.  The
order of callback execution is not specified.

The API to construct asynchronous instruments MUST accept the following parameters:

* The `name` of the Instrument, following the [instrument naming
  rule](#instrument-naming-rule).
* An optional `unit` of measure, following the [instrument unit
  rule](#instrument-unit).
* An optional `description`, following the [instrument description
  rule](#instrument-description).
* Zero or more `callback` functions, responsible for reporting
  [Measurement](#measurement) values of the created instrument.

The API MUST support creation of asynchronous instruments by passing
zero or more `callback` functions to be permanently registered to the
newly created instrument.

A Callback is the conceptual entity created each time a `callback`
function is registered through an OpenTelemetry API.

The API SHOULD support registration of `callback` functions associated with
asynchronous instruments after they are created.

Where the API supports registration of `callback` functions after
asynchronous instrumentation creation, the user MUST be able to undo
registration of the specific callback after its registration by some means.

Every currently registered Callback associated with a set of instruments MUST
be evaluated exactly once during collection prior to reading data for
that instrument set.

Callback functions MUST be documented as follows for the end user:

- Callback functions SHOULD be reentrant safe.  The SDK expects to evaluate
  callbacks for each MetricReader independently.
- Callback functions SHOULD NOT take an indefinite amount of time.
- Callback functions SHOULD NOT make duplicate observations (more than one
  `Measurement` with the same `attributes`) across all registered
  callbacks.

The resulting behavior when a callback violates any of these
RECOMMENDATIONS is explicitly not specified at the API level.

[OpenTelemetry API](../overview.md#api) authors MAY decide what is the idiomatic
approach for capturing measurements from callback functions. Here are some examples:

* Return a list (or tuple, generator, enumerator, etc.) of individual
  `Measurement` values.
* Pass an *Observable Result* as a formal parameter of the callback,
  where `result.Observe()` captures individual `Measurement` values.

Callbacks registered at the time of instrument creation MUST apply to
the single instruments which is under construction.

Callbacks registered after the time of instrument creation MAY be
associated with multiple instruments.

Idiomatic APIs for multiple-instrument Callbacks MUST distinguish the
instrument associated with each observed `Measurement` value.

Multiple-instrument Callbacks MUST be associated at the time of
registration with a declared set of asynchronous instruments from the
same `Meter` instance.  This requirement that Instruments be
declaratively associated with Callbacks allows an SDK to execute only
those Callbacks that are necessary to evaluate instruments that are in
use by a configured [View](sdk.md#view).

The API MUST treat observations from a single Callback as logically
taking place at a single instant, such that when recorded,
observations from a single callback MUST be reported with identical
timestamps.

The API SHOULD provide some way to pass `state` to the
callback. [OpenTelemetry API](../overview.md#api) authors MAY decide
what is the idiomatic approach (e.g.  it could be an additional
parameter to the callback function, or captured by the lambda closure,
or something else).

### Counter

`Counter` is a [synchronous Instrument](#synchronous-instrument-api) which supports
non-negative increments.

Example uses for `Counter`:

* count the number of bytes received
* count the number of requests completed
* count the number of accounts created
* count the number of checkpoints run
* count the number of HTTP 5xx errors

#### Counter creation

There MUST NOT be any API for creating a `Counter` other than with a
[`Meter`](#meter). This MAY be called `CreateCounter`. If strong type is
desired, [OpenTelemetry API](../overview.md#api) authors MAY decide the language
idiomatic name(s), for example `CreateUInt64Counter`, `CreateDoubleCounter`,
`CreateCounter<UInt64>`, `CreateCounter<double>`.

See the [general requirements for synchronous instruments](#synchronous-instrument-api).

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```python
# Python

exception_counter = meter.create_counter(name="exceptions", description="number of exceptions caught", value_type=int)
```

```csharp
// C#

var counterExceptions = meter.CreateCounter<UInt64>("exceptions", description="number of exceptions caught");

readonly struct PowerConsumption
{
    [HighCardinality]
    string customer;
};

var counterPowerUsed = meter.CreateCounter<double, PowerConsumption>("power_consumption", unit="kWh");
```

#### Counter operations

##### Add

Increment the Counter by a fixed amount.

This API SHOULD NOT return a value (it MAY return a dummy value if required by
certain programming languages or systems, for example `null`, `undefined`).

Required parameters:

* Optional [attributes](../common/README.md#attribute).
* The increment amount, which MUST be a non-negative numeric value.

The [OpenTelemetry API](../overview.md#api) authors MAY decide to allow flexible
[attributes](../common/README.md#attribute) to be passed in as arguments. If
the attribute names and types are provided during the [counter
creation](#counter-creation), the [OpenTelemetry API](../overview.md#api)
authors MAY allow attribute values to be passed in using a more efficient way
(e.g. strong typed struct allocated on the callstack, tuple). The API MUST allow
callers to provide flexible attributes at invocation time rather than having to
register all the possible attribute names during the instrument creation. Here
are some examples that [OpenTelemetry API](../overview.md#api) authors might
consider:

```python
# Python

exception_counter.add(1, {"exception_type": "IOError", "handled_by_user": True})
exception_counter.add(1, exception_type="IOError", handled_by_user=True)
```

```csharp
// C#

counterExceptions.Add(1, ("exception_type", "FileLoadException"), ("handled_by_user", true));

counterPowerUsed.Add(13.5, new PowerConsumption { customer = "Tom" });
counterPowerUsed.Add(200, new PowerConsumption { customer = "Jerry" }, ("is_green_energy", true));
```

### Asynchronous Counter

Asynchronous Counter is an [asynchronous Instrument](#asynchronous-instrument-api)
which reports [monotonically](https://wikipedia.org/wiki/Monotonic_function)
increasing value(s) when the instrument is being observed.

Example uses for Asynchronous Counter:

* [CPU time](https://wikipedia.org/wiki/CPU_time), which could be reported for
  each thread, each process or the entire system. For example "the CPU time for
  process A running in user mode, measured in seconds".
* The number of [page faults](https://wikipedia.org/wiki/Page_fault) for each
  process.

#### Asynchronous Counter creation

There MUST NOT be any API for creating an Asynchronous Counter other than with a
[`Meter`](#meter). This MAY be called `CreateObservableCounter`. If strong type
is desired, [OpenTelemetry API](../overview.md#api) authors MAY decide the
language idiomatic name(s), for example `CreateUInt64ObservableCounter`,
`CreateDoubleObservableCounter`, `CreateObservableCounter<UInt64>`,
`CreateObservableCounter<double>`.

It is highly recommended that implementations use the name `ObservableCounter`
(or any language idiomatic variation, e.g. `observable_counter`) unless there is
a strong reason not to do so. Please note that the name has nothing to do with
[asynchronous
pattern](https://en.wikipedia.org/wiki/Asynchronous_method_invocation) and
[observer pattern](https://en.wikipedia.org/wiki/Observer_pattern).

See the [general requirements for asynchronous instruments](#asynchronous-instrument-api).

Note: Unlike [Counter.Add()](#add) which takes the increment/delta value, the
callback function reports the absolute value of the counter. To determine the
reported rate the counter is changing, the difference between successive
measurements is used.

[OpenTelemetry API](../overview.md#api) authors MAY decide what is the idiomatic
approach. Here are some examples:

* Return a list (or tuple, generator, enumerator, etc.) of `Measurement`s.
* Use an observable result argument to allow individual `Measurement`s to be
  reported.

User code is recommended not to provide more than one `Measurement` with the
same `attributes` in a single callback. If it happens, [OpenTelemetry
SDK](../overview.md#sdk) authors MAY decide how to handle it in the
[SDK](./README.md#sdk). For example, during the callback invocation if two
measurements `value=1, attributes={pid:4, bitness:64}` and `value=2,
attributes={pid:4, bitness:64}` are reported, [OpenTelemetry
SDK](../overview.md#sdk) authors MAY decide to simply let them pass through (so
the downstream consumer can handle duplication), drop the entire data, pick the
last one, or something else. The API MUST treat observations from a single
callback as logically taking place at a single instant, such that when recorded,
observations from a single callback MUST be reported with identical timestamps.

The API SHOULD provide some way to pass `state` to the callback. [OpenTelemetry
API](../overview.md#api) authors MAY decide what is the idiomatic approach (e.g.
it could be an additional parameter to the callback function, or captured by the
lambda closure, or something else).

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```python
# Python

def pf_callback():
    # Note: in the real world these would be retrieved from the operating system
    return (
        (8,        ("pid", 0),   ("bitness", 64)),
        (37741921, ("pid", 4),   ("bitness", 64)),
        (10465,    ("pid", 880), ("bitness", 32)),
    )

meter.create_observable_counter(name="PF", description="process page faults", pf_callback)
```

```python
# Python

def pf_callback(result):
    # Note: in the real world these would be retrieved from the operating system
    result.Observe(8,        ("pid", 0),   ("bitness", 64))
    result.Observe(37741921, ("pid", 4),   ("bitness", 64))
    result.Observe(10465,    ("pid", 880), ("bitness", 32))

meter.create_observable_counter(name="PF", description="process page faults", pf_callback)
```

```csharp
// C#

// A simple scenario where only one value is reported

interface IAtomicClock
{
    UInt64 GetCaesiumOscillates();
}

IAtomicClock clock = AtomicClock.Connect();

meter.CreateObservableCounter<UInt64>("caesium_oscillates", () => clock.GetCaesiumOscillates());
```

#### Asynchronous Counter operations

Asynchronous Counter uses an idiomatic interface for reporting
measurements through a `callback`, which is registered during
[Asynchronous Counter creation](#asynchronous-counter-creation).

For callback functions registered after an asynchronous instrument is
created, the API is required to support a mechanism for
unregistration.  For example, the object returned from `register_callback`
can support an `unregister()` method directly.

```python
# Python
class Device:
    """A device with one counter"""

    def __init__(self, meter, x):
        self.x = x
        counter = meter.create_observable_counter(name="usage", description="count of items used")
        self.cb = counter.register_callback(self.counter_callback)

    def counter_callback(self, result):
        result.Observe(self.read_counter(), {'x', self.x})

    def read_counter(self):
        return 100  # ...

    def stop(self):
        self.cb.unregister()
```

### Histogram

`Histogram` is a [synchronous Instrument](#synchronous-instrument-api) which can be
used to report arbitrary values that are likely to be statistically meaningful.
It is intended for statistics such as histograms, summaries, and percentile.

Example uses for `Histogram`:

* the request duration
* the size of the response payload

#### Histogram creation

There MUST NOT be any API for creating a `Histogram` other than with a
[`Meter`](#meter). This MAY be called `CreateHistogram`. If strong type is
desired, [OpenTelemetry API](../overview.md#api) authors MAY decide the language
idiomatic name(s), for example `CreateUInt64Histogram`, `CreateDoubleHistogram`,
`CreateHistogram<UInt64>`, `CreateHistogram<double>`.

See the [general requirements for synchronous instruments](#synchronous-instrument-api).

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```python
# Python

http_server_duration = meter.create_histogram(
    name="http.server.duration",
    description="measures the duration of the inbound HTTP request",
    unit="milliseconds",
    value_type=float)
```

```csharp
// C#

var httpServerDuration = meter.CreateHistogram<double>(
    "http.server.duration",
    description: "measures the duration of the inbound HTTP request",
    unit: "milliseconds"
    );
```

#### Histogram operations

##### Record

Updates the statistics with the specified amount.

This API SHOULD NOT return a value (it MAY return a dummy value if required by
certain programming languages or systems, for example `null`, `undefined`).

Parameters:

* The amount of the `Measurement`, which MUST be a non-negative numeric value.
* Optional [attributes](../common/README.md#attribute).

[OpenTelemetry API](../overview.md#api) authors MAY decide to allow flexible
[attributes](../common/README.md#attribute) to be passed in as individual
arguments. [OpenTelemetry API](../overview.md#api) authors MAY allow attribute
values to be passed in using a more efficient way (e.g. strong typed struct
allocated on the callstack, tuple). Here are some examples that [OpenTelemetry
API](../overview.md#api) authors might consider:

```python
# Python

http_server_duration.Record(50, {"http.method": "POST", "http.scheme": "https"})
http_server_duration.Record(100, http_method="GET", http_scheme="http"})
```

```csharp
// C#

httpServerDuration.Record(50, ("http.method", "POST"), ("http.scheme", "https"));
httpServerDuration.Record(100, new HttpRequestAttributes { method = "GET", scheme = "http" });
```

### Asynchronous Gauge

Asynchronous Gauge is an [asynchronous Instrument](#asynchronous-instrument-api)
which reports non-additive value(s) (e.g. the room temperature - it makes no
sense to report the temperature value from multiple rooms and sum them up) when
the instrument is being observed.

Note: if the values are additive (e.g. the process heap size - it makes sense
to report the heap size from multiple processes and sum them up, so we get the
total heap usage), use [Asynchronous Counter](#asynchronous-counter) or
[Asynchronous UpDownCounter](#asynchronous-updowncounter).

Example uses for Asynchronous Gauge:

* the current room temperature
* the CPU fan speed

#### Asynchronous Gauge creation

There MUST NOT be any API for creating an Asynchronous Gauge other than with a
[`Meter`](#meter). This MAY be called `CreateObservableGauge`. If strong type is
desired, [OpenTelemetry API](../overview.md#api) authors MAY decide the language
idiomatic name(s), for example `CreateUInt64ObservableGauge`,
`CreateDoubleObservableGauge`, `CreateObservableGauge<UInt64>`,
`CreateObservableGauge<double>`.

It is highly recommended that implementations use the name `ObservableGauge`
(or any language idiomatic variation, e.g. `observable_gauge`) unless there is
a strong reason not to do so. Please note that the name has nothing to do with
[asynchronous
pattern](https://en.wikipedia.org/wiki/Asynchronous_method_invocation) and
[observer pattern](https://en.wikipedia.org/wiki/Observer_pattern).

See the [general requirements for asynchronous instruments](#asynchronous-instrument-api).

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```python
# Python

def cpu_frequency_callback():
    # Note: in the real world these would be retrieved from the operating system
    return (
        (3.38, ("cpu", 0), ("core", 0)),
        (3.51, ("cpu", 0), ("core", 1)),
        (0.57, ("cpu", 1), ("core", 0)),
        (0.56, ("cpu", 1), ("core", 1)),
    )

meter.create_observable_gauge(
    name="cpu.frequency",
    description="the real-time CPU clock speed",
    callback=cpu_frequency_callback,
    unit="GHz",
    value_type=float)
```

```python
# Python

def cpu_frequency_callback(result):
    # Note: in the real world these would be retrieved from the operating system
    result.Observe(3.38, ("cpu", 0), ("core", 0))
    result.Observe(3.51, ("cpu", 0), ("core", 1))
    result.Observe(0.57, ("cpu", 1), ("core", 0))
    result.Observe(0.56, ("cpu", 1), ("core", 1))

meter.create_observable_gauge(
    name="cpu.frequency",
    description="the real-time CPU clock speed",
    callback=cpu_frequency_callback,
    unit="GHz",
    value_type=float)
```

```csharp
// C#

// A simple scenario where only one value is reported

meter.CreateObservableGauge<double>("temperature", () => sensor.GetTemperature());
```

#### Asynchronous Gauge operations

Asynchronous Gauge uses an idiomatic interface for reporting
measurements through a `callback`, which is registered during
[Asynchronous Gauge creation](#asynchronous-gauge-creation).

For callback functions registered after an asynchronous instrument is
created, the API is required to support a mechanism for
unregistration.  For example, the object returned from `register_callback`
can support an `unregister()` method directly.

```python
# Python
class Device:
    """A device with one gauge"""

    def __init__(self, meter, x):
        self.x = x
        gauge = meter.create_observable_gauge(name="pressure", description="force/area")
        self.cb = gauge.register_callback(self.gauge_callback)

    def gauge_callback(self, result):
        result.Observe(self.read_gauge(), {'x', self.x})

    def read_gauge(self):
        return 100  # ...

    def stop(self):
        self.cb.unregister()
```

### UpDownCounter

`UpDownCounter` is a [synchronous Instrument](#synchronous-instrument-api) which
supports increments and decrements.

Note: if the value is
[monotonically](https://wikipedia.org/wiki/Monotonic_function) increasing, use
[Counter](#counter) instead.

Example uses for `UpDownCounter`:

* the number of active requests
* the number of items in a queue

An `UpDownCounter` is intended for scenarios where the absolute values are not
pre-calculated, or fetching the "current value" requires extra effort. If the
pre-calculated value is already available or fetching the snapshot of the
"current value" is straightforward, use [Asynchronous
UpDownCounter](#asynchronous-updowncounter) instead.

UpDownCounter supports counting **the size of a collection** incrementally, e.g.
reporting the number of items in a concurrent bag by the "color" and "material"
properties as they are added and removed.

| Color    | Material     | Count |
| -------- | -----------  | ----- |
| Red      | Aluminum     | 1     |
| Red      | Steel        | 2     |
| Blue     | Aluminum     | 0     |
| Blue     | Steel        | 5     |
| Yellow   | Aluminum     | 0     |
| Yellow   | Steel        | 3     |

```python
# Python

items_counter = meter.create_up_down_counter(
    name="store.inventory",
    description="the number of the items available")

def restock_item(color, material):
    inventory.add_item(color=color, material=material)
    items_counter.add(1, {"color": color, "material": material})
    return true

def sell_item(color, material):
    succeeded = inventory.take_item(color=color, material=material)
    if succeeded:
        items_counter.add(-1, {"color": color, "material": material})
    return succeeded
```

#### UpDownCounter creation

There MUST NOT be any API for creating an `UpDownCounter` other than with a
[`Meter`](#meter). This MAY be called `CreateUpDownCounter`. If strong type is
desired, [OpenTelemetry API](../overview.md#api) authors MAY decide the language
idiomatic name(s), for example `CreateInt64UpDownCounter`,
`CreateDoubleUpDownCounter`, `CreateUpDownCounter<Int64>`,
`CreateUpDownCounter<double>`.

See the [general requirements for synchronous instruments](#synchronous-instrument-api).

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```python
# Python

customers_in_store = meter.create_up_down_counter(
    name="grocery.customers",
    description="measures the current customers in the grocery store",
    value_type=int)
```

```csharp
// C#

var customersInStore = meter.CreateUpDownCounter<int>(
    "grocery.customers",
    description: "measures the current customers in the grocery store",
    );
```

#### UpDownCounter operations

##### Add

Increment or decrement the UpDownCounter by a fixed amount.

This API SHOULD NOT return a value (it MAY return a dummy value if required by
certain programming languages or systems, for example `null`, `undefined`).

Parameters:

* The amount to be added, can be positive, negative or zero.
* Optional [attributes](../common/README.md#attribute).

[OpenTelemetry API](../overview.md#api) authors MAY decide to allow flexible
[attributes](../common/README.md#attribute) to be passed in as individual
arguments. [OpenTelemetry API](../overview.md#api) authors MAY allow attribute
values to be passed in using a more efficient way (e.g. strong typed struct
allocated on the callstack, tuple). Here are some examples that [OpenTelemetry
API](../overview.md#api) authors might consider:

```python
# Python
customers_in_store.add(1, {"account.type": "commercial"})
customers_in_store.add(-1, account_type="residential")
```

```csharp
// C#
customersInStore.Add(1, ("account.type", "commercial"));
customersInStore.Add(-1, new Account { Type = "residential" });
```

### Asynchronous UpDownCounter

Asynchronous UpDownCounter is an [asynchronous
Instrument](#asynchronous-instrument-api) which reports additive value(s) (e.g. the
process heap size - it makes sense to report the heap size from multiple
processes and sum them up, so we get the total heap usage) when the instrument
is being observed.

Note: if the value is
[monotonically](https://wikipedia.org/wiki/Monotonic_function) increasing, use
[Asynchronous Counter](#asynchronous-counter) instead; if the value is
non-additive, use [Asynchronous Gauge](#asynchronous-gauge) instead.

Example uses for Asynchronous UpDownCounter:

* the process heap size
* the approximate number of items in a lock-free circular buffer

#### Asynchronous UpDownCounter creation

There MUST NOT be any API for creating an Asynchronous UpDownCounter other than
with a [`Meter`](#meter). This MAY be called `CreateObservableUpDownCounter`. If
strong type is desired, [OpenTelemetry API](../overview.md#api) authors MAY
decide the language idiomatic name(s), for example
`CreateUInt64ObservableUpDownCounter`, `CreateDoubleObservableUpDownCounter`,
`CreateObservableUpDownCounter<UInt64>`,
`CreateObservableUpDownCounter<double>`.

It is highly recommended that implementations use the name
`ObservableUpDownCounter` (or any language idiomatic variation, e.g.
`observable_updowncounter`) unless there is a strong reason not to do so. Please
note that the name has nothing to do with [asynchronous
pattern](https://en.wikipedia.org/wiki/Asynchronous_method_invocation) and
[observer pattern](https://en.wikipedia.org/wiki/Observer_pattern).

See the [general requirements for asynchronous instruments](#asynchronous-instrument-api).

Note: Unlike [UpDownCounter.Add()](#add-1) which takes the increment/delta value,
the callback function reports the absolute value of the Asynchronous
UpDownCounter. To determine the reported rate the Asynchronous UpDownCounter is
changing, the difference between successive measurements is used.

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```python
# Python

def ws_callback():
    # Note: in the real world these would be retrieved from the operating system
    return (
        (8,      ("pid", 0),   ("bitness", 64)),
        (20,     ("pid", 4),   ("bitness", 64)),
        (126032, ("pid", 880), ("bitness", 32)),
    )

meter.create_observable_updowncounter(
    name="process.workingset",
    description="process working set",
    callback=ws_callback,
    unit="kB",
    value_type=int)
```

```python
# Python

def ws_callback(result):
    # Note: in the real world these would be retrieved from the operating system
    result.Observe(8,      ("pid", 0),   ("bitness", 64))
    result.Observe(20,     ("pid", 4),   ("bitness", 64))
    result.Observe(126032, ("pid", 880), ("bitness", 32))

meter.create_observable_updowncounter(
    name="process.workingset",
    description="process working set",
    callback=ws_callback,
    unit="kB",
    value_type=int)
```

```csharp
// C#

// A simple scenario where only one value is reported

meter.CreateObservableUpDownCounter<UInt64>("memory.physical.free", () => WMI.Query("FreePhysicalMemory"));
```

#### Asynchronous UpDownCounter operations

Asynchronous UpDownCounter uses an idiomatic interface for reporting
measurements through a `callback`, which is registered during
[Asynchronous Updowncounter creation](#asynchronous-updowncounter-creation).

For callback functions registered after an asynchronous instrument is
created, the API is required to support a mechanism for
unregistration.  For example, the object returned from `register_callback`
can support an `unregister()` method directly.

```python
# Python
class Device:
    """A device with one updowncounter"""

    def __init__(self, meter, x):
        self.x = x
        updowncounter = meter.create_observable_updowncounter(name="queue_size", description="items in process")
        self.cb = updowncounter.register_callback(self.updowncounter_callback)

    def updowncounter_callback(self, result):
        result.Observe(self.read_updowncounter(), {'x', self.x})

    def read_updowncounter(self):
        return 100  # ...

    def stop(self):
        self.cb.unregister()
```

## Measurement

A `Measurement` represents a data point reported via the metrics API to the SDK.
Please refer to the [Metrics Programming Model](./README.md#programming-model)
for the interaction between the API and SDK.

`Measurement`s encapsulate:

* A value
* [`Attributes`](../common/README.md#attribute)

### Multiple-instrument callbacks

[The Metrics API MAY support an interface allowing the use of multiple
instruments from a single registered
Callback](#asynchronous-instrument-api).  The API to register a new
Callback SHOULD accept:

- A `callback` function
- A list (or tuple, etc.) of Instruments used in the `callback` function.

It is RECOMMENDED that the API authors use one of the following forms
for the `callback` function:

* The list (or tuple, etc.) returned by the `callback` function
  contains `(Instrument, Measurement)` pairs.
* the Observable Result parameter receives an additional `(Instrument,
  Measurement)` pairs

This interface is typically a more performant way to report multiple
measurements when they are obtained through an expensive process, such
as reading `/proc` files or probing the garbage collection subsystem.

For example,

```Python
# Python
class Device:
    """A device with two instruments"""

    def __init__(self, meter, property):
        self.property = property
        self.usage = meter.create_observable_counter(name="usage", description="count of items used")
        self.pressure = meter.create_observable_gauge(name="pressure", description="force per unit area")

        # Note the two associated instruments are passed to the callback.
        meter.register_callback([self.usage, self.pressure], self.observe)

    def observe(self, result):
        usage, pressure = expensive_system_call()
        result.observe(self.usage, usage, {'property', self.property})
        result.observe(self.pressure, pressure, {'property', self.property})
```

## Compatibility requirements

All the metrics components SHOULD allow new APIs to be added to
existing components without introducing breaking changes.

All the metrics APIs SHOULD allow optional parameter(s) to be added to existing
APIs without introducing breaking changes, if possible.

## Concurrency requirements

For languages which support concurrent execution the Metrics APIs provide
specific guarantees and safeties.

**MeterProvider** - all methods are safe to be called concurrently.

**Meter** - all methods are safe to be called concurrently.

**Instrument** - All methods of any Instrument are safe to be called
concurrently.
