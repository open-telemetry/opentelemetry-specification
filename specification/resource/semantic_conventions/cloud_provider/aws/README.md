# AWS Semantic Conventions

**Status**: [Experimental](../../../../document-status.md)

This directory defines standards for resource attributes that only apply to Amazon
Web Services (AWS) resources. If an attribute could apply to resources from more than one cloud
provider (like account ID, operating system, etc), it belongs in the parent
`semantic_conventions` directory.

## Generic AWS Attributes

Attributes that relate to AWS or use AWS-specific terminology, but are used by several
services within AWS or are abstracted away from any particular service:

- [AWS Logs](./logs.md)

## Services

Attributes that relate to an individual AWS service:

- [Elastic Container Service](./ecs.md)
