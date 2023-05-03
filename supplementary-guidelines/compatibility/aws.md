# Compatibility Considerations for AWS

This document highlights compatibility considerations for OpenTelemetry
instrumentations when interacting with AWS managed services using an aws-sdk,
a third-party library, or a direct HTTP request.

## Context Propagation

When making calls to AWS managed services using an AWS SDK, a third-party
library, or a direct HTTP request, an AWS service-supported propagation format should
be used to add context propagation to HTTP headers on the outgoing request in order
to propagate the context to services indirectly invoked by such call.

Instrumentation may allow a different propagator to be explicitly configured for
the instrumentation (e.g. an explicitly provided propagator, or an option to use the
globally configured propagator for all or certain calls).
This will be useful for certain cases where the services allow transporting these
headers to a receiving side, for example SQS or SNS with message attributes.
Note that this also means that instrumentations providing this option cannot just
replace their call to the X-Ray propagator with a call to another propagator (as
that would only send HTTP headers in the API REST call that would be immediately
ignored by the receiving AWS service), but will need to introduce per-service-call
implementations where it makes sense (e.g., for SQS send and SQS receive).
This can allow for transporting additional context that may not be supported by X-Ray,
such as baggage or tracestate, or supporting certain legacy propagation formats.
Documentation should advise that doing so is subject to attribute limits and billing impacts.

Propagation headers must be added before the signature is calculated to prevent
errors on signed requests. If injecting into the request itself (not just adding
additional HTTP headers), additional considerations may apply (for example, the
.NET AWS SDK calculates a hash of the attributes it sends and compares it with
the  `MD5OfMessageAttributes` that it receives).

The following formats are currently natively supported by AWS services for propagation:

* [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)

AWS service-supported context propagation is necessary to allow context propagation
through AWS managed services, for example: `S3 -> SNS -> SQS -> Lambda`.

(See the [aws-lambda sqs-event semantic convention](../../specification/trace/semantic_conventions/instrumentation/aws-lambda.md#sqs-event)
doc for details on how this context propagation is consumed by Lambda instrumentation.)
