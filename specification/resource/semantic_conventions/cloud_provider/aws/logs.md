# AWS Logs

**Status**: [Experimental](../../../../document-status.md)

**Type:** `aws.log`

**Description:** Log attributes for Amazon Web Services.

<!-- semconv aws.log -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.log.group.names` | string[] | The name(s) of the AWS log group(s) an application is writing to. [1] | `[/aws/lambda/my-function, opentelemetry-service]` | No |
| `aws.log.group.arns` | string[] | The Amazon Resource Name(s) (ARN) of the AWS log group(s). [2] | `[arn:aws:logs:us-west-1:123456789012:log-group:/aws/my/group:*]` | No |
| `aws.log.stream.names` | string[] | The name(s) of the AWS log stream(s) an application is writing to. | `[logs/main/10838bed-421f-43ef-870a-f43feacbbb5b]` | No |
| `aws.log.stream.arns` | string[] | The ARN(s) of the AWS log stream(s). [3] | `[arn:aws:logs:us-west-1:123456789012:log-group:/aws/my/group:log-stream:logs/main/10838bed-421f-43ef-870a-f43feacbbb5b]` | No |

**[1]:** Multiple log groups must be supported for cases like multi-container applications, where a single application has sidecar containers, and each write to their own log group.

**[2]:** See the [log group ARN format documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-access-control-overview-cwl.html#CWL_ARN_Format).

**[3]:** See the [log stream ARN format documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-access-control-overview-cwl.html#CWL_ARN_Format). One log group can contain several log streams, so these ARNs necessarily identify both a log group and a log stream.
<!-- endsemconv -->
