# Entity Commands

Comprehensive toolkit for managing catalog entities, classifications, labels, and business metadata in Microsoft Purview.

!!! tip "Quick Start"
    Start with entity operations: Create, read, update, delete, classify, label, and bulk-process catalog entities and their metadata.

## What You Can Do

- Create and update individual or bulk entities
- Add and manage classifications, labels, and business metadata
- Bulk import/export entity data
- Manage entity collections
- Change entity ownership and assignments

## Quick Examples

=== "Read an entity"
    ```bash
    pvw entity read --guid <entity-guid>
    ```

=== "Create an entity"
    ```bash
    pvw entity create --help
    ```

=== "Bulk create from JSON"
    ```bash
    pvw entity createbulk --help
    ```

=== "Add classifications"
    ```bash
    pvw entity createclassifications --help
    ```

## Available Actions

### Read Operations

| Command | Purpose |
| --- | --- |
| `read` | Retrieve a single entity by GUID |
| `readbulk` | Retrieve multiple entities by GUID |
| `readbulkuniqueattribute` | Retrieve by qualified name |
| `readheader` | Get entity header information |
| `readclassification` | Get classifications for entity |
| `readclassifications` | List all classifications |
| `readuniqueattribute` | Retrieve entity by unique attribute |

### Create Operations

| Command | Purpose |
| --- | --- |
| `create` | Create a single entity |
| `createbulk` | Create multiple entities |
| `createclassifications` | Add classifications |
| `createbulkclassification` | Bulk add classifications |
| `createorupdatecollection` | Create or assign to collection |
| `createorupdatecollectionbulk` | Bulk collection assignment |

### Update Operations

| Command | Purpose |
| --- | --- |
| `put` | Create or update entity |
| `putclassifications` | Set classifications |
| `putuniqueattribute` | Update by unique attribute |
| `putuniqueattributeclassifications` | Update classifications by unique attribute |
| `addorupdatebusinessmetadata` | Add or update business metadata |
| `addorupdatebusinessattribute` | Add or update business attribute |

### Label Operations

| Command | Purpose |
| --- | --- |
| `addlabels` | Add labels to entity |
| `setlabels` | Set labels (replaces existing) |
| `deletelabels` | Remove labels |
| `addlabelsByUniqueAttribute` | Add labels by unique attribute |
| `setLabelsByUniqueAttribute` | Set labels by unique attribute |
| `deleteLabelsByUniqueAttribute` | Remove labels by unique attribute |

### Delete Operations

| Command | Purpose |
| --- | --- |
| `delete` | Delete entity |
| `deletebulk` | Delete multiple entities |
| `deleteclassification` | Remove classification |
| `deletebusinessmetadata` | Remove business metadata |
| `deletebusinessattribute` | Remove business attribute |

### Collection Management

| Command | Purpose |
| --- | --- |
| `changecollection` | Move entity to different collection |
| `createorupdatecollection` | Assign to collection |

### Business Metadata

| Command | Purpose |
| --- | --- |
| `getbusinessmetadatatemplate` | Get metadata template |
| `importbusinessmetadata` | Import metadata definitions |
| `addorupdatebusinessmetadata` | Update metadata |

## Common Workflows

### Bulk Import Entities

For high-volume entity creation with performance optimization, see [Entity Bulk CSV Guide](../../entity-bulk-csv-guide.md).

### Classify Entities

```bash
# Add classification to single entity
pvw entity createclassifications --help

# Bulk add classifications
pvw entity createbulkclassification --help
```

### Manage Labels

```bash
# Add labels
pvw entity addlabels --help

# Set labels (replaces)
pvw entity setlabels --help
```

## Related Topics

- [Create Tasks](../task-create.md)
- [Update Tasks](../task-update.md)
- [Delete Tasks](../task-delete.md)
- [Import Tasks](../task-import.md)
- [Search commands](../search/main.md)
- [Entity Bulk CSV Guide](../../entity-bulk-csv-guide.md)
