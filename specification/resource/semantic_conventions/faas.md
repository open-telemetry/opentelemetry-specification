# Function as a Service

**Status**: [Experimental](../../document-status.md)

**type:** `faas`

**Description:** A "function as a service" aka "serverless function" instance.

See also:

- The [Trace semantic conventions for FaaS](../../trace/semantic_conventions/faas.md)
- The [Cloud resource conventions](cloud.md)

<!-- semconv faas_resource -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `faas.name` | string | The name of the single function that this runtime instance executes. | `my-function` | Yes |
| `faas.id` | string | The unique ID of the single function that this runtime instance executes. [1] | `arn:aws:lambda:us-west-2:123456789012:function:my-function` | No |
| `faas.version` | string | The immutable version of the function being executed. [2] | `26`; `pinkfroid-00002` | No |
| `faas.instance` | string | The execution environment ID as a string, that will be potentially reused for other invocations to the same function/function version. [3] | `2021/06/28/[$LATEST]2f399eb14537447da05ab2a2e39309de` | No |
| `faas.max_memory` | int | The amount of memory available to the serverless function in MiB. [4] | `128` | No |

**[1]:** Depending on the cloud provider, use:

* **AWS Lambda:** The function [ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html).
Take care not to use the "invoked ARN" directly but replace any
[alias suffix](https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html) with the resolved function version, as the same runtime instance may be invokable with multiple
different aliases.
* **GCP:** The [URI of the resource](https://cloud.google.com/iam/docs/full-resource-names)
* ***Azure:** The [Fully Qualified Resource ID](https://docs.microsoft.com/en-us/rest/api/resources/resources/get-by-id).

On some providers, it may not be possible to determine the full ID at startup,
which is why this field cannot be made required. For example, on AWS the account ID
part of the ARN is not available without calling another AWS API
which may be deemed too slow for a short-running lambda function.
As an alternative, consider setting `faas.id` as a span attribute instead.

**[2]:** Depending on the cloud provider and platform, use:

* **AWS Lambda:** The [function version](https://docs.aws.amazon.com/lambda/latest/dg/configuration-versions.html)
  (an integer represented as a decimal string).
* **Google Cloud Run:** The [revision](https://cloud.google.com/run/docs/managing/revisions)
  (i.e., the function name plus the revision suffix).
* **Google Cloud Functions:** The value of the
  [`K_REVISION` environment variable](https://cloud.google.com/functions/docs/env-var#runtime_environment_variables_set_automatically).
* **Azure Functions:** Not applicable. Do not set this attribute.

**[3]:** * **AWS Lambda:** Use the (full) log stream name.

**[4]:** It's recommended to set this attribute since e.g. too little memory can easily stop a Java AWS Lambda function from working correctly. On AWS Lambda, the environment variable `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` provides this information.
<!-- endsemconv -->

Note: The resource attribute `faas.instance` differs from the span attribute `faas.execution`. For more information see the [Semantic conventions for FaaS spans](../../trace/semantic_conventions/faas.md#difference-between-execution-and-instance).
