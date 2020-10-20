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
| `cloud.infrastructure.service` | string | The cloud infrastructure resource in use. | `EC2`<br>`VM`<br>`ComputeEngine` | No |

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
| `EC2` | AWS Elastic Compute Cloud |
| `ECS` | AWS Elastic Container Service |
| `EKS` | AWS Elastic Kubernetes Service |
| `Lambda` | AWS Lambda |
| `ElasticBeanstalk` | AWS Elastic Beanstalk |
| `VM` | Azure Virtual Machines |
| `ContainerInstances` | Azure Container Instances |
| `AKS` | Azure Kubernetes Service |
| `Functions` | Azure Functions |
| `AppService` | Azure App Service |
| `ComputeEngine` | GCP Compute Engine |
| `CloudRun` | GCP Cloud Run |
| `GKE` | Google Kubernetes Engine |
| `CloudFunctions` | GCP Cloud Functions |
| `AppEngine` | GCP App Engine |
<!-- endsemconv -->
