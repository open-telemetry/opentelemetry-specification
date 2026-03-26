# Remove the LabelSet object from the metrics API

The proposal is to remove the current [`LabelSet`](./0049-metric-label-set.md)
API and change all the current APIs that accept LabelSet to accept directly the
labels (list of key-values, or a map of key-values based on the language
capabilities).

## Motivation

The [`LabelSet`](./0049-metric-label-set.md) API type was added to serve as a
handle on a predefined set of labels for the Metrics API.

This API represents an optimization for the current metrics API that allows the
implementations to avoid encoding and checking labels restrictions multiple
times for the same set of lables. Usages and implementations of the metrics API
have shown that LabelSet adds extra unnecessary complexity with little benefit.

Some users prefer to avoid this performance optimization for the benefit of a
cleaner code and OpenTelemetry needs to address them as well, so this means that
it is important for OpenTelemetry to support record APIs where users can pass
directly the labels.

OpenTelemetry can always add this optimization later (backward compatible
change) if we determine that it is very important to have.

## Trade-offs and mitigations

In case where performance matters, here are the ways to achieve almost the same performance:

- In the current API if a `LabelSet` is reused across multiple individual
records across different instruments (one record to every instrument) then user
can use the batch recording mechanism, so internally the SDK can do the labels
encoding once.
- In the current API if a `LabelSet` is used multiple times to record to the
same instrument then user can use instrument bindings.
- In the current API if a `LabelSet` is used across multiple batch recordings,
and this pattern becomes very important, then OpenTelemetry can add support for
batches to accept bindings.

To ensure that the current batch recording can help in scenarios where there are
some local conditions that control which measurements to be recorded, the
recommendation is to have the `newBatchRecorder` return an interface called
`BatchRecorder` that can be used to add `measurement` and when all entries are
added call `record` to record all the `measurements`.

## Prior art and alternatives

Almost all the existing Metric libraries do not require users to create
something like LabelSet when recording a value.
