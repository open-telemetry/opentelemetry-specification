# Concurrency and Thread-Safety of OpenTelemetry API

For languages which support concurrent execution the OpenTelemetry APIs provide
specific guarantees and safeties. Not all of API functions are safe to
be called concurrently. Function and method documentation must explicitly
specify whether it is safe or no to make concurrent calls and in what 
situations.

The following are general recommendations of concurrent call safety of
specific subsets of the API.

**Tracer** - all methods are safe to be called concurrently.

**SpanBuilder** - It is not safe to concurrently call any methods of the 
same SpanBuilder instance. Different instances of SpanBuilder can be safely 
used concurrently by different threads/coroutines, provided that no single
SpanBuilder is used by more than one thread/coroutine.

**Span** - All methods of Span are safe to be called concurrently. 

**SpanData** - SpanData is immutable and is safe to be used concurrently.

**Link** - same as SpanData.
