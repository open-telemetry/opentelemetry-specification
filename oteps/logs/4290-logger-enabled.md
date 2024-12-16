# Logger.Enabled

## Motivation

In applications requiring high performance,
while optimizing the performance of enabled logging is important,
it is often equally or more critical to minimize the overhead of logging
for disabled or un-exported logs.

The consumers of OpenTelemetry clients want to:

1. **Correctly** and **efficiently** bridge features
   like `LogLevelEnabled` in log bridge/appender implementations.
2. Avoid allocating memory to store a log record,
   avoid performing computationally expensive operations,
   and avoid exporting
   when emitting a log or event record is unnecessary.
3. Configure a minimum a log severity level on the SDK level.
4. Filter out log and event records when they are inside a span
   that has been sampled out (span is valid and has sampled flag of `false`).
5. **Efficiently** support high-performance logging destination
   like [Linux user_events](https://docs.kernel.org/trace/user_events.html)
   and [ETW (Event Tracing for Windows)](https://learn.microsoft.com/windows/win32/etw/about-event-tracing).
6. Allow **fine-grained** filtering control for logging pipelines
   when using an OpenTelemetry Collector is not feasible
   e.g. for mobile devices, serverless, IoT.

Without a `Logger.Enabled` check in the OpenTelemetry Logs API
and corresponding implementations in the SDK,
achieving this goal is not feasible.

## Explanation

For (1) (2), the user can use the Logs API `Logger.Enabled` function, which tells the user whether a `Logger` for given arguments is going to emit a log record.

For (3) (4), the user can declaratively configure the Logs SDK using `LoggerConfigurator` to set the `disabled`, `minimum_severity_level`, and maybe even `disabled_on_sampled_out_spans` of a `LoggerConfig`.

For (5) (6), the user can hook to `Logger.Enabled` Logs API calls by adding to the Logs SDK a `LogRecordProcessor` implementing `OnEnabled`.

## Internal details

From a technical perspective, how do you propose accomplishing the proposal? In particular, please explain:

* How the change would impact and interact with existing functionality
* Likely error modes (and how to handle them)
* Corner cases (and how to handle them)

While you do not need to prescribe a particular implementation - indeed, OTEPs should be about **behaviour**, not implementation! - it may be useful to provide at least one suggestion as to how the proposal *could* be implemented. This helps reassure reviewers that implementation is at least possible, and often helps them inspire them to think more deeply about trade-offs, alternatives, etc.

## Trade-offs and mitigations

_What are some (known!) drawbacks? What are some ways that they might be mitigated?_

## Prior art and alternatives

_What are some prior and/or alternative approaches? What are some ideas that you have rejected?_

## Open questions

_What are some questions that you know aren't resolved yet by the OTEP? These may be questions that could be answered through further discussion, implementation experiments, or anything else that the future may bring._

## Future possibilities

_What are some future changes that this proposal would enable?_
