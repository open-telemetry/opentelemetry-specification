# General

The conventions described in this section aim both Functions running as a service (FaaS) and on-premise setups. When Functions are operated, metric events about those operations will be generated and reported to provide insight into the
operations. By adding Functions dedicated labels to metric events it allows for finely tuned filtering.

**Disclaimer:** These are initial Function metric instruments and labels but more may be added in the future. Not all instruments
apply to all environments.

## Metric Instruments

The following metric instruments MUST be used to describe Function operations. They MUST be of the specified
type and units.

### Function Invocations

Below is a table of Function invocation metric instruments.

| Name | Instrument | Units | Description |
|------|------------|-------|-------------|
| `func.invoke_duration` | ValueRecorder | milliseconds | Measures the duration of the invocation where real work is being done.  |
| `func.init_duration` | ValueRecorder | milliseconds | Measures the duration of the function's initialization, such as a cold start |
| `func.coldstarts` | Counter | number of cold starts | Number of invocation cold starts. |
| `func.errors` | Counter | number of errors | Number of invocation errors. |
| `func.executions` | Counter | number of invocations | number of successful invocations. |
| `func.timeouts` | Counter | number of timeouts | number of invocation timeouts. |

## Labels

Below is a table of the labels that SHOULD be included on Func metric events if applicable.

| Name | Recommended | Notes and examples |
|------|-------------|--------------------|
| `func.trigger` | Yes | Type of the trigger on which the function is invoked. SHOULD be one of: `datasource`, `http`, `pubsub`, `timer`, `other` |
| `func.invoked_name` | Yes | Name of the invoked function. Example: `my-function` |
| `func.invoked_provider` | Yes | Cloud provider of the invoked function. Corresponds to the resource `cloud.provider`. Example: `aws` |
| `func.invoked_region` | Yes | Cloud provider region of invoked function. Corresponds to resource `cloud.region`. Example: `us-east-1` |

## References

### Metric Reference

Below are links to documentation regarding metrics that are available with different
FaaS providers and other vendors. This list is not exhaustive.

* [AWS Lambda Metrics](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html)
* [Azure Functions Metrics](https://docs.microsoft.com/en-us/azure/azure-monitor/platform/metrics-supported)
* [Google CloudFunctions Metrics](https://cloud.google.com/monitoring/api/metrics_gcp#gcp-cloudfunctions)
* [OpenFaas Metrics](https://docs.openfaas.com/architecture/metrics/)
* [Openwhisk Metrics](https://github.com/apache/openwhisk/blob/master/docs/metrics.md)
