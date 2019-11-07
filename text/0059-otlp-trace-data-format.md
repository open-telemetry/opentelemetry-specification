# OTLP Trace Data Format

_Author: Tigran Najaryan, Splunk_

**Status:** `approved`

OTLP Trace Data Format specification describes the structure of the trace data that is transported by OpenTelemetry Protocol (RFC0035).

## Motivation

This document is a continuation of OpenTelemetry Protocol RFC0035 and is necessary part of OTLP specification.

## Explanation

OTLP Trace Data Format is primarily inherited from OpenCensus protocol. Several changes are introduced with the goal of more efficient serialization. Notable differences from OpenCensus protocol are:

1. Removed `Node` as a concept.
2. Extended `Resource` to better describe the source of the telemetry data.
3. Replaced attribute maps by lists of key/value pairs.
4. Eliminated unnecessary additional nesting in various values.

Changes 1-2 are conceptual, changes 3-4 improve performance.

## Internal details

This section specifies data format in Protocol Buffers.

### Resource

```protobuf
// Resource information. This describes the source of telemetry data.
message Resource {
  // labels is a collection of attributes that describe the resource. See OpenTelemetry
  // specification semantic conventions for standardized label names:
  // https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/data-resource-semantic-conventions.md
  repeated AttributeKeyValue labels = 1;

  // dropped_labels_count is the number of dropped labels. If the value is 0, then
  // no labels were dropped.
  int32 dropped_labels_count = 2;
}
```

### Span

