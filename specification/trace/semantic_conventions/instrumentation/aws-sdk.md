# Semantic conventions for AWS SDK

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting the AWS SDK. They map request or response
parameters in AWS SDK API calls to attributes on a Span. The conventions have been collected over time based
on feedback from AWS users of tracing and will continue to increase as new interesting conventions
are found.

Some descriptions are also provided for populating general OpenTelemetry semantic conventions based on these APIs.

## Context Propagation

See [compatibility](../../../../supplementary-guidelines/compatibility/aws.md#context-propagation).

## Common Attributes

The span name MUST be of the format `Service.Operation` as per the AWS HTTP API, e.g., `DynamoDB.GetItem`,
`S3.ListBuckets`. This is equivalent to concatenating `rpc.service` and `rpc.method` with `.` and consistent
with the naming guidelines for RPC client spans.

<!-- semconv aws -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.request_id` | string | The AWS request ID as returned in the response headers `x-amz-request-id` or `x-amz-requestid`. | `79b9da39-b7ae-508a-a6bc-864b2829c622`; `C9ER4AJX75574TDJ` | Recommended |
| [`rpc.method`](../rpc.md) | string | The name of the operation corresponding to the request, as returned by the AWS SDK [1] | `GetItem`; `PutItem` | Recommended |
| [`rpc.service`](../rpc.md) | string | The name of the service to which a request is made, as returned by the AWS SDK. [2] | `DynamoDB`; `S3` | Recommended |
| [`rpc.system`](../rpc.md) | string | The value `aws-api`. | `aws-api` | Required |

**[1]:** This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).

**[2]:** This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).
<!-- endsemconv -->

## DynamoDB

### Common Attributes

These attributes are filled in for all DynamoDB request types.

<!-- semconv dynamodb.all -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`db.system`](../database.md) | string | The value `dynamodb`. | `dynamodb` | Required |
<!-- endsemconv -->

### DynamoDB.BatchGetItem

<!-- semconv dynamodb.batchgetitem -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.table_names` | string[] | The keys in the `RequestItems` object field. | `[Users, Cats]` | Recommended |
<!-- endsemconv -->

### DynamoDB.BatchWriteItem

<!-- semconv dynamodb.batchwriteitem -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | Recommended |
| `aws.dynamodb.table_names` | string[] | The keys in the `RequestItems` object field. | `[Users, Cats]` | Recommended |
<!-- endsemconv -->

### DynamoDB.CreateTable

<!-- semconv dynamodb.createtable -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.global_secondary_indexes` | string[] | The JSON-serialized value of each item of the `GlobalSecondaryIndexes` request field | `[{ "IndexName": "string", "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" }, "ProvisionedThroughput": { "ReadCapacityUnits": number, "WriteCapacityUnits": number } }]` | Recommended |
| `aws.dynamodb.local_secondary_indexes` | string[] | The JSON-serialized value of each item of the `LocalSecondaryIndexes` request field. | `[{ "IndexArn": "string", "IndexName": "string", "IndexSizeBytes": number, "ItemCount": number, "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" } }]` | Recommended |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | Recommended |
| `aws.dynamodb.provisioned_read_capacity` | double | The value of the `ProvisionedThroughput.ReadCapacityUnits` request parameter. | `1.0`; `2.0` | Recommended |
| `aws.dynamodb.provisioned_write_capacity` | double | The value of the `ProvisionedThroughput.WriteCapacityUnits` request parameter. | `1.0`; `2.0` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.DeleteItem

<!-- semconv dynamodb.deleteitem -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.DeleteTable

<!-- semconv dynamodb.deletetable -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.DescribeTable

<!-- semconv dynamodb.describetable -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.GetItem

<!-- semconv dynamodb.getitem -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | Recommended |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.projection` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.ListTables

