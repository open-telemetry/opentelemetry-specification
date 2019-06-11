# Concurrency and Thread-Safety of OpenTelemetry API

For languages which support concurrent execution the OpenTelemetry APIs provide
specific guarantees and safeties. Not all of API functions are safe to
call concurrently. Function and method documentation must explicitly
specify whether it is safe or no to make concurrent calls and in what 
situations.

The following are general recommendations of concurrent call safety of
specific subsets of the API.

**Tracer** - the tracer is a singleton and all of its methods are safe to call
concurrently.

**SpanBuilder** - It is not safe to concurrently call any methods of the 
same SpanBuilder instance. Different instances of SpanBuilder can be safely 
used concurrently by different threads/coroutines, provided that no single
SpanBuilder is used by more than one thread/coroutine.

**Span** - Span methods are not safe to be called concurrently by user code 
for the same instance of the Span. 

**SpanData** - same guarantees as **Span**.

**Link** - same guarantees as **Span**. In addition a Link should never
created for a Span that is already finished.
