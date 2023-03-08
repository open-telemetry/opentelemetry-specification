# Function as a Service

**Status**: [Experimental](../../document-status.md)

**type:** `faas`

**Description:** A "function as a service" aka "serverless function" instance.

See also:

- The [Trace semantic conventions for FaaS](../../trace/semantic_conventions/faas.md)
- The [Cloud resource conventions](cloud.md)

## FaaS resource attributes

<!-- semconv faas_resource -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `faas.name` | string | The name of the single function that this runtime instance executes. [1] | `my-function`; `myazurefunctionapp/some-function-name` | Required |
| `faas.version` | string | The immutable version of the function being executed. [2] | `26`; `pinkfroid-00002` | Recommended |
| `faas.instance` | string | The execution environment ID as a string, that will be potentially reused for other invocations to the same function/function version. [3] | `2021/06/28/[$LATEST]2f399eb14537447da05ab2a2e39309de` | Recommended |
| `faas.max_memory` | int | The amount of memory available to the serverless function converted to Bytes. [4] | `134217728` | Recommended |

**[1]:** This is the name of the function as configured/deployed on the FaaS
platform and is usually different from the name of the callback
function (which may be stored in the
[`code.namespace`/`code.function`](../../trace/semantic_conventions/span-general.md#source-code-attributes)
span attributes).

For some cloud providers, the above definition is ambiguous. The following
definition of function name MUST be used for this attribute
(and consequently the span name) for the listed cloud providers/products:

* **Azure:**  The full name `<FUNCAPP>/<FUNC>`, i.e., function app name
  followed by a forward slash followed by the function name (this form
  can also be seen in the resource JSON for the function).
  This means that a span attribute MUST be used, as an Azure function
  app can host multiple functions that would usually share
  a TracerProvider (see also the `cloud.resource_id` attribute).

**[2]:** Depending on the cloud provider and platform, use:

* **AWS Lambda:** The [function version](https://docs.aws.amazon.com/lambda/latest/dg/configuration-versions.html)
  (an integer represented as a decimal string).
* **Google Cloud Run:** The [revision](https://cloud.google.com/run/docs/managing/revisions)
  (i.e., the function name plus the revision suffix).
* **Google Cloud Functions:** The value of the
  [`K_REVISION` environment variable](https://cloud.google.com/functions/docs/env-var#runtime_environment_variables_set_automatically).
* **Azure Functions:** Not applicable. Do not set this attribute.

**[3]:** * **AWS Lambda:** Use the (full) log stream name.

**[4]:** It's recommended to set this attribute since e.g. too little memory can easily stop a Java AWS Lambda function from working correctly. On AWS Lambda, the environment variable `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` provides this information (which must be multiplied by 1,048,576).
<!-- endsemconv -->

Note: The resource attribute `faas.instance` differs from the span attribute `faas.invocation_id`. For more information see the [Semantic conventions for FaaS spans](../../trace/semantic_conventions/faas.md#difference-between-invocation-and-instance).

## Using span attributes instead of resource attributes

There are cases where a FaaS resource attribute is better applied as a span
attribute instead.
See the [FaaS trace conventions](../../trace/semantic_conventions/faas.md) for more.
