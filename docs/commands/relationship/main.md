# Relationship Commands

Manage relationships and connections between entities and metadata objects in your Purview catalog.

!!! tip "Quick Start"
    Create and inspect links between assets and metadata objects, establishing relationships for data lineage and connections.

## What You Can Do

- Create relationships between entities
- Read and inspect existing relationships
- Update relationship properties
- Delete obsolete relationships

## Quick Examples

=== "Read relationship"
    ```bash
    pvw relationship read --help
    ```

=== "Create relationship"
    ```bash
    pvw relationship create --help
    ```

=== "Update relationship"
    ```bash
    pvw relationship put --help
    ```

=== "Delete relationship"
    ```bash
    pvw relationship delete --help
    ```

## Available Actions

| Command | Purpose |
| --- | --- |
| `create` | Create new relationship between entities |
| `read` | Get relationship details |
| `put` | Create or update relationship |
| `delete` | Remove relationship |

## Relationship Types

Relationships connect different types of metadata:

- Asset-to-asset relationships
- Asset-to-classification relationships
- Asset-to-glossary term relationships
- Custom relationships based on business rules

## Related Topics

- [Entity commands](../entity/main.md)
- [Lineage commands](../lineage/main.md)
- [Create Tasks](../task-create.md)
- [Delete Tasks](../task-delete.md)
