# OpenCensus Library Encoding Package
This documentation serves to document the on-the-wire encoding format supported in
OpenCensus. It describes the key types and the overall behavior.

## Formats
* [Binary Encoding](BinaryEncoding.md)
  * [TraceContext Binary Encoding](BinaryEncoding.md#trace-context)
  * [TagContext Binary Encoding](BinaryEncoding.md#tag-context)
  * [Census Server Stats Encoding](CensusServerStatsEncoding.md)

* HTTP Encoding
  * [W3C TraceContext](https://github.com/TraceContext/tracecontext-spec)
  * [W3C Correlation Context](https://github.com/w3c/correlation-context)
  * [Stackdriver TraceContext Header](https://cloud.google.com/trace/docs/support)
  * [B3 TraceContext Header](https://github.com/openzipkin/b3-propagation)
