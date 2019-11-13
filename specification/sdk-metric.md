# Metric SDK

_This document is derived from the Golang Metrics SDK prototype.  See
the currently open PRs:_
1. [Pipeline and stdout exporter](https://github.com/open-telemetry/opentelemetry-go/pull/265)
1. [Dogstatsd exporter](https://github.com/jmacd/opentelemetry-go/pull/7)
1. [Prometheus exporter](https://github.com/open-telemetry/opentelemetry-go/pull/296)

## Glossary

__Metric update__: The term _metric update_ refers to any single
operation on a metric instrument; each handle-oriented and direct call
imply a single metric update, whereas each RecordBatch operation
implies a batch of metric updates.  See the user-facing API
specification for definitions of the three [calling
conventions](api-metrics-user.md).

__Aggregator__: The term _aggregator_ refers to an implementation that
can combine multiple metric updates into a single, combined state.
For example, a Sum aggregator combines multiple `Add()` updates into
single sum.  Aggregators must support concurrent updates.  Aggregators
support a `Checkpoint()` operation, which saves a snapshot of the
current aggregate state for collection, and a `Merge()` operation,
which combines state from two aggregators into one.

__Dimensionality reduction__: The user-facing metric API allows users
to supply LabelSets containing an unlimited number of labels for any
metric update.  Some metric exporters will reduce the set of labels
when exporting metric data, either to reduce cost or because of
system-imposed requirements.  A _dimensionality reduction_ maps input
LabelSets with (potentially) a large number of labels into a smaller
LabelSet containing only labels for an explicit set of label keys.
Performing dimensionality reduction in an metrics export pipeline
generally means merging aggregators computed for original LabelSets
into a single combined aggregator for the reduced-dimension LabelSet.

__Export record__: The _Export record_ is an exporter-independent
in-memory representation combining the metric instrument, the LabelSet
for export, and the associated (checkpointed) aggregator containing
its state.  Metric instruments are described by a metric descriptor.

__Metric descriptor__: A _metric descriptor_ is an in-memory
representation of the metric instrument, including all the information
provided in when it was defined.

## Meter implementation

The Meter API provides methods to create metric instruments, metric
instrument handles, and label sets.  This document describes the
standard Meter implementation and supporting packages used to build
a complete metric export pipeline.

The Meter implementation stands at the start of the export pipeline,
where it interfaces with the user-facing API and receives metric
updates.  The Meter's primary job is to maintain active state about
pending metric updates.  The most important requirement placed on the
Meter implementation is that be able to "forget" state about metric
updates after they are collected.

The Meter implementation SHOULD ensure that operations on instrument
handles be fast.  Metric updates made via an instrument handle, when
used with an aggregator defined by simple atomic operations, should
follow a very short code path.

The Meter implementation provides a `Collect()` method to initiate
collection.  Batcher and Exporter implementations are written with the
assumption that collection is single-threaded, therefore the Meter
implementation MUST prevent concurrent `Collect()` calls.  During the
collection pass, the Meter implementation checkpoints each active
aggregator and passes it to the Batcher for processing.

This document does not specify how to coordinate synchronization
between user-facing metric updates and metric collection activity,
however Meter implementations SHOULD make efforts to avoid lock
contention by holding locks only briefly or using lock-free
techniques.  Meter implementations MUST ensure that there are no lost
updates.

### Meter aggregation preserves LabelSet dimensions

The Meter acts as a short-term store for aggregating metric updates
within a collection period.  The Meter implementation maintains
aggregators for active metric instruments according to the complete,
original LabelSet.  This ensures a relatively simple code path for
entering metric updates into the Meter implementation.

Reducing dimensions for export is the responsibility of the Batcher.
As a consequence, the cost and complexity of dimensionality reduction
affects only the collection pass.

### Recommended implementation

The Meter implementation supports all three metric [calling
conventions](api-metrics-user.md): handle-oriented calls, direct
calls, and RecordBatch calls.  Although not a requirement, we
recommended the following approach for organizing the Meter
implementation.

Of the three calling conventions, direct calls and RecordBatch calls
can be easily converted into handle-oriented calls using short-lived
handles.  For example, a direct call can be implemented by acquiring a
handle, operating on the handle, and immediately releasing the handle.

```golang
// RecordOne converts a direct call into a handle-oriented call by allocating
// a short-lived handle.
func (inst *instrument) RecordOne(ctx context.Context, number core.Number, labelSet api.LabelSet) {
	h := inst.AcquireHandle(labelSet)
	defer h.Release()
	h.RecordOne(ctx, number)
}
```

The Meter implementation tracks an internal set of records, where
every record either: (1) has a current, un-released handle pinning it
in memory, (2) has pending updates that have not been collected, (3)
is a candidate for removing from memory.  The Meter maintains a
mapping from the pair (Instrument, LabelSet) to an active record.
Each active record contains an aggregator implementation, which is
responsible for incorporating a series of metric updates into the
current state.

Because of short-lived handles, the SDK may accumulate records that
are not associated with a user-held handle.  After these records are
collected they may be removed from the (Instrument, LabelSet) map of
active records.

## Aggregator implementations

The Aggregator interface supports combining multiple metric events
into a single aggregated state.  Different concrete aggregator types
provide different functionality and levels of concurrent performance.

Aggregators MUST support `Update()`, `Checkpoint()`, and `Merge()`.
`Update()` is called directly from the Meter in response to a metric
event, and may be called concurrently.  `Update()` is also passed the
user's telemetry context, which allows it to access the current trace
context and distributed correlations, however none of the built-in
aggregators use this information.

The `Checkpoint()` operation is called to atomically save a snapshot
of the Aggregator, since `Checkpoint()` may be called concurrently
with `Update()`.  The `Merge()` operation supports dimensionality
reduction by combining state from multiple aggregators into a single
Aggregator state.  

The Metric SDK SHOULD include six built-in aggregator types.  Two
standard aggregators MUST be included that implement standard counter
and gauge aggregations.

1. Counter: This aggregator MUST maintain a Sum.  In languages with
support for atomic operations, the Counter aggregator SHOULD be
implemented using only a single word of memory for the current state
and a single word of memory for its checkpoint.
1. Gauge: This aggregator MUST maintain the last value and its
timestamp.  In languages with support for atomic operations, this
aggregator's update operation SHOULD be implemented by a single memory
allocation--to store the value and timestamp--followed by an atomic
pointer swap; if the gauge is defined as monotonic, the should use
atomic compare-and-swap to ensure monotonicity.

Aggregators for [Measure metric instruments](api-metrics.md#measure)
are more challenging in nature than the Counter and Gauge aggregators,
since their task is to aggregate a series of individual measurements.
To perform this duty exactly requires storing the entire set of
measurements, which may be cost-prohibitive.  The common mechanisms
for exporting recorded measurements from a Measure metric instrument
are: as a series of raw measurements, as a summary of pre-determined
quantiles, and as a histogram with pre-determined boundaries.  A
definition for _Quantile_ is given below.

Four aggregators SHOULD be provided for use with Measure metric
instruments that support the common mechanisms for exporting recorded
measurements with a range of performance options.

1. MinMaxSumCount: This aggregator is intended as an inexpensive
alternative to the Sketch, Histogram, and Exact aggregators for
Measure instruments.  This aggregator MUST compute the min, max, sum,
and count of recorded measurements.  In languages with support for
atomic operations, this aggregator's update operation SHOULD maintain
its state using four independent atomic updates.  In this case, the
aggregator's update operation SHOULD NOT be atomic with respect to its
checkpoint operation, implying that a checkpoint could witness an
inconsistent state; that is intentional given the inexpensive nature
of this aggregator.
1. Sketch: This aggregator computes an approximate data structure that
MUST estimate quantiles of the distribution of recorded measurements.
Example algorithms that could be used to implement this aggregator are
include: GK-Sketch, DDSketch, Q-Digest, T-Digest, and HDR-Histogram.
The choice of algorithm should be made based on available libraries in
each language, but implementations with well-defined error bounds
SHOULD be preferred.
1. Histogram: This aggregator MUST compute a histogram with
pre-determined boundaries.  This aggregator MAY support quantile
estimation, but is generally intended for cases where a histogram will
be exported directly and the exporter wants explicit control over
histogram boundaries.
1. Exact: This aggregator MUST store an array of all recorded
measurements.  This aggregator MUST support exact quantile
computations and it MUST support exporting raw values in the order
they were recorded, however it is not required to support both of
these modes simultaneously (since computing quantiles requires sorting
the measurements).

### Quantile definition

When exporting a summary of recorded measurements for a Measure metric
instrument, it is common to report _quantiles_ of the distribution.
When computing quantiles from an exact aggregation (i.e., the complete
data set), the "nearest rank" definition of quantile SHOULD be used.
The nearest-rank definition ensures that the resulting value belongs
to the original data set.  Interpolation is not used in this method.

The definition for the nearest-rank quantile given here makes use of
the _cumulative distribution function_, a standard concept from
probability theory.  Quantiles are parameterized by `q`, where `0 <= q
<= 1`.  The value for quantile `q` is the least element of the
original data set at or above the point where the cumulative
distribution function equals `q`.

For example, taking a data set of five values `{10, 20, 30, 40, 50}`,
the `q=0.5` quantile (i.e., the median) equals 30, which is precisely
the point where the cumulative distribution function equals 0.5.

With an even-sized data set, for example `{10, 20, 30, 40}`, the
`q=0.5` quantile equals 30.  In this case, the cumulative distribution
function equals 0.5 halfway between 20 and 30 and the greater value is
selected as the nearest rank.

When using an approximate aggregator to compute estimated quantile
values, the nearest-rank quantile definition does not apply.

## Batcher implementation

The Batcher acts as the primary source of configuration for exporting
metrics from the SDK.  The two kinds of configuration are:

1. Given a metric instrument, choose which concrete aggregator type to apply for in-process aggregation.
1. Given a metric instrument, choose which dimensions to export by (i.e., the "grouping" function).

The first choice--which concrete aggregator type to apply--is made
whenever the Meter implementation encounters a new (Instrument,
LabelSet) pair.  Each concrete type of aggregator will perform a
different function.  Aggregators for counter and gauge instruments are
relatively straightforward, but many concrete aggregators are possible
for measure metric instruments.  The Batcher has an opportunity to
disable instruments at this point simply by returning a `nil`
aggregator.

The second choice--which dimensions to export by--affects how the
batcher processes records emitted by the Meter implementation during
collection.  During collection, the Meter implementation emits an
export record for each metric instrument with pending updates to the
Batcher.

During the collection pass, the Batcher receives a full set of
checkpointed aggregators corresponding to each (Instrument, LabelSet)
pair with an active record managed by the Meter implementation.
According to its own configuration, the Batcher at this point
determines which dimensions to aggregate for export; it computes a
checkpoint of (possibly) reduced-dimension export records ready for
export.

Batcher implementations support the option of being stateless or
stateful.  Stateless Batchers compute checkpoints which describe the
updates of a single collection period (i.e., deltas).  Stateful
Batchers compute checkpoints from over the process lifetime; these may
be useful for simple exporters but are prone to consuming a large and
ever-growing amount of memory, depending on LabelSet cardinality.

Two standard Batcher implementations are provided.

1. The "defaultkeys" Batcher reduces the export dimensions of each
metric instrument to the Recommended keys declared with the
instrument.
1. The "ungrouped" Batcher exports metric instruments at full
dimensionality; each LabelSet is exported without reducing dimensions.

## Controller implementation

A controller is needed to coordinate the decision to begin collection.
Controllers generally are responsible for binding the Meter
implementation, the Batcher, and the Exporter.

Once the decision has been made, the controller's job is to call
`Collect()` on the Meter implementation, then read the checkpoint from
the Batcher, then invoke the Exporter.

One standard "push" controller is provided, which triggers collection
using a fixed period.  The controller is responsible for flushing
metric events prior to shutting down the process.

Metric exporters that wish to pull metric updates are likely to
integrate a controller directly into the exporter itself.

## Exporter implementations

The exporter is called with a checkpoint of finished export records.
Most configuration decisions have been made before the exporter is
invoked, including which instruments are enabled, which concrete
aggregator types to use, and which dimensions to aggegate by.

There is very little left for the exporter to do other than format the
metric updates into the desired format and send them on their way.

## Multiple exporter support

The metric export pipeline specified here does not include explicit
support for multiple export pipelines.  In principle, any one of the
interfaces here could be satisfied by a multiplexing implementation,
but in practice, it will be costly to run multiple Batchers or
aggregators in parallel.

If multiple exporters are required, therefore, it is best if they can
share a single Batcher configuration.

## LabelEncoder optimizations

The Meter implementation and some Batcher implementations are required
to compute a unique key corresponding to a LabelSet, for the purposes
of locating an aggregator to use for metric updates.  Where possible,
Exporters can avoid a duplicate computation by providing a
LabelEncoder to the Meter implementation.

This optimization applies for any Exporter that will internally
compute a unique encoding for a set of labels, whether using a text or
a binary encoding.  For example, a dogstatsd Exporter will benefit by
providing its specific LabelEncoder implementation to the Meter
implementation; consequently, the export records it sees will be
accompanied by a pre-computed encoding of the export LabelSet.

## Metric descriptors

The metric descriptor contains a complete description of the metric
instrument, including the kind of metric (Counter, Gauge, or Measure)
and all arguments passed to the instrument's constructor.

Exporters MUST have a mechanism to lookup internal state based on the
metric descriptor.  This requirement could be satisfied by exposing
descriptors as reference objects (i.e., their memory address is
unique, can be used to lookup Exporter-specific state).  Another way
to meet this requirement is to give each distinct metric instrument a
unique identifier that is included in the export record.
