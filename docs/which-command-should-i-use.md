# Which Command Should I Use?

Use this quick decision guide to choose the right command family.

## Decision Tree

1. Are you working with assets/entities in the catalog?
- Yes: Use `entity` commands.
- No: Go to step 2.

2. Are you managing business terms, categories, or glossaries?
- Yes: Use `glossary` commands.
- No: Go to step 3.

3. Are you configuring scans, data sources, or scan rulesets?
- Yes: Use `scan` commands.
- No: Go to step 4.

4. Are you managing relationships between entities?
- Yes: Use `relationship` commands.
- No: Go to step 5.

5. Are you handling data sharing artifacts?
- Yes: Use `share` commands.
- No: Go to step 6.

6. Are you changing account-level settings?
- Account data-plane settings and collections: use `account`.
- Account control-plane operations: use `management`.

## Operation Type

After choosing the command family, pick the task page:

- Create: [Create Tasks](commands/task-create.md)
- Update: [Update Tasks](commands/task-update.md)
- Delete: [Delete Tasks](commands/task-delete.md)
- Import/Bulk: [Import Tasks](commands/task-import.md)

## High-Frequency Examples

```bash
# Entity bulk create/update from CSV
python -m purviewcli entity bulk-create-csv --help
python -m purviewcli entity bulk-update-csv --help

# Glossary imports
python -m purviewcli glossary import-terms --help

# Scan setup and run
python -m purviewcli scan putdatasource --help
python -m purviewcli scan putscan --help
python -m purviewcli scan runscan --help
```

## Practical Routing

- For large CSV ingestion: start at [Entity Bulk CSV Guide](entity-bulk-csv-guide.md)
- For retries/throttling/schema issues: use [Bulk CSV Troubleshooting](bulk-csv-troubleshooting.md)
- For full exhaustive reference: use [Full Documentation Catalog](documentation-catalog.md)
