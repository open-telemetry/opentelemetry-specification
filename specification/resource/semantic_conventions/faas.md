# Function as a Service

**type:** `faas`

**Description:** A serverless instance.

| Label  | Description  | Example  | Required |
|---|---|---|--|
| faas.name | The name of the function being executed. | `my-function` | Yes |
| faas.id | The unique name of the function being executed. <br /> For example, in AWS Lambda this field corresponds to the [ARN] value, in GCP to the URI of the resource, and in Azure to the [FunctionDirectory] field. | `arn:aws:lambda:us-west-2:123456789012:function:my-function` | Yes |
| faas.version | The version string of the function being executed as defined in [Version Attributes](./README.md#version-attributes) | `semver:2.0.0` | No |
| faas.instance | The execution environment ID as a string. | `my-function:instance-0001` | No |

Note: The resource attribute `faas.instance` differs from the span attribute `faas.execution`. For more information see the [Semantic conventions for FaaS spans](../../trace/semantic_conventions/faas.md#difference-between-execution-and-instance).

[ARN]:https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
[FunctionDirectory]: https://github.com/Azure/azure-functions-host/wiki/Retrieving-information-about-the-currently-running-function
