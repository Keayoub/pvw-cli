# pvw management defaultAccount
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > defaultAccount

## Description
Perform operation on Purview account.

## Syntax
```
pvw management defaultAccount --scopeTenantId=<val> --scopeType=<val> --scope=<val>
```

## Required Arguments
- `--scopeTenantId`: scopeTenantId parameter
- `--scopeType`: scopeType parameter
- `--scope`: scope parameter

## Optional Arguments
- `--subscriptionId`: The subscription ID. (string)
- `--resourceGroupName`: The name of the resource group. (string)
- `--accountName`: The name of the account. (string)
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
Management Data Plane > Management > [Defaultaccount]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/defaultAccount
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