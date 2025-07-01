# Scenarios and Open Questions for Tracing semantic conventions for HTTP

This document aims to capture scenarios/open questions and a road map, both of
which will serve as a basis for [stabilizing](../../specification/versioning-and-stability.md#stable)
the [existing semantic conventions for HTTP](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/http),
which are currently in an [experimental](../../specification/versioning-and-stability.md#development)
state. The goal is to declare HTTP semantic conventions stable before the
end of Q1 2022.

## Motivation

Most observability scenarios involve HTTP communication. For Distributed Tracing
to be useful across the entire scenario, having good observability for
HTTP is critical. To achieve this, OpenTelemetry must provide stable conventions
and guidelines for instrumenting HTTP communication.

Bringing the existing experimental semantic conventions for HTTP to a
stable state is a crucial step for users and instrumentation authors, as it
allows them to rely on [stability guarantees](../../specification/versioning-and-stability.md#semantic-conventions-stability),
and thus to ship and use stable instrumentation.

> NOTE. This OTEP captures a scope for changes should be done to existing
experimental semantic conventions for HTTP, but does not propose solutions.

## Roadmap for v1.0

1. This OTEP, consisting of scenarios/open questions and a proposed roadmap, is
   approved and merged.
2. [Stability guarantees](../../specification/versioning-and-stability.md#semantic-conventions-stability)
   for semantic conventions are approved and merged. This is not strictly related
   to semantic conventions for HTTP but is a prerequisite for stabilizing any
   semantic conventions.
3. Separate PRs addressing the scenarios and open questions listed in this
   document are approved and merged.
4. Proposed specification changes are verified by prototypes for the scenarios
   and examples below.
5. The [specification for HTTP semantic conventions for tracing](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/http)
   are updated according to this OTEP and are declared
   [stable](../../specification/versioning-and-stability.md#stable).

The steps in the roadmap don't necessarily need to happen in the given order,
some steps can be worked on in parallel.

## Scope for v1.0: scenarios and open questions

> NOTE. The scope defined here is subject for discussions and can be adjusted
  until this OTEP is merged.

Scenarios and open questions mentioned below must be addressed via separate PRs.

### Error status defaults

4xx responses are no longer create error status codes in case of
`SpanKind.SERVER`. It seems reasonable to define the same/similar behavior
for `SpanKind.CLIENT`.

### Required attribute sets

> At least one of the following sets of attributes is required:
>
> * `http.url`
> * `http.scheme`, `http.host`, `http.target`
> * `http.scheme`, `net.peer.name`, `net.peer.port`, `http.target`
> * `http.scheme`, `net.peer.ip`, `net.peer.port`, `http.target`

As a result, users that write queries against raw data or Zipkin/Jaeger don't
have consistent story across instrumentations and languages. e.g. they'd need to
write queries like
`select * where (getPath(http.url) == "/a/b" || getPath(http.target) == "/a/b")`

Related issue: [open-telemetry/opentelemetry-specification#2114](https://github.com/open-telemetry/opentelemetry-specification/issues/2114).

### Retries and redirects

Should each try/redirect request have unique context to be traceable and
to unambiguously ask for support from downstream service(which implies span per
call)?

Redirects: users may need observability into what server hop had an error/took
too long. E.g., was 500/timeout from the final destination or a proxy?

Related issues: [open-telemetry/opentelemetry-specification#1747](https://github.com/open-telemetry/opentelemetry-specification/issues/1747),
[open-telemetry/opentelemetry-specification#729](https://github.com/open-telemetry/opentelemetry-specification/issues/729).

PR addressing this scenario: [open-telemetry/opentelemetry-specification#2078](https://github.com/open-telemetry/opentelemetry-specification/pull/2078).

### Context propagation

How to propagate context between tries? Should it be cleaned up before making
a call in case of reusing instances of client HTTP requests?

## Scope for vNext: scenarios and open questions

### Error status configuration

In many cases 4xx error criteria depends on the app (e.g., for 404/409). As an
end user, I might want to have an ability to override existing defaults and
define what HTTP status codes count as errors.

### Optional attributes

As a library owner, I don't understand the benefits of optional attributes:
they create overhead, they don't seem to be generically useful (e.g. flavor),
and are inconsistent across languages/libraries unless unified.

Related issue: [open-telemetry/opentelemetry-specification#2114](https://github.com/open-telemetry/opentelemetry-specification/issues/2114).

### Security concerns

Some attributes can contain potentially sensitive information. Most likely, by
default web frameworks/http clients should not expose that. For example,
`http.target` has a query string that may contain credentials.

> NOTE. We didn’t omit security concerns from v1.0 on purpose, it’s just not
  something we’ve fleshed out so far.

### Sampling for noop case

To make it efficient for noop case, it might be useful to have a hint for
instrumentation (e.g., `GlobalOTel.isEnabled()`) that SDK is present and
configured before creating pre-sampling attributes.

### Long-polling and streaming

Are there any specifics for these scenarios, e.g. from span duration or status
code perspective? How to model multiple requests within the same logical
session?

### HTTP/2, gRPC, WebSockets

Anything we can do better here? In many cases connection has app-lifetime,
messages are independent - can we explain to users how to do manual tracing
for individual messages? Do span events per message make sense at all?
Need some real-life/expertize here.

### Request/Response body capturing

> NOTE. This is technically out-of-scope, but we should have an idea how to let
  users do it

There is a lot of user feedback that they want it, but

* We can’t read body in generic instrumentation
* We can let users collect them
* Attaching to server span is trivial
* Spec for client: we should have an approach to let users unambiguously
  associate body with http client span (e.g. outer manual span that wraps HTTP
  call and response reading and has event/log with body)
* Reading/writing body may happen outside of HTTP client API (e.g. through
  network streams) – how users can track it too?

Related issue: [open-telemetry/semantic-conventions#1219](https://github.com/open-telemetry/semantic-conventions/issues/1219).

## Out of scope

HTTP protocol is being widely used within many different platforms and systems,
which brings a lot of intersections with a transmission protocol layer and an
application layer. However, for HTTP Semantic Conventions specification we want
to be strictly focused on HTTP-specific aspects of distributed tracing to keep
the specification clear. Therefore, the following scenarios, including but not
limited to, are considered out of scope for this workgroup:

* Batch operations.
* Fan-in and fan-out operations (e.g., GraphQL).
* Hedging policies. Hedging enables aggressively sending multiple copies of a
  single request without waiting for a response. Hedged RPCs may be be executed
  multiple times on the server side, typically by different backends.
* HTTP as a transport layer for other systems (e.g., Messaging system built on
  top of HTTP).

To address these scenarios, we might want to work with OpenTelemetry community
to build instrumentation guidelines going forward.

## General OpenTelemetry open questions

There are several general OpenTelemetry open questions exist today which most
likely will affect the way scenarios and open questions above are addressed:

* What does a config language look like for overriding certain defaults.
  For example, what HTTP status codes count as errors?
* How to handle additional levels of detail for spans, such as retries and
  redirects?
  Should it even be designed as levels of detail or as layers reflecting logical
  or physical interactions/transactions.
* What is the data model for links? What would a reasonable storage
  implementation look like?
