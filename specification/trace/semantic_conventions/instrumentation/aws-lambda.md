# Instrumenting AWS Lambda

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting an AWS Lambda request handler. AWS
Lambda largely follows the conventions for [FaaS](../faas.md) while [HTTP](../http.md) conventions are also
applicable when handlers are for HTTP requests.

There are a variety of triggers for Lambda functions, and this document will grow over time to cover all the
use cases.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i specification/trace/semantic_conventions/instrumentation/aws-lambda.md` -->

<!-- toc -->

- [All triggers](#all-triggers)
  * [Determining the parent of a span](#determining-the-parent-of-a-span)
- [API Gateway](#api-gateway)
- [SQS](#sqs)
  * [SQS Event](#sqs-event)
  * [SQS Message](#sqs-message)
- [Examples](#examples)
  * [API Gateway Request Proxy (Lambda tracing passive)](#api-gateway-request-proxy-lambda-tracing-passive)
  * [API Gateway Request Proxy (Lambda tracing active)](#api-gateway-request-proxy-lambda-tracing-active)
  * [SQS (Lambda tracing passive)](#sqs-lambda-tracing-passive)
  * [SQS (Lambda tracing active)](#sqs-lambda-tracing-active)

<!-- tocstop -->

## All triggers

For all events, a span with kind `SERVER` MUST be created corresponding to the function invocation unless stated
otherwise below. Unless stated otherwise below, the name of the span MUST be set to the function name from the
Lambda `Context`.

The following attributes SHOULD be set:

- [`faas.execution`](../faas.md) - The value of the AWS Request ID, which is always available through an accessor on the Lambda `Context`
- [`faas.id`](../../../resource/semantic_conventions/faas.md) - The value of the invocation ARN for the function, which is always available through an accessor on the Lambda `Context`
- [`cloud.account.id`](../../../resource/semantic_conventions/cloud.md) - In some languages, this is available as an accessor on the Lambda `Context`. Otherwise, it can be parsed from the value of `faas.id` as the fifth item when splitting on `:`

### Determining the parent of a span

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

The Lambda span name and the [`http.route` span attribute](../http.md#http-server-semantic-conventions) SHOULD
be set to the [resource property][] from the proxy request event, which corresponds to the user configured HTTP
route instead of the function name.

[`faas.trigger`](../faas.md) MUST be set to `http`. [HTTP attributes](../http.md) SHOULD be set based on the
available information in the proxy request event. `http.scheme` is available as the `x-forwarded-proto` header
in the proxy request. Refer to the [input format][] for more details.

[resource property]: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
[input format]: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

## SQS

Amazon Simple Queue Service (SQS) is a message queue that triggers a Lambda function with a batch of messages.
So we consider processing both of a batch and of each individual message. The function invocation span MUST
correspond to the SQS event, which is the batch of messages. For each message, an additional span SHOULD be
created to correspond with the handling of the SQS message. Because handling of a message will be inside user
business logic, not the Lambda framework, automatic instrumentation mechanisms without code change will often
not be able to instrument the processing of the individual messages. Instrumentation SHOULD provide utilities
for creating message processing spans within user code.

The span kind for both types of SQS spans MUST be `CONSUMER`.

### SQS Event

For the SQS event span, if all the messages in the event have the same event source, the name of the span MUST
be `<event source> process`. If there are multiple sources in the batch, the name MUST be
`multiple_sources process`. The parent MUST be the `SERVER` span corresponding to the function invocation.

For every message in the event, the [message system attributes][] (not message attributes, which are provided by
the user) SHOULD be checked for the key `AWSTraceHeader`. If it is present, an OpenTelemetry `Context` SHOULD be
parsed from the value of the attribute using the [AWS X-Ray Propagator](../../../context/api-propagators.md) and
added as a link to the span. This means the span may have as many links as messages in the batch.

- [`faas.trigger`](../faas.md) MUST be set to `pubsub`.
- [`messaging.operation`](../messaging.md) MUST be set to `process`.
- [`messaging.system`](../messaging.md) MUST be set to `AmazonSQS`.
- [`messaging.destination_kind`](../messaging.md#messaging-attributes) MUST be set to `queue`.

### SQS Message

For the SQS message span, the name MUST be `<event source> process`.  The parent MUST be the `CONSUMER` span
corresponding to the SQS event. The [message system attributes][] (not message attributes, which are provided by
the user) SHOULD be checked for the key `AWSTraceHeader`. If it is present, an OpenTelemetry `Context` SHOULD be
parsed from the value of the attribute using the [AWS X-Ray Propagator](../../../context/api-propagators.md) and
added as a link to the span.

- [`faas.trigger`](../faas.md) MUST be set to `pubsub`.
- [`messaging.operation`](../messaging.md#messaging-attributes) MUST be set to `process`.
- [`messaging.system`](../messaging.md#messaging-attributes) MUST be set to `AmazonSQS`.
- [`messaging.destination_kind`](../messaging.md#messaging-attributes) MUST be set to `queue`.

Other [Messaging attributes](../messaging.md#messaging-attributes) SHOULD be set based on the available information in the SQS message
event.

Note that `AWSTraceHeader` is the only supported mechanism for propagating `Context` in instrumentation for SQS
to prevent conflicts with other sources. Notably, message attributes (user-provided, not system) are not supported -
the linked contexts are always expected to have been sent as HTTP headers of the `SQS.SendMessage` request that
the message originated from. This is a function of AWS SDK instrumentation, not Lambda instrumentation.

Using the `AWSTraceHeader` ensures that propagation will work across AWS services that may be integrated to
Lambda via SQS, for example a flow that goes through S3 -> SNS -> SQS -> Lambda. `AWSTraceHeader` is only a means
of propagating context and not tied to any particular observability backend. Notably, using it does not imply
using AWS X-Ray - any observability backend will fully function using this propagation mechanism.

[message system attributes]: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-metadata.html#sqs-message-system-attributes

## Examples

### API Gateway Request Proxy (Lambda tracing passive)

Given a process C that sends an HTTP request to an API Gateway endpoint with path `/pets/{petId}` configured for
a Lambda function F:

```
Process C: | Span Client        |
--
Function F:    | Span Function |
```

| Field or Attribute | `Span Client` | `Span Function` |
|-|-|-|
| Span name | `HTTP GET` | `/pets/{petId}` |
| Parent |  | Span Client |
| SpanKind | `CLIENT` | `SERVER` |
| Status | `Ok` | `Ok` |
| `faas.execution` | | `79104EXAMPLEB723` |
| `faas.id` | | `arn:aws:lambda:us-west-2:123456789012:function:my-function` |
| `faas.trigger` | | `http` |
| `cloud.account.id` | | `12345678912` |
| `net.peer.name` | `foo.execute-api.us-east-1.amazonaws.com` |  |
| `net.peer.port` | `413` |  |
| `http.method` | `GET` | `GET` |
| `http.user_agent` | `okhttp 3.0` | `okhttp 3.0` |
| `http.url` | `https://foo.execute-api.us-east-1.amazonaws.com/pets/10` |  |
| `http.scheme` | | `https` |
| `http.host` | | `foo.execute-api.us-east-1.amazonaws.com` |
| `http.target` | | `/pets/10` |
| `http.route` | | `/pets/{petId}` |
| `http.status_code` | `200` | `200` |

