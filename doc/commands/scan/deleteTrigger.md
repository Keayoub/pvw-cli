# pvw scan deleteTrigger
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > deleteTrigger

## Description
Deletes the trigger associated with the scan

## Syntax
```
pvw scan deleteTrigger --dataSourceName=<val> --scanName=<val>
```

## Required Arguments
`--dataSourceName` (string)  
The data source name.

`--scanName` (string)  
The scan name.

## Optional Arguments
*None*

## API Mapping
Scanning Data Plane > Triggers > [Delete Trigger](https://docs.microsoft.com/en-us/rest/api/purview/scanningdataplane/triggers/delete-trigger)
```
DELETE https://{accountName}.purview.azure.com/scan/datasources/{dataSourceName}/scans/{scanName}/triggers/default
```

## Examples
Delete a scan trigger by data source name and scan name.
```powershell
pvw scan deleteTrigger --dataSourceName "AzureDataLakeStorage-EqK" --scanName "Scan-xTh"
```
