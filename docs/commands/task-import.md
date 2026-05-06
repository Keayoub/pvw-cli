# Import Tasks

Use this page for import, bulk ingest, and CSV/JSON-driven operations.

## Quick Command Examples

Use these as starting templates.

```bash
# Import and bulk entity operations
python -m purviewcli entity import-business-metadata --help
python -m purviewcli entity bulk-create --help
python -m purviewcli entity bulk-read --help

# Import glossary terms
python -m purviewcli glossary import-terms --help

# CSV workflow references
python -m purviewcli entity bulk-create-csv --help
python -m purviewcli entity bulk-update-csv --help
```

## Entity Import and Bulk

- [Bulk create entities](entity/createBulk.md)
- [Bulk read entities](entity/readBulk.md)
- [Bulk read by unique attributes](entity/readBulkUniqueAttribute.md)
- [Import business metadata](entity/importBusinessMetadata.md)

## Glossary Import and Export

- [Import terms](glossary/createTermsImport.md)
- [Read term import format](glossary/readTermsImport.md)
- [Export terms](glossary/createTermsExport.md)

## Bulk CSV Practical Guide

- [Entity Bulk CSV Guide](../entity-bulk-csv-guide.md)
- [Bulk CSV Troubleshooting](../bulk-csv-troubleshooting.md)

## Sample Inputs

- [Full Samples Catalog](../samples-catalog.md)
