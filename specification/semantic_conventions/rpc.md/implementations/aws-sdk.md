# Semantic conventions for AWS SDK

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting the AWS SDK. They map request or response
parameters in AWS SDK API calls to attributes on a Span. The conventions have been collected over time based
on feedback from AWS users of tracing and will continue to increase as new interesting conventions
are found.

Some descriptions are also provided for populating general OpenTelemetry semantic conventions based on these APIs.

## Requirements

The span name MUST be of the format `Service.Operation` as per the AWS HTTP API, e.g., `DynamoDB.GetItem`,
`S3.ListBuckets`. This is equivalent to concatenating `rpc.service` and `rpc.method` with `.` and consistent
with the naming guidelines for RPC client spans.

## Attributes

<!-- semconv aws -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`rpc.method`](../rpc.md) | string | The name of the operation corresponding to the request, as returned by the AWS SDK [1] | `GetItem`; `PutItem` | No |
| [`rpc.service`](../rpc.md) | string | The name of the service to which a request is made, as returned by the AWS SDK. [2] | `DynamoDB`; `S3` | No |
| [`rpc.system`](../rpc.md) | string | The value `aws-api`. | `aws-api` | Yes |

**[1]:** This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).

**[2]:** This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).
<!-- endsemconv -->