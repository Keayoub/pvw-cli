# Delete Tasks

Use this page to quickly find delete and cleanup commands.

## Quick Command Examples

Use these as starting templates.

```bash
# Delete entity resources
pvw entity delete --help
pvw entity bulk-delete --help
pvw entity bulk-delete-csv --help

# Delete glossary resources
pvw glossary delete --help
pvw glossary delete-term --help

# Delete relationships and shares
pvw relationship delete --help
pvw share delete-asset --help

# Delete scan resources
pvw scan deletescan --help
pvw scan deletedatasource --help

# Cleanup expired business metadata definitions
pvw uc metadata cleanup --name "SecteursActivite" --check-only --verbose
pvw uc metadata cleanup --name "SecteursActivite" --verbose
pvw uc metadata delete-definition --name "Glossaire" --dry-run
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

## Unified Catalog Metadata Cleanup

- `pvw uc metadata cleanup --name <definition-or-attribute-name> --check-only --verbose`
- `pvw uc metadata cleanup --name <definition-or-attribute-name> --verbose`
- `pvw uc metadata delete-definition --name <definition-name> --dry-run`
- `pvw uc metadata delete --asset-id <guid> --group <definition-name>`

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
