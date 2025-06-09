"""
Comprehensive Lineage CLI with Advanced CSV Processing and API Integration

This module provides comprehensive lineage management capabilities including:
- Direct lineage read operations with pagination support
- Advanced lineage analysis and impact assessment  
- Full CSV batch processing pipeline with validation
- Template generation and management
- Both manual and auto-generated API command access

Available Commands (15 total):
    # Main lineage operations (7 commands):
    pvw lineage read --guid=<val> [--depth=<val> --width=<val> --direction=<val> --output=<val>]
    pvw lineage read-next --guid=<val> [--direction=<val> --offset=<val> --limit=<val> --output=<val>]  
    pvw lineage read-api --guid=<val> [--depth=<val> --width=<val> --direction=<val>]
    pvw lineage read-next-api --guid=<val> [--direction=<val> --offset=<val> --limit=<val>]
    pvw lineage analyze --entity-guid=<val> [--direction=<val> --depth=<val> --output-file=<val>]
    pvw lineage impact --entity-guid=<val> [--output-file=<val>]
    
    # CSV lineage operations (8 subcommands):
    pvw lineage csv process <csv_file> [--batch-size=<val> --validate-entities --create-missing-entities --progress]
    pvw lineage csv process-api <csv_file> [--batch-size=<val>]
    pvw lineage csv generate-sample <output_file> [--num-samples=<val> --template=<val>]
    pvw lineage csv sample-api [--num-samples=<val>]
    pvw lineage csv validate <csv_file>
    pvw lineage csv validate-api <csv_file>
    pvw lineage csv templates
    pvw lineage csv templates-api

options:
    --purviewName=<val>               [string]  Azure Purview account name.
    --depth=<depth>                   [integer] The number of hops for lineage [default: 3].
    --direction=<direction>           [string]  The direction of the lineage, which could be INPUT, OUTPUT or BOTH [default: BOTH].
    --guid=<val>                      [string]  The globally unique identifier of the entity.
    --entity-guid=<val>               [string]  Entity GUID for advanced lineage operations.
    --limit=<val>                     [integer] The page size - by default there is no paging [default: -1].
    --offset=<val>                    [integer] Offset for pagination purpose [default: 0].
    --width=<width>                   [integer] The number of max expanding width in lineage [default: 6].
    --output=<val>                    [string]  Output format: json, table [default: json].
    --output-file=<val>               [string]  Export results to file.
    --batch-size=<val>                [integer] Number of lineage relationships to process in each batch [default: 100].
    --validate-entities               [flag]    Validate that source and target entities exist before creating lineage.
    --create-missing-entities         [flag]    Create placeholder entities if they don't exist.
    --progress                        [flag]    Show progress during processing.
    --num-samples=<val>               [integer] Number of sample rows to generate [default: 10].
    --template=<val>                  [string]  Template type: basic, etl, column-mapping [default: basic].

"""

from docopt import docopt

def main():
    """Main entry point for lineage commands using docopt"""
    arguments = docopt(__doc__)
    
    # Note: Actual implementation is handled by the Click-based CLI in cli.py
    # This file only defines the docopt interface for documentation purposes
    print("Lineage commands are handled by the main CLI. Use 'pvw lineage --help' for available commands.")

if __name__ == '__main__':
    main()
