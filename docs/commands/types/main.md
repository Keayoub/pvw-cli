# Types Commands

Manage type definitions that control the schema for entities, classifications, and other metadata objects in Purview.

!!! tip "Quick Start"
    Inspect and manage type definitions and schema metadata for custom entity types, classifications, and business metadata.

## What You Can Do

- View type definitions and schemas
- Create custom entity types
- Define classification types
- Manage business metadata definitions
- Configure relationship types
- Define enumeration types

## Available Actions

### Read Type Definitions

| Command | Purpose |
| --- | --- |
| `readentitydef` | Get entity type definition |
| `readclassificationdef` | Get classification type definition |
| `readbusinessmetadatadef` | Get business metadata definition |
| `readrelationshipdef` | Get relationship type definition |
| `readenumdef` | Get enumeration definition |
| `readstructdef` | Get structure definition |
| `readtermtemplatedef` | Get term template definition |
| `readtypedef` | Get specific type definition |
| `readtypedefs` | Get all type definitions |
| `readtypedefsheaders` | Get type definition headers |
| `readstatistics` | Get type statistics |

### Create & Update Types

| Command | Purpose |
| --- | --- |
| `createtypedefs` | Create new type definitions |
| `puttypedefs` | Create or update types |

### Delete Types

| Command | Purpose |
| --- | --- |
| `deletetypedef` | Delete single type |
| `deletetypedefs` | Delete multiple types |

## Type Definitions

Type definitions control:

- **Entity Types**: Structure and properties of assets
- **Classification Types**: Tagging and labeling schemas
- **Business Metadata**: Custom metadata structures
- **Relationships**: Connections between entities
- **Enumerations**: Predefined value lists
- **Structures**: Complex object types

## Related Topics

- [Entity commands](../entity/main.md)
- [Glossary commands](../glossary/main.md)
- [Create Tasks](../task-create.md)
