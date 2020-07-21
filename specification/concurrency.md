# Concurrency and Thread-Safety of OpenTelemetry API

For languages which support concurrent execution the OpenTelemetry APIs provide
specific guarantees and safeties. Not all of API functions are safe to
be called concurrently. Function and method documentation must explicitly
specify whether it is safe or no to make concurrent calls and in what
situations.

The following are general recommendations of concurrent call safety of
specific subsets of the API.

## Trace API

**TracerProvider** - all methods are safe to be called concurrently.

**Tracer** - all methods are safe to be called concurrently.

**SpanBuilder** - It is not safe to concurrently call any methods of the
same SpanBuilder instance. Different instances of SpanBuilder can be safely
used concurrently by different threads/coroutines, provided that no single
SpanBuilder is used by more than one thread/coroutine.

**Span** - All methods of Span are safe to be called concurrently.

**Event** - Events are immutable and safe to be used concurrently. Lazy
initialized events must be thread safe. This is the responsibility of the
implementer of these events.

**Link** - Links are immutable and is safe to be used concurrently. Lazy
initialized links must be thread safe. This is the responsibility of the
implementer of these links.

## Metrics API

**MeterProvider** - all methods are safe to be called concurrently.

**Meter** - all methods are safe to be called concurrently.

**Instrument** - All methods of any Instrument are safe to be called concurrently.

**Bound Instrument** - All methods of any Bound Instrument are safe to be called concurrently.
