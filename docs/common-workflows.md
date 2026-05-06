# Common Workflows

Use this page when you know the outcome you want, but do not want to browse the full command catalog.

## Start With The Workflow, Not The Command

- __First successful command__

  Install the CLI, authenticate with Azure, and verify your environment.

  [Open guide](getting-started.md)

- __Route to the right family__

  Choose between entity, glossary, scan, account, management, and Unified Catalog.

  [Open guide](which-command-should-i-use.md)

- __Bulk CSV ingestion__

  High-volume entity create and update with the right operating profile.

  [Open guide](entity-bulk-csv-guide.md)

- __Retry and repair failures__

  Fix throttling, schema errors, and malformed input files.

  [Open guide](bulk-csv-troubleshooting.md)
{: .grid .cards }

## Workflow 1: Find An Asset And Read Its Metadata

Use this when you know a keyword, qualified name fragment, or general subject area.

```bash
pvw search query --keywords "customer"
pvw entity read --guid <entity-guid>
```

Go deeper with:

- [Search commands](commands/search/main.md)
- [Entity commands](commands/entity/main.md)

## Workflow 2: Create Or Update Assets In Bulk

Use this when your source of truth is CSV or structured metadata exports.

```bash
pvw entity --help
```

Then continue with:

- [Entity Bulk CSV Guide](entity-bulk-csv-guide.md)
- [Import Tasks](commands/task-import.md)
- [Bulk CSV Troubleshooting](bulk-csv-troubleshooting.md)

## Workflow 3: Manage Glossary Terms And Categories

Use this when you are building business vocabulary, assigning terms, or importing term sets.

```bash
pvw glossary readTerms
pvw glossary createTerm --help
pvw glossary createTermsImport --help
```

Go deeper with:

- [Glossary commands](commands/glossary/main.md)
- [Create Tasks](commands/task-create.md)
- [Update Tasks](commands/task-update.md)

## Workflow 4: Configure Scans And Run Them

Use this when onboarding a source, updating credentials, changing rulesets, or triggering scans.

```bash
pvw scan putdatasource --help
pvw scan putscan --help
pvw scan runscan --help
```

Go deeper with:

- [Scan commands](commands/scan/main.md)
- [Authentication Troubleshooting](authentication-troubleshooting.md)

## Workflow 5: Manage Collections Or Purview Account Settings

Use this split when you are unsure whether the task is `account` or `management`.

- Use [account](commands/account/main.md) for collections, collection paths, and resource set rules.
- Use [management](commands/management/main.md) for Purview account resources, private endpoints, keys, and default account settings.

## Workflow 6: Work In Unified Catalog

Use this when your task is centered on domains, terms, data products, objectives, key results, CDEs, or quality reporting.

```bash
pvw uc --help
pvw uc term list
pvw uc domain list
pvw uc dataproduct list
```

Go deeper with:

- [Unified Catalog guide](unified-catalog.md)
- [Quick reference](quick-reference.md)
- [Unified Catalog commands](commands/unified-catalog.md)

## Pick The Right Task Guide

- Create resources and entities: [Create Tasks](commands/task-create.md)
- Update resources and metadata: [Update Tasks](commands/task-update.md)
- Delete resources and cleanup: [Delete Tasks](commands/task-delete.md)
- Import and bulk ingest: [Import Tasks](commands/task-import.md)

## Bulk CSV Operating Profiles

- Fast: highest throughput when the tenant is stable and throttling is low
- Balanced: default choice for most environments
- Safe: lowest risk when throttling, large payloads, or service sensitivity are concerns

For exact flags, command examples, and tuning guidance, use [Entity Bulk CSV Guide](entity-bulk-csv-guide.md).
