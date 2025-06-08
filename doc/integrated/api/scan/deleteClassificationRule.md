# pvw scan deleteClassificationRule
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > deleteClassificationRule

## Description
Deletes a classification rule

## Syntax
```
pvw scan deleteClassificationRule --classificationRuleName=<val>
```

## Required Arguments
`--classificationRuleName` (string)  
The name of the classification rule.

## Optional Arguments
*None*

## API Mapping
Scanning Data Plane > Classification Rules > [Delete](https://docs.microsoft.com/en-us/rest/api/purview/scanningdataplane/classification-rules/delete)
```
DELETE https://{accountName}.purview.azure.com/scan/classificationrules/{classificationRuleName}
```

## Examples
Delete a classification rule by name.
```powershell
pvw scan deleteClassificationRule --classificationRuleName "twitter_handle"
```
