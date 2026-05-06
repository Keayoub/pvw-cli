# Search Commands

Query and explore the Purview catalog with powerful search, browse, autocomplete, and suggestion capabilities.

!!! tip "Quick Start"
    Find, browse, and discover assets in your catalog using keyword search, facets, and intelligent suggestions.

## What You Can Do

- Search assets by keyword, type, or classification
- Browse the catalog by entity type
- Get autocomplete suggestions
- Discover related assets
- Filter by facets (type, status, owner, etc.)

## Quick Examples

=== "Search by keyword"
    ```bash
    pvw search query --keywords "customer"
    ```

=== "Browse by entity type"
    ```bash
    pvw search browse --help
    ```

=== "Get suggestions"
    ```bash
    pvw search suggest --help
    ```

=== "Autocomplete"
    ```bash
    pvw search autocomplete --help
    ```

## Available Actions

| Command | Purpose |
| --- | --- |
| `query` | Search catalog by keywords, filters, and facets |
| `browse` | Browse assets by entity type |
| `autocomplete` | Get autocomplete suggestions while typing |
| `suggest` | Get suggestions for search terms |

## Search Capabilities

### Keyword Search

Find assets by name, description, or content:

```bash
pvw search query --keywords "customer data"
```

### Faceted Search

Filter by classifications, owner, entity type, and more.

### Browse

Explore catalog structure by entity type without keyword search.

## Common Workflows

### Find Assets To Classify

```bash
pvw search query --keywords "unclassified"
```

### Discover Related Assets

```bash
pvw search browse --help
```

### Build Search Queries

Use autocomplete to discover available search terms and facets.

## Related Topics

- [Entity commands](../entity/main.md)
- [Common Workflows](../../common-workflows.md)
- [Entity Bulk CSV Guide](../../entity-bulk-csv-guide.md)
