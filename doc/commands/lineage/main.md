# pvw lineage
[Command Reference](../../README.md#command-reference) > lineage

## Description
Comprehensive lineage management operations in Azure Purview with advanced CSV processing capabilities.

## Syntax
```
pvw lineage <action> [options]
```

## Available Actions

### Core Lineage Operations

#### [read](./read.md)
Retrieve lineage information for an entity with customizable depth and direction.

#### [read-next](./read-next.md) 
Retrieve next page of lineage results with pagination support.

#### [analyze](./analyze.md)
Perform advanced lineage analysis with configurable depth and direction.

#### [impact](./impact.md)
Analyze lineage impact assessment for an entity.

### CSV Lineage Operations

#### [csv process](./csv-process.md)
Process CSV file to create lineage relationships with batch processing and validation.

#### [csv generate-sample](./csv-generate-sample.md)
Generate sample CSV files with customizable templates for lineage creation.

#### [csv validate](./csv-validate.md)
Validate CSV file format and content for lineage processing.

#### [csv templates](./csv-templates.md)
Display available CSV lineage templates and their structures.

### API Direct Access Commands

For each main operation, API-direct commands are also available:
- `read-api` - Direct API access to lineage read
- `read-next-api` - Direct API access to lineage read-next
- `csv process-api` - Direct API access to CSV processing
- `csv sample-api` - Direct API access to sample generation
- `csv validate-api` - Direct API access to CSV validation
- `csv templates-api` - Direct API access to template listing

## Command Statistics

- **Total Commands**: 15
- **Main Lineage Commands**: 7
- **CSV Subgroup Commands**: 8
- **Manual Implementations**: User-friendly with rich output formatting
- **API Commands**: Direct client access with minimal processing

## Examples

```bash
# List all available lineage commands
pvw lineage --help

# List CSV subcommands
pvw lineage csv --help

# Get help for specific action
pvw lineage <action> --help

# Basic lineage read
pvw lineage read --guid "entity-guid-123"

# CSV processing with validation
pvw lineage csv process relationships.csv --validate-entities --progress

# Generate sample CSV
pvw lineage csv generate-sample sample.csv --template basic --num-samples 5
```

## See Also

- [Command Reference](../../README.md#command-reference)
- [API Documentation](../api/index.html)
