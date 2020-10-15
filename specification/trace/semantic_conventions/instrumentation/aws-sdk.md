# AWS SDK Semantic Conventions

These conventions apply to operations using the AWS SDK. They map request or response parameters
in AWS SDK API calls to attributes on a Span. The conventions have been collected over time based
on feedback from AWS users of tracing and will continue to increase as new interesting conventions
are found.

Some descriptions are also provided for populating OpenTelemetry semantic conventions.

## General

| Attribute | Type | Description | Examples |
|---|---|---|---|
|awssdk.service | string | The service name of the request, as returned by the AWS SDK | `DynamoDB`, `S3` |
|awssdk.operation | string | The operation name of the request, as returned by the AWS SDK | `GetItem`, `PutObject` |

The following attributes are all copied from parameters in the request or response of the SDK call.

## DynamoDB

### BatchGetItem

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.table_names` | string array | Extract the keys of the `RequestItems` object field in the request |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |

### BatchWriteItem

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.table_names` | string array | Extract the keys of the `RequestItems` object field in the request |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |
| `awssdk.item_collection_metrics` | string | JSON-serialize the `ItemCollectionMetrics` response object field |

### CreateTable

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.global_secondary_indexes` | string | JSON-serialize the `GlobalSecondaryIndexes` request list field |
| `awssdk.local_secondary_indexes` | string | JSON-serialize the `LocalSecondaryIndexes` request list field |
| `awssdk.provisioned_throughput. | int | d_capacity_units` - Copy the `ProvisionedThroughput.ReadCapacityUnits` request parameter |
| `awssdk.provisioned_throughput. | int | te_capacity_units` - Copy the `ProvisionedThroughput.ReadCapacityUnits` request parameter |

### DeleteItem

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |
| `awssdk.item_collection_metrics` | string | JSON-serialize the `ItemCollectionMetrics` response object field |

### DeleteTable

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |

### DescribeTable

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |

### GetItem

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.consistent_read` | bool | Copy the `ConsistentRead` request parameter |
| `awssdk.projection_expression` | string | Copy the `ProjectionExpression` request parameter |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |

### ListTables

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.exclusive_start_table_name` | string | Copy the `ExclusiveStartTableName` request parameter |
| `awssdk.limit` | int | Copy the `Limit` request parameter |
| `awssdk.table_count` | int | Fill in the number of elements in the `TableNames` response list parameter |

### PutItem

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |
| `awssdk.item_collection_metrics` | string | JSON-serialize the `ItemCollectionMetrics` response object field |

### Query

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.attributes_to_get` | string array | Copy the `AttributesToGet` list request parameter |
| `awssdk.consistent_read` | bool | Copy the `ConsistentRead` request parameter |
| `awssdk.index_name` | string | Copy the `IndexName` request parameter |
| `awssdk.limit` | int | Copy the `Limit` request parameter |
| `awssdk.projection_expression` | string | Copy the `ProjectionExpression` request parameter |
| `awssdk.scan_index_forward` | bool | Copy the `ScanIndexForward` request parameter |
| `awssdk.select` | string | Copy the `Select` request parameter |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |

### Scan

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.attributes_to_get` | string array | Copy the `AttributesToGet` list request parameter |
| `awssdk.consistent_read` | bool | Copy the `ConsistentRead` request parameter |
| `awssdk.index_name` | string | Copy the `IndexName` request parameter |
| `awssdk.limit` | int | Copy the `Limit` request parameter |
| `awssdk.projection_expression` | string | Copy the `ProjectionExpression` request parameter |
| `awssdk.segment` | int | Copy the `Segment` request parameter |
| `awssdk.select` | string | Copy the `Select` request parameter |
| `awssdk.total_segments` | int | Copy the `TotalSegments` request parameter |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |
| `awssdk.count` | int | Copy the `Count` response parameter |
| `awssdk.scanned_count` | int | Copy the `ScannedCount` response parameter |

### UpdateItem

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.consumed_capacity` | string | JSON-serialize the `ConsumedCapacity` response list field |
| `awssdk.item_collection_metrics` | string | JSON-serialize the `ItemCollectionMetrics` response object field |

