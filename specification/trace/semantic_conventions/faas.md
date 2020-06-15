# Semantic conventions for FaaS spans

This document defines how to describe an instance of a function that runs without provisioning or managing of servers (also known as serverless) with spans.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [General Attributes](#general-attributes)
  * [Difference between execution and instance](#difference-between-execution-and-instance)
- [Function Trigger Type](#function-trigger-type)
  * [Datasource](#datasource)
  * [HTTP](#http)
  * [PubSub](#pubsub)
  * [Timer](#timer)
  * [Other](#other)

<!-- tocstop -->

## General Attributes

Span `name` should be set to the function name being executed. Depending on the value of the `faas.trigger` attribute, additional attributes MUST be set. For example, an `http` trigger SHOULD follow the [HTTP Server semantic conventions](http.md#http-server-semantic-conventions). For more information, refer to the [Function Trigger Type](#function-trigger-type) section.

If Spans following this convention are produced, a Resource of type `faas` MUST exist following the [Resource semantic convention](../../resource/semantic_conventions/README.md#function-as-a-service).

| Attribute name  | Notes  and examples  | Required? |
|---|---|--|
| `faas.trigger` | Type of the trigger on which the function is executed. <br > It SHOULD be one of the following strings: "datasource", "http", "pubsub", "timer", or "other". | Yes |
| `faas.execution` | String containing the execution id of the function. E.g. `af9d5aa4-a685-4c5f-a22b-444f80b3cc28` | No |
| `faas.coldstart` | A boolean indicating that the serverless function is executed for the first time (aka cold start). | No |

### Difference between execution and instance

For performance reasons (e.g. [AWS lambda], or [Azure functions]), FaaS providers allocate an execution environment for a single instance of a function that is used to serve multiple requests.
Developers exploit this fact to solve the **cold start** issue, caching expensive resource computations between different function executions.
Furthermore, FaaS providers encourage this behavior, e.g. [Google functions].
This field MAY be set to help correlate function executions that belong to the same execution environment.
The span attribute `faas.execution` differs from the resource attribute `faas.instance` in the following:

- `faas.execution` refers to the current request ID handled by the function;
- `faas.instance` refers to the execution environment ID of the function.

[AWS lambda]: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
[Azure functions]: https://docs.microsoft.com/en-us/azure/azure-functions/manage-connections#static-clients
[Google functions]: https://cloud.google.com/functions/docs/concepts/exec#function_scope_versus_global_scope

## Function Trigger Type

This section describes how to handle the span creation and additional attributes based on the value of the attribute `faas.trigger`.

### Datasource

A datasource function is triggered as a response to some data source operation such as a database or filesystem read/write.
For `faas` spans with trigger `datasource`, it is recommended to set the following attributes.

| Attribute name  | Notes  and examples  | Required? |
|---|---|--|
| `faas.document.collection` | The name of the source on which the operation was perfomed. For example, in Cloud Storage or S3 corresponds to the bucket name, and in Cosmos DB to the database name. | Yes |
| `faas.document.operation`  | Describes the type of the operation that was performed on the data.<br /> It SHOULD be one of the following strings: "insert", "edit", "delete". | Yes |
| `faas.document.time`       | A string containing the time when the data was accessed in the [ISO 8601] format expressed in [UTC]. E.g. `"2020-01-23T13:47:06Z"` | Yes |
| `faas.document.name`       | The document name/table subjected to the operation.<br /> For example, in Cloud Storage or S3 is the name of the file, and in Cosmos DB the table name.  | No |

### HTTP

The function responsibility is to provide an answer to an inbound HTTP request. The `faas` span SHOULD follow the recommendations described in the [HTTP Server semantic conventions](http.md#http-server-semantic-conventions).

### PubSub

A function is set to be executed when messages are sent to a messaging system.
In this case, multiple messages could be batch and forwarded at once to the same function execution.
Therefore, a different root span of type `faas` MUST be created for each message processed by the function, following the [Messaging systems semantic conventions](messaging.md).
This way, it is possible to correlate each individual message with its execution sender.

### Timer

A function is scheduled to be executed regularly. The following additional attributes are recommended.

| Attribute name  | Notes  and examples  | Required? |
|---|---|--|
| `faas.time` | A string containing the function invocation time in the [ISO 8601] format expressed in [UTC]. E.g. `"2020-01-23T13:47:06Z"`| Yes |
| `faas.cron` | A string containing the schedule period as [Cron Expression]. E.g. `"0/5 * * * ? *"`| No |

[Cron Expression]: https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm
[ISO 8601]: https://www.iso.org/iso-8601-date-and-time-format.html
[UTC]: https://www.w3.org/TR/NOTE-datetime

### Other

Function as a Service offers such flexibility that it is not possible to fully cover with semantic conventions.
When a function does not satisfy any of the aforementioned cases, a span MUST set the attribute `faas.trigger` to `"other"`.
In this case, it is responsibility of the framework or instrumentation library to define the most appropriate attributes.
