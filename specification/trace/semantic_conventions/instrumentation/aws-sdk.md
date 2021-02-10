# Semantic conventions for AWS SDK

**Status**: [Experimental](../../../document-status.md)

## Common Attributes

<!-- semconv aws -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.service` | string | The name of the service to which a request is made, as returned by the AWS SDK. | `DynamoDB`; `S3` | No |
| `aws.operation` | string | The name of the operation corresponding to the request, as returned by the AWS SDK | `GetItem`; `PutItem` | No |
<!-- endsemconv -->

## DynamoDB

### Shared Attributes

These attributes correspond to multiple request types and are referenced from individual methods below.

<!-- semconv dynamodb.shared -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.table_names` | string[] | The keys in the `RequestItems` object field in a request operating on multiple tables. | `[Users, Cats]` | No |
| `aws.consumed_capacity` | string[] | The JSON-serialized value of each item in the `ConsumedCapacity` response field. | `[{ "CapacityUnits": number, "GlobalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "LocalSecondaryIndexes": { "string" : { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number } }, "ReadCapacityUnits": number, "Table": { "CapacityUnits": number, "ReadCapacityUnits": number, "WriteCapacityUnits": number }, "TableName": "string", "WriteCapacityUnits": number }]` | No |
| `aws.item_collection_metrics` | string | The JSON-serialized value of the `ItemCollectionmetrics` response field. | `{ "string" : [ { "ItemCollectionKey": { "string" : { "B": blob, "BOOL": boolean, "BS": [ blob ], "L": [ "AttributeValue" ], "M": { "string" : "AttributeValue" }, "N": "string", "NS": [ "string" ], "NULL": boolean, "S": "string", "SS": [ "string" ] } }, "SizeEstimateRangeGB": [ number ] } ] }` | No |
| `aws.provisioned_throughput.read_capacity_units` | number | The value of the `ProvisionedThroughput.ReadCapacityUnits` request parameter. | `1`; `2` | No |
| `aws.provisioned_throughput.write_capacity_units` | number | The value of the `ProvisionedThroughput.WriteCapacityUnits` request parameter. | `1`; `2` | No |
| `aws.consistent_read` | boolean | The value of the `ConsistentRead` request parameter. |  | No |
| `aws.projection_expression` | string | The value of the `ProjectionExpression` request parameter. | `Title`; `Title, Price, Color`; `Title, Description, RelatedItems, ProductReviews` | No |
| `aws.limit` | number | The value of the `Limit` request parameter. | `10` | No |
| `aws.attributes_to_get` | string[] | The value of the `AttributesToGet` request parameter. | `[lives, id]` | No |
| `aws.index_name` | string | The value of the `IndexName` request parameter. | `name_to_group` | No |
| `aws.select` | string | The value of the `Select` request parameter. | `ALL_ATTRIBUTES`; `COUNT` | No |
<!-- endsemconv -->

### DynamoDB.BatchGetItem

<!-- semconv dynamodb.batchgetitem -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `aws.table_names`, `aws.consumed_capacity`
<!-- endsemconv -->

### DynamoDB.BatchWriteItem

<!-- semconv dynamodb.batchwriteitem -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `aws.table_names`, `aws.consumed_capacity`, `aws.item_collection_metrics`
<!-- endsemconv -->

### DynamoDB.CreateTable

<!-- semconv dynamodb.createtable -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.global_secondary_indexes` | string[] | The JSON-serialized value of each item of the`GlobalSecondaryIndexes` request field | `[{ "IndexName": "string", "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" }, "ProvisionedThroughput": { "ReadCapacityUnits": number, "WriteCapacityUnits": number } }]` | No |
| `aws.local_secondary_indexes` | string[] | The JSON-serialized value of each item of the `LocalSecondaryIndexes` request field. | `[{ "IndexArn": "string", "IndexName": "string", "IndexSizeBytes": number, "ItemCount": number, "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" } }]` | No |

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.item_collection_metrics`, `aws.provisioned_throughput.read_capacity_units`, `aws.provisioned_throughput.write_capacity_units`
<!-- endsemconv -->

### DynamoDB.DeleteItem

<!-- semconv dynamodb.deleteitem -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.item_collection_metrics`
<!-- endsemconv -->

### DynamoDB.DeleteTable

<!-- semconv dynamodb.deletetable -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md)
<!-- endsemconv -->

### DynamoDB.DescribeTable

<!-- semconv dynamodb.describetable -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md)
<!-- endsemconv -->

### DynamoDB.GetItem

<!-- semconv dynamodb.getitem -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.consistent_read`, `aws.projection_expression`
<!-- endsemconv -->

### DynamoDB.ListTables

<!-- semconv dynamodb.listtables -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.exclusive_start_table_name` | string | The value of the `ExclusiveStartTableName` request parameter. | `Users`; `CatsTable` | No |
| `aws.table_count` | number | The the number of items in the `TableNames` response parameter. | `20` | No |

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* `aws.limit`
<!-- endsemconv -->

### DynamoDB.PutItem

<!-- semconv dynamodb.putitem -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.item_collection_metrics`
<!-- endsemconv -->

### DynamoDB.Query

<!-- semconv dynamodb.query -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.scan_index_forward` | boolean | The value of the `ScanIndexForward` request parameter. |  | No |

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.consistent_read`, `aws.limit`, `aws.projection_expression`, `aws.attributes_to_get`, `aws.index_name`, `aws.select`
<!-- endsemconv -->

### DynamoDB.Scan

<!-- semconv dynamodb.scan -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.segment` | number | The value of the `Segment` request parameter. | `10` | No |
| `aws.total_segments` | number | The value of the `TotalSegments` request parameter. | `100` | No |
| `aws.count` | number | The value of the `Count` response parameter. | `10` | No |
| `aws.scanned_count` | number | The value of the `ScannedCount` response parameter. | `50` | No |

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.consistent_read`, `aws.limit`, `aws.projection_expression`, `aws.attributes_to_get`, `aws.index_name`, `aws.select`
<!-- endsemconv -->

### DynamoDB.UpdateItem

<!-- semconv dynamodb.updateitem -->

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.item_collection_metrics`
<!-- endsemconv -->

### DynamoDB.UpdateTable

<!-- semconv dynamodb.updatetable -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `aws.attribute_definitions` | string[] | The JSON-serialized value of each item in the `AttributeDefinitions` request field. | `[{ "AttributeName": "string", "AttributeType": "string" }]` | No |
| `aws.global_secondary_index_updates` | string[] | The JSON-serialized value of each item in the the `GlobalSecondaryIndexUpdates` request field. | `[{ "Create": { "IndexName": "string", "KeySchema": [ { "AttributeName": "string", "KeyType": "string" } ], "Projection": { "NonKeyAttributes": [ "string" ], "ProjectionType": "string" }, "ProvisionedThroughput": { "ReadCapacityUnits": number, "WriteCapacityUnits": number } }]` | No |

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`db.name`](../database.md), `aws.consumed_capacity`, `aws.provisioned_throughput.read_capacity_units`, `aws.provisioned_throughput.write_capacity_units`
<!-- endsemconv -->
