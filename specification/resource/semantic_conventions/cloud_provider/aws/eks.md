# AWS EKS

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**Status**: [Experimental](../../../../document-status.md)

**type:** `aws.eks`

**Description:** Resources used by AWS Elastic Kubernetes Service (EKS).

<!-- semconv aws.eks -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.eks.cluster.arn` | string | The ARN of an EKS cluster. | `arn:aws:ecs:us-west-2:123456789123:cluster/my-cluster` | Recommended |
<!-- endsemconv -->
