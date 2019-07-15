# Exporter Interface

Exporter defines the interface that protocol-specific exporters must implement so that they can be plugged into OpenTelemetry SDK and support sending of telemetry data.

The goals of the interface are:

- Minimize burden of implementation for protocol-dependant telemetry exporters. The protocol exporter is expected to be primarily a simple telemetry data encoder and transmitter.

- Allow implementing helpers as composable components that use the same chainable Exporter interface. SDK authors are encouraged to implement common functionality such as queuing, batching, tagging, etc. as helpers. This functionality will be applicable regardless of what protocol exporter is used.

## Interface Definition

The exporter must support two functions: **Export** and **Shutdown**. In strongly typed languages typically there will be 2 separate Exporter interfaces, one that accepts spans (SpanExporter) and one that accepts metrics (MetricsExporter).

### Export(batch)

Exports a batch of telemetry data. Protocol exporters that will implement this function are typically expected to serialize and transmit the data to the destination.

Export() will never be called concurrently for the same exporter instance. Export() can be called again only after the current call returns.

Export() must not block indefinitely, there must be a reasonable upper limit after which the call must time out with an error result(typically CannotExport).

**Parameters:**

batch - a batch of telemetry data. The exact data type of the batch is language specific, typically it is a list of telemetry items, e.g. for spans in Java it will be typically `Collection<ExportableSpan>` 

Note that the data type for a span for illustration purposes here is written as an imaginary type ExportableSpan (similarly for metrics it would be e.g. ExportableMetrics). The actual data type must be specified by language library authors, it should be able to represent the span data that can be read by the exporter.

**Returns:** ExportResult:

ExportResult is one of:

- Success - batch is successfully exported. For protocol exporters this typically means that the data is sent over the wire and delivered to the destination server.

- BadData - batch contains bad data and cannot be sent. The caller must not retry exporting the same batch. The batch must be dropped.

- CannotExport - cannot export to the destination. The destination is unavailable, network error or endpoint does not exist. The caller should record the error and may retry exporting the same batch after some time.

### Shutdown()

Shutdowns the exporter. Called when the SDK is shutdown. This is an opportunity for exporter to do any cleanup required.

## Further Language Specialization

Based on the generic interface definition layed out above library authors must define the exact interface for the particular language. 

Authors are encouraged to use efficient data structures on the interface boundary that are well suited for fast serialization to wire formats by protocol exporters and minimize the pressure on memory managers. The latter typically requires understanding of how to optimize the rapidly-generated, short-lived telemetry data structures to make life easier for the memory manager of the specific language. General recommendation is to minimize the number of allocations and use allocation arenas where possible, thus avoiding explosion of allocation/deallocation/collection operations in the presence of high rate of telemetry data generation.

### Examples

These are examples on what the Exporter interface can look like in specific languages. Examples are for illustration purposes only. Language library authors are free to deviate from these provided that their design remain true to the spirit of Exporter concept.

#### Go SpanExporter Interface

```go
type SpanExporter interface {
    Export(batch []ExportableSpan) ExportResult
    Shutdown()
}

type ExportResult struct {
    Code         ExportResultCode
    WrappedError error
}

type ExportResultCode int

const (
    Success ExportResultCode = iota
    BadData
    CannotExport
)
```

#### Java SpanExporter Interface

```java
public interface SpanExporter {
 public enum ResultCode {
   Success, BadData, CannotExport
 }

 ResultCode export(Collection<ExportableSpan> batch);
 void shutdown();
}
```
