# pvw management createAccount
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > createAccount

## Description
Create a new Purview account.

## Syntax
```
pvw management createAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --payloadFile=<val>
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter
- `--accountName`: accountName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
Management Data Plane > Management > [Createaccount]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/createAccount
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