<!-- semconv dynamodb.listtables -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.exclusive_start_table` | string | The value of the `ExclusiveStartTableName` request parameter. | `Users`; `CatsTable` | Recommended |
| `aws.dynamodb.table_count` | int | The the number of items in the `TableNames` response parameter. | `20` | Recommended |
| `aws.dynamodb.limit` | int | The value of the `Limit` request parameter. | `10` | Recommended |
<!-- endsemconv -->

### DynamoDB.PutItem

<!-- semconv dynamodb.putitem -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | Recommended |
| `aws.dynamodb.table_names` | string[] | The keys in the `RequestItems` object field. | `[Users, Cats]` | Recommended |
<!-- endsemconv -->

### DynamoDB.Query

<!-- semconv dynamodb.query -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.scan_forward` | boolean | The value of the `ScanIndexForward` request parameter. |  | Recommended |
| `aws.dynamodb.attributes_to_get` | string[] | The value of the `AttributesToGet` request parameter. | `[lives, id]` | Recommended |
| `aws.dynamodb.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | Recommended |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.index_name` | string | The value of the `IndexName` request parameter. | `name_to_group` | Recommended |
| `aws.dynamodb.limit` | int | The value of the `Limit` request parameter. | `10` | Recommended |
| `aws.dynamodb.projection` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | Recommended |
| `aws.dynamodb.select` | string | The value of the `Select` request parameter. | `ALL_ATTRIBUTES`; `COUNT` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.Scan

<!-- semconv dynamodb.scan -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.segment` | int | The value of the `Segment` request parameter. | `10` | Recommended |
| `aws.dynamodb.total_segments` | int | The value of the `TotalSegments` request parameter. | `100` | Recommended |
| `aws.dynamodb.count` | int | The value of the `Count` response parameter. | `10` | Recommended |
| `aws.dynamodb.scanned_count` | int | The value of the `ScannedCount` response parameter. | `50` | Recommended |
| `aws.dynamodb.attributes_to_get` | string[] | The value of the `AttributesToGet` request parameter. | `[lives, id]` | Recommended |
| `aws.dynamodb.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | Recommended |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.index_name` | string | The value of the `IndexName` request parameter. | `name_to_group` | Recommended |
| `aws.dynamodb.limit` | int | The value of the `Limit` request parameter. | `10` | Recommended |
| `aws.dynamodb.projection` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | Recommended |
| `aws.dynamodb.select` | string | The value of the `Select` request parameter. | `ALL_ATTRIBUTES`; `COUNT` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.UpdateItem

<!-- semconv dynamodb.updateitem -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

### DynamoDB.UpdateTable

<!-- semconv dynamodb.updatetable -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.dynamodb.attribute_definitions` | string[] | The JSON-serialized value of each item in the `AttributeDefinitions` request field. | `[{ "AttributeName": "string", "AttributeType": "string" }]` | Recommended |
| `aws.dynamodb.global_secondary_index_updates` | string[] | The JSON-serialized value of each item in the the `GlobalSecondaryIndexUpdates` request field. | `[{ "Create": { "IndexName": "string", "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" }, "ProvisionedThroughput": { "ReadCapacityUnits": number, "WriteCapacityUnits": number } }]` | Recommended |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | Recommended |
| `aws.dynamodb.provisioned_read_capacity` | double | The value of the `ProvisionedThroughput.ReadCapacityUnits` request parameter. | `1.0`; `2.0` | Recommended |
| `aws.dynamodb.provisioned_write_capacity` | double | The value of the `ProvisionedThroughput.WriteCapacityUnits` request parameter. | `1.0`; `2.0` | Recommended |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | Recommended |
<!-- endsemconv -->

## S3

