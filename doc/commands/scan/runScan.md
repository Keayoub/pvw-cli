# pvw scan runScan
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > runScan

## Description
Execute data source scan.

## Syntax
```
pvw scan runScan --dataSourceName=<val> --scanName=<val> [--scanLevel=<val>]
```

## Required Arguments
- `--dataSourceName`: dataSourceName parameter
- `--scanName`: scanName parameter
- `--scanLevel`: scanLevel parameter

## Optional Arguments
- `--scanLevel`: scanLevel parameter (optional)
- `--purviewName`: Azure Purview account name. (string)
- `--action`: Allowed values: Delete or Keep. (string)
- `--classificationRuleName`: Name of the classification rule. (string)
- `--classificationRuleVersion`: Version of the classification rule. (integer)
- `--scanRulesetName`: Name of the scan ruleset. (string)
- `--keyVaultName`: Name of the key vault. (string)
- `--runId`: The unique identifier of the run. (string)
- `--dataSourceType`: Type of data source. (string)
- `--collectionName`: The unique collection name. (string)
- `--credentialName`: The name of the credential. (string)

## API Mapping
Scanning Data Plane > Scan > [Runscan]()
```
 https://{accountName}.purview.azure.com/scan/api/runScan
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