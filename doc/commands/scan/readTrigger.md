# pvw scan readTrigger
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > readTrigger

## Description
Readtrigger operation for scan

## Syntax
```
pvw scan readTrigger --dataSourceName=<val> --scanName=<val>
```

## Required Arguments
- `--dataSourceName`: dataSourceName parameter
- `--scanName`: scanName parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--action`: Allowed values: Delete or Keep. (string)
- `--classificationRuleName`: Name of the classification rule. (string)
- `--classificationRuleVersion`: Version of the classification rule. (integer)
- `--scanRulesetName`: Name of the scan ruleset. (string)
- `--keyVaultName`: Name of the key vault. (string)
- `--runId`: The unique identifier of the run. (string)
- `--dataSourceType`: Type of data source. (string)
- `--scanLevel`: Allowed values: Full or Incremental [default: Full]. (string)
- `--collectionName`: The unique collection name. (string)
- `--credentialName`: The name of the credential. (string)

## API Mapping
 >  > []()
```
GET /api/scan/readTrigger
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