<!-- semconv aws.s3 -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `aws.s3.bucket` | string | The S3 bucket name the request refers to. Corresponds to the `--bucket` parameter of the [S3 API](https://docs.aws.amazon.com/cli/latest/reference/s3api/index.html) operations. [1] | `some-bucket-name` | Recommended |
| `aws.s3.key` | string | The S3 object key the request refers to. Corresponds to the `--key` parameter of the [S3 API](https://docs.aws.amazon.com/cli/latest/reference/s3api/index.html) operations. [2] | `someFile.yml` | Recommended |
| `aws.s3.copy_source` | string | The source object (in the form `bucket`/`key`) for the copy operation. [3] | `someFile.yml` | Recommended |
| `aws.s3.upload_id` | string | Upload ID that identifies the multipart upload. [4] | `dfRtDYWFbkRONycy.Yxwh66Yjlx.cph0gtNBtJ` | Recommended |
| `aws.s3.delete` | string | The delete request container that specifies the objects to be deleted. [5] | `Objects=[{Key=string,VersionId=string},{Key=string,VersionId=string}],Quiet=boolean` | Recommended |
| `aws.s3.part_number` | int | The part number of the part being uploaded in a multipart-upload operation. This is a positive integer between 1 and 10,000. [6] | `3456` | Recommended |

**[1]:** The `bucket` attribute is applicable to all S3 operations that reference a bucket, i.e. that require the bucket name as a mandatory parameter.
This applies to almost all S3 operations except `list-buckets`.

**[2]:** The `key` attribute is applicable to all object-related S3 operations, i.e. that require the object key as a mandatory parameter.
This applies in particular to the following operations:

- [copy-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/copy-object.html)
- [delete-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/delete-object.html)
- [get-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object.html)
- [head-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/head-object.html)
- [put-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-object.html)
- [restore-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/restore-object.html)
- [select-object-content](https://docs.aws.amazon.com/cli/latest/reference/s3api/select-object-content.html)
- [abort-multipart-upload](https://docs.aws.amazon.com/cli/latest/reference/s3api/abort-multipart-upload.html)
- [complete-multipart-upload](https://docs.aws.amazon.com/cli/latest/reference/s3api/complete-multipart-upload.html)
- [create-multipart-upload](https://docs.aws.amazon.com/cli/latest/reference/s3api/create-multipart-upload.html)
- [list-parts](https://docs.aws.amazon.com/cli/latest/reference/s3api/list-parts.html)
- [upload-part](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part.html)
- [upload-part-copy](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part-copy.html)

**[3]:** The `copy_source` attribute applies to S3 copy operations and corresponds to the `--copy-source` parameter
of the [copy-object operation within the S3 API](https://docs.aws.amazon.com/cli/latest/reference/s3api/copy-object.html).
This applies in particular to the following operations:

- [copy-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/copy-object.html)
- [upload-part-copy](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part-copy.html)

**[4]:** The `upload_id` attribute applies to S3 multipart-upload operations and corresponds to the `--upload-id` parameter
of the [S3 API](https://docs.aws.amazon.com/cli/latest/reference/s3api/index.html) multipart operations.
This applies in particular to the following operations:

- [abort-multipart-upload](https://docs.aws.amazon.com/cli/latest/reference/s3api/abort-multipart-upload.html)
- [complete-multipart-upload](https://docs.aws.amazon.com/cli/latest/reference/s3api/complete-multipart-upload.html)
- [list-parts](https://docs.aws.amazon.com/cli/latest/reference/s3api/list-parts.html)
- [upload-part](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part.html)
- [upload-part-copy](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part-copy.html)

**[5]:** The `delete` attribute is only applicable to the [delete-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/delete-object.html) operation.
The `delete` attribute corresponds to the `--delete` parameter of the
[delete-objects operation within the S3 API](https://docs.aws.amazon.com/cli/latest/reference/s3api/delete-objects.html).

**[6]:** The `part_number` attribute is only applicable to the [upload-part](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part.html)
and [upload-part-copy](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part-copy.html) operations.
The `part_number` attribute corresponds to the `--part-number` parameter of the
[upload-part operation within the S3 API](https://docs.aws.amazon.com/cli/latest/reference/s3api/upload-part.html).
<!-- endsemconv -->