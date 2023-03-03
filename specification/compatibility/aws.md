# Compatibility Considerations for AWS

**Status**: [Experimental](../document-status.md)

This document highlights compatibility considerations when interacting with AWS managed services.

## Context Propagation

When making outgoing calls using an aws-sdk, an AWS service-supported propagation format MUST be used to add
context propagation to HTTP headers on the outgoing request, unless another propagator is explicitly provided,
in which case the provided propagator MUST be used.
Propagation headers MUST be added before the signature is calculated to prevent errors on signed requests.

The following formats are currently natively supported by AWS services for propagation:

* [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)

AWS service-supported context propagation is necessary to allow context propagation
through AWS managed services, for example: S3 -> SNS -> SQS -> Lambda.

(See the [aws-lambda sqs-event semantic convention](../trace/semantic_conventions/instrumentation/aws-lambda.md#sqs-event)
doc for details on how this context propagation is consumed by Lambda instrumentation.)

Additional propagation formats MAY be applied to individual request types that support arbitrary attributes such as `SqsMessage`.
This can allow for transporting additional context that may not be supported by x-ray, such as baggage or tracestate.
Documentation SHOULD advise that doing so is subject to attribute limits and billing impacts.

