# A Proposal For SDK Support for Configurable Batching and Aggregations (Basic Views)

Add support to the default SDK for the ability to configure Metric Aggregations.

## Motivation

OpenTelemetry's architecture separates the concerns of instrumentation and operation. The Metric Instruments
provided by the Metric API are all defined to have a default aggregation. And, by default, aggregations are
performed with all Labels being used to define a unit of aggregation. Although this is a good default
configuration for the SDK to provide, more configurability is needed.

There are 3 main use-cases that this proposal is intended to address:

1) The application developer/operator wishes to use an aggregation other than the default provided by the SDK
for a given instrument or set of instruments.
2) An exporter author wishes to inform the SDK what "Temporality" (delta vs. cumulative) the resulting metric
data points represent. "Delta" means only metric recordings since the last reporting interval are considered
in the aggregation, and "Cumulative" means that all metric recordings over the lifetime of the Instrument are
considered in the aggregation.
3) The application developer/operator wishes to constrain the cardinality of labels for metrics being reported
to the metric vendor/backend of choice.

## Explanation

I propose a new feature for the default SDK, available on the interface of the SDK's MeterProvider implementation, to configure
the batching strategies and aggregations that will be used by the SDK when metric recordings are made. This is the beginnings
of a "Views" API, but does not intend to implement the full View functionality from OpenCensus.

The basic API has two parts.

* InstrumentSelector - Enables specifying the selection of one or more instruments for the configuration to apply to.
  - Selection options include: the instrument type (Counter, ValueRecorder, etc), and a regex for instrument name.
  - If more than one option is provided, they are considered additive.
  - Example: select all ValueRecorders whose name ends with ".duration".
* View - configures how the batching and aggregation should be done.
  - 3 things can be specified: The aggregation (Sum, MinMaxSumCount, Histogram, etc), the "temporality" of the batching,
    and a set of pre-defined labels to consider as the subset to be used for aggregations.
    - Note: "temporality" can be one of "DELTA" and "CUMULATIVE" and specifies whether the values of the aggregation
      are reset after a collection is done or not, respectively.
  - If not all are specified, then the others should be considered to be requesting the default.
  - Examples:
    - Use a MinMaxSumCount aggregation, and provide delta-style batching.
    - Use a Histogram aggregation, and only use two labels "route" and "error" for aggregations.
    - Use a quantile aggregation, and drop all labels when aggregating.

In this proposal, there is only one View associated with each selector.

As a concrete example, in Java, this might look something like this:

```java
 // get a handle to the MeterSdkProvider (note, this is concrete name of the default SDK class in java, not a general SDK)
 MeterSdkProvider meterProvider = OpenTelemetrySdk.getMeterProvider();

 // create a selector to select which instruments to customize:
 InstrumentSelector instrumentSelector = InstrumentSelector.newBuilder()
  .instrumentType(InstrumentType.COUNTER)
  .build();

 // create a configuration of how you want the metrics aggregated:
 View view =
      View.create(Aggregations.minMaxSumCount(), Temporality.DELTA);

 //register the configuration with the MeterSdkProvider
 meterProvider.registerView(instrumentSelector, view);
```

## Internal details

This OTEP does not specify how this should be implemented in a particular language, only the functionality that is desired.

A prototype with a partial implementation of this proposal in Java is available in PR form [here](https://github.com/open-telemetry/opentelemetry-java/pull/1412)

## Trade-offs and mitigations

This does not intend to deliver a full "Views" API, although it is the basis for one. The goal here is
simply to allow configuration of the batching and aggregation by operators and exporter authors.

This does not intend to specify the exact interface for providing these configurations, nor does it
consider a non-programmatic configuration option.

## Prior art and alternatives

* Prior Art is probably mostly in the [OpenCensus Views](https://opencensus.io/stats/view/) system.
* Another [OTEP](https://github.com/open-telemetry/oteps/pull/89) attempted to address building a Views API.

## Open questions (to be resolved in an official specification)

1. Should custom aggregations be allowable for all instruments? How should an SDK respond to a request for a non-supported aggregation?
2. Should the requesting of DELTA vs. CUMULATIVE be only available via an exporter-only API, rather than generally available to all operators?
3. Is regex-based name matching too broad and dangerous? Would the alternative (having to know the exact name of all instruments to configure) be too onerous?
4. Is there anything in this proposal that would make implementing a full Views API (i.e. having multiple, named aggregations per instrument) difficult?
5. How should an exporter interact with the SDK for which it is configured, in order to change aggregation settings?
6. Should the first implementation include label reduction, or should that be done in a follow-up OTEP/spec?
7. Does this support disabling an aggregation altogether, and if so, what is the interface for that?
8. What is the precedence of selectors, if more than one selector can apply to a given Instrument?

## Future possibilities

What are some future changes that this proposal would enable?

- A full-blown views API, which would allow multiple "views" per instrument. It's unclear how an exporter would specify which one it wanted, or if it would all the generated metrics.
- Additional non-programmatic configuration options.
