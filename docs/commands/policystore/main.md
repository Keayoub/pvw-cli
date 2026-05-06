# Policy Store Commands

Manage data policies and metadata policies for governance and access control in Purview.

!!! tip "Quick Start"
    Manage data policies, scopes, and metadata policy definitions for controlling access and governance.

## What You Can Do

- Create and manage data policies
- Define policy scopes
- Configure metadata policies
- Manage policy roles and permissions
- Enforce data access controls

## Available Actions

### Data Policies

| Command | Purpose |
| --- | --- |
| `readdatapolicies` | List all data policies |
| `putdatapolicy` | Create or update policy |
| `deletedatapolicy` | Remove policy |
| `readdatapolicyscopes` | List policy scopes |
| `putdatapolicyscope` | Create or update scope |
| `deletedatapolicyscope` | Remove scope |

### Metadata Policies

| Command | Purpose |
| --- | --- |
| `readmetadatapolicies` | List metadata policies |
| `readmetadatapolicy` | Get specific policy |
| `putmetadatapolicy` | Create or update policy |
| `readmetadataroles` | List available roles |

## Common Workflows

### Create Data Policy

```bash
pvw policystore putdatapolicy --help
```

### Define Policy Scope

```bash
pvw policystore putdatapolicyscope --help
```

## Related Topics

- [Account commands](../account/main.md)
- [Management commands](../management/main.md)
- [Create Tasks](../task-create.md)
