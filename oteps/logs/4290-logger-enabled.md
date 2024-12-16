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

For (1) (2), the user can use the Logs API `Logger.Enabled` function,
which tells the user whether a `Logger` for given arguments
is going to emit a log record.

For (3) (4), the user can declaratively configure the Logs SDK
using `LoggerConfigurator` to set the `disabled`, `minimum_severity_level`,
and maybe even `disabled_on_sampled_out_spans` of a `LoggerConfig`.

For (5) (6), the user can hook to `Logger.Enabled` Logs API calls
by adding to the Logs SDK a `LogRecordProcessor` implementing `Enabled`.

## Internal details

Regarding (1) (2), the Logs API specification has already introduced `Logger.Enabled`:
- [Add Enabled method to Logger #4020](https://github.com/open-telemetry/opentelemetry-specification/pull/4020)
- [Define Enabled parameters for Logger #4203](https://github.com/open-telemetry/opentelemetry-specification/pull/4203)

The main purpose of this OTEP is to extend the SDK's `LoggerConfig`
with `minimum_severity_level` and optionally `disabled_on_sampled_out_spans`
and to extend the `LogRecordProcessor` with an `Enabled` operation.

The addition of `LoggerConfig.minimum_severity_level` is supposed
to serve the (3) use case in an easy to setup and efficient way.

_(4) (5) (6) TO BE DESCRIBED_

Both `LoggerConfig` and registered `LogRecordProcessors` take part
in the evalaution of the `Logger.Enabled`.
First the `LoggerConfig` is evaluated. If it is going to return
`true`, as it mean that Logger is enabled,
and `LogRecordProcessors` are going to be evaluated.
In such case `false` is returned only if all registered
`LogRecordProcessors'` `Enabled` calls returned `false`,
as it means that there no processor does is going to process
the log record.
Pseudo-code:

```go
func (l *logger) Enabled(ctx context.Context, param EnabledParameters) bool {
	config := l.config()
	if config.Disabled {
		// The logger is disabled.
		return false
	}
	if params.Severity > config.MinSeverityLevel {
		// The severity is less severe than the minimum level.
		return false
	}

	processors := l.provider.processors()
	for _, p := range processors {
		if p.Enabled(ctx, param) {
			// At least one processor will process the record.
			return true
		}
	}
	// No processor will process the record.
	return false
}
```

_TBD_

## Trade-offs and mitigations

_What are some (known!) drawbacks? What are some ways that they might be mitigated?_

## Prior art and alternatives

_What are some prior and/or alternative approaches? What are some ideas that you have rejected?_


- [Specify how Logs SDK implements Enabled #4207](https://github.com/open-telemetry/opentelemetry-specification/issues/4207)

## Open questions

_What are some questions that you know aren't resolved yet by the OTEP? These may be questions that could be answered through further discussion, implementation experiments, or anything else that the future may bring._

## Future possibilities

The `Enabled` API may in future also accept
an optional `Event Name` parameter
given it will be relevant for processing event records.
