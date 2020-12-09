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
| `cloud.infrastructure_service` | string | The cloud infrastructure resource in use. [2] | `aws_ec2`<br>`azure_vm`<br>`gcp_compute_engine` | No |

**[1]:** In AWS, this is called availability-zone.

**[2]:** The prefix of the service SHOULD match the one specified in `cloud.provider`.

`cloud.provider` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |

`cloud.infrastructure_service` MUST be one of the following or, if none of the listed values apply, a custom value:

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
| `gcp_compute_engine` | GCP Compute Engine |
| `gcp_cloud_run` | GCP Cloud Run |
| `gcp_gke` | Google Kubernetes Engine |
| `gcp_cloud_functions` | GCP Cloud Functions |
| `gcp_app_engine` | GCP App Engine |
<!-- endsemconv -->
