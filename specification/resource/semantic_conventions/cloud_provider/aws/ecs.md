# AWS ECS

**Status**: [Experimental](../../../../document-status.md)

**type:** `aws.ecs`

**Description:** Resources used by AWS Elastic Container Service (ECS).

<!-- semconv aws.ecs -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.ecs.container.arn` | string | The Amazon Resource Name (ARN) of an [ECS container instance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_instances.html). | `arn:aws:ecs:us-west-1:123456789123:container/32624152-9086-4f0e-acae-1a75b14fe4d9` | No |
| `aws.ecs.cluster.arn` | string | The ARN of an [ECS cluster](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/clusters.html). | `arn:aws:ecs:us-west-2:123456789123:cluster/my-cluster` | No |
| `aws.ecs.launchtype` | string | The [launch type](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html) for an ECS task. | `ec2`; `fargate` | No |
| `aws.ecs.task.arn` | string | The ARN of an [ECS task definition](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html). | `arn:aws:ecs:us-west-1:123456789123:task/10838bed-421f-43ef-870a-f43feacbbb5b` | No |
| `aws.ecs.task.family` | string | The task definition family this task definition is a member of. | `opentelemetry-family` | No |

`aws.ecs.launchtype` MUST be one of the following:

| Value  | Description |
|---|---|
| `ec2` | ec2 |
| `fargate` | fargate |
<!-- endsemconv -->
