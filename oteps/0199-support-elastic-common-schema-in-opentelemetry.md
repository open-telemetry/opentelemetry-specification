# Merge Elastic Common Schema with OpenTelemetry Semantic Conventions

## Introduction

This proposal is to merge the Elastic Common Schema (ECS) with the OpenTelemetry Semantic Conventions (SemConv) and provide full interoperability in OpenTelemetry component implementations. We propose to implement this by aligning the OpenTelemetry Semantic Conventions with [ECS FieldSets](https://www.elastic.co/docs/reference/ecs/ecs-field-reference#ecs-fieldsets) and vice versa where feasible. The long-term goal is to achieve convergence of ECS and OTel Semantic Conventions into a single open schema so that OpenTelemetry Semantic Conventions truly is a successor of the Elastic Common Schema.

## The Goal

- Long-term, ECS and OTel SemConv will converge into one open standard that is maintained by OpenTelemetry. To kick off this effort, Elastic will nominate several domain experts to join the OpenTelemetry Semantic Convention Approvers to help with maintaining the new standard.
- OTel SemConv will adopt ECS in its full scope (except for individual adjustments in detail where inevitable), including the logging, observability and security domain fields, to make the new schema a true successor of ECS and OTel SemConv.
- Elastic and OpenTelemetry will coordinate and officially announce the direction of the merger (e.g. through official sites, blog posts, etc.)
- Migrate ECS and OTel SemConv users to the new common schema over time and provide utilities to allow the migration to be as easy as possible.

## Scope and Overlap of ECS and OTel SemConv

ECS and OTel SemConv have some overlap today, but also significant areas of mutually enriching fields. The following diagram illustrates the different areas:

<p align="center">
<img src="https://user-images.githubusercontent.com/866830/223049510-93c5dab0-0fc1-4b54-8ac4-e5bcfef81156.png" width="300">
</p>

1. `A`: ECS comes with a rich set of fields that cover broad logging, observability and security use cases. Many fields are additive to the OTel SemConv and would enrich the OTel SemConv without major conflicts. Examples are [Geo information fields](https://www.elastic.co/docs/reference/ecs/ecs-geo), [Threat Fields](https://www.elastic.co/docs/reference/ecs/ecs-threat), and many others.
2. `B`: Conversely, there are attributes in the OTel SemConv that do not exist in ECS and would be an enrichment to ECS. Examples are the [Messaging semantic conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/messaging/) or technology-specific conventions, such as the [AWS SDK conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/aws/).
3. `C`: There is some significant area of overlap between ECS and OTel SemConv. The are `C` represents overlapping fields/attributes that are very similar in ECS and OTel SemConv. The field conflicts in `C` can be resolved through simple field renames and simple transformations.
4. `D`: For some of the fields and attributes there will be conflicts that cannot be resolved through simple renaming or transformation and would require introducing breaking changes on ECS or OTel SemConv side for the purpose of merging the schemas.

## Proposed process to merge ECS with OTel SemConv

The process of merging ECS with OTel SemConv will take time and we propose to do it as part of the stabilization effort for OTel SemConv. During that period and also for a significant period after the merger (sunset period), Elastic will continue to support ECS as a schema. However, further evolution of ECS will happen on the basis of the new, common schema. Elastic will nominate ECS experts to help with maintaining the new schema and will require the approver role for the semantic conventions in OpenTelemetry for the new schema.

With the merger there will be different categories of field conflicts between ECS fields and OTel SemConv attributes (as illustrated in the above figure). We expect the areas `A` and `B` to be less controversial and potentially low-hanging fruits for an enriched, new schema.

For the areas `C` and `D` we propose to resolve conflicts through a close collaboration as part of the stabilization initiative of the OTel SemConv. Where feasible, the goal is to align the OTel SemConv attributes as close as possible with the existing, stable ECS fields. Where alignment is not feasible, the goal is to identify ways to address field conflicts through technical transformations and aliasing, to bridge existing fields and formats into the new schema and vice versa (e.g. through OpenTelemetry Collector Processors).

While realistically truly breaking changes on ECS and OTel SemConv won't be avoidable as part of the merger, they should be the last resort and need to be discussed on a field-by-field basis.  

## Motivation

Adding the Elastic Common Schema (ECS) to OpenTelemetry (OTel) is a great way to accelerate the integration of vendor-created logging and OTel component logs (i.e. OTel Collector Logs Receivers). The goal is to define vendor neutral semantic conventions for most popular types of systems and support vendor-created or open source components (for example HTTP access logs, network logs, system access/authentication logs) extending OTel correlation to these new signals.

Adding the coverage of ECS to OTel would provide guidance to authors of OpenTelemetry Collector Logs Receivers and help establish the OTel Collector as a de facto standard log collector with a well-defined schema to allow for richer data definition.

In addition to the use case of structured logs, the maturity of ECS for SIEM (Security Information and Event Management) is a great opportunity for OpenTelemetry to expand its scope to the security use cases.

Another significant use case is providing first-class support for Kubernetes application logs, system logs, and application introspection events. We would also like to see support for structured events (e.g. [`k8seventsreceiver`](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8seventsreceiver)) and using 'content-type' to identify event types.

We'd like to see different categories of structured logs being well-supported in the [OTel Log Data Model](../specification/logs/data-model.md), presumably through [semantic conventions for log attributes](../specification/logs/data-model.md#field-attributes). For example, NGINX access logs and Apache access logs should be processed the same way as structured logs. This would help in trace and metric correlation with such log data as well as it would help grow the ecosystem of curated UIs provided by observability backends and monitoring dashboards (e.g. one single HTTP access log dashboard benefiting Apache httpd, NGINX, and HAProxy).

## Customer Motivation

Adoption of OTel logs will accelerate greatly if ECS is leveraged as the common standard, using this basis for normalization. OTel Logs adoption will be accelerated by this support. For example, ECS can provide the unified structured format for handling vendor-generated logs along with open source logs.

Customers will benefit from turnkey logs integrations that will be fully recognized by OTel-compatible observability products and services.

OpenTelemetry logging is today mostly structured when instrumentation libraries are used. However, most of the logs which exist today are generated by software, hardware, and cloud services which the user cannot control. OpenTelemetry provides a limited set of "reference integrations" to structure logs: primarily the [OpenTelemetry Collector Kubernetes Events Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8seventsreceiver) and an example of a regular expression based parsing of Tomcat access logs with OpenTelemetry Collector File Receiver ([here](https://github.com/open-telemetry/opentelemetry-log-collection/blob/30807b96b2f0771e7d11452ebf98fe5e211ed6d7/examples/tomcat/config.yaml#L20)).
By expanding the OTel semantic conventions with further namespaces already defined in ECS, a broader coverage of such mappings from different sources can be defined and implemented in the OTel collector.
This, for example, includes logs from network appliances (mapping to the `network` and `interface` namespaces in ECS).

The semantic conventions of a log are a challenge. What is a specific component defined in a log and how does it relate to other logs which have the same semantic component defined differently? ECS has already done some heavy-lifting on defining a unified set of semantic conventions which can be adopted in OTel.

OpenTelemetry has the potential to grow exponentially if the data from these other services can be correlated with instrumented code and components. In order to do this, industry stakeholders should leverage a common and standard logging data model which allows for the mapping of these different data types. The OpenTelemetry data protocol can provide this interoperable open standard. This unlocks countless use cases, and ensures that OpenTelemetry can work with other technologies which are not OpenTelemetry compliant.

## Background

### What is ECS?

The [Elastic Common Schema (ECS)](https://github.com/elastic/ecs) is an open source specification, developed with support from Elastic's user community. ECS defines a common set of fields to be used when storing data in Elasticsearch, such as logs, metrics, and security and audit events. The goal of ECS is to enable and encourage users of Elasticsearch to normalize their event data, so that they can better analyze, visualize, and correlate the data represented in their events. Learn more at: [https://www.elastic.co/docs/reference/ecs](https://www.elastic.co/docs/reference/ecs)

The coverage of ECS is very broad including in depth support for logs, security, and network events such as "[logs.* fields](https://www.elastic.co/docs/reference/ecs/ecs-log)" , "[geo.* fields](https://www.elastic.co/docs/reference/ecs/ecs-geo)", "[tls.* fields](https://www.elastic.co/docs/reference/ecs/ecs-tls)", "[dns.* fields](https://www.elastic.co/docs/reference/ecs/ecs-dns)", or "[vulnerability.* fields](https://www.elastic.co/docs/reference/ecs/ecs-vulnerability)".

ECS has the following guiding principles:

* ECS favors human readability in order to enable broader adoption as many fields can be understood without having to read up their meaning in the reference,
* ECS events include metadata to enable correlations across any dimension (host, data center, Docker image, ip address...),
  * ECS does not differentiate the metadata fields that are specific to each event of the event source and the metadata that is shared by all the events of the source in the way OTel does, which differentiates between Resource Attributes and Log/Span/Metrics Attributes,
* ECS groups fields in namespaces in order to:
  * Offer consistency and readability,
  * Enable reusability of namespaces in different contexts,
    * For example, the "geo" namespace is nested in the "client.geo", "destination.geo", "host.geo" or "threat.indicator.geo" namespaces
  * Enable extensibility by adding fields to namespaces and adding new namespaces,
  * Prevent field name conflicts
* ECS covers a broad spectrum of events with 40+ namespaces including detailed coverage of security and network events. It's much broader than simple logging use cases.

### Example of a log message structured with ECS: NGINX access logs

Example of a NGINX Access Log entry structured with ECS

```json
{
   "@timestamp":"2020-03-25T09:51:23.000Z",
   "client":{
      "ip":"10.42.42.42"
   },
   "http":{
      "request":{
         "referrer":"-",
         "method":"GET"
      },
      "response":{
         "status_code":200,
         "body":{
            "bytes":2571
         }
      },
      "version":"1.1"
   },
   "url":{
      "path":"/blog"
   },
   "user_agent":{
      "original":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
      "os":{
         "name":"Mac OS X",
         "version":"10.14.0",
         "full":"Mac OS X 10.14.0"
      },
      "name":"Chrome",
      "device":{
         "name":"Other"
      },
      "version":"70.0.3538.102"
   },
   "log":{
      "file":{
         "path":"/var/log/nginx/access.log"
      },
      "offset":33800
   },
   "host": {
     "hostname": "cyrille-laptop.home",
     "os": {
       "build": "19D76",
       "kernel": "19.3.0",
       "name": "Mac OS X",
       "family": "darwin",
       "version": "10.15.3",
       "platform": "darwin"
     },
     "name": "cyrille-laptop.home",
     "id": "04A12D9F-C409-5352-B238-99EA58CAC285",
     "architecture": "x86_64"
   }
}
```

## Comparison between OpenTelemetry Semantic Conventions for logs and ECS

## Principles

| Description | [OTel Logs and Event Record](../specification/logs/data-model.md#log-and-event-record-definition) | [Elastic Common Schema (ECS)](https://www.elastic.co/docs/reference/ecs) |
| ----------- | ------------- | -------- |
| Metadata shared by all the Log Messages / Spans / Metrics of an application instance | Resource Attributes | ECS fields |
| Metadata specific to each Log Message / Span / Metric data point | Attributes | ECS Fields |
| Message of log events | Body | [message field](https://www.elastic.co/docs/reference/ecs/ecs-base#field-message) |
| Naming convention | Dotted names | Dotted names |
| Reusability of namespaces | Namespaces are intended to be composed | Namespaces are intended to be composed |
| Extensibility | Attributes can be extended by either adding a user defined field to an existing namespaces or introducing new namespaces. | Extra attributes can be added in each namespace and users can create their own namespaces |

## Data Types

| Category | <a href="../specification/logs/data-model.md#log-and-event-record-definition">OTel Logs and Event Record</a> (all or a subset of <a href="https://protobuf.dev/programming-guides/proto3/">GRPC data types</a>) | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/field-data-types">ECS Data Types</a> |
| --- | --- | --- |
| Text | string | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/text#text-field-type">text</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/text#match-only-text-field-type">match_only_text</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword#keyword-field-type">keyword</a> <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword#constant-keyword-field-type">constant_keyword</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword#wildcard-field-type">wildcard</a> |
| Dates | uint64 nanoseconds since UNIX epoch | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/date">date</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/date_nanos">date_nanos</a> |
| Numbers | number | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/number">long</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/number">double</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/number">scaled_float</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/boolean">boolean</a>… |
| Objects | uint32, uint64… | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/object">object</a> (JSON object), <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/flattened">flattened</a> (An entire JSON object as a single field value) |
| Structured Objects | No complex semantic data type specified for the moment (e.g. string is being used for ip addresses rather than having an "ip" data structure in OTel). <br/> Note that OTel supports arrays and nested objects. | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/ip">ip</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/geo-point">geo_point</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/geo-shape">geo_shape</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/version">version</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/range">long_range</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/range">date_range</a>, <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/range">ip_range</a> |
| Binary data | Byte sequence | <a href="https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/binary">binary</a> |

## Known Differences

Some differences exist on fields that are both defined in OpenTelemetry Semantic Conventions and in ECS. In this case, it would make sense for overlapping ECS fields to not be integrated in the new specification.

<!-- 
As the markdown code of the tables is hard to read and maintain with very long lines, we experiment maintaining this one as an HTML table 
-->

<table>
  <tr>
   <td><strong><a href="../specification/logs/data-model.md#log-and-event-record-definition">OTel Logs and Event Record</a></strong>
   </td>
   <td><strong><a href="https://www.elastic.co/docs/reference/ecs">Elastic Common Schema (ECS)</a></strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td><a href="../specification/logs/data-model.md#log-and-event-record-definition">Timestamp</a> (uint64 nanoseconds since UNIX epoch)
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-base#field-timestamp">@timestamp</a> (date)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td><a href="../specification/logs/data-model.md#log-and-event-record-definition">TraceId</a> (byte sequence), <a href="../specification/logs/data-model.md#log-and-event-record-definition">SpanId</a> (byte sequence)
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-tracing#field-trace-id">trace.id</a> (keyword), <a href="https://www.elastic.co/docs/reference/ecs/ecs-tracing#field-trace-id">span.id</a> (keyword)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>N/A
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-tracing#field-transaction-id">Transaction.id</a> (keyword)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td><a href="../specification/logs/data-model.md#log-and-event-record-definition">SeverityText</a> (string)
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-log#field-log-syslog-severity-name">log.syslog.severity.name</a> (keyword), <a href="https://www.elastic.co/docs/reference/ecs/ecs-log#field-log-level">log.level</a> (keyword)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td><a href="../specification/logs/data-model.md#log-and-event-record-definition">SeverityNumber</a> (number)
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-log#field-log-syslog-severity-code">log.syslog.severity.code</a>
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td><a href="../specification/logs/data-model.md#log-and-event-record-definition">Body</a> (any)
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-base#field-message">message</a> (match_only_text)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>process.cpu.load (not specified but collected by OTel Collector)
<br/>
<a href="https://github.com/open-telemetry/semantic-conventions/blob/main/docs/system/process-metrics.md">process.cpu.time</a> (async counter)
<br/>
<a href="https://github.com/open-telemetry/semantic-conventions/blob/main/docs/system/system-metrics.md">system.cpu.utilization</a>
   </td>
   <td><a href="https://www.elastic.co/docs/reference/ecs/ecs-host#field-host-cpu-usage">host.cpu.usage</a> (scaled_float) with a slightly different measurement than what OTel metrics measure
   </td>
   <td>Note that most metrics have slightly different names and semantics between ECS and OpenTelemetry
   </td>
  </tr>
</table>

## How would OpenTelemetry users practically use the new OpenTelemetry Semantic Conventions Attributes brought by ECS

The concrete usage of ECS-enriched OpenTelemetry Semantic Conventions Attributes depends on the use case and the fieldset.
In general, OpenTelemetry users would transparently upgrade to ECS and benefit from the alignment of attributes for new use cases.
The main goal of this work is to enable producers of OpenTelemetry signals (collectors/exporters) to create enriched uniform signals for existing and new use cases.
The uniformity allows for easier correlation between signals originating from different producers. The richness ensures more options for Root Cause Analysis, correlation and reporting.

While ECS covers many different use cases and scenarios, in the following, we outline two examples:

### Example: OpenTelemetry Collector Receiver to collect the access logs of a web server

The author of the "OTel Collector Access logs file receiver for web server XXX" would find in the OTel Semantic Convention specifications all
the guidance to map the fields of the web server logs, not only the attributes that the OTel Semantic Conventions has specified today for
[HTTP calls](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.9.0/specification/trace/semantic_conventions/http.md),
but also attributes for the [User Agent](https://www.elastic.co/docs/reference/ecs/ecs-user_agent)
or the [Geo Data](https://www.elastic.co/docs/reference/ecs/ecs-geo).

This completeness of the mapping will help the author of the integration to produce OTel Log messages that will be compatible with access logs
of other web components (web servers, load balancers, L7 firewalls...) allowing turnkey integration with observability solutions
and enabling richer correlations.

### Other Examples

- [Logs with sessions (VPN Logs, Network Access Sessions, RUM sessions, etc.)](https://github.com/elastic/ecs/blob/main/rfcs/text/0004-session.md#usage)
- [Logs from systems processing files](https://www.elastic.co/docs/reference/ecs/ecs-file)

## Alternatives / Discussion

### Prometheus Naming Conventions

Prometheus is a de facto standard for observability metrics and OpenTelemetry already provides full interoperability with the Prometheus ecosystem.

It would be useful to get interoperability between metrics collected by [official Prometheus exporters](https://prometheus.io/docs/instrumenting/exporters/) (e.g. the [Node/system metrics exporter](https://github.com/prometheus/node_exporter) or the [MySQL server exporter](https://github.com/prometheus/mysqld_exporter)) and their equivalent OpenTelemetry Collector receivers (e.g. OTel Collector [Host Metrics Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/hostmetricsreceiver) or [MySQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/mysqlreceiver)).

Note that one of the challenges with Prometheus metrics naming conventions is that these are implicit conventions defined by each integration author which doesn't enable correlation due to the lack of consistency across integrations. For example, this inconsistency increases the complexity that an end user has to deal with when configuring and monitoring alerts.

Prometheus' conventions are restricted to the style of the name of the metrics (see [Prometheus Metric and label naming](https://prometheus.io/docs/practices/naming/)) but don't specify unified metric names.

## Other areas that need to be addressed by OTel (the project)

Some areas that need to be addressed in the long run as ECS is integrated into OTel include defining the innovation process,
ensuring the OTel specification incorporates the changes to accommodate ECS, and a process for handling breaking changes if any (the proposal
[Define semantic conventions and instrumentation stability #2180](https://github.com/open-telemetry/opentelemetry-specification/pull/2180)
should tackle this point). Also, migration of existing naming (e.g. Prometheus exporter) to standardized convention (see
[Semantic Conventions for System Metrics](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/system/system-metrics.md) ,
[Semantic Conventions for OS Process Metrics](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/system/process-metrics.md)).
