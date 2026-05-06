# Create Tasks

Use this page to quickly find create-oriented commands.

## Quick Command Examples

Use these as starting templates.

```bash
# Bulk create entities from CSV (safe preview)
python -m purviewcli entity bulk-create-csv --csv-file .\\samples\\csv\\entities.csv --dry-run

# Create glossary resources
python -m purviewcli glossary create --help
python -m purviewcli glossary create-term --help

# Create relationship
python -m purviewcli relationship create --help

# Create share assets
python -m purviewcli share create-asset --help

# Create scan resources
python -m purviewcli scan putdatasource --help
python -m purviewcli scan putscan --help
```

## Entity Create

- [Create single entity](entity/create.md)
- [Create bulk entities](entity/createBulk.md)
- [Create bulk classifications](entity/createBulkClassification.md)
- [Create or update collection assignment](entity/createOrUpdateCollection.md)
- [Create or update collection assignment in bulk](entity/createOrUpdateCollectionBulk.md)

## Glossary Create

- [Create glossary](glossary/create.md)
- [Create category](glossary/createCategory.md)
- [Create categories](glossary/createCategories.md)
- [Create term](glossary/createTerm.md)
- [Create terms](glossary/createTerms.md)

## Relationship Create

- [Create relationship](relationship/create.md)

## Share Create

- [Create asset](share/createAsset.md)
- [Create asset mapping](share/createAssetMapping.md)
- [Create received share](share/createReceivedShare.md)
- [Create sent invitation](share/createSentInvitation.md)
- [Create sent share](share/createSentShare.md)

## Management Create

- [Create account](management/createAccount.md)

## Scan Create/Configure

- [Create or update data source](scan/putDataSource.md)
- [Create or update scan](scan/putScan.md)
- [Create or update scan ruleset](scan/putScanRuleset.md)
- [Create or update trigger](scan/putTrigger.md)
