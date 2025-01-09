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
   e.g., for mobile devices, serverless, or IoT.

Without a `Logger.Enabled` check in the OpenTelemetry Logs API
and corresponding implementations in the SDK,
achieving this goal is not feasible.

OpenTelemetry Logs SDK users require:

- A declarative configuration to conveniently address
  the most popular use cases.
- A dynamic hook for advanced customization and flexibility.

The main purpose of this OTEP is to have foundations for:

- extending the SDK's `LoggerConfig` with `minimum_severity_level` field,
- extending the `LogRecordProcessor` with an `Enabled` operation,

and address [Specify how Logs SDK implements Enabled #4207](https://github.com/open-telemetry/opentelemetry-specification/issues/4207).

## Explanation

For (1) (2), the user can use the Logs API `Logger.Enabled` function,
which tells the user whether a `Logger` for given arguments
is going to emit a log record.

For (3), the user can declaratively configure the Logs SDK
using `LoggerConfigurator` to set the `minimum_severity_level`
of a `LoggerConfig` for given `Logger`.

For (4), the user can use the Tracing API to check whether
there is a sampled span in the current context before creating
and emitting a log record.

For (5) (6), the user can hook to `Logger.Enabled` Logs API calls
by adding to the Logs SDK a `LogRecordProcessor` implementing `Enabled`
(or alternatively other hook such as `LogRecordFilterer`;
see [here](#separate-logrecordfilterer-abstraction)).

## Internal details

Regarding (1) (2), the Logs API specification has already introduced `Logger.Enabled`:

- [Add Enabled method to Logger #4020](https://github.com/open-telemetry/opentelemetry-specification/pull/4020)
- [Define Enabled parameters for Logger #4203](https://github.com/open-telemetry/opentelemetry-specification/pull/4203)

The addition of `LoggerConfig.minimum_severity_level` is supposed
to serve the (3) use case in an easy-to-setup and efficient way.

Regarding (4) the API callers can decide whether to emit log records
for spans that are not sampled. Example in Go:

<!-- markdownlint-disable no-hard-tabs -->
```go
if trace.SpanContextFromContext(ctx).IsSampled() && logger.Enabled(ctx, params) {
	logger.Emit(ctx, createLogRecord(payload))
}
```
<!-- markdownlint-enable no-hard-tabs -->

For instrumentation libraries, the API-level control might be more appropriate,
than configuring such behavior on the SDK level.

The addition of `LogRecordProcessor.Enabled` is necessary for
use cases where filtering is dynamic and coupled to processing,
such as (5) and (6).

Both `LoggerConfig` and registered `LogRecordProcessors` take part
in the evalaution of the `Logger.Enabled` operation.
If it returns `true`, meaning the logger is enabled,
then the `LogRecordProcessors` are evaluated.
In such cases, `false` is returned only if all registered
`LogRecordProcessors` return `false` in their `Enabled` calls,
as this means no processor will process the log record.
Pseudo-code:

<!-- markdownlint-disable no-hard-tabs -->
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
<!-- markdownlint-enable no-hard-tabs -->

## Trade-offs and mitigations

For some langagues extending the `LogRecordProcessor` may be seen as breaking.
For these languages implementing `LogRecordProcessor.Enabled` must be optional.
The SDK `LogRecordProcessor` must return `true` if `Enabled` is not implemented.
This approach is currently taken by OpenTelemetry Go.

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
enabling efficient log emission to user_events.

Regarding the (6) use case,
OpenTelemetry Go Contrib provides
[`minsev` processor](https://pkg.go.dev/go.opentelemetry.io/contrib/processors/minsev)
allowing distinict minimum severity levels
for different log destinations.

## Alternatives

Below are some alternatives that would be further explored
during the Development phase.

### Dynamic Evaluation in LoggerConfig

There is a [proposal](https://github.com/open-telemetry/opentelemetry-specification/issues/4207#issuecomment-2501688210)
suggested dynamic evaluation in `LoggerConfig` instead of static configuration
to make the `LoggerConfig` to support dynamic evaluation.

However, since the purpose of `LoggerConfig` is static configuration,
and use cases (5) and (6) are tied to log record processing,
extending `LogRecordProcessor` seem more appropriate.

### Separate LogRecordFilterer Abstraction

There is a [proposal](https://github.com/open-telemetry/opentelemetry-specification/issues/4207#issuecomment-2354859647)
to add a distinct `LogRecordFilterer` abstraction.
Here is [a dicsussion](https://github.com/open-telemetry/opentelemetry-specification/pull/4290#discussion_r1887795096).

However, this approach is less suited for use case (5)
and offers limited flexibility for use case (6).
The initial feedback after [an experiment](https://github.com/open-telemetry/opentelemetry-go/pull/5825)
with `LogRecordFilterer` was that it can make composing
processing pipelines harder and more bug-prone.

Adding `Enabled` to `LogRecordProcessor` should be:

- Simpler. There is no need for separate code for
  global filterers and processor filterers.
- More composable. Filtering could be applied at any place,
  even after some pre-processing.
- More cohesive: Filtering can be coupled to processing,
  e.g. making a rate limiting processor should be more
  straighforward.

## Open questions

### Need of LogRecordExporter.Enabled

There is a [proposal](https://github.com/open-telemetry/opentelemetry-specification/pull/4290#discussion_r1878379347)
to additionally extend `LogRecordExporter` with `Enabled` operation.
However, at this point of time, this extension seems unnecessary.
The `LogRecordExporter` abstraction is primarily designed
for batching exporters, whereas the (5) use cases is focused
on synchronous exporters, which can be implemented as a `LogRecordProcessor`.
Skipping this additional level of abstraction would also reduce overhead.
It is worth noticing that, `LogRecordExporter.Enabled`
can always be added in future.

## Future possibilities

### Extending LoggerConfig

In future, more fields can be added to `LoggerConfig`
in order to conveniently address the most popular use cases.

One example could be the addition of `LoggerConfig.trace_based`.
This configuration can be used only capture the log records that are
within sampled spans. It could serve the (4) use case in a declarative way
configured on the SDK level. This configuration was discussed
e.g. [here](https://github.com/open-telemetry/opentelemetry-specification/pull/4290#discussion_r1898672657)
and is beyond the scope of this OTEP.

### Extending Logger.Enabled

The `Enabled` API could be extended in the future
to include additional parameters, such as `Event Name`,
for processing event records.
This would fit well a simple design where `LogRecordProcessor`
is used for both log records and event records.
References:

- [Add EventName parameter to Logger.Enabled #4220](https://github.com/open-telemetry/opentelemetry-specification/issues/4220).
- OpenTelemetry Go: [[Prototype] log: Events support with minimal non-breaking changes #6018](https://github.com/open-telemetry/opentelemetry-go/pull/6018)
