# Data Model Appendix

Note: this document is NOT a spec, it is provided to support the Logs
[Data Model](./data-model.md) specification. These examples provided purely
for demonstrative purposes and are not exhaustive or canonical; please refer to
the respective exporter documentation if exact details are required.

<!-- toc -->

- [Appendix A. Example Mappings](#appendix-a-example-mappings)
  * [RFC5424 Syslog](#rfc5424-syslog)
  * [Windows Event Log](#windows-event-log)
  * [SignalFx Events](#signalfx-events)
  * [Splunk HEC](#splunk-hec)
  * [Log4j](#log4j)
  * [Zap](#zap)
  * [Apache HTTP Server access log](#apache-http-server-access-log)
  * [CloudTrail Log Event](#cloudtrail-log-event)
  * [Google Cloud Logging](#google-cloud-logging)
  * [Elastic Common Schema](#elastic-common-schema)
- [Appendix B: `SeverityNumber` example mappings](#appendix-b-severitynumber-example-mappings)
- [References](#references)

<!-- tocstop -->

## Appendix A. Example Mappings

This section contains examples of mapping of other events and logs formats to
this data model.

### RFC5424 Syslog

<table>
  <tr>
    <td>Property</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>TIMESTAMP</td>
    <td>Timestamp</td>
    <td>Time when an event occurred measured by the origin clock.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>SEVERITY</td>
    <td>enum</td>
    <td>Defines the importance of the event. Example: <code>Debug</code></td>
    <td>Severity</td>
  </tr>
  <tr>
    <td>FACILITY</td>
    <td>enum</td>
    <td>Describes where the event originated. A predefined list of UNIX processes. Part of event source identity. Example: <code>mail system</code></td>
    <td>`Attributes["syslog.facility"]`</td>
  </tr>
  <tr>
    <td>VERSION</td>
    <td>number</td>
    <td>Meta: protocol version, orthogonal to the event.</td>
    <td>`Attributes["syslog.version"]`</td>
  </tr>
  <tr>
    <td>HOSTNAME</td>
    <td>string</td>
    <td>Describes the location where the event originated. Possible values are FQDN, IP address, etc.</td>
    <td>`Resource["host.name"]`</td>
  </tr>
  <tr>
    <td>APP-NAME</td>
    <td>string</td>
    <td>User-defined app name. Part of event source identity.</td>
    <td>`Resource["service.name"]`</td>
  </tr>
  <tr>
    <td>PROCID</td>
    <td>string</td>
    <td>Not well defined. May be used as a meta field for protocol operation purposes or may be part of event source identity.</td>
    <td>`Attributes["syslog.procid"]`</td>
  </tr>
  <tr>
    <td>MSGID</td>
    <td>string</td>
    <td>Defines the type of the event. Part of event source identity. Example: "TCPIN"</td>
    <td>`Attributes["syslog.msgid"]`</td>
  </tr>
  <tr>
    <td>STRUCTURED-DATA</td>
    <td>array of maps of string to string</td>
    <td>A variety of use cases depending on the SD-ID:<br>
Can describe event source identity.<br>
Can include data that describes particular occurrence of the event.<br>
Can be meta-information, e.g. quality of timestamp value.</td>
    <td>SD-ID origin.swVersion map to `Resource["service.version"]`. SD-ID origin.ip map to `Attributes["client.address"]`. Rest of SD-IDs -> `Attributes["syslog.*"]`</td>
  </tr>
  <tr>
    <td>MSG</td>
    <td>string</td>
    <td>Free-form text message about the event. Typically human readable.</td>
    <td>Body</td>
  </tr>
</table>

### Windows Event Log

<table>
  <tr>
    <td>Property</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>TimeCreated</td>
    <td>Timestamp</td>
    <td>The time stamp that identifies when the event was logged.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>Level</td>
    <td>enum</td>
    <td>Contains the severity level of the event.</td>
    <td>Severity</td>
  </tr>
  <tr>
    <td>Computer</td>
    <td>string</td>
    <td>The name of the computer on which the event occurred.</td>
    <td>`Resource["host.name"]`</td>
  </tr>
  <tr>
    <td>EventID</td>
    <td>uint</td>
    <td>The identifier that the provider used to identify the event.</td>
    <td>`Attributes["winlog.event_id"]`</td>
  </tr>
  <tr>
    <td>Message</td>
    <td>string</td>
    <td>The message string.</td>
    <td>Body</td>
  </tr>
  <tr>
    <td>Rest of the fields.</td>
    <td>any</td>
    <td>All other fields in the event.</td>
    <td>`Attributes["winlog.*"]`</td>
  </tr>
</table>

### SignalFx Events

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>Timestamp</td>
    <td>Timestamp</td>
    <td>Time when the event occurred measured by the origin clock.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>EventType</td>
    <td>string</td>
    <td>Short machine understandable string describing the event type. SignalFx specific concept. Non-namespaced. Example: k8s Event Reason field.</td>
    <td>`Attributes["com.splunk.signalfx.event_type"]`</td>
  </tr>
  <tr>
    <td>Category</td>
    <td>enum</td>
    <td>Describes where the event originated and why. SignalFx specific concept. Example: AGENT. </td>
    <td>`Attributes["com.splunk.signalfx.event_category"]`</td>
  </tr>
  <tr>
    <td>Dimensions</td>
    <td>map&lt;string, string></td>
    <td>Helps to define the identity of the event source together with EventType and Category. Multiple occurrences of events coming from the same event source can happen across time and they all have the value of Dimensions. </td>
    <td>Resource</td>
  </tr>
  <tr>
    <td>Properties</td>
    <td>map&lt;string, any></td>
    <td>Additional information about the specific event occurrence. Unlike Dimensions which are fixed for a particular event source, Properties can have different values for each occurrence of the event coming from the same event source.</td>
    <td>Attributes</td>
  </tr>
</table>

### Splunk HEC

We apply this mapping from HEC to the unified model:

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>time</td>
    <td>numeric, string</td>
    <td>The event time in epoch time format, in seconds.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>host</td>
    <td>string</td>
    <td>The host value to assign to the event data. This is typically the host name of the client that you are sending data from.</td>
    <td>`Resource["host.name"]`</td>
  </tr>
  <tr>
    <td>source</td>
    <td>string</td>
    <td>The source value to assign to the event data. For example, if you are sending data from an app you are developing, you could set this key to the name of the app.</td>
    <td>`Resource["com.splunk.source"]`</td>
  </tr>
  <tr>
    <td>sourcetype</td>
    <td>string</td>
    <td>The sourcetype value to assign to the event data.</td>
    <td>`Resource["com.splunk.sourcetype"]`</td>
  </tr>
  <tr>
    <td>event</td>
    <td>any</td>
    <td>The JSON representation of the raw body of the event. It can be a string, number, string array, number array, JSON object, or a JSON array.</td>
    <td>Body</td>
  </tr>
  <tr>
    <td>fields</td>
    <td>map&lt;string, any></td>
    <td>Specifies a JSON object that contains explicit custom fields.</td>
    <td>Attributes</td>
  </tr>
  <tr>
    <td>index</td>
    <td>string</td>
    <td>The name of the index by which the event data is to be indexed. The index you specify here must be within the list of allowed indexes if the token has the indexes parameter set.</td>
    <td>`Attributes["com.splunk.index"]`</td>
  </tr>
</table>

When mapping from the unified model to HEC, we apply this additional mapping:

<table>
  <tr>
    <td>Unified model element</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to HEC</td>
  </tr>
  <tr>
    <td>SeverityText</td>
    <td>string</td>
    <td>The severity of the event as a human-readable string.</td>
    <td>`Fields["otel.log.severity.text"]`</td>
  </tr>
    <tr>
    <td>SeverityNumber</td>
    <td>string</td>
    <td>The severity of the event as a number.</td>
    <td>`Fields["otel.log.severity.number"]`</td>
  </tr>
  <tr>
    <td>Name</td>
    <td>string</td>
    <td>Short event identifier that does not contain varying parts.</td>
    <td>`Fields["otel.log.name"]`</td>
  </tr>
  <tr>
    <td>TraceId</td>
    <td>string</td>
    <td>Request trace id.</td>
    <td>`Fields["trace_id"]`</td>
  </tr>
  <tr>
    <td>SpanId</td>
    <td>string</td>
    <td>Request span id.</td>
    <td>`Fields["span_id"]`</td>
  </tr>
  <tr>
    <td>TraceFlags</td>
    <td>string</td>
    <td>W3C trace flags.</td>
    <td>`Fields["trace_flags"]`</td>
  </tr>
</table>

### Log4j

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>Instant</td>
    <td>Timestamp</td>
    <td>Time when an event occurred measured by the origin clock.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>Level</td>
    <td>enum</td>
    <td>Log level.</td>
    <td>Severity</td>
  </tr>
  <tr>
    <td>Message</td>
    <td>string</td>
    <td>Human readable message.</td>
    <td>Body</td>
  </tr>
  <tr>
    <td>All other fields</td>
    <td>any</td>
    <td>Structured data.</td>
    <td>Attributes</td>
  </tr>
</table>

### Zap

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>ts</td>
    <td>Timestamp</td>
    <td>Time when an event occurred measured by the origin clock.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>level</td>
    <td>enum</td>
    <td>Logging level.</td>
    <td>Severity</td>
  </tr>
  <tr>
    <td>caller</td>
    <td>string</td>
    <td>Calling function's filename and line number.
</td>
    <td>Attributes, key=TBD</td>
  </tr>
  <tr>
    <td>msg</td>
    <td>string</td>
    <td>Human readable message.</td>
    <td>Body</td>
  </tr>
  <tr>
    <td>All other fields</td>
    <td>any</td>
    <td>Structured data.</td>
    <td>Attributes</td>
  </tr>
</table>

### Apache HTTP Server access log

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>%t</td>
    <td>Timestamp</td>
    <td>Time when an event occurred measured by the origin clock.</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>%a</td>
    <td>string</td>
    <td>Client address</td>
    <td>`Attributes["network.peer.address"]`</td>
  </tr>
  <tr>
    <td>%A</td>
    <td>string</td>
    <td>Server address</td>
    <td>`Attributes["network.local.address"]`</td>
  </tr>
  <tr>
    <td>%h</td>
    <td>string</td>
    <td>Client hostname.</td>
    <td>`Attributes["client.address"]`</td>
  </tr>
  <tr>
    <td>%m</td>
    <td>string</td>
    <td>The request method.</td>
    <td>`Attributes["http.request.method"]`</td>
  </tr>
  <tr>
    <td>%v,%p,%U,%q</td>
    <td>string</td>
    <td>Multiple fields that can be composed into URL.</td>
    <td>`Attributes["url.full"]`</td>
  </tr>
  <tr>
    <td>%>s</td>
    <td>string</td>
    <td>Response status.</td>
    <td>`Attributes["http.response.status_code"]`</td>
  </tr>
  <tr>
    <td>All other fields</td>
    <td>any</td>
    <td>Structured data.</td>
    <td>Attributes, key=TBD</td>
  </tr>
</table>

### CloudTrail Log Event

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>eventTime</td>
    <td>string</td>
    <td>The date and time the request was made, in coordinated universal time (UTC).</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>eventSource</td>
    <td>string</td>
    <td>The service that the request was made to. This name is typically a short form of the service name without spaces plus .amazonaws.com.</td>
    <td>`Resource["service.name"]`?</td>
  </tr>
  <tr>
    <td>awsRegion</td>
    <td>string</td>
    <td>The AWS region that the request was made to, such as us-east-2.</td>
    <td>`Resource["cloud.region"]`</td>
  </tr>
  <tr>
    <td>sourceIPAddress</td>
    <td>string</td>
    <td>The IP address that the request was made from.</td>
    <td>`Attributes["client.address"]`</td>
  </tr>
  <tr>
    <td>errorCode</td>
    <td>string</td>
    <td>The AWS service error if the request returns an error.</td>
    <td>`Attributes["cloudtrail.error_code"]`</td>
  </tr>
  <tr>
    <td>errorMessage</td>
    <td>string</td>
    <td>If the request returns an error, the description of the error.</td>
    <td>Body</td>
  </tr>
  <tr>
    <td>All other fields</td>
    <td>*</td>
    <td></td>
    <td>`Attributes["cloudtrail.*"]`</td>
  </tr>
</table>

### Google Cloud Logging

| Field | Type | Description | Maps to Unified Model Field |
| ----- | ---- | ----------- | --------------------------- |
| timestamp | string | The time the event described by the log entry occurred. | Timestamp |
| resource | MonitoredResource | The monitored resource that produced this log entry. | Resource |
| log_name | string | The URL-encoded LOG_ID suffix of the log_name field identifies which log stream this entry belongs to. | `Attributes["gcp.log_name"]` |
| json_payload | google.protobuf.Struct | The log entry payload, represented as a structure that is expressed as a JSON object. | Body |
| proto_payload | google.protobuf.Any | The log entry payload, represented as a protocol buffer. | Body |
| text_payload | string | The log entry payload, represented as a Unicode string (UTF-8). | Body |
| severity | LogSeverity | The severity of the log entry. | Severity |
| trace | string | The trace associated with the log entry, if any. | TraceId |
| span_id | string | The span ID within the trace associated with the log entry. | SpanId |
| labels | map<string,string> | A set of user-defined (key, value) data that provides additional information about the log entry. | Attributes |
| http_request | HttpRequest | The HTTP request associated with the log entry, if any. | `Attributes["gcp.http_request"]` |
| trace_sampled | boolean | The sampling decision of the trace associated with the log entry. | TraceFlags.SAMPLED |
| All other fields | | | `Attributes["gcp.*"]` |

### Elastic Common Schema

<table>
  <tr>
    <td>Field</td>
    <td>Type</td>
    <td>Description</td>
    <td>Maps to Unified Model Field</td>
  </tr>
  <tr>
    <td>@timestamp</td>
    <td>datetime</td>
    <td>Time the event was recorded</td>
    <td>Timestamp</td>
  </tr>
  <tr>
    <td>message</td>
    <td>string</td>
    <td>Any type of message</td>
    <td>Body</td>
  </tr>
  <tr>
    <td>labels</td>
    <td>key/value</td>
    <td>Arbitrary labels related to the event</td>
    <td>Attributes[*]</td>
  </tr>
  <tr>
    <td>tags</td>
    <td>array of string</td>
    <td>List of values related to the event</td>
    <td>?</td>
  </tr>
  <tr>
    <td>trace.id</td>
    <td>string</td>
    <td>Trace ID</td>
    <td>TraceId</td>
  </tr>
  <tr>
    <td>span.id*</td>
    <td>string</td>
    <td>Span ID</td>
    <td>SpanId</td>
  </tr>
  <tr>
    <td>agent.ephemeral_id</td>
    <td>string</td>
    <td>Ephemeral ID created by agent</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>agent.id</td>
    <td>string</td>
    <td>Unique identifier of this agent</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>agent.name</td>
    <td>string</td>
    <td>Name given to the agent</td>
    <td>`Resource["telemetry.sdk.name"]`</td>
  </tr>
  <tr>
    <td>agent.type</td>
    <td>string</td>
    <td>Type of agent</td>
    <td>`Resource["telemetry.sdk.language"]`</td>
  </tr>
  <tr>
    <td>agent.version</td>
    <td>string</td>
    <td>Version of agent</td>
    <td>`Resource["telemetry.sdk.version"]`</td>
  </tr>
  <tr>
    <td>source.ip, client.ip</td>
    <td>string</td>
    <td>The IP address that the request was made from.</td>
    <td>`Attributes["client.address"]`</td>
  </tr>
  <tr>
    <td>cloud.account.id</td>
    <td>string</td>
    <td>ID of the account in the given cloud</td>
    <td>`Resource["cloud.account.id"]`</td>
  </tr>
  <tr>
    <td>cloud.availability_zone</td>
    <td>string</td>
    <td>Availability zone in which this host is running.</td>
    <td>`Resource["cloud.zone"]`</td>
  </tr>
  <tr>
    <td>cloud.instance.id</td>
    <td>string</td>
    <td>Instance ID of the host machine.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>cloud.instance.name</td>
    <td>string</td>
    <td>Instance name of the host machine.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>cloud.machine.type</td>
    <td>string</td>
    <td>Machine type of the host machine.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>cloud.provider</td>
    <td>string</td>
    <td>Name of the cloud provider. Example values are aws, azure, gcp, or digitalocean.</td>
    <td>`Resource["cloud.provider"]`</td>
  </tr>
  <tr>
    <td>cloud.region</td>
    <td>string</td>
    <td>Region in which this host is running.</td>
    <td>`Resource["cloud.region"]`</td>
  </tr>
  <tr>
    <td>cloud.image.id*</td>
    <td>string</td>
    <td></td>
    <td>`Resource["host.image.name"]`</td>
  </tr>
  <tr>
    <td>container.id</td>
    <td>string</td>
    <td>Unique container id</td>
    <td>`Resource["container.id"]`</td>
  </tr>
  <tr>
    <td>container.image.name</td>
    <td>string</td>
    <td>Name of the image the container was built on.</td>
    <td>`Resource["container.image.name"]`</td>
  </tr>
  <tr>
    <td>container.image.tag</td>
    <td>Array of string</td>
    <td>Container image tags.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>container.labels</td>
    <td>key/value</td>
    <td>Image labels.</td>
    <td>Attributes[*]</td>
  </tr>
  <tr>
    <td>container.name</td>
    <td>string</td>
    <td>Container name.</td>
    <td>`Resource["container.name"]`</td>
  </tr>
  <tr>
    <td>container.runtime</td>
    <td>string</td>
    <td>Runtime managing this container. Example: "docker"</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>destination.address</td>
    <td>string</td>
    <td>Destination address for the event</td>
    <td>`Attributes["destination.address"]`</td>
  </tr>
  <tr>
    <td>error.code</td>
    <td>string</td>
    <td>Error code describing the error.</td>
    <td>`Attributes["error.code"]`</td>
  </tr>
  <tr>
    <td>error.id</td>
    <td>string</td>
    <td>Unique identifier for the error.</td>
    <td>`Attributes["error.id"]`</td>
  </tr>
  <tr>
    <td>error.message</td>
    <td>string</td>
    <td>Error message.</td>
    <td>`Attributes["error.message"]`</td>
  </tr>
  <tr>
    <td>error.stack_trace</td>
    <td>string</td>
    <td>The stack trace of this error in plain text.</td>
    <td>`Attributes["error.stack_trace]</td>
  </tr>
  <tr>
    <td>host.architecture</td>
    <td>string</td>
    <td>Operating system architecture</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>host.domain</td>
    <td>string</td>
    <td>Name of the domain of which the host is a member.<br>For example, on Windows this could be the host’s Active Directory domain or NetBIOS domain name. For Linux this could be the domain of the host’s LDAP provider.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>host.name</td>
    <td>string</td>
    <td>Hostname of the host.<br>It normally contains what the hostname command returns on the host machine.</td>
    <td>`Resource["host.name"]`</td>
  </tr>
  <tr>
    <td>host.id</td>
    <td>string</td>
    <td>Unique host id.</td>
    <td>`Resource["host.id"]`</td>
  </tr>
  <tr>
    <td>host.ip</td>
    <td>Array of string</td>
    <td>Host IP</td>
    <td>`Resource["host.ip"]`</td>
  </tr>
  <tr>
    <td>host.mac</td>
    <td>array of string</td>
    <td>MAC addresses of the host</td>
    <td>`Resource["host.mac"]`</td>
  </tr>
  <tr>
    <td>host.name</td>
    <td>string</td>
    <td>Name of the host.<br>It may contain what hostname returns on UNIX systems, the fully qualified, or a name specified by the user. </td>
    <td>`Resource["host.name"]`</td>
  </tr>
  <tr>
    <td>host.type</td>
    <td>string</td>
    <td>Type of host.</td>
    <td>`Resource["host.type"]`</td>
  </tr>
  <tr>
    <td>host.uptime</td>
    <td>string</td>
    <td>Seconds the host has been up.</td>
    <td>?</td>
  </tr>
  <tr>
    <td>service.ephemeral_id</td>
    <td>string</td>
    <td>Ephemeral identifier of this service</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>service.id</td>
    <td>string</td>
    <td>Unique identifier of the running service. If the service is comprised of many nodes, the service.id should be the same for all nodes.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>service.name</td>
    <td>string</td>
    <td>Name of the service data is collected from.</td>
    <td>`Resource["service.name"]`</td>
  </tr>
  <tr>
    <td>service.node.name</td>
    <td>string</td>
    <td>Specific node serving that service</td>
    <td>`Resource["service.instance.id"]`</td>
  </tr>
  <tr>
    <td>service.state</td>
    <td>string</td>
    <td>Current state of the service.</td>
    <td>`Attributes["service.state"]`</td>
  </tr>
  <tr>
    <td>service.type</td>
    <td>string</td>
    <td>The type of the service data is collected from.</td>
    <td>**Resource</td>
  </tr>
  <tr>
    <td>service.version</td>
    <td>string</td>
    <td>Version of the service the data was collected from.</td>
    <td>`Resource["service.version"]`</td>
  </tr>
</table>

\* Not yet formalized into ECS.

\*\* A resource that doesn’t exist in the
[OpenTelemetry resource semantic convention](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md).

This is a selection of the most relevant fields. See
[for the full reference](https://www.elastic.co/docs/reference/ecs/ecs-field-reference)
for an exhaustive list.

## Appendix B: `SeverityNumber` example mappings

|Syslog       |WinEvtLog  |Log4j |Zap   |java.util.logging|.NET (Microsoft.Extensions.Logging)|SeverityNumber|
|-------------|-----------|------|------|-----------------|-----------------------------------|--------------|
|             |           |TRACE |      | FINEST          |LogLevel.Trace                     |TRACE         |
|Debug        |Verbose    |DEBUG |Debug | FINER           |LogLevel.Debug                     |DEBUG         |
|             |           |      |      | FINE            |                                   |DEBUG2        |
|             |           |      |      | CONFIG          |                                   |DEBUG3        |
|Informational|Information|INFO  |Info  | INFO            |LogLevel.Information               |INFO          |
|Notice       |           |      |      |                 |                                   |INFO2         |
|Warning      |Warning    |WARN  |Warn  | WARNING         |LogLevel.Warning                   |WARN          |
|Error        |Error      |ERROR |Error | SEVERE          |LogLevel.Error                     |ERROR         |
|Critical     |Critical   |      |Dpanic|                 |                                   |ERROR2        |
|Alert        |           |      |Panic |                 |                                   |ERROR3        |
|Emergency    |           |FATAL |Fatal |                 |LogLevel.Critical                  |FATAL         |

## References

- [OTEP0097 Log Data Model, Appendix A. Example Mappings](../../oteps/logs/0097-log-data-model.md#appendix-a-example-mappings)
