# Semantic Conventions

**Status**: [Experimental](../document-status.md)

Spans and metrics often represent well-known protocols such as HTTP requests, database calls, or message queues.
It is important to record these operations consistently across every implementation in every language.
Predictible, uniform data enables observability backends to perform deep automated analysis.
In OpenTelemetry, these definitions are called **semantic conventions**.

Semantic conventions are defined for the following operations:

* [Networking](networking/networking.md): Lower-level session, transport, and network protocols.
* [HTTP](http/http.md): HTTP clients and servers.
* [Database](database/): SQL and NoSQL client calls.
* [RPC/RMI](rpc/): Remote procedure calls (e.g., gRPC).
* [Messaging](messaging/messaging.md): messaging system components (queues, publish/subscribe, etc.).
* [FaaS](faas/): Function as a Service (e.g., AWS Lambda).
* [Runtime](runtime/): Aspects of programming languages and runtimes such as exceptions, threads, and source code annotations.
