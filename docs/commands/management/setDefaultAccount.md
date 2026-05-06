# pvw management setDefaultAccount
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > setDefaultAccount

## Description
Set DefaultAccount for Purview account.

## Syntax
```
pvw management setDefaultAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --scopeTenantId=<val> --scopeType=<val> --scope=<val>
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter
- `--accountName`: accountName parameter
- `--scopeTenantId`: scopeTenantId parameter
- `--scopeType`: scopeType parameter
- `--scope`: scope parameter

## Optional Arguments
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
Management Data Plane > Management > [Setdefaultaccount]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/setDefaultAccount
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