# pvw scan cancelScan
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > cancelScan

## Description
Cancel data source scan.

## Syntax
```
pvw scan cancelScan --dataSourceName=<val> --scanName=<val> --runId=<val>
```

## Required Arguments
- `--dataSourceName`: dataSourceName parameter
- `--scanName`: scanName parameter
- `--runId`: runId parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--action`: Allowed values: Delete or Keep. (string)
- `--classificationRuleName`: Name of the classification rule. (string)
- `--classificationRuleVersion`: Version of the classification rule. (integer)
- `--scanRulesetName`: Name of the scan ruleset. (string)
- `--keyVaultName`: Name of the key vault. (string)
- `--dataSourceType`: Type of data source. (string)
- `--scanLevel`: Allowed values: Full or Incremental [default: Full]. (string)
- `--collectionName`: The unique collection name. (string)
- `--credentialName`: The name of the credential. (string)

## API Mapping
Scanning Data Plane > Scan > [Cancelscan]()
```
 https://{accountName}.purview.azure.com/scan/api/cancelScan
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