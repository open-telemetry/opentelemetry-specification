# Metrics SDK

Note: This document assumes you are familiar with the [Metrics
API](api.md) specification.  Note that the examples below are copied
from the current OpenTelemetry-Go SDK:

TODO: TOC

## Purpose

This document describes a model implementation of the OpenTelemetry
Metrics SDK.  The architectural details of the model SDK described
here are meant to offer guidance to implementors, not to mandate an
exact reproduction of the model architecture across languages.

## Expectations

The SDK implementors are expected to follow the best practices for the
language and runtime environment when implementing the OpenTelemetry
API.  Implementors SHOULD follow the general prescriptions on safety
and performance given in [OpenTelemetry library
guidelines](../library-guidelines.md).

## Export Pipeline Terminology

**Export Pipeline** is used to describe a whole assembly of SDK parts.
There are three major components of the Metrics SDK that data flows
through, in order:

1. **Accumulator**: Receives metric events from the API, computes one Accumulation per active Instrument and Label Set pair
2. **Processor**: Receives Accumulations from the Accumulator, transforms into ExportRecordSet
3. **Exporter**: Receives ExportRecordSet, transforms into some protocol and sends it somewhere.

These terms are defined in the Metrics API specification:

- **Metric Instrument**: the API object used by a developer for instrumentation
- **Synchronous Instrument**: a metric instrument called by the user with application context
- **Asynchronous Instrument**: a metric instrument invoked through a callback from the SDK
- **Metric Descriptor**: describes a metric instrument
- **Metric Event**: a single recorded or observed (Instrument, Label Set, Measurement)
- **Collection Interval**: the period between calls to Accumulator.Collect()
- **Label**: a key-value describing a property of the metric event
- **Label Set**: a set of key-values with unique keys
- **Measurement**: an integer or floating point number.

Defined in the [Resource SDK](../resource/sdk.md) specification:

- **Resource**: a set of key-values with unique keys describing the process.

These are the significant data types used in the model architecture:

- **Aggregator**: aggregates one or more measurements in a useful way
- **AggregatorSelector**: chooses which Aggregator to assign to a metric instrument
- **Aggregation**: the result of aggregating one or more events by a specific aggregator
- **AggregationKind**: describes the kind of read API the Aggregation supports (e.g., Sum)
- **Accumulation**: consists of Instrument, Label Set, Resource, and Aggregator snapshot
- **Controller**: coordinates the Accumulator, Processor, and Exporter components in an export pipeline
- **ExportKind**: one of Delta, Cumulative, or Pass-Through
- **ExportKindSelector**: chooses which ExportKind to use for a metric instrument.
- **ExportRecord**: consists of Instrument, Label Set, Resource, Timestamp(s), and Aggregation
- **ExportRecordSet**: a set of export records

## Dataflow Diagram

![Metrics SDK Design Diagram](img/metrics-sdk.png)

## Accumulator: Meter Implementation

