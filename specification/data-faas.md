# Semantic conventions for FaaS spans

This document defines how to describe an instance of a function that runs without provisioning or managing of servers (also known as serverless) with spans.

Span `name` should be set to the function name being executed. Depending on the trigger of the function, additional attributes MUST be set. For example, an HTTP trigger must set the `SpanKind` to `Server` and follow the [HTTP Server semantic conventions](data-http.md#http-server-semantic-conventions).

If Spans following this convention are produced, a Resource of type `faas` MUST exist following the [Resource semantic convention](data-resource-semantic-conventions.md#function-as-a-service).

| Attribute name  | Notes  and examples  | Required? |
|---|---|--|
| `component` | Denotes the type of the span and needs to be `"faas"` | Yes | 
| `faas.trigger` | Type of the trigger on which the function is executed. <br > The following spelling SHOULD be used for trigger strings: "event", "http", "manual", "pubsub", "timer". | Yes |
| `faas.instance` | String containing the unique execution id of the function. E.g. `af9d5aa4-a685-4c5f-a22b-444f80b3cc28` | No |
