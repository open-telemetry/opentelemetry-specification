# Metrics API

**Status**: [Experimental](../document-status.md)

**Owner:**

* [Reiley Yang](https://github.com/reyang)

**Domain Experts:**

* [Bogdan Brutu](https://github.com/bogdandrutu)
* [Josh Suereth](https://github.com/jsuereth)
* [Joshua MacDonald](https://github.com/jmacd)

Note: this specification is subject to major changes. To avoid thrusting
language client maintainers, we don't recommend OpenTelemetry clients to start
the implementation unless explicitly communicated via
[OTEP](https://github.com/open-telemetry/oteps#opentelemetry-enhancement-proposal-otep).

<details>
<summary>
Table of Contents
</summary>

* [Overview](#overview)
* [MeterProvider](#meterprovider)
  * [MeterProvider operations](#meterprovider-operations)
* [Meter](#meter)
  * [Meter operations](#meter-operations)
* [Instrument](#instrument)
  * [Counter](#counter)
    * [Counter Creation](#counter-creation)
* [Measurement](#measurement)

</details>

## Overview

The Metrics API consists of these main components:

* [MeterProvider](#meterprovider) is the entry point of the API. It provides
  access to `Meters`.
* [Meter](#meter) is the class responsible for creating `Instruments`.
* [Instrument](#instrument) is responsible for reporting
  [Measurements](#measurement).

Here is an example of the object hierarchy inside a process instrumented with the
metrics API:

```text
+-- MeterProvider(default)
    |
    +-- Meter(name='io.opentelemetry.runtime', version='1.0.0')
    |   |
    |   +-- instruments...
    |
    +-- Meter(name='io.opentelemetry.contrib.mongodb.client', version='2.3.0')
        |
        +-- Instrument<Counter, int>(name='client.exception', attributes=['type'], unit='1')
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

* `name` (required): This name must identify the [instrumentation
  library](../overview.md#instrumentation-libraries) (e.g.
  `io.opentelemetry.contrib.mongodb`). If an application or library has built-in
  OpenTelemetry instrumentation, both [Instrumented
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
  implementation which is not even observability-related). A MeterProvider
  could also return a no-op Meter here if application owners configure the SDK
  to suppress telemetry produced by this library.
* `version` (optional): Specifies the version of the instrumentation library
  (e.g. `1.0.0`).

It is unspecified whether or under which conditions the same or different
`Meter` instances are returned from this functions.

Implementations MUST NOT require users to repeatedly obtain a `Meter` again with
the same name+version to pick up configuration changes. This can be achieved
either by allowing to work with an outdated configuration or by ensuring that
new configuration applies also to previously returned `Meter`s.

Note: This could, for example, be implemented by storing any mutable
configuration in the `MeterProvider` and having `Meter` implementation objects
have a reference to the `MeterProvider` from which they were obtained. If
configuration must be stored per-meter (such as disabling a certain meter), the
meter could, for example, do a look-up with its name+version in a map in the
`MeterProvider`, or the `MeterProvider` could maintain a registry of all
returned `Meter`s and actively update their configuration if it changes.

## Meter

The meter is responsible for creating [Instruments](#instrument).

Note: `Meter` SHOULD NOT be responsible for the configuration. This should be
the responsibility of the `MeterProvider` instead.

### Meter operations

The `Meter` MUST provide functions to create new [Instruments](#instrument):

* [Create a new Counter](#counter-creation) (see the section on `Counter`)

## Instrument

Instruments are used to report [Measurements](#measurement). Each Instrument
will have the following information:

* The `name` of the Instrument
* The `kind` of the Instrument - whether it is a [Counter](#counter) or other
  instruments, whether it is synchronous or asynchronous
* An optional `unit of measure`
* An optional `description`
* An optional list of [`Attribute`](../common/common.md#attributes) names and
  types

Instruments are associated with the Meter during creation, and are identified by
the name:

* Meter implementations MUST return an error when multiple Instruments are
  registered under the same Meter instance using the same name.
* Different Meters MUST be treated as separate namespaces. The names of the
  Instruments under one Meter SHOULD NOT interfere with Instruments under
  another Meter.

<a name="instrument-naming-rule"></a>

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

<a name="instrument-unit"></a>

The `unit` is an optional string provided by the author of the instrument. It
SHOULD be treated as an oqaque string from the API and SDK (e.g. the SDK is not
expected to validate the unit of measurement, or perform the unit conversion).

* If the `unit` is not provided or the `unit` is null, the API and SDK MUST make
  sure that the behavior is the same as an empty `unit` string.
* It MUST be case-sensitive (e.g. `kb` and `kB` are different units), ASCII
  string.
* It can have a maximum length of 63 characters. The number 63 is chosen to
  allow the unit strings (includig the `\0` terminator on certain language
  runtimes) to be stored and compared as 8-bytes integers when performance is
  critical.

<a name="instrument-description"></a>

The `description` is an optional free-form text provided by the author of the
instrument. It MUST be treated as an oqaque string from the API and SDK.

* If the `description` is not provided or the `description` is null, the API and
  SDK MUST make sure that the behavior is the same as an empty `description`
  string.
* It MUST support [BMP (Unicode Plane
  0)](https://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane),
  which is basically only the first three bytes of UTF-8 (or `utf8mb3`).
  Individual language clients can decide if they want to support more Unicode
  [Planes](https://en.wikipedia.org/wiki/Plane_(Unicode)).
* It MUST support at least 1023 characters. Individual language clients can
  decide if they want to support more.

### Counter

`Counter` is a synchronous Instrument which supports non-negative increments.

Example uses for `Counter`:

* count the number of bytes received
* count the number of requests completed
* count the number of accounts created
* count the number of checkpoints run
* count the number of HTTP 5xx errors

#### Counter Creation

There MUST NOT be any API for creating a `Counter` other than with a
[`Meter`](#meter). This MAY be called `CreateCounter`. If strong type is
desired, the client can decide the language idomatic name(s), for example
`CreateUInt64Counter`, `CreateDoubleCounter`, `CreateCounter<UInt64>`,
`CreateCounter<double>`.

The API MUST accept the following parameters:

* The `name` of the Instrument, following the [instrument naming
  rule](#instrument-naming-rule).
* An optional `unit of measure`, following the [instrument unit
  rule](#instrument-unit).
* An optional `description`, following the [instrument description
  rule](#instrument-description).
* An optional list of [`Attribute`](../common/common.md#attributes) names and
  types.

Here are some examples that individual language client might consider:

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

* Optional [attributes](../common/common.md#attributes).
* The increment amount, which MUST be a non-negative numeric value.

The client MAY decide to allow flexible
[attributes](../common/common.md#attributes) to be passed in as arguments. If
the attribute names and types are provided during the [counter
creation](#counter-creation), the client MAY allow attribute values to be passed
in using a more efficient way (e.g. strong typed struct allocated on the
callstack, tuple). The API MUST allow callers to provide flexible attributes at
invocation time rather than having to register all the possible attribute names
during the instrument creation. Here are some examples that individual language
client might consider:

```python
# Python

exception_counter.Add(1, {"exception_type": "IOError", "handled_by_user": True})
exception_counter.Add(1, exception_type="IOError", handled_by_user=True})
```

```csharp
// C#

counterExceptions.Add(1, ("exception_type", "FileLoadException"), ("handled_by_user", true));

counterPowerUsed.Add(13.5, new PowerConsumption { customer = "Tom" });
counterPowerUsed.Add(200, new PowerConsumption { customer = "Jerry" }, ("is_green_energy", true));
```

## Measurement

A `Measurement` represents a data point reported via the metrics API to the SDK.
Please refer to the [Metrics Programming Model](./README.md#programming-model)
for the interaction between the API and SDK.

`Measurement`s encapsulate:

* A value
* [`Attributes`](../common/common.md#attributes)

## Concurrency

For languages which support concurrent execution the Metrics APIs provide
specific guarantees and safeties.

**MeterProvider** - all methods are safe to be called concurrently.

**Meter** - all methods are safe to be called concurrently.

**Instrument** - All methods of any Instrument are safe to be called
concurrently.
