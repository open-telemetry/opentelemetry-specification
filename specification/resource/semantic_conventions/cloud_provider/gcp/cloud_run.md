# Google Cloud Run

**Type:** `gcp.cloud_run`

**Description:** Resource attributes for GCE instances.

<!-- semconv gcp.cloud_run -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `gcp.cloud_run.job.execution` | string | The [execution](https://cloud.google.com/run/docs/managing/job-executions) of the job. | `job-name-xxxx`; `sample-job-mdw84` | Recommended |
| `gcp.cloud_run.job.task_index` | int | The index for a task within an execution as provided by the [`CLOUD_RUN_TASK_INDEX`](https://cloud.google.com/run/docs/container-contract#jobs-env-vars) environment variable. | `0`; `1` | Recommended |
<!-- endsemconv -->