```protobuf
// Span represents a single operation within a trace. Spans can be
// nested to form a trace tree. Spans may also be linked to other spans
// from the same or different trace and form graphs. Often, a trace
// contains a root span that describes the end-to-end latency, and one
// or more subspans for its sub-operations. A trace can also contain
// multiple root spans, or none at all. Spans do not need to be
// contiguous - there may be gaps or overlaps between spans in a trace.
//
// The next field id is 18.
message Span {
  // trace_id is the unique identifier of a trace. All spans from the same trace share
  // the same `trace_id`. The ID is a 16-byte array. An ID with all zeroes
  // is considered invalid.
  //
  // This field is semantically required. If empty or invalid trace_id is received:
  // - The receiver MAY reject the invalid data and respond with the appropriate error
  //   code to the sender.
  // - The receiver MAY accept the invalid data and attempt to correct it.
  bytes trace_id = 1;

  // span_id is a unique identifier for a span within a trace, assigned when the span
  // is created. The ID is an 8-byte array. An ID with all zeroes is considered
  // invalid.
  //
  // This field is semantically required. If empty or invalid span_id is received:
  // - The receiver MAY reject the invalid data and respond with the appropriate error
  //   code to the sender.
  // - The receiver MAY accept the invalid data and attempt to correct it.
  bytes span_id = 2;

  // TraceStateEntry is the entry that is repeated in tracestate field (see below).
  message TraceStateEntry {
    // key must begin with a lowercase letter, and can only contain
    // lowercase letters 'a'-'z', digits '0'-'9', underscores '_', dashes
    // '-', asterisks '*', and forward slashes '/'.
    string key = 1;

    // value is opaque string up to 256 characters printable ASCII
    // RFC0020 characters (i.e., the range 0x20 to 0x7E) except ',' and '='.
    // Note that this also excludes tabs, newlines, carriage returns, etc.
    string value = 2;
  }

  // tracestate conveys information about request position in multiple distributed tracing graphs.
  // It is a collection of TracestateEntry with a maximum of 32 members in the collection.
  //
  // See the https://github.com/w3c/distributed-tracing for more details about this field.
  repeated TraceStateEntry tracestate = 3;

  // parent_span_id is the `span_id` of this span's parent span. If this is a root span, then this
  // field must be omitted. The ID is an 8-byte array.
  bytes parent_span_id = 4;

  // resource that is associated with this span. Optional. If not set, this span
  // should be part of a ResourceSpans message that does include the resource information,
  // unless resource information is unknown.
  Resource resource = 5;

  // name describes the span's operation.
  //
  // For example, the name can be a qualified method name or a file name
  // and a line number where the operation is called. A best practice is to use
  // the same display name at the same call point in an application.
  // This makes it easier to correlate spans in different traces.
  //
  // This field is semantically required to be set to non-empty string.
  //
  // This field is required.
  string name = 6;

  // SpanKind is the type of span. Can be used to specify additional relationships between spans
  // in addition to a parent/child relationship.
  enum SpanKind {
    // Unspecified. Do NOT use as default.
    // Implementations MAY assume SpanKind to be INTERNAL when receiving UNSPECIFIED.
    SPAN_KIND_UNSPECIFIED = 0;

    // Indicates that the span represents an internal operation within an application,
    // as opposed to an operations happening at the boundaries. Default value.
    INTERNAL = 1;

    // Indicates that the span covers server-side handling of an RPC or other
    // remote network request.
    SERVER = 2;

    // Indicates that the span describes a request to some remote service.
    CLIENT = 3;

    // Indicates that the span describes a producer sending a message to a broker.
    // Unlike CLIENT and SERVER, there is often no direct critical path latency relationship
    // between producer and consumer spans. A PRODUCER span ends when the message was accepted
    // by the broker while the logical processing of the message might span a much longer time.
    PRODUCER = 4;

    // Indicates that the span describes consumer receiving a message from a broker.
    // Like the PRODUCER kind, there is often no direct critical path latency relationship
    // between producer and consumer spans.
    CONSUMER = 5;
  }

  // kind field distinguishes between spans generated in a particular context. For example,
  // two spans with the same name may be distinguished using `CLIENT` (caller)
  // and `SERVER` (callee) to identify network latency associated with the span.
  SpanKind kind = 7;

  // start_time_unixnano is the start time of the span. On the client side, this is the time
  // kept by the local machine where the span execution starts. On the server side, this
  // is the time when the server's application handler starts running.
  //
  // This field is semantically required and it is expected that end_time >= start_time.
  //
  // This field is required.
  int64 start_time_unixnano = 8;

  // end_time_unixnano is the end time of the span. On the client side, this is the time
  // kept by the local machine where the span execution ends. On the server side, this
  // is the time when the server application handler stops running.
  //
  // This field is semantically required and it is expected that end_time >= start_time.
  //
  // This field is required.
  int64 end_time_unixnano = 9;

  // attributes is a collection of key/value pairs. The value can be a string,
  // an integer, a double or the Boolean values `true` or `false`. Note, global attributes
  // like server name can be set using the resource API. Examples of attributes:
  //
  //     "/http/user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
  //     "/http/server_latency": 300
  //     "abc.com/myattribute": true
  //     "abc.com/score": 10.239
  repeated AttributeKeyValue attributes = 10;

  // dropped_attributes_count is the number of attributes that were discarded. Attributes
  // can be discarded because their keys are too long or because there are too many
  // attributes. If this value is 0, then no attributes were dropped.
  int32 dropped_attributes_count = 11;

  // TimedEvent is a time-stamped annotation of the span, consisting of either
  // user-supplied key-value pairs, or details of a message sent/received between Spans.
  message TimedEvent {
    // time_unixnano is the time the event occurred.
    int64 time_unixnano = 1;

    // name is a user-supplied description of the event.
    string name = 2;

    // attributes is a collection of attribute key/value pairs on the event.
    repeated AttributeKeyValue attributes = 3;

    // dropped_attributes_count is the number of dropped attributes. If the value is 0,
    // then no attributes were dropped.
    int32 dropped_attributes_count = 4;
  }

  // timed_events is a collection of TimedEvent items.
  repeated TimedEvent timed_events = 12;

  // dropped_timed_events_count is the number of dropped timed events. If the value is 0,
  // then no events were dropped.
  int32 dropped_timed_events_count = 13;

  // Link is a pointer from the current span to another span in the same trace or in a
  // different trace. For example, this can be used in batching operations,
  // where a single batch handler processes multiple requests from different
  // traces or when the handler receives a request from a different project.
  // See also Links specification:
  // https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md#links-between-spans
  message Link {
    // trace_id is a unique identifier of a trace that this linked span is part of.
    // The ID is a 16-byte array.
    bytes trace_id = 1;

    // span_id is a unique identifier for the linked span. The ID is an 8-byte array.
    bytes span_id = 2;

    // tracestate is the trace state associated with the link.
    repeated TraceStateEntry tracestate = 3;

    // attributes is a collection of attribute key/value pairs on the link.
    repeated AttributeKeyValue attributes = 4;

    // dropped_attributes_count is the number of dropped attributes. If the value is 0,
    // then no attributes were dropped.
    int32 dropped_attributes_count = 5;
  }

  // links is a collection of Links, which are references from this span to a span
  // in the same or different trace.
  repeated Link links = 14;

  // dropped_links_count is the number of dropped links after the maximum size was
  // enforced. If this value is 0, then no links were dropped.
  int32 dropped_links_count = 15;

  // status is an optional final status for this span. Semantically when status
  // wasn't set it is means span ended without errors and assume Status.Ok (code = 0).
  Status status = 16;

  // child_span_count is an optional number of local child spans that were generated while this
  // span was active. If set, allows an implementation to detect missing child spans.
  int32 child_span_count = 17;
}

// The Status type defines a logical error model that is suitable for different
// programming environments, including REST APIs and RPC APIs.
message Status {

  // StatusCode mirrors the codes defined at
  // https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-tracing.md#statuscanonicalcode
  enum StatusCode {
    Ok                 = 0;
    Cancelled          = 1;
    UnknownError       = 2;
    InvalidArgument    = 3;
    DeadlineExceeded   = 4;
    NotFound           = 5;
    AlreadyExists      = 6;
    PermissionDenied   = 7;
    ResourceExhausted  = 8;
    FailedPrecondition = 9;
    Aborted            = 10;
    OutOfRange         = 11;
    Unimplemented      = 12;
    InternalError      = 13;
    Unavailable        = 14;
    DataLoss           = 15;
    Unauthenticated    = 16;
  };

  // The status code. This is optional field. It is safe to assume 0 (OK)
  // when not set.
  StatusCode code = 1;

  // A developer-facing human readable error message.
  string message = 2;
}
```