### UpdateTable

| Attribute | Type | Description |
| --- | --- | --- |
| `db.name` | string | Copy the `TableName` request parameter |
| `awssdk.attribute_definitions` | string | JSON-serialize the `AttributeDefinitions` request list field |
| `awssdk.global_secondary_index_updates` | string | JSON-serialize the `GlobalSecondaryIndexUpdates` request list field |
| `awssdk.provisioned_throughput. | int | d_capacity_units` - Copy the `ProvisionedThroughput.ReadCapacityUnits` request parameter |
| `awssdk.provisioned_throughput. | int | te_capacity_units` - Copy the `ProvisionedThroughput.ReadCapacityUnits` request parameter |

## SQS

### AddPermission

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `awssdk.label` | string | Copy the `Label` request field |

### ChangeMessageVisibility

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `awssdk.visibility_timeout` | int | Copy the `VisibilityTimeout` request field |

### ChangeMessageVisibilityBatch

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |

### CreateQueue

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.attributes` | string | JSON serialize the `Attributes` request field. If `Attributes` is a list of key/value pairs, pack them into an object before serializing. |
| `awssdk.queue_name` | string | Copy the `QueueName` request field |

### DeleteMessage

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |

### DeleteMessageBatch

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |

### DeleteQueue

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |

### GetQueueAttributes

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `awssdk.attributes` | string | JSON serialize the `Attributes` response field. If `Attributes` is a list of key/value pairs, pack them into an object before serializing. |

### GetQueueUrl

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` response field |
| `awssdk.queue_name` | string | Copy the `QueueName` request field |
| `awssdk.queue_owner_aws_account_id` | string | Copy the `QueueOwnerAWSAccountId` request field |

### ListDeadLetterSourceQueues

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `awssdk.queue_urls` | string array | Copy the `QueueUrls` response field |

### ListQueues

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.queue_name_prefix` | string | Copy the `QueueNamePrefix` request field |
| `awssdk.queue_count` | int | Fill in the number of elements in the `QueueUrls` response list field |

### PurgeQueue

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |

### ReceiveMessage

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `messaging.operation` | string | Fill in `receive` |
| `awssdk.attribute_names` | string array | Copy the `AttributeNames` request field |
| `awssdk.max_number_of_messages` | int | Copy the `MaxNumberOfMessages` request field |
| `awssdk.message_attribute_names` | string array | Copy the `MessageAttributeNames` request field |
| `awssdk.visibility_timeout` | int | Copy the `VisibilityTimeout` request field |
| `awssdk.wait_time_seconds` | int | py the `WaitTimeSeconds` request field |
| `awssdk.message_count` | int | Fill in the number of elements in the `Messages` response list field |

### RemovePermission

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |

### SendMessage

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `messaging.message_id` | string | Copy the `MessageId` field |
| `messaging.operation` | string | Fill in `send` |
| `awssdk.delay_seconds` | int | Copy the `DelaySeconds` request field |
| `awssdk.message_attributes` | string array | Copy the keys of the `MessageAttributes` request object field |

### SendMessageBatch

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `messaging.operation` | string | Fill in `send` |
| `awssdk.message_count` | int | Fill in the number of elements in the `Messages` request list field |

### SetQueueAttributes

| Attribute | Type | Description |
| --- | --- | --- |
| `messaging.url` | string | Copy the `QueueUrl` request field |
| `awssdk.attribute_names` | string array | Copy the keys of the `Attributes` request object field |

## Lambda

Refer to the [FaaS] common attributes

[FaaS]: ../faas.md

### Invoke

| Attribute | Type | Description |
| --- | --- | --- |
| `faas.invoked_name` | string | Copy the `FunctionName` request field. |
| `faas.invoked_provider` | string | Fill in `aws` |
| `faas.invoked_region` | string | Fill in the value of the region from the API endpoint (SDKs should provide this separate from the request) |
| `awssdk.invocation_type` | string | Copy the `InvocationType` request field |
| `awssdk.log_type` | string | Copy the `LogType` request field |
| `awssdk.qualifier` | string | Copy the `Qualifier` request field |
| `awssdk.function_error` | string | Copy the `X-Amz-Function-Error` response header. SDKs may present this as a `FunctionError` field |

### InvokeAsync

| Attribute | Type | Description |
| --- | --- | --- |
| `faas.invoked_name` | string | Copy the `FunctionName` request field. |
| `faas.invoked_provider` | string | Fill in `aws` |
| `faas.invoked_region` | string | Fill in the value of the region from the API endpoint (SDKs should provide this separate from the request) |

## S3

### CopyObject

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.source_bucket_name` | string | Copy the `SourceBucketName` request field |
| `awssdk.source_key` | string | Copy the `SourceKey` request field |
| `awssdk.destination_bucket_name` | string | Copy the `DestinationBucketName` request field |
| `awssdk.destination_key` | string | Copy the `DestinationKey` request field |

