# Cloud

**Status**: [Experimental](../../document-status.md)

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

<!-- semconv cloud -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `cloud.provider` | string | Name of the cloud provider. | `gcp` | No |
| `cloud.account.id` | string | The cloud account ID the resource is assigned to. | `111111111111`; `opentelemetry` | No |
| `cloud.region` | string | The geographical region the resource is running. Refer to your provider's docs to see the available regions, for example [AWS regions](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/), [Azure regions](https://azure.microsoft.com/en-us/global-infrastructure/geographies/), or [Google Cloud regions](https://cloud.google.com/about/locations). | `us-central1`; `us-east-1` | No |
| `cloud.availability_zone` | string | Cloud regions often have multiple, isolated locations known as zones to increase availability. Availability zone represents the zone where the resource is running. [1] | `us-east-1c` | No |
| `cloud.platform` | string | The cloud platform in use. [2] | `aws_ec2`; `azure_vm`; `gcp_compute_engine` | No |

**[1]:** Availability zones are called "zones" on Google Cloud.

**[2]:** The prefix of the service SHOULD match the one specified in `cloud.provider`.

`cloud.provider` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |

`cloud.platform` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `aws_ec2` | AWS Elastic Compute Cloud |
| `aws_ecs` | AWS Elastic Container Service |
| `aws_eks` | AWS Elastic Kubernetes Service |
| `aws_lambda` | AWS Lambda |
| `aws_elastic_beanstalk` | AWS Elastic Beanstalk |
| `azure_vm` | Azure Virtual Machines |
| `azure_container_instances` | Azure Container Instances |
| `azure_aks` | Azure Kubernetes Service |
| `azure_functions` | Azure Functions |
| `azure_app_service` | Azure App Service |
| `gcp_compute_engine` | Google Cloud Compute Engine (GCE) |
| `gcp_cloud_run` | Google Cloud Run |
| `gcp_kubernetes_engine` | Google Cloud Kubernetes Engine (GKE) |
| `gcp_cloud_functions` | Google Cloud Functions (GCF) |
| `gcp_app_engine` | Google Cloud App Engine (GAE) |
<!-- endsemconv -->
