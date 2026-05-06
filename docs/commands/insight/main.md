# Insight Commands

Run reporting and analytics on your Purview catalog to understand asset distribution, scan coverage, and metadata trends.

!!! tip "Quick Start"
    Generate insights about your catalog including asset distribution, tags, scans, and time-series analysis.

## What You Can Do

- View asset distribution by type
- Analyze scan coverage and status
- Review tag and classification statistics
- Track metrics over time with time-series data
- Identify unclassified or ungrouped assets

## Available Actions

| Command | Purpose |
| --- | --- |
| `assetdistribution` | Get asset distribution by type |
| `scanstatussummary` | Get overall scan status summary |
| `scanstatussummarybyts` | Get scan status as time-series data |
| `filesaggregation` | Get file aggregation metrics |
| `fileswithoutresourceset` | Find files not in resource sets |
| `tags` | Get tag statistics |
| `tagstimeseries` | Get tag metrics over time |

## Common Workflows

### Get Catalog Overview

```bash
pvw insight assetdistribution
```

### Monitor Scan Performance

```bash
pvw insight scanstatussummary
pvw insight scanstatussummarybyts
```

### Find Ungrouped Assets

```bash
pvw insight fileswithoutresourceset
```

## Related Topics

- [Search commands](../search/main.md)
- [Entity commands](../entity/main.md)
- [Scan commands](../scan/main.md)
