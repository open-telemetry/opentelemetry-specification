# Semantic conventions for FaaS spans

**Status**: [Experimental](../../document-status.md)

This document defines how to describe an instance of a function that runs without provisioning
or managing of servers (also known as serverless functions or Function as a Service (FaaS)) with spans.

See also the [additional instructions for instrumenting AWS Lambda](instrumentation/aws-lambda.md).

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [General Attributes](#general-attributes)
  * [Function Name](#function-name)
  * [Difference between invocation and instance](#difference-between-invocation-and-instance)
- [Incoming Invocations](#incoming-invocations)
  * [Incoming FaaS Span attributes](#incoming-faas-span-attributes)
  * [Resource attributes as incoming FaaS span attributes](#resource-attributes-as-incoming-faas-span-attributes)
- [Outgoing Invocations](#outgoing-invocations)
- [Function Trigger Type](#function-trigger-type)
  * [Datasource](#datasource)
  * [HTTP](#http)
  * [PubSub](#pubsub)
  * [Timer](#timer)
  * [Other](#other)
- [Example](#example)

<!-- tocstop -->

## General Attributes

Span `name` should be set to the function name being executed. Depending on the value of the `faas.trigger` attribute, additional attributes MUST be set. For example, an `http` trigger SHOULD follow the [HTTP Server semantic conventions](http.md#http-server-semantic-conventions). For more information, refer to the [Function Trigger Type](#function-trigger-type) section.

If Spans following this convention are produced, a Resource of type `faas` MUST exist following the [Resource semantic convention](../../resource/semantic_conventions/faas.md#function-as-a-service).

<!-- semconv faas_span -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `faas.trigger` | string | Type of the trigger which caused this function invocation. [1] | `datasource` | Recommended |
| `faas.invocation_id` | string | The invocation ID of the current function invocation. | `af9d5aa4-a685-4c5f-a22b-444f80b3cc28` | Recommended |

**[1]:** For the server/consumer span on the incoming side,
`faas.trigger` MUST be set.

Clients invoking FaaS instances usually cannot set `faas.trigger`,
since they would typically need to look in the payload to determine
the event type. If clients set it, it should be the same as the
trigger that corresponding incoming would have (i.e., this has
nothing to do with the underlying transport used to make the API
call to invoke the lambda, which is often HTTP).

`faas.trigger` MUST be one of the following:

| Value  | Description |
|---|---|
| `datasource` | A response to some data source operation such as a database or filesystem read/write. |
| `http` | To provide an answer to an inbound HTTP request |
| `pubsub` | A function is set to be executed when messages are sent to a messaging system. |
| `timer` | A function is scheduled to be executed regularly. |
| `other` | If none of the others apply |
<!-- endsemconv -->

### Function Name

There are 2 locations where the function's name can be recorded: the span name and the
[`faas.name` Resource attribute](../../resource/semantic_conventions/faas.md#function-as-a-service).

It is guaranteed that if `faas.name` attribute is present it will contain the
function name, since it is defined in the semantic convention strictly for that
purpose. It is also highly likely that Span name will contain the function name
(e.g. for Span displaying purposes), but it is not guaranteed (since it is a
weaker "SHOULD" requirement). Consumers that needs such guarantee can use
`faas.name` attribute as the source.

### Difference between invocation and instance

For performance reasons (e.g. [AWS lambda], or [Azure functions]), FaaS providers allocate an execution environment for a single instance of a function that is used to serve multiple requests.
Developers exploit this fact to solve the **cold start** issue, caching expensive resource computations between different function invocations.
Furthermore, FaaS providers encourage this behavior, e.g. [Google functions].
The `faas.instance` resource attribute MAY be set to help correlate function invocations that belong to the same execution environment.
The span attribute `faas.invocation_id` differs from the [resource attribute][FaaS resource attributes] `faas.instance` in the following:

- `faas.invocation_id` refers to the ID of the current invocation of the function;
- `faas.instance` refers to the execution environment ID of the function.

[AWS lambda]: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
[Azure functions]: https://docs.microsoft.com/en-us/azure/azure-functions/manage-connections#static-clients
[Google functions]: https://cloud.google.com/functions/docs/concepts/exec#function_scope_versus_global_scope

## Incoming Invocations

This section describes incoming FaaS invocations as they are reported by the FaaS instance itself.

For incoming FaaS spans, the span kind MUST be `Server`.

### Incoming FaaS Span attributes

<!-- semconv faas_span.in -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `faas.coldstart` | boolean | A boolean that is true if the serverless function is executed for the first time (aka cold-start). |  | Recommended |
| `faas.trigger` | string | Type of the trigger which caused this function invocation. [1] | `datasource` | Required |

**[1]:** For the server/consumer span on the incoming side,
`faas.trigger` MUST be set.

Clients invoking FaaS instances usually cannot set `faas.trigger`,
since they would typically need to look in the payload to determine
the event type. If clients set it, it should be the same as the
trigger that corresponding incoming would have (i.e., this has
nothing to do with the underlying transport used to make the API
call to invoke the lambda, which is often HTTP).
<!-- endsemconv -->

### Resource attributes as incoming FaaS span attributes

In addition to the attributes listed above, any [FaaS](../../resource/semantic_conventions/faas.md) or [cloud](../../resource/semantic_conventions/cloud.md) resource attributes MAY
instead be set as span attributes on incoming FaaS invocation spans: In some
FaaS environments some of the information required for resource
attributes is only readily available in the context of an invocation (e.g. as part of a "request context" argument)
and while a separate API call to look up the resource information is often possible, it
may be prohibitively expensive due to cold start duration concerns.
The `faas.id` and `cloud.account.id` attributes on AWS are some examples.
In principle, the above considerations apply to any resource attribute that fulfills the criteria above
(not being readily available without some extra effort that could be expensive).

## Outgoing Invocations

This section describes outgoing FaaS invocations as they are reported by a client calling a FaaS instance.

For outgoing FaaS spans, the span kind MUST be `Client`.

The values reported by the client for the attributes listed below SHOULD be equal to
the corresponding [FaaS resource attributes][] and [Cloud resource attributes][],
which the invoked FaaS instance reports about itself, if it's instrumented.

<!-- semconv faas_span.out -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `faas.invoked_name` | string | The name of the invoked function. [1] | `my-function` | Required |
| `faas.invoked_provider` | string | The cloud provider of the invoked function. [2] | `alibaba_cloud` | Required |
| `faas.invoked_region` | string | The cloud region of the invoked function. [3] | `eu-central-1` | Conditionally Required: [4] |

**[1]:** SHOULD be equal to the `faas.name` resource attribute of the invoked function.

**[2]:** SHOULD be equal to the `cloud.provider` resource attribute of the invoked function.

**[3]:** SHOULD be equal to the `cloud.region` resource attribute of the invoked function.

**[4]:** For some cloud providers, like AWS or GCP, the region in which a function is hosted is essential to uniquely identify the function and also part of its endpoint. Since it's part of the endpoint being called, the region is always known to clients. In these cases, `faas.invoked_region` MUST be set accordingly. If the region is unknown to the client or not required for identifying the invoked function, setting `faas.invoked_region` is optional.

`faas.invoked_provider` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `alibaba_cloud` | Alibaba Cloud |
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |
| `tencent_cloud` | Tencent Cloud |
<!-- endsemconv -->

[FaaS resource attributes]: ../../resource/semantic_conventions/faas.md
[Cloud resource attributes]: ../../resource/semantic_conventions/cloud.md

## Function Trigger Type

This section describes how to handle the span creation and additional attributes based on the value of the attribute `faas.trigger`.

### Datasource

A datasource function is triggered as a response to some data source operation such as a database or filesystem read/write.
FaaS instrumentations that produce `faas` spans with trigger `datasource`, SHOULD use the following set of attributes.

<!-- semconv faas_span.datasource -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `faas.document.collection` | string | The name of the source on which the triggering operation was performed. For example, in Cloud Storage or S3 corresponds to the bucket name, and in Cosmos DB to the database name. | `myBucketName`; `myDbName` | Required |
| `faas.document.operation` | string | Describes the type of the operation that was performed on the data. | `insert` | Required |
| `faas.document.time` | string | A string containing the time when the data was accessed in the [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format expressed in [UTC](https://www.w3.org/TR/NOTE-datetime). | `2020-01-23T13:47:06Z` | Recommended |
| `faas.document.name` | string | The document name/table subjected to the operation. For example, in Cloud Storage or S3 is the name of the file, and in Cosmos DB the table name. | `myFile.txt`; `myTableName` | Recommended |

`faas.document.operation` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `insert` | When a new object is created. |
| `edit` | When an object is modified. |
| `delete` | When an object is deleted. |
<!-- endsemconv -->

### HTTP

The function responsibility is to provide an answer to an inbound HTTP request. The `faas` span SHOULD follow the recommendations described in the [HTTP Server semantic conventions](http.md#http-server-semantic-conventions).

### PubSub

A function is set to be executed when messages are sent to a messaging system.
In this case, multiple messages could be batch and forwarded at once to the same function invocation.
Therefore, a different root span of type `faas` MUST be created for each message processed by the function, following the [Messaging systems semantic conventions](messaging.md).
This way, it is possible to correlate each individual message with its invocation sender.

### Timer

A function is scheduled to be executed regularly. The following additional attributes are recommended.

<!-- semconv faas_span.timer -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `faas.time` | string | A string containing the function invocation time in the [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format expressed in [UTC](https://www.w3.org/TR/NOTE-datetime). | `2020-01-23T13:47:06Z` | Recommended |
| `faas.cron` | string | A string containing the schedule period as [Cron Expression](https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm). | `0/5 * * * ? *` | Recommended |
<!-- endsemconv -->

### Other

Function as a Service offers such flexibility that it is not possible to fully cover with semantic conventions.
When a function does not satisfy any of the aforementioned cases, a span MUST set the attribute `faas.trigger` to `"other"`.
In this case, it is responsibility of the framework or instrumentation library to define the most appropriate attributes.

## Example

This example shows the FaaS attributes for a (non-FaaS) process hosted on Google Cloud Platform (Span A with kind `Client`), which invokes a Lambda function called "my-lambda-function" in Amazon Web Services (Span B with kind `Server`).

| Attribute Kind | Attribute               | Span A (Client, GCP)   | Span B (Server, AWS Lambda) |
| -------------- | ----------------------- | ---------------------- | -- |
| Resource       | `cloud.provider`        | `"gcp"`                | `"aws"` |
| Resource       | `cloud.region`          | `"europe-west3"`       | `"eu-central-1"` |
| Span           | `faas.invoked_name`     | `"my-lambda-function"` | n/a |
| Span           | `faas.invoked_provider` | `"aws"`                | n/a |
| Span           | `faas.invoked_region`   | `"eu-central-1"`       | n/a |
| Span           | `faas.trigger`          | n/a                    | `"http"` |
| Span           | `faas.invocation_id`    | n/a                    | `"af9d5aa4-a685-4c5f-a22b-444f80b3cc28"` |
| Span           | `faas.coldstart`        | n/a                    | `true` |
| Resource       | `faas.name`             | n/a                    | `"my-lambda-function"` |
| Resource       | `faas.id`               | n/a                    | `"arn:aws:lambda:us-west-2:123456789012:function:my-lambda-function"` |
| Resource       | `faas.version`          | n/a                    | `"semver:2.0.0"` |
| Resource       | `faas.instance`         | n/a                    | `"my-lambda-function:instance-0001"` |
