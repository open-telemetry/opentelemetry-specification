# Google Compute Engine

**Type:** `gcp.gce`

**Description:** Resource attributes for GCE instances.

<!-- semconv gcp.gce -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `gcp.gce.instance.name` | string | The instance name of a GCE instance. This is the value provided by `host.name`, the visible name of the instance in the Cloud Console UI, and the prefix for the default hostname of the instance as defined by the [default internal DNS name](https://cloud.google.com/compute/docs/internal-dns#instance-fully-qualified-domain-names). | `instance-1`; `my-vm-name` | Recommended |
| `gcp.gce.instance.hostname` | string | The hostname of a GCE instance. This is the full value of the default or [custom hostname](https://cloud.google.com/compute/docs/instances/custom-hostname-vm). | `my-host1234.example.com`; `sample-vm.us-west1-b.c.my-project.internal` | Recommended |
<!-- endsemconv -->
