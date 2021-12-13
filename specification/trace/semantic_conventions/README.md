# Trace Semantic Conventions

**Status**: [Experimental](../../document-status.md)

In OpenTelemetry spans can be created freely and it’s up to the implementor to
annotate them with attributes specific to the represented operation. Spans
represent specific operations in and between systems. Some of these operations
represent calls that use well-known protocols like HTTP or database calls.
Depending on the protocol and the type of operation, additional information
is needed to represent and analyze a span correctly in monitoring systems. It is
also important to unify how this attribution is made in different languages.
This way, the operator will not need to learn specifics of a language and
telemetry collected from polyglot (multi-language) micro-service environments
can still be easily correlated and cross-analyzed.

The following semantic conventions for spans are defined:

* [General](span-general.md): General semantic attributes that may be used in describing different kinds of operations.
* [HTTP](http.md): For HTTP client and server spans.
* [Database](database.md): For SQL and NoSQL client call spans.
* [RPC/RMI](rpc.md): For remote procedure call (e.g., gRPC) spans.
* [Messaging](messaging.md): For messaging systems (queues, publish/subscribe, etc.) spans.
* [FaaS](faas.md): For [Function as a Service](https://en.wikipedia.org/wiki/Function_as_a_service) (e.g., AWS Lambda) spans.
* [Exceptions](exceptions.md): For recording exceptions associated with a span.

The following library-specific semantic conventions are defined:

* [AWS Lambda](instrumentation/aws-lambda.md): For AWS Lambda spans.
* [AWS SDK](instrumentation/aws-sdk.md): For AWS SDK spans.

Apart from semantic conventions for traces and [metrics](../../metrics/semantic_conventions/README.md),
OpenTelemetry also defines the concept of overarching [Resources](../../resource/sdk.md) with their own
[Resource Semantic Conventions](../../resource/semantic_conventions/README.md).

## Event Name Reuse Prohibition

A new event MUST NOT be added with the same name as an event that existed in
the past but was renamed (with a corresponding schema file).

When introducing a new event name check all existing schema files to make sure
the name does not appear as a key of any "rename_events" section (keys denote
old event names in rename operations).
