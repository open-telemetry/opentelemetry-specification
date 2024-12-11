# Logger.Enabled

## Motivation

In applications requiring extremely high performance,
minimizing the cost of logging when it is not exported is often more critical
than optimizing the cost of logging when the log record is of interest.

The consumers of OpenTelemetry clients want to:

1. **Correctly** and **efficiently** bridge features like `LogLevelEnabled` in log bridge/appender implementations.
2. Avoid allocating memory to store a log record, avoid performing computationally expensive operations and avoid exporting when emitting a log or event record is unnecessary.
3. Configure a minimum a log serverity level on the SDK level.
4. Filter out log and event records when they are not inside a recording span.
5. Have **fine-grained** filtering control for logging pipelines without using an OpenTelemetry Collector (e.g. mobile devices, serverless, IoT).
6. **Efficiently** support high-performance logging destination like Linux user_events and ETW (Event Tracing for Windows).
7. Add sampling for logging.

Without a `Logger.Enabled` check in the OpenTelemetry Logs API
and corresponding implementations in the SDK,
achieving this goal is not feasible.

## Explanation

For (1) (2), the user can use the Logs API `Logger.Enabled` function, which tells the user wheteher a `Logger` for given arguments is going to emit a log record.

For (3) (4), the user can declarativly configure the Logs SDK using `LoggerConfigurator` to set the `disabled`, `minimum_severity_level`, `disabled_not_recorded_spans` of a `LoggerConfig`.

For (5) (6) (7), the user can hook to `Logger.Enabled` Logs API calls by adding to the Logs SDK a `LogRecordProcessor` implementing `OnEnabled`.

## Internal details

From a technical perspective, how do you propose accomplishing the proposal? In particular, please explain:

* How the change would impact and interact with existing functionality
* Likely error modes (and how to handle them)
* Corner cases (and how to handle them)

While you do not need to prescribe a particular implementation - indeed, OTEPs should be about **behaviour**, not implementation! - it may be useful to provide at least one suggestion as to how the proposal *could* be implemented. This helps reassure reviewers that implementation is at least possible, and often helps them inspire them to think more deeply about trade-offs, alternatives, etc.

## Trade-offs and mitigations

What are some (known!) drawbacks? What are some ways that they might be mitigated?

Note that mitigations do not need to be complete *solutions*, and that they do not need to be accomplished directly through your proposal. A suggested mitigation may even warrant its own OTEP!

## Prior art and alternatives

What are some prior and/or alternative approaches? For instance, is there a corresponding feature in OpenTracing or OpenCensus? What are some ideas that you have rejected?

## Open questions

What are some questions that you know aren't resolved yet by the OTEP? These may be questions that could be answered through further discussion, implementation experiments, or anything else that the future may bring.

## Future possibilities

What are some future changes that this proposal would enable?
