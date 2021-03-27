# Semantic conventions for AWS SDK

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting the AWS SDK. They map request or response
parameters in AWS SDK API calls to attributes on a Span. The conventions have been collected over time based
on feedback from AWS users of tracing and will continue to increase as new interesting conventions
are found.

Some descriptions are also provided for populating general OpenTelemetry semantic conventions based on these APIs.

## Common Attributes

The span name MUST be of the format `Service.Operation` as per the AWS HTTP API, e.g., `DynamoDB.GetItem`,
`S3.ListBuckets`. This is equivalent to concatenating `rpc.service` and `rpc.method` with `.` and consistent
with the naming guidelines for RPC client spans.

<!-- semconv aws -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`rpc.method`](../rpc.md) | string | The name of the operation corresponding to the request, as returned by the AWS SDK | `GetItem`; `PutItem` | No |
| [`rpc.service`](../rpc.md) | string | The name of the service to which a request is made, as returned by the AWS SDK. | `DynamoDB`; `S3` | No |
| [`rpc.system`](../rpc.md) | string | The value `aws-api`. | `aws-api` | Yes |
<!-- endsemconv -->

## DynamoDB

### Common Attributes

These attributes are filled in for all DynamoDB request types.

<!-- semconv dynamodb.all -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| [`db.system`](../database.md) | string | The value `dynamodb`. | `dynamodb` | Yes |
<!-- endsemconv -->

### DynamoDB.BatchGetItem

<!-- semconv dynamodb.batchgetitem -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.table_names` | string[] | The keys in the `RequestItems` object field. | `[Users, Cats]` | No |
<!-- endsemconv -->

### DynamoDB.BatchWriteItem

<!-- semconv dynamodb.batchwriteitem -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | No |
| `aws.dynamodb.table_names` | string[] | The keys in the `RequestItems` object field. | `[Users, Cats]` | No |
<!-- endsemconv -->

### DynamoDB.CreateTable

<!-- semconv dynamodb.createtable -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.global_secondary_indexes` | string[] | The JSON-serialized value of each item of the `GlobalSecondaryIndexes` request field | `[{ "IndexName": "string", "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" }, "ProvisionedThroughput": { "ReadCapacityUnits": number, "WriteCapacityUnits": number } }]` | No |
| `aws.dynamodb.local_secondary_indexes` | string[] | The JSON-serialized value of each item of the `LocalSecondaryIndexes` request field. | `[{ "IndexArn": "string", "IndexName": "string", "IndexSizeBytes": number, "ItemCount": number, "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" } }]` | No |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | No |
| `aws.dynamodb.provisioned_read_capacity` | double | The value of the `ProvisionedThroughput.ReadCapacityUnits` request parameter. | `1.0`; `2.0` | No |
| `aws.dynamodb.provisioned_write_capacity` | double | The value of the `ProvisionedThroughput.WriteCapacityUnits` request parameter. | `1.0`; `2.0` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.DeleteItem

<!-- semconv dynamodb.deleteitem -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.DeleteTable

<!-- semconv dynamodb.deletetable -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.DescribeTable

<!-- semconv dynamodb.describetable -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.GetItem

<!-- semconv dynamodb.getitem -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | No |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.projection` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.ListTables

<!-- semconv dynamodb.listtables -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.exclusive_start_table` | string | The value of the `ExclusiveStartTableName` request parameter. | `Users`; `CatsTable` | No |
| `aws.dynamodb.table_count` | int | The the number of items in the `TableNames` response parameter. | `20` | No |
| `aws.dynamodb.limit` | int | The value of the `Limit` request parameter. | `10` | No |
<!-- endsemconv -->

### DynamoDB.PutItem

<!-- semconv dynamodb.putitem -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | No |
| `aws.dynamodb.table_names` | string[] | The keys in the `RequestItems` object field. | `[Users, Cats]` | No |
<!-- endsemconv -->

### DynamoDB.Query

<!-- semconv dynamodb.query -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.scan_forward` | boolean | The value of the `ScanIndexForward` request parameter. |  | No |
| `aws.dynamodb.attributes_to_get` | string[] | The value of the `AttributesToGet` request parameter. | `[lives, id]` | No |
| `aws.dynamodb.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | No |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.index_name` | string | The value of the `IndexName` request parameter. | `name_to_group` | No |
| `aws.dynamodb.limit` | int | The value of the `Limit` request parameter. | `10` | No |
| `aws.dynamodb.projection` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | No |
| `aws.dynamodb.select` | string | The value of the `Select` request parameter. | `ALL_ATTRIBUTES`; `COUNT` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.Scan

<!-- semconv dynamodb.scan -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.segment` | int | The value of the `Segment` request parameter. | `10` | No |
| `aws.dynamodb.total_segments` | int | The value of the `TotalSegments` request parameter. | `100` | No |
| `aws.dynamodb.count` | int | The value of the `Count` response parameter. | `10` | No |
| `aws.dynamodb.scanned_count` | int | The value of the `ScannedCount` response parameter. | `50` | No |
| `aws.dynamodb.attributes_to_get` | string[] | The value of the `AttributesToGet` request parameter. | `[lives, id]` | No |
| `aws.dynamodb.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | No |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.index_name` | string | The value of the `IndexName` request parameter. | `name_to_group` | No |
| `aws.dynamodb.limit` | int | The value of the `Limit` request parameter. | `10` | No |
| `aws.dynamodb.projection` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | No |
| `aws.dynamodb.select` | string | The value of the `Select` request parameter. | `ALL_ATTRIBUTES`; `COUNT` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.UpdateItem

<!-- semconv dynamodb.updateitem -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionMetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->

### DynamoDB.UpdateTable

<!-- semconv dynamodb.updatetable -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.dynamodb.attribute_definitions` | string[] | The JSON-serialized value of each item in the `AttributeDefinitions` request field. | `[{ "AttributeName": "string", "AttributeType": "string" }]` | No |
| `aws.dynamodb.global_secondary_index_updates` | string[] | The JSON-serialized value of each item in the the `GlobalSecondaryIndexUpdates` request field. | `[{ "Create": { "IndexName": "string", "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" }, "ProvisionedThroughput": { "ReadCapacityUnits": number, "WriteCapacityUnits": number } }]` | No |
| `aws.dynamodb.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.dynamodb.provisioned_read_capacity` | double | The value of the `ProvisionedThroughput.ReadCapacityUnits` request parameter. | `1.0`; `2.0` | No |
| `aws.dynamodb.provisioned_write_capacity` | double | The value of the `ProvisionedThroughput.WriteCapacityUnits` request parameter. | `1.0`; `2.0` | No |
| `aws.dynamodb.table_names` | string[] | A single-element array with the value of the TableName request parameter. | `[Users]` | No |
<!-- endsemconv -->