### API Gateway Request Proxy (Lambda tracing active)

Active tracing in Lambda means an API Gateway span `Span APIGW` and a Lambda runtime invocation span `Span Lambda`
will be exported to AWS X-Ray by the infrastructure (not instrumentation). All attributes above are the same
except that in this case, the parent of `APIGW` is `Span Client` and the parent of `Span Function` is
`Span Lambda`. This means the hierarchy looks like:

```
Span Client --> Span APIGW --> Span Lambda --> Span Function
```

### SQS (Lambda tracing passive)

Given a process P, that sends two messages to a queue Q on SQS, and a Lambda function F, which processes both of them in one batch (Span ProcBatch) and
generates a processing span for each message separately (Spans Proc1 and Proc2).

```
Process P: | Span Prod1 | Span Prod2 |
--
Function F:                      | Span ProcBatch |
                                        | Span Proc1 |
                                               | Span Proc2 |
```

| Field or Attribute | Span Prod1 | Span Prod2 | Span ProcBatch | Span Proc1 | Span Proc2 |
|-|-|-|-|-|-|
| Span name | `Q send` | `Q send` | `Q process` | `Q process` | `Q process` |
| Parent |  |  |  | Span ProcBatch | Span ProcBatch |
| Links |  |  |  | Span Prod1 | Span Prod2 |
| SpanKind | `PRODUCER` | `PRODUCER` | `CONSUMER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `messaging.system` | `AmazonSQS` | `AmazonSQS` | `AmazonSQS` | `AmazonSQS` | `AmazonSQS` |
| `messaging.destination` | `Q` | `Q` | `Q` | `Q` | `Q` |
| `messaging.destination_kind` | `queue` | `queue` | `queue` | `queue` | `queue` |
| `messaging.operation` |  |  | `process` | `process` | `process` |
| `messaging.message_id` | | | | `"a1"` | `"a2"` |

Note that if Span Prod1 and Span Prod2 were sent to different queues, Span ProcBatch would not have
`messaging.destination` set as it would correspond to multiple destinations.

The above requires user code change to create `Span Proc1` and `Span Proc2`. In Java, the user would inherit from
[TracingSqsMessageHandler][] instead of Lambda's standard `RequestHandler` to enable them. Otherwise these two spans
would not exist.

[TracingSqsMessageHandler]: https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/v1.0.1/instrumentation/aws-lambda-1.0/library/src/main/java/io/opentelemetry/instrumentation/awslambda/v1_0/TracingSqsMessageHandler.java

### SQS (Lambda tracing active)

Active tracing in Lambda means a Lambda runtime invocation span `Span Lambda` will be exported to X-Ray by the
infrastructure (not instrumentation). In this case, all of the above is the same except `Span ProcBatch` will
have a parent of `Span Lambda`. This means the hierarchy looks like:

```
Span Lambda --> Span ProcBatch --> Span Proc1 (links to Span Prod1 and Span Prod2)
                               \-> Span Proc2 (links to Span Prod1 and Span Prod2)
```
