# pvw management listKeys
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > listKeys

## Description
List all Purview accounts.

## Syntax
```
pvw management listKeys --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val>
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter
- `--accountName`: accountName parameter

## Optional Arguments
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
Management Data Plane > Management > [Listkeys]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/listKeys
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