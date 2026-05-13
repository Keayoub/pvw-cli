# Command Groups

Use this page when you already know the kind of object or operation you are looking for, but not the exact command name.

!!! tip
    If your question starts with "How do I...", begin with [Which Command Should I Use?](which-command-should-i-use.md).
    If it starts with "Where is the reference for...", begin here.

## Core Catalog Operations

| Command group | Use it for | Entry page |
| --- | --- | --- |
| `entity` | Create, read, update, delete, classify, label, and bulk-process catalog entities | [Entity commands](commands/entity/main.md) |
| `glossary` | Manage glossaries, categories, terms, imports, exports, and assigned entities | [Glossary commands](commands/glossary/main.md) |
| `relationship` | Create and inspect links between assets and metadata objects | [Relationship commands](commands/relationship/main.md) |
| `search` | Query the catalog, browse, autocomplete, and discover assets quickly | [Search commands](commands/search/main.md) |

## Scanning And Operational Setup

| Command group | Use it for | Entry page |
| --- | --- | --- |
| `scan` | Define data sources, credentials, scan rulesets, filters, triggers, and run scans | [Scan commands](commands/scan/main.md) |
| `account` | Work with data-plane settings such as collections and resource set rules | [Account commands](commands/account/main.md) |
| `management` | Manage control-plane resources such as Purview accounts, keys, private endpoints, and defaults | [Management commands](commands/management/main.md) |
| `policystore` | Manage data policies, scopes, and metadata policy definitions | [Policy Store commands](commands/policystore/main.md) |

## Analysis, Discovery, And Sharing

| Command group | Use it for | Entry page |
| --- | --- | --- |
| `lineage` | Inspect upstream and downstream relationships for assets and data movement | [Lineage commands](commands/lineage/main.md) |
| `insight` | Run reporting and insight commands for distribution, tags, scans, and time-series views | [Insight commands](commands/insight/main.md) |
| `share` | Work with data sharing artifacts and workflows | [Share commands](commands/share/main.md) |
| `types` | Inspect and manage type definitions and schema metadata | [Types commands](commands/types/main.md) |

## Modern Governance And Unified Catalog

| Entry point | Use it for |
| --- | --- |
| [Unified Catalog guide](unified-catalog.md) | Start here for domains, terms, data products, OKRs, CDEs, and governance workflows |
| [Unified Catalog commands](commands/unified-catalog.md) | Jump directly into the UC command reference when you already know the area |
| [Purview MCP Server](purview-mcp-server.md) | Run MCP tools for AI-driven Purview operations and workflow automation |
| [Quick reference](quick-reference.md) | Use compact examples when you need command syntax without reading full guides |
| [Samples catalog](samples-catalog.md) | Browse JSON, CSV, PowerShell, and notebook samples by use case |

## Choose By Outcome

| If you want to... | Start with | Why |
| --- | --- | --- |
| Find assets or metadata quickly | [search](commands/search/main.md) | Lowest-friction discovery path |
| Bulk ingest or update assets | [entity](commands/entity/main.md) and [Entity Bulk CSV Guide](entity-bulk-csv-guide.md) | Best documentation for throughput and retries |
| Manage glossary terms and categories | [glossary](commands/glossary/main.md) | Terms, categories, imports, exports |
| Configure scans and data sources | [scan](commands/scan/main.md) | Complete scan lifecycle |
| Work with collections or resource set rules | [account](commands/account/main.md) | Data-plane account operations |
| Create or manage Purview accounts | [management](commands/management/main.md) | Control-plane account operations |
| Work with governance objects in Unified Catalog | [Unified Catalog](unified-catalog.md) | Better entry point than raw command reference |

## Recommended Navigation Pattern

1. Use [Which Command Should I Use?](which-command-should-i-use.md) to choose the command family.
2. Open the matching group page from this page.
3. If the operation is create, update, delete, or import-heavy, jump to the matching task guide.
4. If you are still unsure, use [Full Documentation Catalog](documentation-catalog.md) only as the exhaustive fallback.
