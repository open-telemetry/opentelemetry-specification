# Error Flagging with Status Codes

This proposal reduces the number of status codes to three, adds a new field to identify status codes set by application developers and operators, and adds a mapping of semantic conventions to status codes. This clarifies how error reporting should work in OpenTelemetry.

Note: The term **end user** in this document is defined as the application developers and operators of the system running OpenTelemetry. The term **instrumentation** refers to [instrumentation libraries](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/glossary.md#instrumentation-library) for common code shared between different systems, such as web frameworks and database clients.

## Motivation

Error reporting is a fundamental use case for distributed tracing. While we prefer that error flagging occurs within analysis tools, and not within instrumentation, a number of currently supported analysis tools and protocols rely on the existence of an explicit error flag reported from instrumentation. In OpenTelemetry, the error flag is called "status codes".

However, there is confusion over the mapping of semantic conventions to status codes, and concern over the subjective nature of errors. Which network failures count as an error? Are 404s an error? The answer is often dependent on the situation, but without even a baseline of suggested status codes for each convention, the instrumentation author is placed under the heavy burden of making the decision. Worse, the decisions will not be in sync across different instrumentation.

There is one other missing piece, required for proper error flagging. Both application developers and operators have a deep understanding of what constitutes an error in their system. OpenTelemetry must provide a way for these users to control error flagging, and explicitly indicate that it is the end user setting the status code, and not instrumentation. In these specific cases, the error flagging is known to be correct: the end user has decided the status of the span, and they do not want another interpretation.

While generic instrumentation can only provide a generic schema, end users are capable of making subjective decisions about their systems. And, as the end user, they should get to have the final call in what constitutes an error. In order to accomplish this, there must be a way to differentiate between errors flagged by instrumentation, and errors flagged by the end user.

## Explanation

The following changes add several missing features required for proper error reporting, and are completely backwards compatible with OpenTelemetry today.

### Status Codes

Currently, OpenTelemetry does not have a use case for differentiating between different types of errors. However, this use case may appear in the future. For now, we would like to reduce the number of status codes, and then add them back in as the need becomes clear. We would also like to differentiate between status codes which have not been
set, and an explicit OK status set by an end user.

* `UNSET` is the default status code.
* `ERROR` represents all error types.
* `OK` represents a span which has been explicitly marked as being free of errors, and should not be counted against an error budget. Note that only end users should set this status. Instead, instrumentation should leave the status as `UNSET` for operations that do not generate an error.

### `Status Source`

A new Status Source field identifies the origin of the status code on the span. This is important, as statuses set by application developers and operators have been confirmed by the end user to be correct to the particular situation. Statuses set by instrumentation, on the other hand, are only following a generic schema.

* `INSTRUMENTATION` is the default source. This is used for instrumentation contained within shared code, such as OSS libraries and frameworks. All instrumentation plugins shipped with OpenTelemetry use this status code.
* `USER` identifies statuses set by application developers or operators, either in application code or the collector.

Analysis tools MAY disregard status codes, in favor of their own approach to error analysis. However, it is strongly suggested that analysis tools SHOULD pay attention to the status codes when set by `USER`, as it is a communication from the application developer or operator and contains valuable information.

### Status Mapping Schema

As part of the specification, OpenTelemetry provides a mapping of semantic conventions to status codes. This removes any ambiguity as to what OpenTelemetry ships with out of the box.

Including the correct status codes as part of our semantic conventions will help ensure our instrumentation is consistent when errors relate to a cross-language concept, such as a database protocol.

Please note that semantic conventions, and thus status mapping from conventions, are still a work in progress and will continue to change after GA.

### Status Processor

The collector will provide a processor and a configuration language to make adjustments to this status mapping schema. This provides the flexibility and customization needed for real world scenarios.

### Convenience methods

As a convenience, OpenTelemetry provides helper functions for adding semantic conventions and exceptions to a span. These helper functions will also set the correct status code. This simplifies the life of the instrumentation author, and helps ensure compliance and data quality.

Note that these convenience methods simply wire together multiple API calls. They should live in a helper package, and should not be directly added to existing API interfaces. Given how many semantic conventions we have, there will be a pile of them.

## Internal details

This proposal is mostly backwards compatible with existing code, protocols, and the OpenTracing bridge. The only potential exception is the removal of status code enums from the current OTLP protocol, and the rewriting of the small number of instrumentation that were making use of them.

## BUT ERRORS ARE SUBJECTIVE!! HOW CAN WE KNOW WHAT IS AN ERROR? WHO ARE WE TO DEFINE THIS?

First of all, every tracing system to-date comes with a default set of errors. No system requires that end users start completely from scratch. So... be calm!! Have faith!!

While flagging errors can be a subjective decision, it is true that many semantic conventions qualify as an error. By providing a default mapping of semantic conventions to errors, we ensure compatibility with existing analysis tools (e.g. Jaeger), and provide guidance to users and future implementers.

Obviously, all systems are different, and users will want to adjust error reporting on a case by case basis. Unwanted errors may be suppressed, and additional errors may be added. The collector will provide a processor and a configuration language to make this a straightforward process. Working from a baseline of standard errors will provide a better experience than having to define a schema from scratch.

Note that analysis tools MAY disregard Span Status, and do their own error analysis. There is no requirement that the status code is respected, even when Status Source is set. However, it is strongly suggested that analysis tools SHOULD pay attention to the status code when Status Source is set, as it represents a subjective decision made by either the operator or application developer.

## Remind me why we need status codes again?

Status codes provide a low overhead mechanism for checking if a span counts against an error budget, without having to scan every attribute and event. It is an inexpensive and low cardinality approach to track multiple types of error budgets. This reduces overhead and could be a benefit for many systems.

However, adding in an existing set of error types without first clearly defining their use and how they might be set has caused confusion. If the status codes are not set consistently and correctly, then the resulting error budgeting will not be useful. So we are consolidating all error types into a single ERROR type, to avoid this situation. We may add more error types back in if we can agree on their use cases and a method for applying them consistently.

## Open questions

If we add error processing to the Collector, it is unclear what the overhead would be.

It is also unclear what the cost is for backends to scan for errors on every span, without a hint from instrumentation that an error might be present.

## Prior art and alternatives

In OpenTracing, the lack of a Collector and status mapping schema proved to be unwieldy. It placed a burden on instrumentation plugin authors to set the error flag correctly, and led to an explosion of non-standardized configuration options in every plugin just to adjust the default error flagging. This in turn placed a configuration burden on application developers.

An alternative is the `error.hint` proposal, paired with the removal of status code. This would work, but essentially provides the same mechanism provided in this proposal, only with a large number of breaking changes. It also does not address the need for user overrides.

## Future Work

The inclusion of status codes and status mappings help the OpenTelemetry community speak the same language in terms of error reporting. It lifts the burden on future analysis tools, and (when respected) it allows users to employ multiple analysis tools without having to synchronize an important form of configuration across multiple tools.

In the future, OpenTelemetry may add a control plane which allows dynamic configuration of the status mapping schema.