### AttributeKeyValue

```protobuf
// AttributeKeyValue is a key-value pair that is used to store Span attributes, Resource
// labels, etc.
message AttributeKeyValue {
  // ValueType is the enumeration of possible types that value can have.
  enum ValueType {
    STRING  = 0;
    BOOL    = 1;
    INT64   = 2;
    DOUBLE  = 3;
  };

  // key part of the key-value pair.
  string key = 1;

  // The type of the value.
  ValueType type = 2;

  // Only one of the following fields is supposed to contain data (determined by `type` field value).
  // This is deliberately not using Protobuf `oneof` for performance reasons (verified by benchmarks).

  // A string value.
  string string_value = 3;
  // A 64-bit signed integer.
  int64 int64_value = 4;
  // A Boolean value represented by `true` or `false`.
  bool bool_value = 5;
  // A double value.
  double double_value = 6;
}
```

## Trade-offs and mitigations

Timestamps were changed from google.protobuf.Timestamp to a int64 representation in Unix epoch nanoseconds. This change reduces the type-safety but benchmarks show that for small spans there is 15-20% encoding/decoding CPU speed gain. This is the right trade-off to make because encoding/decoding CPU consumption tends to dominate many workloads (particularly in OpenTelemetry Service).

## Prior art and alternatives

OpenCensus and Jaeger protocol buffer data schemas were used as the inspiration for this specification. OpenCensus was the starting point, Jaeger provided performance improvement ideas.

## Open questions

A follow up RFC is required to define the data format for metrics.

One of the original aspiring goals for OTLP was to _"support very fast pass-through mode (when no modifications to the data are needed), fast augmenting or tagging of data and partial inspection of data"_. This particular goal was not met directly (although performance improvements over OpenCensus encoding make OTLP more suitable for these tasks). This goal remains a good direction of future research and improvement.

## Appendix A - Benchmarking

The following shows [benchmarking of encoding/decoding in Go](https://github.com/tigrannajaryan/exp-otelproto/) using various schemas.

Legend:
- OpenCensus    - OpenCensus protocol schema.
- OTLP/AttrMap  - OTLP schema using map for attributes.
- OTLP/AttrList - OTLP schema using list of key/values for attributes and with reduced nesting for values.
- OTLP/AttrList/TimeWrapped - Same as OTLP/AttrList, except using google.protobuf.Timestamp instead of int64 for timestamps.

Suffixes:
- Attributes - a span with 3 attributes.
- TimedEvent - a span with 3 timed events.

```
BenchmarkEncode/OpenCensus/Attributes-8         	      10	 605614915 ns/op
BenchmarkEncode/OpenCensus/TimedEvent-8         	      10	1025026687 ns/op
BenchmarkEncode/OTLP/AttrAsMap/Attributes-8     	      10	 519539723 ns/op
BenchmarkEncode/OTLP/AttrAsMap/TimedEvent-8     	      10	 841371163 ns/op
BenchmarkEncode/OTLP/AttrAsList/Attributes-8    	      50	 128790429 ns/op
BenchmarkEncode/OTLP/AttrAsList/TimedEvent-8    	      50	 175874878 ns/op
BenchmarkEncode/OTLP/AttrAsList/TimeWrapped/Attributes-8         	      50	 153184772 ns/op
BenchmarkEncode/OTLP/AttrAsList/TimeWrapped/TimedEvent-8         	      30	 232705272 ns/op
BenchmarkDecode/OpenCensus/Attributes-8                          	      10	 644103382 ns/op
BenchmarkDecode/OpenCensus/TimedEvent-8                          	       5	1132059855 ns/op
BenchmarkDecode/OTLP/AttrAsMap/Attributes-8                      	      10	 529679038 ns/op
BenchmarkDecode/OTLP/AttrAsMap/TimedEvent-8                      	      10	 867364162 ns/op
BenchmarkDecode/OTLP/AttrAsList/Attributes-8                     	      50	 228834160 ns/op
BenchmarkDecode/OTLP/AttrAsList/TimedEvent-8                     	      20	 321160309 ns/op
BenchmarkDecode/OTLP/AttrAsList/TimeWrapped/Attributes-8         	      30	 277597851 ns/op
BenchmarkDecode/OTLP/AttrAsList/TimeWrapped/TimedEvent-8         	      20	 443386880 ns/op
```

The benchmark encodes/decodes 1000 batches of 100 spans, each span containing 3 attributes or 3 timed events. The total uncompressed, encoded size of each batch is around 20KBytes.

The results show OTLP/AttrList is 5-6 times faster than OpenCensus in encoding and about 3 times faster in decoding.

Using google.protobuf.Timestamp instead of int64-encoded unix timestamp results in 1.18-1.32 times slower encoding and 1.21-1.38 times slower decoding (depending on what the span contains).
