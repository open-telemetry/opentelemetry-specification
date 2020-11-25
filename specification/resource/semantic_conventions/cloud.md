# Cloud

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

<!-- semconv cloud -->
| Attribute  | Type | Description  | Example  | Required |
|---|---|---|---|---|
| `cloud.provider` | string | Name of the cloud provider. | `gcp` | No |
| `cloud.account.id` | string | The cloud account ID used to identify different entities. | `opentelemetry` | No |
| `cloud.region` | string | A specific geographical location where different entities can run. | `us-central1` | No |
| `cloud.zone` | string | Zones are a sub set of the region connected through low-latency links. [1] | `us-central1-a` | No |
| `cloud.infrastructure_service` | string | The cloud infrastructure resource in use. | `AWS_EC2`<br>`Azure_VM`<br>`GCP_ComputeEngine` | No |

**[1]:** In AWS, this is called availability-zone.

`cloud.provider` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |

`cloud.infrastructure_service` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `AWS_EC2` | AWS Elastic Compute Cloud |
| `AWS_ECS` | AWS Elastic Container Service |
| `AWS_EKS` | AWS Elastic Kubernetes Service |
| `AWS_Lambda` | AWS Lambda |
| `AWS_ElasticBeanstalk` | AWS Elastic Beanstalk |
| `Azure_VM` | Azure Virtual Machines |
| `Azure_ContainerInstances` | Azure Container Instances |
| `Azure_AKS` | Azure Kubernetes Service |
| `Azure_Functions` | Azure Functions |
| `Azure_AppService` | Azure App Service |
| `GCP_ComputeEngine` | GCP Compute Engine |
| `GCP_CloudRun` | GCP Cloud Run |
| `GCP_GKE` | Google Kubernetes Engine |
| `GCP_CloudFunctions` | GCP Cloud Functions |
| `GCP_AppEngine` | GCP App Engine |
<!-- endsemconv -->
