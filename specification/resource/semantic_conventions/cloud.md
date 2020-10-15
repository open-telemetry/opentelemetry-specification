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
| `cloud.infrastructure.service` | string | Description of cloud resource in use. [2] | `AWS::EC2::Instance`<br>`Azure::Compute::VM`<br>`GCP::ComputeEngine::VM` | No |

**[1]:** In AWS, this is called availability-zone.

**[2]:** The first entry should generally be a cloud provider, followed by a product category, then finally a particular piece of compute infrastructure. Each entry is delimited by a double colon (::).

`cloud.provider` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |
<!-- endsemconv -->