### CopyPart

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.source_bucket_name` | string | Copy the `SourceBucketName` request field |
| `awssdk.source_key` | string | Copy the `SourceKey` request field |
| `awssdk.destination_bucket_name` | string | Copy the `DestinationBucketName` request field |
| `awssdk.destination_key` | string | Copy the `DestinationKey` request field |

### GetObject

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### PutObject

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### GetObjectAcl

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### CreateBucket

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListObjectsV2

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.prefix` | string | Copy the `Prefix` request field |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListObjects

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.prefix` | string | Copy the `Prefix` request field |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetObjectTagging

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### SetObjectTagging

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### ListVersions

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.prefix` | string | Copy the `Prefix` request field |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetObjectAcl

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### GetBucketAcl

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketAcl

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### HeadBucket

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### UploadPart

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### DeleteObject

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### DeleteBucket

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteObjects

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteVersion

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### GetBucketPolicy

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketPolicy

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListParts

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### RestoreObject

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### RestoreObjectV2

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### SetBucketNotificationConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketLifecycleConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketNotificationConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketCrossOriginConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketCrossOriginConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketCrossOriginConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListBucketInventoryConfigurations

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketReplicationConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketReplicationConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketReplicationConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketAnalyticsConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketInventoryConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListBucketAnalyticsConfigurations

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteObjectTagging

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### SetBucketVersioningConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketVersioningConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketWebsiteConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketLifecycleConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketLifecycleConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketTaggingConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketTaggingConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetObjectMetadata

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### GetBucketLocation

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketLoggingConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListMultipartUploads

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.prefix` | string | Copy the `Prefix` request field |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketPolicy

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketEncryption

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketAccelerateConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketWebsiteConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### CompleteMultipartUpload

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### InitiateMultipartUpload

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### SetBucketEncryption

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketLoggingConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketWebsiteConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketEncryption

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### AbortMultipartUpload

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |

### GeneratePresignedUrl

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |
| `awssdk.key` | string | Copy the `Key` request field |
| `awssdk.version_id` | string | Copy the `VersionId` request field |

### DeleteBucketTaggingConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketAccelerateConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketMetricsConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### ListBucketMetricsConfigurations

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketInventoryConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketMetricsConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### SetBucketAnalyticsConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### DeleteBucketMetricsConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketAnalyticsConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

### GetBucketInventoryConfiguration

| Attribute | Type | Description |
| --- | --- | --- |
| `awssdk.bucket_name` | string | Copy the `BucketName` request field |

## SageMakerRuntime

### InvokeEndpoint

| Attribute | Type | Description |
| --- | --- | --- |
`awssdk.endpoint_name` | string | Copy the `EndpointName` request field |
