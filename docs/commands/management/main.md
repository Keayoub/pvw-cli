# Management Commands

Manage Purview accounts and control-plane resources including account creation, private endpoints, and default account settings.

!!! tip "Quick Start"
    Manage control-plane resources such as Purview accounts, access keys, private endpoints, and default account settings.

## What You Can Do

- Create and manage Purview accounts
- Manage access keys and authentication
- Set up and manage private link endpoints
- Configure default account for CLI operations
- Add root collection administrators
- Verify account name availability

## Quick Examples

=== "List accounts"
    ```bash
    pvw management readaccounts
    ```

=== "Create account"
    ```bash
    pvw management createaccount --help
    ```

=== "Set default account"
    ```bash
    pvw management setdefaultaccount --help
    ```

=== "List private endpoints"
    ```bash
    pvw management readprivateendpoints
    ```

## Available Actions

### Account Management

| Command | Purpose |
| --- | --- |
| `readaccounts` | List all Purview accounts in subscription |
| `readaccount` | Get specific account details |
| `createaccount` | Create new Purview account |
| `updateaccount` | Update account configuration |
| `deleteaccount` | Delete account |
| `checknameavailability` | Verify account name is available |

### Default Account

| Command | Purpose |
| --- | --- |
| `setdefaultaccount` | Set default account for CLI |
| `defaultaccount` | Get current default account |
| `removedefaultaccount` | Clear default account |

### Access & Security

| Command | Purpose |
| --- | --- |
| `listkeys` | Get account access keys |
| `addrootcollectionadmin` | Add root collection administrator |

### Private Link

| Command | Purpose |
| --- | --- |
| `readprivateendpoints` | List private endpoints |
| `readprivateendpoint` | Get endpoint details |
| `putprivateendpoint` | Create or update endpoint |
| `deleteprivateendpoint` | Remove endpoint |
| `listprivatelinkresources` | List private link resources |

### Operations

| Command | Purpose |
| --- | --- |
| `listoperations` | List available operations |

## Common Workflows

### Set Up Default Account

```bash
# Get available accounts
pvw management readaccounts

# Set default
pvw management setdefaultaccount --help
```

### Configure Private Endpoints

For secure, private connectivity to Purview:

```bash
# Get available resources
pvw management listprivatelinkresources --help

# Create private endpoint
pvw management putprivateendpoint --help
```

## Related Topics

- [Account commands](../account/main.md)
- [Create Tasks](../task-create.md)
- [Update Tasks](../task-update.md)
