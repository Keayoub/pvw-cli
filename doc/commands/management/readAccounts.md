# pvw management readAccounts
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > readAccounts

## Description
Readaccounts operation for management

## Syntax
```
pvw management readAccounts --subscriptionId=<val> [--resourceGroupName=<val>]
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter

## Optional Arguments
- `--resourceGroupName`: resourceGroupName parameter (optional)
- `--accountName`: The name of the account. (string)
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
 >  > []()
```
GET /api/management/readAccounts
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