# Cloud

**Status**: [Experimental](../../document-status.md)

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

<!-- semconv cloud -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `cloud.provider` | string | Name of the cloud provider. | `alibaba_cloud` | Recommended |
| `cloud.account.id` | string | The cloud account ID the resource is assigned to. | `111111111111`; `opentelemetry` | Recommended |
| `cloud.region` | string | The geographical region the resource is running. [1] | `us-central1`; `us-east-1` | Recommended |
| `cloud.availability_zone` | string | Cloud regions often have multiple, isolated locations known as zones to increase availability. Availability zone represents the zone where the resource is running. [2] | `us-east-1c` | Recommended |
| `cloud.platform` | string | The cloud platform in use. [3] | `alibaba_cloud_ecs` | Recommended |

**[1]:** Refer to your provider's docs to see the available regions, for example [Alibaba Cloud regions](https://www.alibabacloud.com/help/doc-detail/40654.htm), [AWS regions](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/), [Azure regions](https://azure.microsoft.com/en-us/global-infrastructure/geographies/), [Google Cloud regions](https://cloud.google.com/about/locations), or [Tencent Cloud regions](https://intl.cloud.tencent.com/document/product/213/6091).

**[2]:** Availability zones are called "zones" on Alibaba Cloud and Google Cloud.

**[3]:** The prefix of the service SHOULD match the one specified in `cloud.provider`.

`cloud.provider` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `alibaba_cloud` | Alibaba Cloud |
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |
| `ibm_cloud` | IBM Cloud |
| `tencent_cloud` | Tencent Cloud |

`cloud.platform` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `alibaba_cloud_ecs` | Alibaba Cloud Elastic Compute Service |
| `alibaba_cloud_fc` | Alibaba Cloud Function Compute |
| `alibaba_cloud_openshift` | Red Hat OpenShift on Alibaba Cloud |
| `aws_ec2` | AWS Elastic Compute Cloud |
| `aws_ecs` | AWS Elastic Container Service |
| `aws_eks` | AWS Elastic Kubernetes Service |
| `aws_lambda` | AWS Lambda |
| `aws_elastic_beanstalk` | AWS Elastic Beanstalk |
| `aws_app_runner` | AWS App Runner |
| `aws_openshift` | Red Hat OpenShift on AWS (ROSA) |
| `azure_vm` | Azure Virtual Machines |
| `azure_container_instances` | Azure Container Instances |
| `azure_aks` | Azure Kubernetes Service |
| `azure_functions` | Azure Functions |
| `azure_app_service` | Azure App Service |
| `azure_openshift` | Azure Red Hat OpenShift |
| `gcp_compute_engine` | Google Cloud Compute Engine (GCE) |
| `gcp_cloud_run` | Google Cloud Run |
| `gcp_kubernetes_engine` | Google Cloud Kubernetes Engine (GKE) |
| `gcp_cloud_functions` | Google Cloud Functions (GCF) |
| `gcp_app_engine` | Google Cloud App Engine (GAE) |
| `gcp_openshift` | Red Hat OpenShift on Google Cloud |
| `ibm_cloud_openshift` | Red Hat OpenShift on IBM Cloud |
| `tencent_cloud_cvm` | Tencent Cloud Cloud Virtual Machine (CVM) |
| `tencent_cloud_eks` | Tencent Cloud Elastic Kubernetes Service (EKS) |
| `tencent_cloud_scf` | Tencent Cloud Serverless Cloud Function (SCF) |
<!-- endsemconv -->
