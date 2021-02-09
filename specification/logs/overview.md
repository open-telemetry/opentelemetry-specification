# OpenTelemetry Logging Overview

**Status**: [Experimental](../document-status.md)

* [Introduction](#introduction)
* [Limitations of non-OpenTelemetry Solutions](#limitations-of-non-opentelemetry-solutions)
* [OpenTelemetry Solution](#opentelemetry-solution)
* [Log Correlation](#log-correlation)
* [Legacy and Modern Log Sources](#legacy-and-modern-log-sources)
  * [System Logs](#system-logs)
  * [Infrastructure Logs](#infrastructure-logs)
  * [Third-party Application Logs](#third-party-application-logs)
  * [Legacy First-Party Applications Logs](#legacy-first-party-applications-logs)
  * [New First-Party Application Logs](#new-first-party-application-logs)
* [OpenTelemetry Collector](#opentelemetry-collector)
* [Auto-Instrumenting Existing Logging](#auto-instrumenting-existing-logging)
* [Trace Context in Legacy Formats](#trace-context-in-legacy-formats)

## Introduction

Of all telemetry signals logs have probably the biggest legacy. Most programming
languages have built-in logging capabilities or well-known, widely used logging
libraries.

For metrics and traces OpenTelemetry takes the approach of a clean-sheet design,
specifies a new API and provides full implementations of this API in multiple
languages.

Our approach with logs is somewhat different. For OpenTelemetry to be
successful in logging space we need to support existing legacy of logs and
logging libraries, while offering improvements and better integration with the
rest of observability world where possible.

This is in essence the philosophy behind OpenTelemetry's logs support. We
embrace existing logging solutions and make sure OpenTelemetry works nicely with
existing logging libraries, log collection and processing solutions.

## Limitations of non-OpenTelemetry Solutions

Unfortunately existing logging solutions are currently weakly integrated with
the rest of the observability signals. Logs typically have limited support in
tracing and monitoring tools in the form of links that use available and often
incomplete correlation information (such as the time and origin attributes).
This correlation may be fragile because attributes are often added to logs,
traces and metrics via different means (e.g. using different collection agents).
There is no standardized way to include the information about the origin and
source of logs (such as the application and the location/infrastructure where
the application runs) that is uniform with traces and metrics and allows all
telemetry data to be fully correlated in a precise and robust manner.

Similarly, logs have no standardized way to propagate and record the request
execution context. In distributed systems this often results in a disjoint set
of logs collected from different components of the system.

This is how a typical non-OpenTelemetry observability collection pipeline looks
like today:

![Separate Collection Diagram](img/separate-collection.png)

There are often different libraries and different collection agents, using
different protocols and data models, with telemetry data ending up in separate
backends that don't know how to work well together.

## OpenTelemetry Solution

Distributed tracing introduced the notion of request context propagation.

Fundamentally, though, nothing prevents the logs to adopt the same context
propagation concepts. If the recorded logs contained request context identifiers
(such as trace and span ids or user-defined baggage) it would result
in much richer correlation between logs and traces, as well as correlation
between logs emitted by different components of a distributed system. This would
make logs significantly more valuable in distributed systems.

This is one of the promising evolutionary directions for observability tools.
Standardizing log correlation with traces and metrics, adding support for
distributed context propagation for logs, unification of source attribution of
logs, traces and metrics will increase the individual and combined value of
observability information for legacy and modern systems. This is the vision of
OpenTelemetry's collection of logs, traces and metrics:

![Unified Collection Diagram](img/unified-collection.png)

We emit logs, traces and metrics in a way that is compliant with OpenTelemetry
data models, send the data through OpenTelemetry Collector, where it can be
enriched and processed in a uniform manner. For example, Collector can add to
all telemetry data coming from a Kubernetes Pod several attributes that describe
the pod and it can be done automatically using
[k8sprocessor](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/k8sprocessor?tab=doc)
without the need for the Application to do anything special. Most importantly
such enrichment is completely uniform for all 3 signals. The Collector
guarantees that logs, traces and metrics have precisely the same attribute names
and values describing the Kubernetes Pod that they come from. This enables exact
and unambiguous correlation of the signals by the Pod in the backend.

For traces and metrics OpenTelemetry defines a new API that application
developers must use to emit traces and metrics.

For logs we did not take the same path. We realized that there is a much bigger
and more diverse legacy in logging space. There are many existing logging
libraries in different languages, each having their own API. Many programming
languages have established standards for using particular logging libraries. For
example in Java world there are several highly popular and widely used logging
libraries, such as Log4j or Logback.

There are also countless existing prebuilt applications or systems that emit
logs in certain formats. Operators of such applications have no or limited
control on how the logs are emitted. OpenTelemetry needs to support these logs.

Given the above state of the logging space we took the following approach:

- OpenTelemetry defines a [log data model](data-model.md). The purpose of the
  data model is to have a common understanding of what a log record is, what
  data needs to be recorded, transferred, stored and interpreted by a logging
  system.

- Newly designed logging systems are expected to emit logs according to
  OpenTelemetry's log data model. More on this [later](#new-first-party-application-logs).

- Existing log formats can be
  [unambiguously mapped](data-model.md#appendix-a-example-mappings) to
  OpenTelemetry log data model. OpenTelemetry Collector can read such logs and
  translate them to OpenTelemetry log data model.

- Existing applications or logging libraries can be modified to emit logs
  according to OpenTelemetry log data model. OpenTelemetry does not define a new
  logging API that application developers are expected to call. Instead we opt
  to make it easy to continue using the common logging libraries that already
  exist. OpenTelemetry provides guidance on how applications or logging
  libraries can be modified to become OpenTelemetry-compliant (link TBD). We
  also provide SDKs for some languages (link TBD) that make it easy to modify
  the existing logging libraries so that they emit OpenTelemetry-compliant logs.

This approach allows OpenTelemetry to read existing system and application logs,
provides a way for newly built application to emit rich, structured,
OpenTelemetry-compliant logs, and ensures that all logs are eventually
represented according to a uniform log data model on which the backends can
operate.

In the future OpenTelemetry may define a new logging API and provide
implementations for various languages (like we currently do for traces and
metrics), but it is not an immediate priority.

Later in this document we will discuss in more details
[how various log sources are handled](#legacy-and-modern-log-sources) by
OpenTelemetry, but first we need to describe in more details an important
concept: the log correlation.

## Log Correlation

Logs can be correlated with the rest of observability data in a few dimensions:

- By the **time of execution**. Logs, traces and metrics can record the moment
  of time or the range of time the execution took place. This is the most basic
  form of correlation.

- By the **execution context**, also known as the request context. It is a
  standard practice to record the execution context (trace and span ids as well
  as user-defined context) in the spans. OpenTelemetry extends this practice to
  logs where possible by including [TraceId](data-model.md#field-traceid) and
  [SpanId](data-model.md#field-spanid) in the log records. This allows to
  directly correlate logs and traces that correspond to the same execution
  context. It also allows to correlate logs from different components of a
  distributed system that participated in the particular request execution.

- By the **origin of the telemetry**, also known as the Resource context.
  OpenTelemetry traces and metrics contain information about the Resource they
  come from. We extend this practice to logs by including the
  [Resource](data-model.md#field-resource) in log records.
  
These 3 correlations can be the foundation of powerful navigational, filtering,
querying and analytical capabilities. OpenTelemetry aims to record and collects
logs in a manner that enables such correlations.

## Legacy and Modern Log Sources

It is important to distinguish several sorts of legacy and modern log sources.
Firstly, this directly affects how exactly we get access to these logs and how
we collect them. Secondly, we have varying levels of control over how these logs
are generated and whether we can amend the information that can be included in
the logs.

Below we list several categories of logs and describe what can be possibly done
for each category to have better experience in the observability solutions.

### System Logs

These are logs generated by the operating system and over which we have no
control. We cannot change the format or affect what information is included.
Examples of system format are Syslog and Windows Event Logs.

System logs are written at the host level (which may be physical, virtual or
containerized) and have a predefined format and content (note that applications
may also be able to write records to standard system logs: this case is covered
below in the [Third-Party Applications](#third-party-application-logs) section).

System operations recorded in the logs can be a result of a request execution.
However system logs either do not include any data about the request context or
if included it is highly idiosyncratic and thus difficult to identify, parse and
use. This makes it nearly impossible to perform request context correlation for
system logs. However we can and should automatically enrich system logs with the
resource context - the information about the host that is available during
collection. This can include the host name, IP address, container or pod name,
etc. This information should be added to the Resource field of collected log
data.

OpenTelemetry Collector can read system logs (link TBD) and automatically enrich
them with Resource information using the
[resourcedetection](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/master/processor/resourcedetectionprocessor)
processor.

### Infrastructure Logs

These are logs generated by various infrastructure components, such as
Kubernetes events (if you are wondering why events are discussed in the context
of logs see Events and Logs (link TBD)). Like system logs, the
infrastructure logs lack a request context and can be enriched by the resource
context - information about the node, pod, container, etc.

OpenTelemetry Collector or other agents can be used to query logs from most
common infrastructure controllers.

### Third-party Application Logs

Applications typically write logs to standard output, to files or other
specialized medium (e.g. Windows Event Logs for applications). These logs can be
in many different formats, spanning a spectrum along these variations:

- Free-form text formats with no easily automatable and reliable way to parse
  structured data from them.

- Better specified and sometimes customizable formats that can be parsed to
  extract structured data (such as Apache logs or RFC5424 Syslog).

- Formally structured formats (e.g. JSON files with well-defined schema or
  Windows Event Log).

The collection system needs to be able to discover most commonly used
applications and have parsers that can convert these logs into a structured
format. Like system and infrastructure logs, application logs often lack request
context but can be enriched by resource context, including the attributes that
describe the host and infrastructure as well as application-level attributes
(such as the application name, version, name of the database - if it is a DBMS,
etc).

OpenTelemetry recommends to collect logs from application logs using FluentBit
or a similar agent,
[then send](https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/fluentforwardreceiver)
to OpenTelemetry Collector where they can be further processed and enriched.

### Legacy First-Party Applications Logs

These are applications that are created in-house. People tasked with setting up
log collection infrastructure sometimes are able to modify these applications to
alter how logs are written and what information is included in the logs. For
example, the application’s log formatters may be reconfigured to output json
instead of plain text and by doing so help improve the reliability of log
collection.

More significant modifications to these applications can be done manually by
their developers, such as addition of the request context to every log
statement, however this is likely going to be vanishingly rare due to the effort
required.

As opposed to manual efforts we have an interesting opportunity to "upgrade"
application logs in a less laborious way by providing full or semi
auto-instrumenting solutions that modify the logging libraries used by the
application to automatically output the request context such as the trace id or
span id with every log statement. The request context can be automatically
extracted from incoming requests if standard compliant request propagation is
used, e.g. via [W3C TraceContext](https://w3c.github.io/trace-context/). In
addition, the requests outgoing from the application may be injected with the
same request context data, thus resulting in context propagation through the
application and creating an opportunity to have full request context in logs
collected from all applications that can be instrumented in this manner.

Some logging libraries are designed to be extended in this manner relatively
easily. There is no need to actually modify the libraries, instead we can
implement "appender" or "exporter" components for such libraries and implement
the additional log record enrichment in these components.

There are typically 2 ways to collect logs from these applications.

The first approach, assuming the logs are written to files or to standard
output, requires ability to read file logs, tail then, work correctly when log
rotation is used, optionally also parse the logs to convert them into more
structured formats. Parings requires support for different parser types, which
can also be configured to parse custom formats as well as ability to add custom
parsers. Examples of common formats that parsers need to support are: CSV,
Common Log Format, Labeled Tab-separated Values (LTSV), Key/Value Pair format,
JSON, etc. To support this approach OpenTelemetry recommends using FluentBit or
similar agent to read the logs,
[then send the logs](https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/fluentforwardreceiver)
to OpenTelemetry Collector.

![Application to File Logs](img/app-to-file-logs.png)

The benefit of this approach is that how logs are produced and where they are
written by the application requires no or minimal changes. The downside is that
it requires the often non-trivial log file reading and parsing functionality.
Parsing may also be not reliable if the output format is not well-defined.

As mentioned earlier OpenTelemetry does not intend to implement parsers and log
file reading functionality, so if this approach is chosen then an external log
collection agent such as FluentBit must be used to collect the logs.

The second approach is to modify the application so that the logs are output via
a network protocol, e.g. via
[OTLP](https://github.com/open-telemetry/opentelemetry-proto/blob/master/opentelemetry/proto/logs/v1/logs.proto).
The most convenient way to achieve this is to provide addons or extensions to
the commonly used logging libraries. The addons implement sending over such
network protocols, which would then typically require small, localized changes
to the application code to change the logging target.

![Application to Collector](img/app-to-otelcol.png)

The application logs will be also enriched by the resource context, similarly to
how it is done for third-party applications and so will potentially have full
correlation information across all context dimensions.

The downside of this approach is that the simplicity of having the logs in a
local file is lost (e.g. ability to easily inspect the log file locally) and
requires a full buy-in in OpenTelemetry's logging approach. This approach also
only works if the destination that the logs need to be delivered is able to
receive logs via the network protocol that OpenTelemetry can send in.

The benefits of this approach is that it emits the logs in well-defined, formal,
highly structured format, removes all complexity associated with file logs, such
as parsers, log tailing and rotation. It also enables the possibility to send
logs directly to the logging backend without using a log collection agent.

To facilitate both approaches described above OpenTelemetry provides SDKs, which
can be used together with existing logging libraries and which automatically
inject the request context in the emitted logs and provide an easy way to send
the logs via OTLP. These SDKs do not require application developers to modify
each logging statement in the source code and instead require the developer to
enable the OpenTelemetry SDK's logging support at the application startup. After
that the SDK intercepts all emitted logs and modifies the emitting behavior as
configured.

### New First-Party Application Logs

These are greenfield developments. OpenTelemetry provides recommendations and
best practices about how to emit logs (along with traces and metrics) from these
applications. For applicable languages and frameworks the auto-instrumentation
or simple configuration of a logging library to use an OpenTelemetry appender or
extension will still be the easiest way to emit context-enriched logs. As
already described earlier we provide extensions to some popular logging
libraries languages to support the manual instrumentation cases. The extensions
will support the inclusion of the request context in the logs and allow to send
logs using OTLP protocol to the backend or to the Collector, bypassing the need
to have the logs represented as text files. Emitted logs are automatically
augmented by application-specific resource context (e.g. process id, programming
language, logging library name and version, etc). Full correlation across all
context dimensions will be available for these logs.

As noted earlier OpenTelemetry does not currently define a new logging API or
create new user-facing logging libraries. Our initial goal is to enhance
existing popular logging libraries as needed. This is how a typical new
application uses OpenTelemetry API, SDK and the existing log libraries:

![Application, API, SDK Diagram](img/application-api-sdk.png)

## OpenTelemetry Collector

To enable log collection according to this specification we use OpenTelemetry
Collector.

The following functionality exists to enable log collection:

- Support for log data type and log pipelines based on the
  [log data model](data-model.md).

- Ability to read logs from text files, tail the files, understand common log
  rotation schemes, watch directories for log file creation, ability to
  checkpoint file positions and resume reading from checkpoints. This ability is
  implemented by using an externally running FluentBit process (or any other
  similar external log collection agent).

- Ability to parse logs in common text formats and to allow end users to
  customize parsing formats and add custom parsers as needed. FluentBit or
  similar agent is used for this.

- Ability to receive logs via common network protocols for logs, such as Syslog
  and interpret them according to semantic conventions defined in this
  specification. FluentBit or similar agent is used for this. Over time some of
  this functionality may be migrated directly to the Collector.

- Ability to send logs via common network protocols for logs, such as Syslog, or
  vendor-specific log formats. Collector contains exporters that directly
  implement this ability.

## Auto-Instrumenting Existing Logging

We can provide auto-instrumentation for most popular logging libraries. The
auto-instrumented logging statements will do the following:

- Read incoming request context (this is part of broader instrumentation that
  auto-instrumenting libraries perform).

- Configure logging libraries to use trace id and span id fields from request
  context as logging context and automatically include them in all logged
  statements.

This is possible to do for certain languages (e.g. in Java) and we can reuse
[existing open-source libraries](https://docs.datadoghq.com/tracing/connect_logs_and_traces/java/?tab=log4j2)
that do this.

A further optional modification would be to auto-instrument loggers to send logs
directly to the backend via OTLP instead or in addition to writing to a file or
standard output.

## Trace Context in Legacy Formats

Earlier we briefly mentioned that it is possible to modify existing applications
so that they include the Request Context information in the emitted logs.

[OTEP0114](https://github.com/open-telemetry/oteps/pull/114) defines how the
trace context should be recorded in logs. To summarize, the following field
names should be used in legacy formats:

- "trace_id" for [TraceId](data-model.md#field-traceid), hex-encoded.
- "span_id" for [SpanId](data-model.md#field-spanid), hex-encoded.
- "trace_flags" for [trace flags](data-model.md#field-traceflags), formatted
  according to W3C traceflags format.

All 3 fields are optional (see the [data model](data-model.md) for details of
which combination of fields is considered valid).

### Syslog RFC5424

Trace id, span id and traceflags SHOULD be recorded via SD-ID "opentelemetry".

For example:

```
[opentelemetry trace_id="102981ABCD2901" span_id="abcdef1010" trace_flags="01"]
```

### Plain Text Formats

The fields should be recorded according to the customary approach used for a
particular format (e.g. field:value format for LTSV). For example:

```
host:192.168.0.1<TAB>trace_id:102981ABCD2901<TAB>span_id:abcdef1010<TAB>time:[01/Jan/2010:10:11:23 -0400]<TAB>req:GET /health HTTP/1.0<TAB>status:200
```

### JSON Formats

The fields should be recorded as top-level fields in the JSON structure. For example:

```json
{
  "timestamp":1581385157.14429,
  "body":"Incoming request",
  "trace_id":"102981ABCD2901",
  "span_id":"abcdef1010"
}
```

### Other Structured Formats

The fields should be recorded as top-level structured attributes of the log
record as it is customary for the particular format.
