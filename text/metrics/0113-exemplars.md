# Integrate Exemplars with Metrics

This OTEP adds exemplar support to aggregations defined in the Metrics SDK.

## Definition

Exemplars are example data points for aggregated data. They provide specific context to otherwise general aggregations. For histogram-type metrics, exemplars are points associated with each bucket in the histogram giving an example of what was aggregated into the bucket. Exemplars are augmented beyond just measurements with references to the sampled trace where the measurement was recorded and labels that were attached to the measurement.

## Motivation

Defining exemplar behaviour for aggregations allows OpenTelemetry to support exemplars in Google Cloud Monitoring.

Exemplars provide a link between metrics and traces. Consider a user using a Histogram aggregation to track response latencies over time for a high QPS server. The histogram is composed of buckets based on the speed of the request, for example, "there were 55 requests that took 400-500 milliseconds". The user wants to troubleshoot slow requests, so they would need to find a trace where the latency was high. With exemplars, the user is able to get an exemplar trace from a high latency bucket, an exemplar trace from a low latency bucket, and compare them to figure out the reason for the high latency.

Exemplars are meaningful for all aggregations where relevant traces can provide more context to the aggregation, as well as when exemplars can display specific information not otherwise shown in the aggregation (for example, the full set of labels where they otherwise might be aggregated away).

## Internal details

An exemplar is a `RawValue`, which is defined as:

```
message RawValue {
  // Numerical value of the measurement that was recorded. Only one of these two fields is
  // used for the data, depending on its type
  double double_value = 0;
  int64 int64_value = 1;
  
  // Exact time that the measurement was recorded
  fixed64 time_unix_nano = 2;

  // 'label:value' map of all labels that were provided by the user recording the measurement
  repeated opentelemetry.proto.common.v1.StringKeyValue labels = 3;

  // Span ID of the current trace
  optional bytes span_id = 4;

  // Trace ID of the current trace
  optional bytes trace_id = 5;

  // When sample_count is non-zero, this exemplar has been chosen in a statistically
  // unbiased way such that the exemplar is representative of `sample_count` individual events
  optional double sample_count = 6;
}
```

Exemplar collection should be enabled through an optional parameter (disabled by default), and when not enabled, there should be no collection/logic performed related to exemplars. This is to ensure that when necessary, aggregators are as high performance as possible. Aggregators should also have a parameter to determine whether exemplars should only be collected if they are recorded during a sampled trace, or if tracing should have no effect on which exemplars are sampled. This allows aggregations to prioritize either the link between metrics and traces or the statistical significance of exemplars, when necessary.

[#347](https://github.com/open-telemetry/opentelemetry-specification/pull/347) describes a set of standard aggregators in the metrics SDK. Here we describe how exemplars could be implemented for each aggregator.

### Exemplar behaviour for standard aggregators

#### HistogramAggregator

The HistogramAggregator MUST (when enabled) maintain a list of exemplars whose values are distributed across all buckets of the histogram (there should be one or more exemplars in every bucket that has a population of at least one sample-able measurement). Implementations SHOULD NOT retain an unbounded number of exemplars.

#### Sketch

A Sketch aggregator SHOULD maintain a list of exemplars whose values are spaced out across the distribution. There is no specific number of exemplars that should be retained (although the amount SHOULD NOT be unbounded), but the implementation SHOULD pick exemplars that represent as much of the distribution as possible. (Specific details not defined, see open questions.)

#### Last-Value

Most (if not all) Last-Value aggregators operate asynchronously and do not ever interact with context. Since the value of a Last-Value is the last measurement (essentially the other parts of an exemplar), exemplars are not worth implementing for Last-Value.

#### Exact

The Exact aggregator will function by maintaining a list of `RawValue`s, which contain all of the information exemplars would carry. Therefore the Exact aggregator will not need to maintain any exemplars.

#### Counter

Exemplars give value to counter aggregations in two ways: One, by tying metric and trace data together, and two, by providing necessary information to re-create the input distribution. When enabled, the aggregator will retain a bounded list of exemplars at each checkpoint, sampled from across the distribution of the data. Exemplars should be sampled in a statistically significant way.

#### MinMaxSumCount

Similar to Counter, MinMaxSumCount should retain a bounded list of exemplars that were sampled from across the input distribution in a statistically significant way.

#### Custom Aggregators

Custom aggregators MAY support exemplars by maintaining a list of exemplars that can be retrieved by exporters. Custom aggregators should select exemplars based on their usage by the connected exporter (for example, exemplars recorded for Google Cloud Monitoring should only be retained if they were recorded within a sampled trace).

Exemplars will always be retrieved from aggregations (by the exporter) as a list of RawValue objects. They will be communicated via a

```
optional repeated RawValue exemplars = 6
```

attribute on the `Metric` object.

## Trade-offs and mitigations

Performance (in terms of memory usage and to some extent time complexity) is the main concern of implementing exemplars. However, by making recording exemplars optional, there should be minimal overhead when exemplars are not enabled.

## Prior art and alternatives

Exemplars are implemented in [OpenCensus](https://github.com/census-instrumentation/opencensus-specs/blob/master/stats/Exemplars.md#exemplars), but only for HistogramAggregator. This OTEP is largely a port from the OpenCensus definition of exemplars, but it also adds exemplar support to other aggregators.

[Cloud monitoring API doc for exemplars](https://cloud.google.com/monitoring/api/ref_v3/rpc/google.api#google.api.Distribution.Exemplar)

## Open questions

- Exemplars usually refer to a span in a sampled trace. While using the collector to perform tail-sampling, the sampling decision may be deferred until after the metric would be exported. How do we create exemplars in this case?

- We don’t have a strong grasp on how the sketch aggregator works in terms of implementation - so we don’t have enough information to design how exemplars should work properly.

- The spec doesn't yet define a standard set of aggregations, just default aggregations for standard metric instruments. Since exemplars are always attached to particular aggregations, it's impossible to fully specify the behavior of exemplars.
