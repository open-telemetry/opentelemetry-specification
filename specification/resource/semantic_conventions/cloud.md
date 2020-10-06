# Cloud

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

| Attribute  | Description  | Example  |
|---|---|---|
| cloud.provider | Name of the cloud provider. See [Cloud Providers](#cloud-providers) for a list of known values. | `gcp` |
| cloud.account.id | The cloud account id used to identify different entities. | `opentelemetry` |
| cloud.region | A specific geographical location where different entities can run | `us-central1` |
| cloud.zone | Zones are a sub set of the region connected through low-latency links.<br/> In aws it is called availability-zone. | `us-central1-a` |

## Cloud Providers

`cloud.provider` MUST be one of the following or, if none of the listed values apply, a custom value:

| cloud.provider | Description |
|---|---|
| aws | Amazon Web Services |
| azure | Microsoft Azure |
| gcp | Google Cloud Platform |
