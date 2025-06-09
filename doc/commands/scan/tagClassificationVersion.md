# pvw scan tagClassificationVersion
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > tagClassificationVersion

## Description
Perform operation on data source scan.

## Syntax
```
pvw scan tagClassificationVersion --classificationRuleName=<val> --classificationRuleVersion=<val> --action=<val>
```

## Required Arguments
- `--classificationRuleName`: classificationRuleName parameter
- `--classificationRuleVersion`: classificationRuleVersion parameter
- `--action`: action parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--dataSourceName`: Name of the data source. (string)
- `--scanName`: Name of the scan. (string)
- `--scanRulesetName`: Name of the scan ruleset. (string)
- `--keyVaultName`: Name of the key vault. (string)
- `--runId`: The unique identifier of the run. (string)
- `--dataSourceType`: Type of data source. (string)
- `--scanLevel`: Allowed values: Full or Incremental [default: Full]. (string)
- `--collectionName`: The unique collection name. (string)
- `--credentialName`: The name of the credential. (string)

## API Mapping
Scanning Data Plane > Scan > [Tagclassificationversion]()
```
 https://{accountName}.purview.azure.com/scan/api/tagClassificationVersion
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