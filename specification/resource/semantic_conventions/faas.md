# Function as a Service

**Status**: [Experimental](../../document-status.md)

**type:** `faas`

**Description:** A serverless instance.

<!-- semconv faas_resource -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `faas.name` | string | The name of the function being executed. | `my-function` | Yes |
| `faas.id` | string | The unique ID of the function being executed. [1] | `arn:aws:lambda:us-west-2:123456789012:function:my-function` | Yes |
| `faas.version` | string | The version string of the function being executed as defined in [Version Attributes](../../resource/semantic_conventions/README.md#version-attributes). | `2.0.0` | No |
| `faas.instance` | string | The execution environment ID as a string. | `my-function:instance-0001` | No |
| `faas.max_memory` | int | The amount of memory available to the serverless function in MiB. [2] | `128` | No |

**[1]:** For example, in AWS Lambda this field corresponds to the [ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) value, in GCP to the URI of the resource, and in Azure to the [FunctionDirectory](https://github.com/Azure/azure-functions-host/wiki/Retrieving-information-about-the-currently-running-function) field.

**[2]:** It's recommended to set this attribute since e.g. too little memory can easily stop a Java AWS Lambda function from working correctly. On AWS Lambda, the environment variable `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` provides this information.
<!-- endsemconv -->

Note: The resource attribute `faas.instance` differs from the span attribute `faas.execution`. For more information see the [Semantic conventions for FaaS spans](../../trace/semantic_conventions/faas.md#difference-between-execution-and-instance).
