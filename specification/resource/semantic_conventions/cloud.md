# Cloud

**type:** `cloud`

**Description:** A cloud infrastructure (e.g. GCP, Azure, AWS).

| Attribute  | Description  | Example  |
|---|---|---|
| cloud.provider | Name of the cloud provider. See [Cloud Providers](#cloud-providers) for a list of known values. It is not guaranteed that this value will be in the set. | `gcp` |
| cloud.account.id | The cloud account id used to identify different entities. | `opentelemetry` |
| cloud.region | A specific geographical location where different entities can run | `us-central1` |
| cloud.zone | Zones are a sub set of the region connected through low-latency links.<br/> In aws it is called availability-zone. | `us-central1-a` |

## Cloud Providers

These are known-used values of `cloud.provider`. However, `cloud.provider` is not necessarily limited to just these in the set.

| cloud.provider | Description |
|---|---|
| aws | Amazon Web Services |
| azure | Microsoft Azure |
| gcp | Google Cloud Platform |
