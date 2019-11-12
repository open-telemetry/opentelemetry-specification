# Metric SDK

_This document is derived from the Golang Metrics SDK prototype.  See
the currently open PRs:_
1. [Pipeline and stdout exporter](https://github.com/open-telemetry/opentelemetry-go/pull/265)
1. [Dogstatsd exporter](https://github.com/jmacd/opentelemetry-go/pull/7)
1. [Prometheus exporter](https://github.com/open-telemetry/opentelemetry-go/pull/296)

## Meter implementation

The Meter API provides methods to create metric instruments, metric
instrument handles, and label sets.  This document describes the
standard Meter implementation and supporting packages used to build
a complete metric export pipeline.

The Meter implementation lies at the bottom of the export pipeline,
where it's primary job is to maintain active state about pending
metric updates.  The most important requirement placed on the Meter
implementation is that be able to "forget" state about metric updates
after they are collected.

The Meter implementation supports all three metric [calling
conventions](api-metrics-user.md): handle-oriented calls, direct
calls, and RecordBatch calls.  Of these three calling conventions,
direct calls and RecordBatch calls can be easily converted into
handle-oriented calls using short-lived handles.  For example, a
direct call is implemented by acquiring a handle, operating on the
handle, and immediately releasing the handle.

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
in memory, (2) has pending updates that have not been collected.  The
Meter maintains a mapping from the pair (Instrument, LabelSet) to an
active record.  Each active record contains an Aggregator
implementation, which is responsible for incorporating a series of
updates into the current state.

Note that storing a map of (Instrument, LabelSet) implies that the
Meter implementation is not directly involved in dimensionality
reduction.  Active records are maintained according to the complete
set of labels in the LabelSet.  If the export pipeline will reduce
dimensionality of the data, that will occur in the collection pass.
The Meter implementation does not reduce dimensionality "up front".

The Meter implementation SHOULD ensure that operations on instrument
handles be fast, bypassing the map lookup described above.  Metric
updates made via an instrument handle, where the aggregator is defined
by simple atomic operations, should follow a very short code path.

Because of short-lived handles, the SDK may accumulate records that
are not associated with a user-held handle.  After these records are
collected they may be removed from the (Instrument, LabelSet) map of
active records.  Meter implementations MUST ensure that there are no
lost updates as a result of clearing entries from the map.

The Meter implementation provides a `Collect()` method to initiate
collection, which MUST prevent concurrent collection.  During the
collection pass, the Meter implementation checkpoints each active
Aggregator and passes it to the Batcher for processing.

This document does not specify how to coordinate synchronization
between user-facing metric updates and metric collection activity,
however Meter implementations SHOULD make efforts to avoid lock
contention by holding locks only briefly or using lock-free
techniques.

## Aggregator implementations

The Aggregator interface supports comnbining multiple metric events
into a single aggregated state.  Different concrete Aggregator types
provide different functionality and levels of concurrent performance.

Aggregators support `Update()`, `Checkpoint()`, `Merge()`, and
`Clone()` operations.  `Update()` is called directly from the Meter in
response to a metric event, and may be called concurrently.
`Update()` is also passed the user's telemetry context, which allows
is to access the current trace context and distributed correlations,
honwever none of the built-in aggregators use this information.

The `Checkpoint()`, `Merge()`, and `Clone()` operations are called in
the collection code path to (atomically) save the current aggregator
state, to combine two aggregator states, and to produce a copy for
maintaining state outside of the Meter implementation.

The Metric SDK comes with six built-in Aggregator types, two of which
are standard for use with counters and gauges.

1. Counter: This aggregator maintains a Sum using only a single word of memory.
1. Gauge: This aggregator maintains a pair containing the last value and its timestamp.

Four aggregators are intended for use with measure metrics.

1. MinMaxSumCount: This aggregator computes the min, max, sum, and count using only four words of memory.
1. Sketch: This aggregator computes an approximate data structure that can estimate quantiles.  Example algorithms include GK-Sketch, Q-Digest, T-Digest, DDSketch, and HDR-Histogram.  The choice of algorithm should be made based on available libraries in each language.
1. Histogram: This aggregator computes a histogram with pre-determined boundaries.  This may be used to estimate quantiles, but is generally intended for cases where a histogram will be exported directly.
1. Exact: This aggregator computes an array of all values, supporting exact quantile computations in the exporter.

## Batcher implementation

The Batcher acts as the primary source of configuration for exporting
metrics from the SDK.  The two kinds of configuration are:

1. Given a metric instrument, choose which concrete Aggregator type to apply for in-process aggregation.
1. Given a metric instrument, choose which dimensions to export by (i.e., the "grouping" function).

The first choice--which concrete Aggregator type to apply--is made
whenever the Meter implementation encounters a new (Instrument,
LabelSet) pair.  Each concrete type of Aggregator will perform a
different function.  Aggregators for counter and gauge instruments are
relatively straightforward, but many concrete Aggregators are possible
for measure metric instruments.  The Batcher has an opportunity to
disable instruments at this point simply by returning a `nil`
Aggregator.

The second choice--which dimensions to export by--affects how the
batcher processes records emitted by the Meter implementation during
collection.  During collection Meter implementation emits an Export
Record for each metric instrument with pending updates to the Batcher.

The Export Record consists of a Descriptor (a description of the
instrument), a LabelSet (the set of labels), and a checkpointed
Aggregator.  The checkpointed Aggregator passed from the Meter
implementation to the Batcher contains a delta summarizing all events
that happened since the prior collection pass.

During the collection pass, the Batcher receives a full set of
checkpointed Aggregators corresponding to each (Instrument, LabelSet)
pair with an active record managed by the Meter implementation.
According to its own configuration, the Batcher at this point
determines which dimensions to aggregate for export; it computes a
checkpoint of (possibly) reduced-dimension Export Records ready for
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

The exporter is called with a checkpoint of finished Export Records.
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
Aggregators in parallel.

If multiple exporters are required, therefore, it is best if they can
share a single Batcher configuration.
