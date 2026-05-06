# Which Command Should I Use?

Use this page as a routing guide before opening detailed command reference pages.

## Quick Decision Matrix

| If you want to... | Use this command family | Start here |
| --- | --- | --- |
| Search or browse the catalog | `search` | [Search commands](commands/search/main.md) |
| Read, create, update, classify, or bulk-load assets | `entity` | [Entity commands](commands/entity/main.md) |
| Manage glossaries, categories, terms, or term imports | `glossary` | [Glossary commands](commands/glossary/main.md) |
| Configure scans, credentials, triggers, filters, or scan rulesets | `scan` | [Scan commands](commands/scan/main.md) |
| Create or inspect relationships between objects | `relationship` | [Relationship commands](commands/relationship/main.md) |
| Inspect lineage graphs and asset dependencies | `lineage` | [Lineage commands](commands/lineage/main.md) |
| Manage collections and resource set rules in the account plane | `account` | [Account commands](commands/account/main.md) |
| Manage Purview accounts, private endpoints, and default account settings | `management` | [Management commands](commands/management/main.md) |
| Work with policies and scopes | `policystore` | [Policy Store commands](commands/policystore/main.md) |
| Work with sharing artifacts | `share` | [Share commands](commands/share/main.md) |
| Work with type definitions | `types` | [Types commands](commands/types/main.md) |
| Work with governance objects such as domains, terms, data products, OKRs, and CDEs | `uc` | [Unified Catalog guide](unified-catalog.md) |

## Choose By The Thing You Are Touching

- Asset, schema, label, classification, business metadata: use [entity](commands/entity/main.md)
- Glossary, term, category, assigned term: use [glossary](commands/glossary/main.md)
- Data source, credential, scan, trigger, ruleset: use [scan](commands/scan/main.md)
- Collection, resource set rule, account-level data-plane configuration: use [account](commands/account/main.md)
- Purview account resource, default account, private endpoint: use [management](commands/management/main.md)
- Relationship edge between metadata objects: use [relationship](commands/relationship/main.md)
- Governance object in the modern Unified Catalog model: use [Unified Catalog](unified-catalog.md)

## Choose By The Outcome You Need

- I need to find something first: start with [search](commands/search/main.md)
- I need to create or update many assets from files: start with [Entity Bulk CSV Guide](entity-bulk-csv-guide.md)
- I need to fix throttling or malformed CSV imports: start with [Bulk CSV Troubleshooting](bulk-csv-troubleshooting.md)
- I need step-by-step operational guidance: start with [Common Workflows](common-workflows.md)
- I need every doc page, even niche ones: use [Full Documentation Catalog](documentation-catalog.md)

## After You Pick The Family

Use the task guides when the family is clear but the verb is not.

- Create: [Create Tasks](commands/task-create.md)
- Update: [Update Tasks](commands/task-update.md)
- Delete: [Delete Tasks](commands/task-delete.md)
- Import and bulk operations: [Import Tasks](commands/task-import.md)

## High-Frequency Routes

### Find and inspect assets

```bash
pvw search query --keywords "customer"
pvw entity read --guid <entity-guid>
```

### Import or update metadata in bulk

```bash
pvw entity --help
pvw glossary createTermsImport --help
```

### Configure and run scans

```bash
pvw scan putdatasource --help
pvw scan putscan --help
pvw scan runscan --help
```

### Work in Unified Catalog

```bash
pvw uc --help
pvw uc term list
pvw uc dataproduct list
```

## If You Are Still Unsure

1. Open [Command Groups](command-groups.md) for a grouped overview.
2. Open the matching command family page.
3. Fall back to [Full Documentation Catalog](documentation-catalog.md) only if the guided routes do not answer the question.
