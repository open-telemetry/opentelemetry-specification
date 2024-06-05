<!--- Hugo front matter used to generate the website version of this page:
linkTitle: No-Op
--->

# Metrics No-Op API Implementation

**Status**: [Stable](../document-status.md)

<details>
<summary> Table of Contents </summary>

<!-- toc -->

- [MeterProvider](#meterprovider)
  * [Meter Creation](#meter-creation)
- [Meter](#meter)
  * [Counter Creation](#counter-creation)
  * [UpDownCounter Creation](#updowncounter-creation)
  * [Histogram Creation](#histogram-creation)
  * [Asynchronous Counter Creation](#asynchronous-counter-creation)
  * [Asynchronous UpDownCounter Creation](#asynchronous-updowncounter-creation)
  * [Asynchronous Gauge Creation](#asynchronous-gauge-creation)
- [Instruments](#instruments)
  * [Counter](#counter)
    + [Counter Add](#counter-add)
  * [UpDownCounter](#updowncounter)
    + [UpDownCounter Add](#updowncounter-add)
  * [Histogram](#histogram)
    + [Histogram Record](#histogram-record)
  * [Asynchronous Counter](#asynchronous-counter)
  * [Asynchronous Counter Observations](#asynchronous-counter-observations)
  * [Asynchronous UpDownCounter](#asynchronous-updowncounter)
  * [Asynchronous UpDownCounter Observations](#asynchronous-updowncounter-observations)
  * [Asynchronous Gauge](#asynchronous-gauge)
  * [Asynchronous Gauge Observations](#asynchronous-gauge-observations)
- [References](#references)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way to disable the API from actually
performing any operations. The No-Op OpenTelemetry API implementation
(henceforth referred to as the No-Op) provides users with this
functionally. It implements the OpenTelemetry API so that no telemetry
is produced and computation resources are minimized.

All language implementations of OpenTelemetry MUST provide a No-Op.

## MeterProvider

The No-Op MUST allow the creation of multiple MeterProviders.

The MeterProviders created by the No-Op needs to hold as small a memory
footprint as possible. Therefore, all MeterProviders created MUST NOT
hold configuration or operational state.

Since all MeterProviders hold the same empty state, a No-Op MAY
provide the same MeterProvider instances to all creation requests.

The No-Op is used by OpenTelemetry users to disable OpenTelemetry
computation overhead and eliminate OpenTelemetry related output. For
this reason, the MeterProvider MUST NOT return a non-empty error or log
any message for any operations it performs.

All operations a MeterProvider provides MUST be safe to be run
concurrently.

### Meter Creation

[New Meter instances are always created with a
MeterProvider](./api.md#meterprovider). Therefore, MeterProviders MUST
allow for the creation of Meters. All Meters created MUST be an instance of the
[No-Op Meter](#meter).

Since all Meters will hold the same empty state, a MeterProvider MAY
return the same Meter instances to all creation requests.

[The API specifies multiple parameters](./api.md#meterprovider) that
need to be accepted by the creation operation. The MeterProvider MUST
accept these parameters. However, the MeterProvider MUST NOT validate
any argument it receives.

## Meter

The Meters created by the No-Op need to hold as small a memory
footprint as possible. Therefore, all Meters created MUST NOT hold
configuration or operational state.

The Meter MUST NOT return a non-empty error or log any message for any
operations it performs.

All operations a Meter provides MUST be safe to be run concurrently.

### Counter Creation

The No-Op Meter MUST allow for the creation of a [Counter
instrument](#counter).

Since all Counters hold the same empty state, a Meter MAY return the
same Counter instance to all creation requests.

[The API specifies multiple
parameters](./api.md#synchronous-instrument-api) that need to be
accepted by the creation operation. The Meter MUST accept these
parameters. However, the Meter MUST NOT validate any argument it
receives.

### UpDownCounter Creation

The No-Op Meter MUST allow for the creation of a [UpDownCounter
instrument](#updowncounter).

Since all UpDownCounters hold the same empty state, a Meter MAY return
the same UpDownCounter instance to all creation requests.

[The API specifies multiple
parameters](./api.md#synchronous-instrument-api) that need to be
accepted by the creation operation. The Meter MUST accept these
parameters. However, the Meter MUST NOT validate any argument it
receives.

### Histogram Creation

The No-Op Meter MUST allow for the creation of a [Histogram
instrument](#histogram).

Since all Histograms hold the same empty state, a Meter MAY return the
same Histogram instance to all creation requests.

[The API specifies multiple
parameters](./api.md#synchronous-instrument-api) that need to be
accepted by the creation operation. The Meter MUST accept these
parameters. However, the Meter MUST NOT validate any argument it
receives.

### Asynchronous Counter Creation

The No-Op Meter MUST allow for the creation of an [Asynchronous Counter
instrument](#asynchronous-counter).

Since all Asynchronous Counters hold the same empty state, a Meter MAY
return the same Asynchronous Counter instance to all creation requests.

[The API specifies multiple
parameters](./api.md#asynchronous-instrument-api) that need to be
accepted by the creation operation. The Meter MUST accept these
parameters. However, the Meter MUST NOT validate any argument it
receives and it MUST NOT hold any reference to the passed callbacks.

### Asynchronous UpDownCounter Creation

The No-Op Meter MUST allow for the creation of an [Asynchronous
UpDownCounter instrument](#asynchronous-updowncounter).

Since all Asynchronous UpDownCounters hold the same empty state, a Meter
MAY return the same Asynchronous UpDownCounter instance to all creation
requests.

[The API specifies multiple
parameters](./api.md#asynchronous-instrument-api) that need to be
accepted by the creation operation. The Meter MUST accept these
parameters. However, the Meter MUST NOT validate any argument it
receives and it MUST NOT hold any reference to the passed callbacks.

### Asynchronous Gauge Creation

The No-Op Meter MUST allow for the creation of an [Asynchronous Gauge
instrument](#asynchronous-gauge).

Since all Asynchronous Gauges hold the same empty state, a Meter MAY
return the same Asynchronous UpDownCounter instance to all creation
requests.

[The API specifies multiple
parameters](./api.md#asynchronous-instrument-api) that need to be
accepted by the creation operation. The Meter MUST accept these
parameters. However, the Meter MUST NOT validate any argument it
receives and it MUST NOT hold any reference to the passed callbacks.

## Instruments

Instruments are used to make measurements and report telemetry for a
system. However, the No-Op is used to disable this production of
telemetry. Because of this, all instruments the No-Op provides MUST NOT
hold any configuration or operational state including the aggregation of
telemetry.

### Counter

Counters MUST NOT return a non-empty error or log any message for any
operations they perform.

All operations a Counter provides MUST be safe to be run concurrently.

#### Counter Add

The No-Op Counter MUST provide the user an interface to Add that
implements the [API](./api.md#add). It MUST NOT validate or retain any
state about the arguments it receives.

### UpDownCounter

UpDownCounters MUST NOT return a non-empty error or log any message for
any operations they perform.

All operations an UpDownCounter provides MUST be safe to be run
concurrently.

#### UpDownCounter Add

The No-Op UpDownCounter MUST provide the user an interface to Add that
implements the [API](./api.md#add-1). It MUST NOT validate or retain any
state about the arguments it receives.

### Histogram

Histograms MUST NOT return a non-empty error or log any message for any
operations they perform.

All operations a Histogram provides MUST be safe to be run concurrently.

#### Histogram Record

The No-Op Histogram MUST provide the user an interface to Record that
implements the [API](./api.md#record). It MUST NOT validate or retain
any state about the arguments it receives.

### Asynchronous Counter

Asynchronous Counters MUST NOT return a non-empty error or log any
message for any operations they perform.

All operations an Asynchronous Counter provides MUST be safe to be run
concurrently.

### Asynchronous Counter Observations

The No-Op Asynchronous Counter MUST NOT validate or retain any state
about observations made for the instrument.

### Asynchronous UpDownCounter

Asynchronous UpDownCounters MUST NOT return a non-empty error or log any
message for any operations they perform.

All operations an Asynchronous UpDownCounter provides MUST be safe to be
run concurrently.

### Asynchronous UpDownCounter Observations

The No-Op Asynchronous UpDownCounter MUST NOT validate or retain any
state about observations made for the instrument.

### Asynchronous Gauge

Asynchronous Gauges MUST NOT return a non-empty error or log any message
for any operations they perform.

All operations an Asynchronous Gauge provides MUST be safe to be run
concurrently.

### Asynchronous Gauge Observations

The No-Op Asynchronous Gauge MUST NOT validate or retain any state about
observations made for the instrument.

## References

- [OTEP0146 Scenarios for Metrics API/SDK Prototyping](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0146-metrics-prototype-scenarios.md)
