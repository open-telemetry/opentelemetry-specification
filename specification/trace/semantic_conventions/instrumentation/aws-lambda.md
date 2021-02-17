# Instrumenting AWS Lambda

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting an AWS Lambda request handler. AWS
Lambda largely follows the conventions for [FaaS](../faas.md) while [HTTP](../http.md) conventions are also
applicable when handlers are for HTTP requests.

There are a variety of triggers for Lambda functions, and this document will grow over time to cover all the
use cases.

## All triggers

For all events, a span with kind `SERVER` MUST be created corresponding to the function invocation. Unless
stated otherwise below, the name of the span MUST be set to the function name from the Lambda `Context`.

<!-- semconv aws.lambda -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`cloud.account.id`](../../../resource/semantic_conventions/cloud.md) | string | The account ID for the function. [1] | `123456789012` | No |
| [`faas.execution`](../faas.md) | string | The value of the AWS Request ID from the Lambda `Context`. | `943ad105-7543-11e6-a9ac-65e093327849` | No |
| [`faas.id`](../../../resource/semantic_conventions/faas.md) | string | The value of the invocation arn for the function from the Lambda `Context`. [2] | `arn:aws:lambda:us-east-2:123456789012:function:my-function:1` | No |

**[1]:** If not provided on Lambda `Context`, it SHOULD be parsed from the value of `faas.id` as the fifth item when splitting on `:`.

**[2]:** For example, in AWS Lambda this field corresponds to the [ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) value, in GCP to the URI of the resource, and in Azure to the [FunctionDirectory](https://github.com/Azure/azure-functions-host/wiki/Retrieving-information-about-the-currently-running-function) field.
<!-- endsemconv -->

The parent of the span MUST be determined by considering both the environment and any headers or attributes
available from the event.

If the `_X_AMZN_TRACE_ID` environment variable is set, it SHOULD be parsed into an OpenTelemetry `Context` using
the [AWS X-Ray Propagator](../../../context/api-propagators.md). If the resulting `Context` is sampled, then this
`Context` is the parent of the function span. The environment variable will be set and the `Context` will be
sampled only if AWS X-Ray has been enabled for the Lambda function. A user can disable AWS X-Ray for the function
if this propagation is not desired.

Otherwise, for an API Gateway Proxy Request, the user's configured propagators should be applied to the HTTP
headers of the request to extract a `Context`.

## API Gateway

API Gateway allows a user to trigger a Lambda function in response to HTTP requests. It can be configured to be
a pure proxy, where the information about the original HTTP request is passed to the Lambda function, or as a
configuration for a REST API, in which case only a deserialized body payload is available.  In the case the API
gateway is configured to proxy to the Lambda function, the instrumented request handler will have access to all
the information about the HTTP request in the form of an API Gateway Proxy Request Event.

The Lambda span name SHOULD be set to the `Resource` from the proxy request event, which corresponds to the user
configured HTTP route instead of the function name.

<!-- semconv aws.lambda.api_gateway_proxy -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`faas.trigger`](../faas.md) | string | MUST be `http`. | `http` | Yes |
| [`http.method`](../http.md) | string | HTTP request method. | `GET`; `POST`; `HEAD` | No |
| [`http.route`](../http.md) | string | The `Resource` from the proxy request event. | `/users/:userID?` | No |
| [`http.status_code`](../http.md) | number | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | No |
| [`http.url`](../http.md) | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. | `https://www.foo.bar/search?q=OpenTelemetry#SemConv` | No |
| [`http.user_agent`](../http.md) | string | Value of the [HTTP User-Agent](https://tools.ietf.org/html/rfc7231#section-5.5.3) header sent by the client. | `CERN-LineMode/2.15 libwww/2.17b3` | No |
<!-- endsemconv -->

## SQS

SQS is a message queue that triggers a Lambda function with a batch of messages. In addition to the span for the
function invocation, two spans SHOULD be generated, one for the batch of messages, called an SQS event, and one
for each individual message, called an SQS message.

The span kind for both spans MUST be `CONSUMER`.

For the SQS event span, if all the messages in the event have the same event source, the name of the span MUST
be `<event source> process`. If there are multiple sources in the batch, the name MUST be
`multiple_sources <process>`. The parent MUST be the `SERVER` span corresponding to the function invocation.

For every message in the event, the message's system attributes (not message attributes, which are provided by
the user) SHOULD be checked for the key `AWSTraceHeader`. If it is present, an OpenTelemetry `Context` SHOULD be
parsed from the value of the attribute using the [AWS X-Ray Propagator](../../../context/api-propagators.md) and
added as a link to the span. This means the span may have as many links as messages in the batch.

<!-- semconv aws.lambda.sqs_event -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`faas.trigger`](../faas.md) | string | MUST be `pubsub`. | `pubsub` | Yes |
| [`messaging.operation`](../messaging.md) | string | MUST be `process`. | `process` | No |
| [`messaging.system`](../messaging.md) | string | MUST be `AmazonSQS`. | `AmazonSQS` | No |
<!-- endsemconv -->

For the SQS message span, the name MUST be `<event source> process`.  The parent MUST be the `CONSUMER` span
corresponding to the SQS event. The message's system attributes (not message attributes, which are provided by
the user) SHOULD be checked for the key `AWSTraceHeader`. If it is present, an OpenTelemetry `Context` SHOULD be
parsed from the value of the attribute using the [AWS X-Ray Propagator](../../../context/api-propagators.md) and
added as a link to the span.

<!-- semconv aws.lambda.sqs_message -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`faas.trigger`](../faas.md) | string | MUST be `pubsub`. | `pubsub` | Yes |
| [`messaging.destination`](../messaging.md) | string | The value of the event source for the message. | `MyQueue`; `MyTopic` | No |
| [`messaging.message_id`](../messaging.md) | string | The value of the message ID for the message. | `452a7c7c7c7048c2f887f61572b18fc2` | No |
| [`messaging.operation`](../messaging.md) | string | MUST be `process`. | `process` | No |
| [`messaging.system`](../messaging.md) | string | MUST be `AmazonSQS`. | `AmazonSQS` | No |
<!-- endsemconv -->

Note that `AWSTraceHeader` is the only supported mechanism for propagating `Context` for SQS to prevent conflicts
with other sources. Notably, message attributes (user-provided, not system) are not supported - the linked contexts
are always expected to have been sent as HTTP headers of the `SQS.SendMessage` request that the message originated
from. This is a function of AWS SDK instrumentation, not Lambda instrumentation.
