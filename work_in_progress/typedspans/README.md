
# Typed Spans (Draft Proposal)

In OpenCensus and OpenTracing spans can be created freely and it’s up to the
implementor to annotate them with attributes specific to the represented operation.
This document proposes to add type information to spans and to define and reserve
mandatory and optional attributes depending on the span type.

## Motivation

Spans represent specific operations in and between systems.

Examples for such operations are

- Local operations like method invocations
- HTTP requests (inbound and outbound)
- Database operations
- Queue/Message publish and consume
- gRPC calls
- Generic RPC operations

Depending on the type of an operation, additional information is needed to
represent and analyze a span correctly in monitoring systems.

While both OpenCensus and OpenTracing define conventions that define some reserved
attributes that can be used to add operation-specific information, there is no
mechanism to specify the type of an operation and to ensure that all needed
attributes are set.

### Proposed types

Below is a list of types and attributes per type.
This document does not include the final naming of attributes and types.
It is assumed that there will be naming conventions that will be applied eventually.

There is also no distinction between mandatory and optional attributes as it is assumed
that there will be a dedicated discussion and document for each type linked in this document.

See [this document by @discostu105](https://docs.google.com/spreadsheets/d/1H0S0BROOgX7zndWF_WL8jb9IW1PN7j3IeryekhX5sKU/edit#gid=0) for type and attribute mappings that exist in OpenCensus and OpenTracing today.

#### HTTP Client
Represents an outbound HTTP request.

##### Attributes
These attributes are not covered in the [main spec](../../semantic-conventions.md):

- Route
- User Agent
- Parameters
- Request Headers
- Response Headers

#### HTTP Server
Represents an inbound HTTP request.

##### Attributes

These attributes are not covered in the [main spec](../../semantic-conventions.md):

- User Agent
- Webserver Name
- Remote Address
- Parameters
- Request Headers
- Response Headers

#### Database Client
Represents a database call.

##### Attributes

These attributes are not covered in the [main spec](../../semantic-conventions.md):

- Channel Type (e.g. TCP)

#### gRPC Client
Represents an outbound gRPC request.

##### Attributes

These attributes are not covered in the [main spec](../../semantic-conventions.md):

- Channel Type (e.g. TCP)

#### gRPC Server
Represents an inbound gRPC request.

##### Attributes

These attributes are not covered in the [main spec](../../semantic-conventions.md):

- Channel Type (e.g. TCP)

#### Remoting Client
Represents an outbound RPC request.

##### Attributes
- Service Endpoint
- Channel Type (e.g. TCP)
- Channel Endpoint
- Service Name
- Service Method


#### Remoting Server
Represents an inbound RPC request.

##### Attributes
- Service Method
- Service Name
- Service Endpoint
- Protocol Name


#### Messaging Consumer
Represents an inbound message.

##### Attributes
- Vendor Name
- Destination Name
- Destination Type
- Channel Type
- Channel Endpoint
- Operation Type
- Message Id
- Correlation Id

#### Messaging Producer
Represents an outbound message.

##### Attributes
- Vendor Name
- Destination Name
- Channel Type
- Channel Endpoint
- Message Id
- Correlation Id

## Proposal
* Add a field `CanonicalType` that contains the type of span
* Define mandatory and optional attributes per span type
* Provide an API that supports creating typed spans and ensures that at least all
  mandatory attributes for this `CanonicalType` are present

## Challenges and Objections
- Some mandatory attributes for a given type may not be available at the time of creation

### POC
Here is [a POC for HTTP Client Spans for Node.js and OpenCensus](https://github.com/danielkhan/opencensus-node-typed-span-sample)

## Action Items
- Define all types
- Agree on type and attribute naming conventions
- Specify each type and agree on mandatory and optional attributes per type
