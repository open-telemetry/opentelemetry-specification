# Span
 

... parts of this document moved to [terminology.md](../terminology.md) ...

A span contains a SpanContext and allows users to record tracing events based on the data model 
defined [here][SpanDataModel].

## Span structure


## Span creation
The implementation MUST allow users to create two types of Spans:
* Root Spans - spans that do not have a parent.
* Child Spans - the parent can be explicitly set or inherit from the Context.

When creating a Span the implementation MUST allow users to create the Span attached or detached 
from the Context, this allows users to manage the interaction with the Context independently of 
the Span lifetime:
* Attached to the Context - the newly created Span is attached to the Context.
* Detached from the Context - the newly created Span is not attached to any Context.

### How Span interacts with Context?
Context interaction represents the process of attaching/detaching a Span to the Context 
in order to propagate it in-process (possibly between threads) and between function calls.

There are two supported implementations for the Context based on how the propagation is implemented:
* With implicit propagation - implicitly passed between function calls and threads, usually 
implemented using thread-local variables (e.g. Java [io.grpc.Context][javaContext])
* With explicit propagation - explicitly passed between function calls and threads (e.g. Go 
[context.Context][goContext])

When an implicit propagated Context is used, the implementation MUST use scoped objects to 
attach/detach a Span (scoped objects represent auto closable objects, e.g. stack allocated 
objects in C++):
* When attach/detach an already created Span the API MAY be called `WithSpan`.
* When attach/detach at the creation time the API MAY be called `StartSpan` or `StartScopedSpan`.

When an explicit propagated Context is used, the implementation MUST create a new Context when a 
Span is attached (immutable Context):
* When attach/detach an already created Span the API MAY be called `WithSpan`.
* When attach/detach at the creation time the API MAY be called `StartSpan` or `StartScopedSpan`.

### Why support Spans that are not attached to the Context?
* Allow users to use the OpenCensus library without using a Context.
* Allow users to have more control for the lifetime of the Span.
* There are cases, for example HTTP/RPC interceptors, where the Span creation and usage happens in 
different places, and the user does not have control of the framework to control the Context 
propagation.

[goContext]: https://golang.org/pkg/context
[javaContext]: https://github.com/grpc/grpc-java/blob/master/context/src/main/java/io/grpc/Context.java
[SpanDataModel]: https://github.com/census-instrumentation/opencensus-proto/blob/master/src/opencensus/proto/trace/v1/trace.proto   
