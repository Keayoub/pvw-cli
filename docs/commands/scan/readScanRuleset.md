# pvw scan readScanRuleset
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > readScanRuleset

## Description
Retrieve data source scan.

## Syntax
```
pvw scan readScanRuleset --scanRulesetName=<val>
```

## Required Arguments
- `--scanRulesetName`: scanRulesetName parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--action`: Allowed values: Delete or Keep. (string)
- `--classificationRuleName`: Name of the classification rule. (string)
- `--classificationRuleVersion`: Version of the classification rule. (integer)
- `--dataSourceName`: Name of the data source. (string)
- `--scanName`: Name of the scan. (string)
- `--keyVaultName`: Name of the key vault. (string)
- `--runId`: The unique identifier of the run. (string)
- `--dataSourceType`: Type of data source. (string)
- `--scanLevel`: Allowed values: Full or Incremental [default: Full]. (string)
- `--collectionName`: The unique collection name. (string)
- `--credentialName`: The name of the credential. (string)

## API Mapping
Scanning Data Plane > Scan > [Readscanruleset]()
```
 https://{accountName}.purview.azure.com/scan/api/readScanRuleset
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