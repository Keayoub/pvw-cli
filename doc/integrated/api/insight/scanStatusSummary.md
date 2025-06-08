# pvw insight scanStatusSummary
[Command Reference](../../../README.md#command-reference) > [insight](./main.md) > scanStatusSummary

## Description
Total number of scans by status.

## Syntax
```
pvw insight scanStatusSummary [--numberOfDays=<val>]
```

## Required Arguments
*None*

## Optional Arguments
`--numberOfDays` (integer)  
Trailing time period in days [default: 30].

## API Mapping
```
GET https://{accountName}.purview.azure.com/mapanddiscover/reports/scanstatus2/summaries
```

## Examples
Get the total number of scans by status.
```powershell
pvw insight scanStatusSummary
```
<details><summary>Sample response.</summary>
<p>

```json
{
    "values": [
        {
            "count": 33,
            "type": "Succeeded"
        },
        {
            "count": 9,
            "type": "Failed"
        }
    ]
}
```
</p>
</details>