The Accumulator is the first component an OpenTelemetry Metric export
pipeline, implementing the front-line [`Meter`
interface]((api.md#meter-interface)).

```
// NewAccumulator constructs a new Accumulator for the given
// Processor and options.
func NewAccumulator(processor export.Processor, opts ...Option) *Accumulator
```

The Accumulator MUST provide the option to associate a
[`Resource`](../resource/sdk.md) with the Accumulations that it
produces.

```
// WithResource sets the Resource configuration option of a Config.
func WithResource(res *resource.Resource) Option
```

The Accumulator is called by the Controller (see below) to coordinate
collection using a `Collect()` method.

```
// Collect traverses the list of active instruments and exports
// data.  Collect() may not be called concurrently.
//
// During the collection pass, the Processor will receive
// one Process(Accumulation) call per current aggregation.
//
// Returns the number of accumulations that were exported.
func (m *Accumulator) Collect(ctx context.Context) int
```

### Implement the SDK-level API matching the user-level Metric API

The OpenTelemetry Metric API specifies a number of instruments and
supports several calling conventions, giving it a relatively large
number of types and methods ("surface area").  The OpenTelemetry API
SHOULD be designed and implemented following the style idioms of the
source language, in such a way that the SDK must implement a
significantly narrower interface.

This interface sits at the boundary of the SDK and the API, with three
core methods:

```
// MeterImpl is the interface an SDK must implement to supply a Meter
// implementation.
type MeterImpl interface {
	// RecordBatch atomically records a batch of measurements.
	RecordBatch(context.Context, []label.KeyValue, ...Measurement)

	// NewSyncInstrument returns a newly constructed
	// synchronous instrument implementation or an error, should
	// one occur.
	NewSyncInstrument(descriptor Descriptor) (SyncImpl, error)

	// NewAsyncInstrument returns a newly constructed
	// asynchronous instrument implementation or an error, should
	// one occur.
	NewAsyncInstrument(
		descriptor Descriptor,
		runner AsyncRunner,
	) (AsyncImpl, error)
}
```

These methods cover all the necessary entry points for implementing
the OpenTelemetry Metric API.

[`RecordBatch`](api.md#recordbatch-calling-convention) is a user-level API
implemented directly by the SDK.

The two instrument kinds of instrument constructor build [_synchronous_
and _asynchronous_](api.md#synchronous-and-asynchronous-instruments-compared)
SDK instruments.

The user is generally interested in the [Metric API `Meter`
interface](api.md#meter-interface), obtained through a [Metric API
`Provider` interface](api.md#meter-provider).  The `Meter` interface can be
constructed by wrapping the SDK `Meter` implementation:

```
// WrapMeterImpl constructs a `Meter` implementation from a
// `MeterImpl` implementation.
func WrapMeterImpl(impl MeterImpl, instrumentatioName string, opts ...MeterOption) Meter
```

Optional to this method:

- setting the version of the OpenTelemetry API in use.

### Provide access to the instrument descriptor

The SDK instruments are the underlying implementation for
[OpenTelemetry Metric instruments](api.md#metric-instruments).  This
interface links API and the SDK:

```
// InstrumentImpl is a common interface for synchronous and
// asynchronous instruments.
type InstrumentImpl interface {
	// Descriptor returns a copy of the instrument's Descriptor.
	Descriptor() Descriptor
}
```

The API `Descriptor` method defines the instrument in terms of
API-level constructs including name, instrument kind, description, and
units of measure.  The SDK instrument MUST provide access to the
`Descriptor` that was passed to its constructor.

#### Synchronous SDK instrument

The [synchronous SDK instrument](api.md#synchronous-instrument-details)
supports both direct and bound calling conventions.

```
// SyncImpl is the implementation-level interface to a generic
// synchronous instrument (e.g., ValueRecorder and Counter instruments).
type SyncImpl interface {
        // InstrumentImpl provides Descriptor() and Implementation()
	InstrumentImpl

	// Bind creates an implementation-level bound instrument,
	// binding a label set with this instrument implementation.
	Bind(labels []label.KeyValue) BoundSyncImpl

	// RecordOne captures a single synchronous metric event.
	RecordOne(ctx context.Context, number Number, labels []label.KeyValue)
}

// BoundSyncImpl is the implementation-level interface to a
// generic bound synchronous instrument
type BoundSyncImpl interface {

	// RecordOne captures a single synchronous metric event.
	RecordOne(ctx context.Context, number Number)

	// Unbind frees the resources associated with this bound instrument.
	Unbind()
}
```

#### Asynchronous SDK instrument

The [asynchronous SDK instrument](api.md#asynchronous-instrument-details)
supports both single-observer and batch-observer calling conventions.
The interface used for running Observer callbacks is passed at the
constructor, so there are no other API-level access methods for
asynchronous instruments.

```
// AsyncImpl is an implementation-level interface to an
// asynchronous instrument (e.g., Observer instruments).
type AsyncImpl interface {
        // InstrumentImpl provides Descriptor() and Implementation()
	InstrumentImpl
}
```

The asynchronous "runner" interface (`AsyncRunner`) passed in the
asynchronous SDK instrument constructor supports both
[single](api.md#single-instrument-observer) and
[batch](api.md#batch-observer) calling conventions.  These are
considered language-specific details.

### Instrument registration

The OpenTelemetry API SHOULD provide a wrapper for the Meter
implementation (`MeterImpl`) that:

- Provided the instrument definitions match, returns a unique SDK instrument
- When the instrument definitions do not match, returns a errors and a no-op instrument.

```
// NewUniqueInstrumentMeterImpl returns a wrapped metric.MeterImpl with
// the addition of uniqueness checking.
func NewUniqueInstrumentMeterImpl(impl metric.MeterImpl) metric.MeterImpl {
```

### Concurrency expectations

Synchronous metric instruments are expected to be used concurrently.
Unless concurrency is not a feature of the source language, the SDK
Accumulator component SHOULD be designed with concurrent performance
in mind.

SDK implementations SHOULD use the best concurrency primitives
available in the source language.  Accumulators MAY use exclusive
locking to maintain a map of synchronous instrument updates, but MUST
not hold any exclusive lock while calling an Aggregator (see below).

## Export pipeline detail

TODO: define AggregatorSelector, Aggregator, Accumulation, ExportKind,
ExportKindSelector, Aggregation, AggregationKind ExportRecord,
ExportRecordSet

## Processor Detail

TODO: define the Processor interface

### Basic Processor

TODO: define how ExportKind conversion works (delta->cumulative
required, cumulative->delta optional), Memory option (to not forget
prior collection state).

### Reducing Processor

TODO: Label filter, LabelFilterSelector

## Controller Detail

TODO: Push, Pull

## Aggregator Implementations

TODO: Sum, LastValue, Histogram, MinMaxSumCount, Exact, and Sketch.

## Pending issues

### ValueRecorder instrument default aggregation

TODO: The default SDK behavior for `ValueRecorder` instruments is
still in question.  Options are: LastValue, Histogram, MinMaxSumCount,
and Sketch.

https://github.com/open-telemetry/opentelemetry-specification/issues/636
https://github.com/open-telemetry/oteps/pull/117
https://github.com/open-telemetry/oteps/pull/118

### Standard sketch histogram aggregation

TODO: T.B.D.: DDSketch considered a good choice for ValueRecorder
instrument default aggregation.
