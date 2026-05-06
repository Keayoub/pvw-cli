# pvw management addRootCollectionAdmin
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > addRootCollectionAdmin

## Description
Add RootCollectionAdmin for Purview account.

## Syntax
```
pvw management addRootCollectionAdmin --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --objectId=<val>
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter
- `--accountName`: accountName parameter
- `--objectId`: objectId parameter

## Optional Arguments
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)

## API Mapping
Management Data Plane > Management > [Addrootcollectionadmin]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/addRootCollectionAdmin
```

## Examples
DESCRIBE_EXAMPLE.
```powershell
EXAMPLE_COMMAND
```
<details><summary>Example payload.</summary>
<p>

```json
PASTE_JSON_HERE
```
</p>
</details>