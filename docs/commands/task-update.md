# Update Tasks

Use this page to quickly find update-oriented commands.

## Quick Command Examples

Use these as starting templates.

```bash
# Bulk update entities from CSV (safe preview)
python -m purviewcli entity bulk-update-csv --csv-file .\\samples\\csv\\entity_guid_update_example.csv --dry-run

# Update glossary resources
python -m purviewcli glossary put --help
python -m purviewcli glossary put-term --help

# Update relationships
python -m purviewcli relationship put --help

# Update account settings
python -m purviewcli account update-account --help
python -m purviewcli management updateaccount --help

# Update scan configuration
python -m purviewcli scan putscanruleset --help
```

## Entity Update

- [Update entity by GUID](entity/put.md)
- [Update entity by unique attribute](entity/putUniqueAttribute.md)
- [Add or update business metadata](entity/addOrUpdateBusinessMetadata.md)
- [Add or update business attribute](entity/addOrUpdateBusinessAttribute.md)
- [Set labels](entity/setLabels.md)
- [Set labels by unique attribute](entity/setLabelsByUniqueAttribute.md)
- [Update classifications](entity/putClassifications.md)

## Glossary Update

- [Update glossary](glossary/put.md)
- [Update category](glossary/putCategory.md)
- [Partial update category](glossary/putCategoryPartial.md)
- [Update term](glossary/putTerm.md)
- [Partial update term](glossary/putTermPartial.md)

## Relationship Update

- [Update relationship](relationship/put.md)

## Management Update

- [Update account](management/updateAccount.md)
- [Set default account](management/setDefaultAccount.md)

## Scan Update

- [Update classification rule](scan/putClassificationRule.md)
- [Update credential](scan/putCredential.md)
- [Update filter](scan/putFilter.md)
- [Update key vault](scan/putKeyVault.md)
