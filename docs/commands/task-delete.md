# Delete Tasks

Use this page to quickly find delete and cleanup commands.

## Quick Command Examples

Use these as starting templates.

```bash
# Delete entity resources
python -m purviewcli entity delete --help
python -m purviewcli entity bulk-delete --help
python -m purviewcli entity bulk-delete-csv --help

# Delete glossary resources
python -m purviewcli glossary delete --help
python -m purviewcli glossary delete-term --help

# Delete relationships and shares
python -m purviewcli relationship delete --help
python -m purviewcli share delete-asset --help

# Delete scan resources
python -m purviewcli scan deletescan --help
python -m purviewcli scan deletedatasource --help
```

## Entity Delete

- [Delete entity](entity/delete.md)
- [Delete entities in bulk](entity/deleteBulk.md)
- [Delete classification](entity/deleteClassification.md)
- [Delete labels](entity/deleteLabels.md)
- [Delete business metadata](entity/deleteBusinessMetadata.md)

## Glossary Delete

- [Delete glossary](glossary/delete.md)
- [Delete category](glossary/deleteCategory.md)
- [Delete term](glossary/deleteTerm.md)

## Relationship Delete

- [Delete relationship](relationship/delete.md)

## Share Delete

- [Delete asset](share/deleteAsset.md)
- [Delete asset mapping](share/deleteAssetMapping.md)
- [Delete received share](share/deleteReceivedShare.md)
- [Delete sent invitation](share/deleteSentInvitation.md)

## Account and Management Delete

- [Delete collection](account/deleteCollection.md)
- [Delete resource set rule](account/deleteResourceSetRule.md)
- [Delete account](management/deleteAccount.md)
- [Delete private endpoint](management/deletePrivateEndpoint.md)

## Scan Delete

- [Delete data source](scan/deleteDataSource.md)
- [Delete scan](scan/deleteScan.md)
- [Delete scan ruleset](scan/deleteScanRuleset.md)
- [Delete trigger](scan/deleteTrigger.md)
