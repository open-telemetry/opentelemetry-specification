# Semantic conventions for FaaS spans

This document defines how to describe an instance of a function that runs without provisioning or managing of servers (also known as serverless) with spans.

Span `name` should be set to the function name being executed. Depending on the trigger of the function, additional attributes MUST be set. For example, an HTTP trigger must set the `SpanKind` to `Server` and follow the [HTTP Server semantic conventions](data-http.md#http-server-semantic-conventions).

If Spans following this convention are produced, a Resource of type `faas` MUST exist following the [Resource semantic convention](data-resource-semantic-conventions.md#function-as-a-service). 

| Attribute name  | Notes  and examples  | Required? |
|---|---|--|
| `component` | Denotes the type of the span and needs to be `"faas"` | Yes | 
| `faas.trigger` | Type of the trigger on which the function is executed. <br > The following spelling SHOULD be used for trigger strings: "event", "http", "manual", "pubsub", "timer". | Yes |
| `faas.id` | String containing the unique execution id of the function. E.g. `af9d5aa4-a685-4c5f-a22b-444f80b3cc28` | No |

## Difference between id and instance

For performance reasons (e.g. [AWS lambda], or [Azure functions]), FaaS providers allocate an execution environment for a single instance of a function that is used to serve multiple requests.
Developers exploit this fact to solve the **cold start** issue, caching expensive resources computation between different function execution. 
Furthermore, FaaS providers encourage this behavior, e.g. [Google functions].
Therefore, the attribute `faas.id` differs from `faas.instance` in the following:

    - `faas.id` refers to the current request ID handled by the function;
    - `faas.instance` refers to the execution environment ID of the function.



[AWS lambda]: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
[Azure functions]: https://docs.microsoft.com/en-us/azure/azure-functions/manage-connections#static-clients
[Google functions]: https://cloud.google.com/functions/docs/concepts/exec#function_scope_versus_global_scope