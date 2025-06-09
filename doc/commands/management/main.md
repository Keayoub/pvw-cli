# pvw management
[Command Reference](../../README.md#command-reference) > management

## Description
Commands for managing metastore operations in Azure Purview.

## Syntax
```
pvw management <action> [options]
```

## Available Actions

### [addrootcollectionadmin](./addrootcollectionadmin.md)
Add RootCollectionAdmin for Purview account.

### [checknameavailability](./checknameavailability.md)
Check Purview account.

### [createaccount](./createaccount.md)
Create a new Purview account.

### [defaultaccount](./defaultaccount.md)
Perform operation on Purview account.

### [deleteaccount](./deleteaccount.md)
Delete Purview account.

### [deleteprivateendpoint](./deleteprivateendpoint.md)
Delete Purview account.

### [listkeys](./listkeys.md)
List all Purview accounts.

### [listoperations](./listoperations.md)
List all Purview accounts.

### [listprivatelinkresources](./listprivatelinkresources.md)
List all Purview accounts.

### [putprivateendpoint](./putprivateendpoint.md)
Create or update Purview account.

### [readaccount](./readaccount.md)
Retrieve Purview account.

### [readaccounts](./readaccounts.md)
Retrieve Purview account.

### [readprivateendpoint](./readprivateendpoint.md)
Retrieve Purview account.

### [readprivateendpoints](./readprivateendpoints.md)
Retrieve Purview account.

### [removedefaultaccount](./removedefaultaccount.md)
Remove DefaultAccount for Purview account.

### [setdefaultaccount](./setdefaultaccount.md)
Set DefaultAccount for Purview account.

### [updateaccount](./updateaccount.md)
Update an existing Purview account.

## Examples

```bash
# List available actions
pvw management --help

# Get help for specific action
pvw management <action> --help
```

## See Also

- [Command Reference](../../README.md#command-reference)
- [API Documentation](../api/index.html)
