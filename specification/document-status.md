# Definitions of Document Statuses

Specification documents (files) may explicitly define a "Status", typically
shown immediately after the document title. When present, the "Status" applies
to the individual document only and not to the entire specification or any other
documents. The following table describes what the statuses mean.

## Lifecycle status

The support guarantees and allowed changes are governed by the lifecycle of the document.Lifecycle stages are defined in the [Versioning and Stability](versioning-and-stability.md) document.

| Status               | Explanation                                                                                                         |
|----------------------|---------------------------------------------------------------------------------------------------------------------|
| No explicit "Status" | Equivalent to Experimental.                                                                                         |
| Experimental         | Breaking changes are allowed.                                                                                       |
| Frozen               | Not accepting new features, signifies cool-down period prior to stabilization.                                      |
| Stable               | Breaking changes are no longer allowed. See [stability guarantees](versioning-and-stability.md#stable) for details. |
| Deprecated           | Changes are no longer allowed, except for editorial changes.                                                        |

## Mixed

Some documents have individual sections with different statuses. These documents are marked with the status `Mixed` at the top, for clarity.
