# AWS Logs

**Type:** `aws.log`

**Description:** Log attributes for Amazon Web Services.

<!-- semconv aws.log -->
| Attribute  | Type | Description  | Example  | Required |
|---|---|---|---|---|
| `aws.log.group.name` | string | The name of the AWS log group an application is writing to. | `/aws/lambda/my-function`<br>`opentelemetry-service` | No |
| `aws.log.group.arn` | string | The Amazon Resource Name (ARN) of an AWS log group. [1] | `arn:aws:logs:us-west-1:123456789012:log-group:/aws/my/group:*` | No |
| `aws.log.stream.name` | string | The name of the AWS log stream an application is writing to. | `logs/main/10838bed-421f-43ef-870a-f43feacbbb5b` | No |
| `aws.log.stream.arn` | string | The ARN of the AWS log stream. [2] | `arn:aws:logs:us-west-1:123456789012:log-group:/aws/my/group:log-stream:logs/main/10838bed-421f-43ef-870a-f43feacbbb5b` | No |

**[1]:** See the [log group ARN format documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-access-control-overview-cwl.html#CWL_ARN_Format).

**[2]:** See the [log stream ARN format documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-access-control-overview-cwl.html#CWL_ARN_Format). One log group can contain several log streams, so this ARN necessarily identifies both a log group and a log stream.
<!-- endsemconv -->
