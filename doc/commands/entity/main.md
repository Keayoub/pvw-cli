# pvw entity
[Command Reference](../../README.md#command-reference) > entity

## Description
Commands for managing entity operations in Azure Purview.

## Syntax
```
pvw entity <action> [options]
```

## Available Actions

### [addLabels](./addLabels.md)
Append labels to an entity.

### [addLabelsByUniqueAttribute](./addLabelsByUniqueAttribute.md)
Append labels to an entity identified by its type and unique attributes.

### [addOrUpdateBusinessAttribute](./addOrUpdateBusinessAttribute.md)
Add or update business attributes to an entity.

### [addOrUpdateBusinessMetadata](./addOrUpdateBusinessMetadata.md)
Add or update business metadata to an entity.

### [deleteBusinessAttribute](./deleteBusinessAttribute.md)
Delete business metadata from an entity.

### [deleteBusinessMetadata](./deleteBusinessMetadata.md)
Remove business metadata from an entity.

### [deleteLabels](./deleteLabels.md)
Delete label(s) from an entity.

### [deleteLabelsByUniqueAttribute](./deleteLabelsByUniqueAttribute.md)
Delete label(s) from an entity identified by its type and unique attributes.

### [getBusinessMetadataTemplate](./getBusinessMetadataTemplate.md)
Get a sample template for uploading/creating business metadata in bulk.

### [importBusinessMetadata](./importBusinessMetadata.md)
 Import business metadata in bulk.

### [setLabels](./setLabels.md)
Overwrite labels for an entity.

### [setLabelsByUniqueAttribute](./setLabelsByUniqueAttribute.md)
Overwrite labels for an entity identified by its type and unique attributes.

## Examples

```bash
# List available actions
pvw entity --help

# Get help for specific action
pvw entity <action> --help
```

## See Also

- [Command Reference](../../README.md#command-reference)
- [API Documentation](../api/index.html)
