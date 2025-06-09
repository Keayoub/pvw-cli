# pvw scan putDataSource
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > putDataSource

## Description
Create or update data source scan.

## Syntax
```
pvw scan putDataSource --dataSourceName=<val> --payloadFile=<val>
```

## Required Arguments
- `--dataSourceName`: dataSourceName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--action`: Allowed values: Delete or Keep. (string)
- `--classificationRuleName`: Name of the classification rule. (string)
- `--classificationRuleVersion`: Version of the classification rule. (integer)
- `--scanName`: Name of the scan. (string)
- `--scanRulesetName`: Name of the scan ruleset. (string)
- `--keyVaultName`: Name of the key vault. (string)
- `--runId`: The unique identifier of the run. (string)
- `--dataSourceType`: Type of data source. (string)
- `--scanLevel`: Allowed values: Full or Incremental [default: Full]. (string)
- `--collectionName`: The unique collection name. (string)
- `--credentialName`: The name of the credential. (string)

## API Mapping
Scanning Data Plane > Scan > [Putdatasource]()
```
 https://{accountName}.purview.azure.com/scan/api/putDataSource
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