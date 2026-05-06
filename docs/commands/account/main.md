# Account Commands

Manage collections, access control, and resource set rules in the Purview account data plane.

!!! tip "Quick Start"
    Work with data-plane settings such as collections, collection hierarchies, resource set rules, and collection permissions.

## What You Can Do

- Create and manage collections for organizing assets
- Set up collection hierarchies and parent-child relationships
- Define resource set rules for asset grouping
- Retrieve collection path information
- Get collection access details

## Quick Examples

=== "Get account info"
    ```bash
    pvw account getaccount
    ```

=== "List collections"
    ```bash
    pvw account getcollections
    ```

=== "Create collection"
    ```bash
    pvw account putcollection --help
    ```

=== "Get collection path"
    ```bash
    pvw account getcollectionpath --help
    ```

## Available Actions

### Account Information

| Command | Purpose |
| --- | --- |
| `getaccount` | Get account details and configuration |
| `updateaccount` | Update account settings |
| `getaccesskeys` | Retrieve account access keys |
| `regenerateaccesskeys` | Generate new access keys |

### Collection Management

| Command | Purpose |
| --- | --- |
| `getcollections` | List all collections |
| `getcollection` | Get specific collection |
| `getchildcollectionnames` | List child collections |
| `getcollectionpath` | Get full collection path |
| `putcollection` | Create or update collection |
| `deletecollection` | Remove collection |

### Resource Set Rules

| Command | Purpose |
| --- | --- |
| `getresourcesetrules` | List all rules |
| `getresourcsetrule` | Get specific rule |
| `putresourcesetrule` | Create or update rule |
| `deleteresourcesetrule` | Remove rule |

## Common Workflows

### Organize Assets With Collections

```bash
# 1. Create root collection
pvw account putcollection --help

# 2. Create child collections
pvw account putcollection --help

# 3. View collection hierarchy
pvw account getcollections --help

# 4. Get full path
pvw account getcollectionpath --help
```

### Set Up Resource Set Rules

Resource set rules automatically group similar assets (e.g., timestamped files) into virtual sets for cleaner catalog organization.

```bash
# Create rule
pvw account putresourcesetrule --help

# List active rules
pvw account getresourcesetrules --help
```

## Collection Hierarchy

Collections organize assets into logical containers. Each collection can have:

- Name and description
- Parent collection reference
- Access control settings
- Collection-level administrators

## Related Topics

- [Create Tasks](../task-create.md)
- [Update Tasks](../task-update.md)
- [Delete Tasks](../task-delete.md)
- [Management commands](../management/main.md)
- [Collections Permissions Guide](../../collections-permissions.md)
