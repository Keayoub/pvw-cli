# Purview CLI Documentation

Purview CLI docs rebuilt around navigation, not file listings.

Start from what you need to do: install the CLI, choose the correct command family, follow a common workflow, or jump straight into the full reference.

[Get started](getting-started.md){ .md-button .md-button--primary }
[Find a command](which-command-should-i-use.md){ .md-button }
[Browse command groups](command-groups.md){ .md-button }

## Start With Your Goal

- __Install and authenticate__

  Set up `pvw-cli`, sign in with Azure, and verify your first commands.

  [Open guide](getting-started.md)

- __Choose a command family__

  Map your task to the correct top-level group before reading detailed command docs.

  [Open guide](which-command-should-i-use.md)

- __Follow common workflows__

  Use task-oriented paths for search, glossary work, scans, collections, and bulk ingestion.

  [Open guide](common-workflows.md)

- __Run bulk CSV operations__

  Use the guided path for high-volume entity create and update operations.

  [Open guide](entity-bulk-csv-guide.md)

- __Work with Unified Catalog__

  Navigate domains, data products, terms, OKRs, CDEs, and quality reporting.

  [Open guide](unified-catalog.md)

- __Open the full reference__

  Browse every documentation page only when you need exhaustive coverage.

  [Open guide](documentation-catalog.md)
{: .grid .cards }

## Command Families At A Glance

| If you need to... | Use | Start here |
| --- | --- | --- |
| Query or browse the catalog | [search](commands/search/main.md) | [Search commands](commands/search/main.md) |
| Manage assets and metadata | [entity](commands/entity/main.md) | [Entity commands](commands/entity/main.md) |
| Manage glossaries, terms, and categories | [glossary](commands/glossary/main.md) | [Glossary commands](commands/glossary/main.md) |
| Configure scans, credentials, and rulesets | [scan](commands/scan/main.md) | [Scan commands](commands/scan/main.md) |
| Manage collections and resource set rules | [account](commands/account/main.md) | [Account commands](commands/account/main.md) |
| Manage Purview accounts and control-plane settings | [management](commands/management/main.md) | [Management commands](commands/management/main.md) |
| Inspect links between assets | [relationship](commands/relationship/main.md) and [lineage](commands/lineage/main.md) | [Command groups](command-groups.md) |
| Work with modern governance objects | [Unified Catalog](unified-catalog.md) | [Unified Catalog guide](unified-catalog.md) |

## Fast Paths

1. New user: [Getting Started](getting-started.md)
2. Not sure where to begin: [Which Command Should I Use?](which-command-should-i-use.md)
3. Need task-oriented guidance: [Common Workflows](common-workflows.md)
4. Need exhaustive command coverage: [Full Documentation Catalog](documentation-catalog.md)
5. Need examples and sample inputs: [Full Samples Catalog](samples-catalog.md)

## Five-Minute Start

```bash
pip install pvw-cli
az login
pvw --help
pvw search query --keywords "customer"
pvw glossary readTerms
```

## Use The Catalogs Last

The documentation and samples catalogs are still available, but they work best as exhaustive indexes after you already know the area you want. For faster navigation, start with [Which Command Should I Use?](which-command-should-i-use.md) or [Command Groups](command-groups.md).
