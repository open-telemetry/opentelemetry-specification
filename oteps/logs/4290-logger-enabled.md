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

Address [Specify how Logs SDK implements Enabled #4207](https://github.com/open-telemetry/opentelemetry-specification/issues/4207).

## Explanation

For (1) (2), the user can use the Logs API `Logger.Enabled` function,
which tells the user whether a `Logger` for given arguments
is going to emit a log record.

For (3), the user can declaratively configure the Logs SDK
using `LoggerConfigurator` to set the `minimum_severity_level`
of a `LoggerConfig`.

For (4), the user can use the Tracing API to check whether
there is a sampled span in the current context before creating
and emitting log record.
However, the user can may also want to declaratively configure the Logs SDK
using `LoggerConfigurator` to set the `disabled_on_sampled_out_spans`
of a `LoggerConfig`.

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

The addition of `LoggerConfig.disabled_on_sampled_out_spans` can serve the (4)
use case in a declarative way configured on the SDK level
if the user would want to only capture the log records that are
within sampled spans.

The addition of `LogRecordProcessor.Enabled` is necessary for
use cases where the filtering is dynamic and coupled
to the processing such as (5) and (6).

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
		// The severity is less severe than the logger minimum level.
		return false
	}
	if config.DisabledNotSampledSpans && !trace.SpanContextFromContext(ctx).IsSampled() {
		// The logger is disabled on sampled out spans.
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

## Trade-offs and mitigations

For some langagues extending the `LogRecordProcessor` may be seen as breaking.
For these languages implementing `LogRecordProcessor.Enabled` must be optional.
The SDK `LogRecordProcessor` must return `true` if `Enabled` is not implemented.
This is the approach currently taken by OpenTelemetry Go.

## Prior art

`Logger.Enabled` is already defined by:

- [OpenTelemetry C++](https://github.com/open-telemetry/opentelemetry-cpp/blob/main/api/include/opentelemetry/logs/logger.h)
- [OpenTelemetry Go](https://github.com/open-telemetry/opentelemetry-go/blob/main/log/logger.go)
- [OpenTelemetry PHP](https://github.com/open-telemetry/opentelemetry-php/blob/main/src/API/Logs/LoggerInterface.php)
- [OpenTelemetry Rust](https://github.com/open-telemetry/opentelemetry-rust/blob/main/opentelemetry/src/logs/logger.rs)

`LoggerConfig` (with only `disabled`) is already defined by:

- [OpenTelemetry Java](https://github.com/open-telemetry/opentelemetry-java/blob/main/sdk/logs/src/main/java/io/opentelemetry/sdk/logs/internal/LoggerConfig.java)
- [OpenTelemetry PHP](https://github.com/open-telemetry/opentelemetry-php/blob/main/src/SDK/Logs/LoggerConfig.php)

`LogRecordProcessor.Enabled` is already defined by:

- [OpenTelemetry Go](https://github.com/open-telemetry/opentelemetry-go/tree/main/sdk/log/internal/x)
- [OpenTelemetry Rust](https://github.com/open-telemetry/opentelemetry-rust/blob/main/opentelemetry-sdk/src/logs/log_processor.rs)

Regarding the (5) use case,
OpenTelemetry Rust provides
[OpenTelemetry Log Exporter for Linux user_events](https://github.com/open-telemetry/opentelemetry-rust-contrib/blob/1cb39edbb6467375f71f5dab25ccbc49ac9bf1d5/opentelemetry-user-events-logs/src/logs/exporter.rs)
which enables emitting logs efficiently to user_events.

Regarding the (6) use case,
OpenTelemetry Go Contrib provides
[`minsev` processor](https://pkg.go.dev/go.opentelemetry.io/contrib/processors/minsev)
which enables to have different severity levels
for different log record destinations.

## Alternatives

There was a [proposal](https://github.com/open-telemetry/opentelemetry-specification/issues/4207#issuecomment-2501688210)
to make the `LoggerConfig` to support dynamic evaluation
instead of supporting only static configuration.
However, it seems that the purpose of the `LoggerConfig` is static configuration.
Moreover, both (5) and (6) use cases are coupled to log record processing,
therefore it seems more straighforward to extend `LogRecordProcessor`.

There was a [proposal](https://github.com/open-telemetry/opentelemetry-specification/issues/4207#issuecomment-2354859647)
to add a separate `LogRecordFilterer` abstraction.
However, it does not looks well-suited for (5) use case
and also would not give a lot flexibility for (6) use case.

## Open questions

At this point of time, it is not yet known if `LoggerConfig`
needs a new `disabled_on_sampled_out_spans` field.
It is difficult to know whether it is not only the API caller
who should know whether the log record should not be emitted
when the span is not sampled. For instrumentation libraries
it may make more sense to control it on the API level, e.g.:

```go
if trace.SpanContextFromContext(ctx).IsSampled() && logger.Enabled(ctx, params) {
	logger.Emit(ctx, createLogRecord(payload))
}
```

## Future possibilities

The `Enabled` API may in future also accept
an optional `Event Name` parameter
given it will be relevant for processing event records.
