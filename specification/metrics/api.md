<!--- Hugo front matter used to generate the website version of this page:
linkTitle: API
--->

# Metrics API

**Status**: [Stable](../document-status.md), except where otherwise specified

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
    + [Instrument name syntax](#instrument-name-syntax)
    + [Instrument unit](#instrument-unit)
    + [Instrument description](#instrument-description)
    + [Instrument advisory parameters](#instrument-advisory-parameters)
      - [Instrument advisory parameter: `ExplicitBucketBoundaries`](#instrument-advisory-parameter-explicitbucketboundaries)
      - [Instrument advisory parameter: `Attributes`](#instrument-advisory-parameter-attributes)
    + [Synchronous and Asynchronous instruments](#synchronous-and-asynchronous-instruments)
      - [Synchronous Instrument API](#synchronous-instrument-api)
      - [Asynchronous Instrument API](#asynchronous-instrument-api)
  * [General operations](#general-operations)
    + [Enabled](#enabled)
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
  * [Gauge](#gauge)
    + [Gauge creation](#gauge-creation)
    + [Gauge operations](#gauge-operations)
      - [Record](#record-1)
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
- [References](#references)

<!-- tocstop -->

</details>

## Overview

The Metrics API consists of these main components:

* [MeterProvider](#meterprovider) is the entry point of the API. It provides
  access to `Meters`.
* [Meter](#meter) is responsible for creating `Instruments`.
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
        +-- Instrument<Histogram, double>(name='client.duration', attributes=['server.address', 'server.port'], unit='ms')
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

Normally, the `MeterProvider` is expected to be accessed from a central place.
Thus, the API SHOULD provide a way to set/register and access a global default
`MeterProvider`.

### MeterProvider operations

The `MeterProvider` MUST provide the following functions:

* Get a `Meter`

#### Get a Meter

This API MUST accept the following parameters:

* `name`: This name uniquely identifies the [instrumentation
  scope](../glossary.md#instrumentation-scope), such as the
  [instrumentation library](../glossary.md#instrumentation-library) (e.g.
  `io.opentelemetry.contrib.mongodb`), package,
  module or class name. If an application or library has built-in OpenTelemetry
  instrumentation, both [Instrumented
  library](../glossary.md#instrumented-library) and [Instrumentation
  library](../glossary.md#instrumentation-library) can refer to the same
  library. In that scenario, the `name` denotes a module name or component name
  within that library or application.
* `version`: Specifies the version of the instrumentation scope if the scope
  has a version (e.g. a library version). Example value: `1.0.0`.

  Users can provide a `version`, but it is up to their discretion. Therefore,
  this API needs to be structured to accept a `version`, but MUST NOT obligate
  a user to provide one.
* [since 1.4.0] `schema_url`: Specifies the Schema URL that should be recorded
  in the emitted telemetry.

  Users can provide a `schema_url`, but it is up to their discretion.
  Therefore, this API needs to be structured to accept a `schema_url`, but MUST
  NOT obligate a user to provide one.
* [since 1.13.0] `attributes`: Specifies the instrumentation scope attributes
  to associate with emitted telemetry.

  Users can provide attributes to associate with the instrumentation scope, but
  it is up to their discretion. Therefore, this API MUST be structured to
  accept a variable number of attributes, including none.

Meters are identified by `name`, `version`, and `schema_url` fields.  When more
than one `Meter` of the same `name`, `version`, and `schema_url` is created, it
is unspecified whether or under which conditions the same or different `Meter`
instances are returned. It is a user error to create Meters with different
attributes but the same identity.

The term *identical* applied to Meters describes instances where all identifying
fields are equal. The term *distinct* applied to Meters describes instances where
at least one identifying field has a different value.

## Meter

The meter is responsible for creating [Instruments](#instrument).

Note: `Meter` SHOULD NOT be responsible for the configuration. This should be
the responsibility of the `MeterProvider` instead.

### Meter operations

The `Meter` MUST provide functions to create new [Instruments](#instrument):

* [Create a new Counter](#counter-creation)
* [Create a new Asynchronous Counter](#asynchronous-counter-creation)
* [Create a new Histogram](#histogram-creation)
* [Create a new Gauge](#gauge-creation)
* [Create a new Asynchronous Gauge](#asynchronous-gauge-creation)
* [Create a new UpDownCounter](#updowncounter-creation)
* [Create a new Asynchronous UpDownCounter](#asynchronous-updowncounter-creation)

Also see the respective sections below for more information on instrument creation.

## Instrument

Instruments are used to report [Measurements](#measurement). Each Instrument
will have the following parameters:

* The `name` of the Instrument
* The `kind` of the Instrument - whether it is a [Counter](#counter) or
  one of the other kinds, whether it is synchronous or asynchronous
* An optional `unit` of measure
* An optional `description`
* Optional `advisory` parameters (**development**)

Instruments are associated with the Meter during creation. Instruments
are identified by the `name`, `kind`, `unit`, and `description`.

Language-level features such as the distinction between integer and
floating point numbers SHOULD be considered as identifying.

The term *identical* applied to an Instrument describes instances where all
identifying fields are equal.

### General characteristics

#### Instrument name syntax

The instrument name syntax is defined below using the [Augmented Backus-Naur
Form](https://tools.ietf.org/html/rfc5234):

```abnf
instrument-name = ALPHA 0*254 ("_" / "." / "-" / "/" / ALPHA / DIGIT)

ALPHA = %x41-5A / %x61-7A; A-Z / a-z
DIGIT = %x30-39 ; 0-9
```

* They are not null or empty strings.
* They are case-insensitive, ASCII strings.
* The first character must be an alphabetic character.
* Subsequent characters must belong to the alphanumeric characters, '_', '.', '-',
  and '/'.
* They can have a maximum length of 255 characters.

#### Instrument unit

The `unit` is an optional string provided by the author of the Instrument. The
API SHOULD treat it as an opaque string.

* It MUST be case-sensitive (e.g. `kb` and `kB` are different units), ASCII
  string.
* It can have a maximum length of 63 characters. The number 63 is chosen to
  allow the unit strings (including the `\0` terminator on certain language
  runtimes) to be stored and compared as fixed size array/struct when
  performance is critical.

#### Instrument description

The `description` is an optional free-form text provided by the author of the
instrument. The API MUST treat it as an opaque string.

* It MUST support [BMP (Unicode Plane
  0)](https://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane),
  which is basically only the first three bytes of UTF-8 (or `utf8mb3`).
  [OpenTelemetry API](../overview.md#api) authors MAY decide if they want to
  support more Unicode [Planes](https://en.wikipedia.org/wiki/Plane_(Unicode)).
* It MUST support at least 1023 characters. [OpenTelemetry
  API](../overview.md#api) authors MAY decide if they want to support more.

#### Instrument advisory parameters

**Status**: [Mixed](../document-status.md)

`advisory` parameters are an optional set of recommendations provided by the
author of the Instrument, aimed at assisting implementations in providing
useful output with minimal configuration. They differ from other parameters
in that Implementations MAY ignore `advisory` parameters.

OpenTelemetry SDKs MUST handle `advisory` parameters as described
[here](./sdk.md#instrument-advisory-parameters).

`advisory` parameters may be general, or may be accepted only for specific
instrument `kind`s.

##### Instrument advisory parameter: `ExplicitBucketBoundaries`

**Status**: [Stable](../document-status.md)

Applies to Histogram instrument type.

`ExplicitBucketBoundaries` (`double[]`) is the recommended set of bucket
boundaries to use if aggregating to
[explicit bucket Histogram metric data point](./data-model.md#histogram).

##### Instrument advisory parameter: `Attributes`

**Status**: [Development](../document-status.md)

Applies to all instrument types.

`Attributes` (a list of [attribute keys](../common/README.md#attribute)) is
the recommended set of attribute keys to be used for the resulting metrics.

#### Synchronous and Asynchronous instruments

Instruments are categorized on whether they are synchronous or
asynchronous:

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

##### Synchronous Instrument API

The API to construct synchronous instruments MUST accept the following parameters:

* A `name` of the Instrument.

  The `name` needs to be provided by a user. If possible, the API SHOULD be
  structured so a user is obligated to provide this parameter. If it is not
  possible to structurally enforce this obligation, the API MUST be documented
  in a way to communicate to users that this parameter is needed.

  The API SHOULD be documented in a way to communicate to users that the `name`
  parameter needs to conform to the [instrument name
  syntax](#instrument-name-syntax). The API SHOULD NOT validate the `name`;
  that is left to implementations of the API.
* A `unit` of measure.

  Users can provide a `unit`, but it is up to their discretion. Therefore, this
  API needs to be structured to accept a `unit`, but MUST NOT obligate a user
  to provide one.

  The `unit` parameter needs to support the [instrument unit
  rule](#instrument-unit). Meaning, the API MUST accept a case-sensitive string
  that supports ASCII character encoding and can hold at least 63 characters.
  The API SHOULD NOT validate the `unit`.
* A `description` describing the Instrument in human-readable terms.

  Users can provide a `description`, but it is up to their discretion.
  Therefore, this API needs to be structured to accept a `description`, but
  MUST NOT obligate a user to provide one.

  The `description` needs to support the [instrument description
  rule](#instrument-description). Meaning, the API MUST accept a string that
  supports at least [BMP (Unicode Plane
  0)](https://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane)
  encoded characters and hold at least 1023 characters.

* `advisory` parameters associated with the instrument `kind`.

  Users can provide `advisory` parameters, but its up to their discretion.
  Therefore, this API needs to be structured to accept `advisory` parameters,
  but MUST NOT obligate the user to provide it.

  `advisory` parameters need to be structured as described in
  [instrument advisory parameters](#instrument-advisory-parameters), with
  parameters that are general and specific to a particular instrument `kind`.
  The API SHOULD NOT validate `advisory` parameters.

##### Asynchronous Instrument API

Asynchronous instruments have associated `callback` functions which
are responsible for reporting [Measurement](#measurement)s. Callback
functions will be called only when the Meter is being observed.  The
order of callback execution is not specified.

The API to construct asynchronous instruments MUST accept the following parameters:

* A `name` of the Instrument.

  The `name` needs to be provided by a user. If possible, the API SHOULD be
  structured so a user is obligated to provide this parameter. If it is not
  possible to structurally enforce this obligation, the API MUST be documented
  in a way to communicate to users that this parameter is needed.

  The API SHOULD be documented in a way to communicate to users that the `name`
  parameter needs to conform to the [instrument name
  syntax](#instrument-name-syntax). The API SHOULD NOT validate the `name`,
  that is left to implementations of the API.
* A `unit` of measure.

  Users can provide a `unit`, but it is up to their discretion. Therefore, this
  API needs to be structured to accept a `unit`, but MUST NOT obligate a user
  to provide one.

  The `unit` parameter needs to support the [instrument unit
  rule](#instrument-unit). Meaning, the API MUST accept a case-sensitive string
  that supports ASCII character encoding and can hold at least 63 characters.
  The API SHOULD NOT validate the `unit`.
* A `description` describing the Instrument in human-readable terms.

  Users can provide a `description`, but it is up to their discretion.
  Therefore, this API needs to be structured to accept a `description`, but
  MUST NOT obligate a user to provide one.

  The `description` needs to support the [instrument description
  rule](#instrument-description). Meaning, the API MUST accept a string that
  supports at least [BMP (Unicode Plane
  0)](https://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane)
  encoded characters and hold at least 1023 characters.
* `advisory` parameters associated with the instrument `kind`.

  Users can provide `advisory` parameters, but its up to their discretion.
  Therefore, this API needs to be structured to accept `advisory` parameters,
  but MUST NOT obligate the user to provide it.

  `advisory` parameters need to be structured as described in
  [instrument advisory parameters](#instrument-advisory-parameters), with
  parameters that are general and specific to a particular instrument `kind`.
  The API SHOULD NOT validate `advisory` parameters.
* `callback` functions that report [Measurements](#measurement) of the created
  instrument.

  Users can provide `callback` functions, but it is up to their discretion.
  Therefore, this API MUST be structured to accept a variable number of
  `callback` functions, including none.

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

### General operations

All instruments SHOULD provide functions to:

* [Report if instrument is `Enabled`](#enabled)

#### Enabled

**Status**: [Experimental](../document-status.md)

To help users avoid performing computationally expensive operations when
recording measurements, instruments SHOULD provide this `Enabled` API.

There are currently no required parameters for this API. Parameters can be
added in the future, therefore, the API MUST be structured in a way for
parameters to be added.

This API MUST return a language idiomatic boolean type. A returned value of
`true` means the instrument is enabled for the provided arguments, and a returned
value of `false` means the instrument is disabled for the provided arguments.

The returned value is not always static, it can change over time. The API
SHOULD be documented that instrumentation authors needs to call this API each
time they record a measurement to ensure they have the most up-to-date response.

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

This API MUST accept the following parameter:

* A numeric increment value.

  The increment value needs to be provided by a user. If possible, this API
  SHOULD be structured so a user is obligated to provide this parameter. If it
  is not possible to structurally enforce this obligation, this API MUST be
  documented in a way to communicate to users that this parameter is needed.

  The increment value is expected to be non-negative. This API SHOULD be
  documented in a way to communicate to users that this value is expected to be
  non-negative. This API SHOULD NOT validate this value, that is left to
  implementations of the API.
* [Attributes](../common/README.md#attribute) to associate with the increment
  value.

  Users can provide attributes to associate with the increment value, but it is
  up to their discretion. Therefore, this API MUST be structured to accept a
  variable number of attributes, including none.

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
which reports [monotonically](https://en.wikipedia.org/wiki/Monotonic_function)
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

It is highly recommended that the name `ObservableCounter` (or any language
idiomatic variation, e.g. `observable_counter`) be used unless there is a
strong reason not to do so. Please note that the name has nothing to do with
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
    unit="ms",
    value_type=float)
```

```csharp
// C#

var httpServerDuration = meter.CreateHistogram<double>(
    "http.server.duration",
    description: "measures the duration of the inbound HTTP request",
    unit: "ms"
    );
```

#### Histogram operations

##### Record

Updates the statistics with the specified amount.

This API SHOULD NOT return a value (it MAY return a dummy value if required by
certain programming languages or systems, for example `null`, `undefined`).

This API MUST accept the following parameter:

* A numeric value to record.

  The value needs to be provided by a user. If possible, this API SHOULD be
  structured so a user is obligated to provide this parameter. If it is not
  possible to structurally enforce this obligation, this API MUST be documented
  in a way to communicate to users that this parameter is needed.

  The value is expected to be non-negative. This API SHOULD be documented in a
  way to communicate to users that this value is expected to be non-negative.
  This API SHOULD NOT validate this value, that is left to implementations of
  the API.
* [Attributes](../common/README.md#attribute) to associate with the value.

  Users can provide attributes to associate with the value, but it is up to
  their discretion. Therefore, this API MUST be structured to accept a variable
  number of attributes, including none.

[OpenTelemetry API](../overview.md#api) authors MAY decide to allow flexible
[attributes](../common/README.md#attribute) to be passed in as individual
arguments. [OpenTelemetry API](../overview.md#api) authors MAY allow attribute
values to be passed in using a more efficient way (e.g. strong typed struct
allocated on the callstack, tuple). Here are some examples that [OpenTelemetry
API](../overview.md#api) authors might consider:

```python
# Python

http_server_duration.Record(50, {"http.request.method": "POST", "url.scheme": "https"})
http_server_duration.Record(100, http_method="GET", http_scheme="http")
```

```csharp
// C#

httpServerDuration.Record(50, ("http.request.method", "POST"), ("url.scheme", "https"));
httpServerDuration.Record(100, new HttpRequestAttributes { method = "GET", scheme = "http" });
```

### Gauge

`Gauge` is a [synchronous Instrument](#synchronous-instrument-api) which can be
used to record non-additive value(s) (e.g. the background noise level - it makes
no sense to record the background noise level value from multiple rooms and sum
them up) when changes occur.

Note: If the values are additive (e.g. the process heap size - it makes sense to
report the heap size from multiple processes and sum them up, so we get the
total heap usage), use [UpDownCounter](#asynchronous-updowncounter).

Note: Synchronous Gauge is normally used when the measurements are exposed via a
subscription to change events (
i.e. `backgroundNoiseLevel.onChange(value -> gauge.record(value))`). If the
measurement is exposed via an accessor,
use [Asynchronous Gauge](#asynchronous-gauge) to invoke the accessor in a
callback function (
i.e. `createObservableGauge(observable -> observable.record(backgroundNoiseLevel.getCurrentValue()))`.

Example uses for Gauge:

* subscribe to change events for the background noise level
* subscribe to change events for the CPU fan speed

#### Gauge creation

There MUST NOT be any API for creating a `Gauge` other than with a
[`Meter`](#meter). This MAY be called `CreateGauge`. If strong type is
desired, [OpenTelemetry API](../overview.md#api) authors MAY decide the language
idiomatic name(s), for example `CreateUInt64Gauge`, `CreateDoubleGauge`,
`CreateGauge<UInt64>`, `CreateGauge<double>`.

See the [general requirements for synchronous instruments](#synchronous-instrument-api).

Here are some examples that [OpenTelemetry API](../overview.md#api) authors
might consider:

```java
// Java

DoubleGauge backgroundNoiseLevel = meter.gaugeBuilder("facility.noise.level")
    .setDescription("Background noise level of rooms")
    .setUnit("B")
    .build();
```

#### Gauge operations

##### Record

Record the Gauge current value.

This API SHOULD NOT return a value (it MAY return a dummy value if required by
certain programming languages or systems, for example `null`, `undefined`).

This API MUST accept the following parameter:

* A numeric value. The current absolute value.

  The value needs to be provided by a user. If possible, this API
  SHOULD be structured so a user is obligated to provide this parameter. If it
  is not possible to structurally enforce this obligation, this API MUST be
  documented in a way to communicate to users that this parameter is needed.
* [Attributes](../common/README.md#attribute) to associate with the value.

  Users can provide attributes to associate with the value, but it is
  up to their discretion. Therefore, this API MUST be structured to accept a
  variable number of attributes, including none.

The [OpenTelemetry API](../overview.md#api) authors MAY decide to allow flexible
[attributes](../common/README.md#attribute) to be passed in as arguments. If
the attribute names and types are provided during the [gauge
creation](#gauge-creation), the [OpenTelemetry API](../overview.md#api)
authors MAY allow attribute values to be passed in using a more efficient way
(e.g. strong typed struct allocated on the callstack, tuple). The API MUST allow
callers to provide flexible attributes at invocation time rather than having to
register all the possible attribute names during the instrument creation. Here
are some examples that [OpenTelemetry API](../overview.md#api) authors might
consider:

```java
// Java
Attributes roomA = Attributes.builder().put("room.id", "Rack A");
Attributes roomB = Attributes.builder().put("room.id", "Rack B");

backgroundNoiseLevel.record(4.3, roomA);
backgroundNoiseLevel.record(2.5, roomB);
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

It is highly recommended that the name `ObservableGauge` (or any language
idiomatic variation, e.g. `observable_gauge`) be used unless there is a strong
reason not to do so. Please note that the name has nothing to do with
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
[monotonically](https://en.wikipedia.org/wiki/Monotonic_function) increasing, use
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

This API MUST accept the following parameter:

* A numeric value to add.

  The value needs to be provided by a user. If possible, this API SHOULD be
  structured so a user is obligated to provide this parameter. If it is not
  possible to structurally enforce this obligation, this API MUST be documented
  in a way to communicate to users that this parameter is needed.
* [Attributes](../common/README.md#attribute) to associate with the value.

  Users can provide attributes to associate with the value, but it is up to
  their discretion. Therefore, this API MUST be structured to accept a variable
  number of attributes, including none.

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
[monotonically](https://en.wikipedia.org/wiki/Monotonic_function) increasing, use
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

It is highly recommended that the name `ObservableUpDownCounter` (or any
language idiomatic variation, e.g. `observable_up_down_counter`) be used unless
there is a strong reason not to do so. Please note that the name has nothing to
do with [asynchronous
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

meter.create_observable_up_down_counter(
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

meter.create_observable_up_down_counter(
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
    """A device with one up_down_counter"""

    def __init__(self, meter, x):
        self.x = x
        updowncounter = meter.create_observable_up_down_counter(name="queue_size", description="items in process")
        self.cb = updowncounter.register_callback(self.up_down_counter_callback)

    def up_down_counter_callback(self, result):
        result.Observe(self.read_up_down_counter(), {'x', self.x})

    def read_up_down_counter(self):
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

## References

- [OTEP0003 Consolidate pre-aggregated and raw metrics APIs](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0003-measure-metric-type.md)
- [OTEP0008 Metrics observer specification](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0008-metric-observer.md)
- [OTEP0009 Metric Handle API specification](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0009-metric-handles.md)
- [OTEP0010 Rename "Cumulative" to "Counter" in the metrics API](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0010-cumulative-to-counter.md)
- [OTEP0049 Metric `LabelSet` specification](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0049-metric-label-set.md)
- [OTEP0070 Rename metric instrument Handles to "Bound Instruments"](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0070-metric-bound-instrument.md)
- [OTEP0072 Metric observer specification (refinement)](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0072-metric-observer.md)
- [OTEP0080 Remove the Metric API Gauge instrument](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0080-remove-metric-gauge.md)
- [OTEP0088 Metric Instruments](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0088-metric-instrument-optional-refinements.md)
- [OTEP0090 Remove the LabelSet object from the metrics API](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0090-remove-labelset-from-metrics-api.md)
- [OTEP0098 Explain the metric instruments](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0098-metric-instruments-explained.md)
- [OTEP0108 Metric instrument naming guidelines](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0108-naming-guidelines.md)
- [OTEP0146 Scenarios for Metrics API/SDK Prototyping](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0146-metrics-prototype-scenarios.md)
