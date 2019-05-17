
# Typed Spans

## Rationale

Spans represent different _canonical_ _types _of operations. Examples are

* Local operations like method invocations
* HTTP requests (inbound and outbound)
* Database requests
* eneric RPC requests like GRPC

A span consists of a number of mandatory and optional attributes that add information
about the represented operation to it.

Depending on the _canonical type_ of an operation some attributes might be needed
to represent and analyze a span correctly.

**Example:** A HTTP request needs a status code to distinguish successful or
unsuccessful operations.

Right now, spans can be created freely and it’s up to the implementor to set all
the attributes needed to represent the given type.

## Existing work

* There is already a _Type_ field that describes if a span is a parent or child span
* There is already a _SpanKind_ field that describes if a span is a server or
  client span - this distinguishes inbound and outbound requests.
* There should be already a TypedSpanBuilder for Java

## Proposal

* Implement a **TypedSpanBuilder** for all platforms that ensures that all
  needed attributes and the type is set.
* Add a field **CanonicalType** that contains the type of span.

### Proposed types

(derived from [this doc](https://docs.google.com/spreadsheets/d/1H0S0BROOgX7zndWF_WL8jb9IW1PN7j3IeryekhX5sKU/edit#gid=0) by @discostu)

The following canonical types should be implemented.
The attributes are taken from the OC spec first with a fallback to the OT spec if
there is no equivalent in OC. Additionally, some attributes that may enrich the
span further are proposed.

**Bold** = mandatory.

#### HttpClient

<table>
  <tr>
   <td><strong>CanonicalType = HTTP</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = CLIENT</strong>
   </td>
  </tr>
  <tr>
   <td><strong>http.method</strong>
   </td>
  </tr>
  <tr>
   <td><strong>http.host</strong>
   </td>
  </tr>
  <tr>
   <td><strong>http.path</strong>
   </td>
  </tr>
  <tr>
   <td>http.status_code
   </td>
  </tr>
  <tr>
   <td>http.route
   </td>
  </tr>
  <tr>
   <td>http.user_agent
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
parameters, requestHeaders, responseHeaders
   </td>
  </tr>
</table>

#### HttpServer

<table>
  <tr>
   <td><strong>CanonicalType = HTTP</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = SERVER</strong>
   </td>
  </tr>
  <tr>
   <td><strong>http.method</strong>
   </td>
  </tr>
  <tr>
   <td><strong>http.host</strong>
   </td>
  </tr>
  <tr>
   <td><strong>http.path</strong>
   </td>
  </tr>
  <tr>
   <td>http.status_code
   </td>
  </tr>
  <tr>
   <td>http.route
   </td>
  </tr>
  <tr>
   <td>http.user_agent
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
webServerName, remoteAddress, parameters, requestHeaders, responseHeaders
   </td>
  </tr>
</table>

#### DbClient

<table>
  <tr>
   <td><strong>CanonicalType = DB</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = CLIENT</strong>
   </td>
  </tr>
  <tr>
   <td><strong>db.instance</strong>
   </td>
  </tr>
  <tr>
   <td><strong>component</strong>
   </td>
  </tr>
  <tr>
   <td><strong>peer.*</strong>
   </td>
  </tr>
  <tr>
   <td><strong>db.statement</strong>
   </td>
  </tr>
  <tr>
   <td>db.type
   </td>
  </tr>
  <tr>
   <td>db.user
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
channelType, rowsReturned, roundTrips
   </td>
  </tr>
</table>

#### RemotingClient


<table>
  <tr>
   <td><strong>CanonicalType = RPC</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = CLIENT</strong>
   </td>
  </tr>
  <tr>
   <td><strong>peer.*</strong>
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
<strong>channelType, serviceMethod, serviceName, channelEndpoint</strong>
   </td>
  </tr>
</table>

#### RemotingServer


<table>
  <tr>
   <td><strong>CanonicalType = RPC</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = SERVER</strong>
   </td>
  </tr>
  <tr>
   <td><strong>peer.* (exists in OC)</strong>
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
<strong>serviceMethod, serviceName, channelEndpoint</strong>
   </td>
  </tr>
</table>

#### MessagingConsumer

<table>
  <tr>
   <td><strong>CanonicalType = MSG</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = CLIENT</strong>
   </td>
  </tr>
  <tr>
   <td><strong>message_bus.destination</strong>
   </td>
  </tr>
  <tr>
   <td><strong>peer.*</strong>
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
<strong>vendorName. channelType, operationType, messageDestination</strong>
   </td>
  </tr>
</table>

#### MessagingProducer

<table>
  <tr>
   <td><strong>CanonicalType = MSG</strong>
   </td>
  </tr>
  <tr>
   <td><strong>SpanKind = SERVER</strong>
   </td>
  </tr>
  <tr>
   <td><strong>message_bus.destination</strong>
   </td>
  </tr>
  <tr>
   <td><strong>peer.*</strong>
   </td>
  </tr>
  <tr>
   <td>Proposed additions:
<strong>vendorName. channelType</strong>
   </td>
  </tr>
</table>

## Challenges and Objections

* Some mandatory attributes for a given type may not be available at the time of creation

### POC
Here is [a POC for HTTP Client Spans for Node.js and OC](https://github.com/danielkhan/opencensus-node-typed-span-sample)