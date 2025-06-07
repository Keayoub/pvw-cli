"""
Enhanced Lineage CLI with CSV Batch Processing

usage: 
    pv lineage read --guid=<val> [--depth=<val> --width=<val> --direction=<val>]
    pv lineage readNext --guid=<val> [--direction<val> --offset=<val> --limit=<val>]
    pv lineage csv process <csv_file> [--batch-size=<val> --validate-entities --create-missing-entities --progress]
    pv lineage csv generate-sample <output_file> [--num-samples=<val> --template=<val>]
    pv lineage csv validate <csv_file>
    pv lineage csv templates

options:
    --purviewName=<val>               [string]  Azure Purview account name.
    --depth=<depth>                   [integer] The number of hops for lineage [default: 3].
    --direction=<direction>           [string]  The direction of the lineage, which could be INPUT, OUTPUT or BOTH [default: BOTH].
    --guid=<val>                      [string]  The globally unique identifier of the entity.
    --limit=<val>                     [integer] The page size - by default there is no paging [default: -1].
    --offset=<val>                    [integer] Offset for pagination purpose [default: 0].
    --width=<width>                   [integer] The number of max expanding width in lineage [default: 6].
    --batch-size=<val>                [integer] Number of lineage relationships to process in each batch [default: 100].
    --validate-entities               [flag]    Validate that source and target entities exist before creating lineage.
    --create-missing-entities         [flag]    Create placeholder entities if they don't exist.
    --progress                        [flag]    Show progress during processing.
    --num-samples=<val>               [integer] Number of sample rows to generate [default: 10].
    --template=<val>                  [string]  Template type: basic, etl, column-mapping [default: basic].

"""
import asyncio
import json
import sys
from pathlib import Path
from docopt import docopt
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import print as rprint

from ..client.csv_lineage_processor import CSVLineageProcessor, LineageCSVTemplates
from ..client.api_client import EnhancedPurviewClient
from ..client.config import config_manager

console = Console()

async def handle_csv_lineage_commands(arguments, purview_client):
    """Handle CSV lineage processing commands"""
    
    processor = CSVLineageProcessor(purview_client)
    
    if arguments.get('process'):
        await process_lineage_csv(arguments, processor)
    elif arguments.get('generate-sample'):
        generate_sample_csv(arguments, processor)
    elif arguments.get('validate'):
        validate_csv_file(arguments, processor)
    elif arguments.get('templates'):
        show_templates()

async def process_lineage_csv(arguments, processor):
    """Process lineage relationships from CSV file"""
    csv_file = arguments['<csv_file>']
    batch_size = int(arguments.get('--batch-size', 100))
    validate_entities = arguments.get('--validate-entities', False)
    create_missing_entities = arguments.get('--create-missing-entities', False)
    show_progress = arguments.get('--progress', False)
    
    if not Path(csv_file).exists():
        console.print(f"[red]Error: CSV file not found: {csv_file}[/red]")
        return
    
    console.print(f"[blue]Processing lineage from CSV file: {csv_file}[/blue]")
    console.print(f"[dim]Batch size: {batch_size}, Validate entities: {validate_entities}, Create missing: {create_missing_entities}[/dim]")
    
    # Progress tracking
    progress_data = {'current': 0, 'total': 0, 'processed': 0, 'failed': 0}
    
    def progress_callback(percent, processed, failed):
        progress_data.update({'current': percent, 'processed': processed, 'failed': failed})
        if show_progress:
            console.print(f"[green]Progress: {percent:.1f}% - Processed: {processed}, Failed: {failed}[/green]")
    
    try:
        with console.status("[bold green]Processing lineage relationships...") as status:
            result = await processor.process_lineage_csv(
                csv_file_path=csv_file,
                batch_size=batch_size,
                validate_entities=validate_entities,
                create_missing_entities=create_missing_entities,
                progress_callback=progress_callback if show_progress else None
            )
        
        # Display results
        if result.success:
            console.print("\n[bold green]✅ Lineage processing completed successfully![/bold green]")
            
            # Results table
            table = Table(title="Processing Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Relationships", str(result.total_rows))
            table.add_row("Successfully Processed", str(result.processed))
            table.add_row("Failed", str(result.failed))
            table.add_row("Success Rate", f"{result.success_rate:.1f}%")
            table.add_row("Processing Time", f"{result.processing_time:.2f} seconds")
            
            console.print(table)
            
            # Show errors if any
            if result.errors:
                console.print(f"\n[yellow]⚠️ {len(result.errors)} errors encountered:[/yellow]")
                for i, error in enumerate(result.errors[:10], 1):  # Show first 10 errors
                    console.print(f"   {i}. {error}")
                if len(result.errors) > 10:
                    console.print(f"   ... and {len(result.errors) - 10} more errors")
        else:
            console.print("[bold red]❌ Lineage processing failed![/bold red]")
            for error in result.errors:
                console.print(f"[red]Error: {error}[/red]")
                
    except Exception as e:
        console.print(f"[red]Error processing lineage CSV: {str(e)}[/red]")

def generate_sample_csv(arguments, processor):
    """Generate sample CSV file for lineage"""
    output_file = arguments['<output_file>']
    num_samples = int(arguments.get('--num-samples', 10))
    template_type = arguments.get('--template', 'basic')
    
    console.print(f"[blue]Generating sample CSV: {output_file}[/blue]")
    console.print(f"[dim]Template: {template_type}, Samples: {num_samples}[/dim]")
    
    try:
        output_path = processor.generate_sample_csv(output_file, num_samples)
        console.print(f"[green]✅ Sample CSV generated: {output_path}[/green]")
        
        # Show template info
        templates = LineageCSVTemplates()
        if template_type == 'basic':
            template_info = templates.get_basic_template()
        elif template_type == 'etl':
            template_info = templates.get_etl_template()
        elif template_type == 'column-mapping':
            template_info = templates.get_column_mapping_template()
        else:
            template_info = templates.get_basic_template()
        
        console.print(f"\n[cyan]Template: {template_info['name']}[/cyan]")
        console.print(f"[dim]{template_info['description']}[/dim]")
        console.print(f"[dim]Columns: {', '.join(template_info['columns'])}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error generating sample CSV: {str(e)}[/red]")

def validate_csv_file(arguments, processor):
    """Validate CSV file format"""
    csv_file = arguments['<csv_file>']
    
    if not Path(csv_file).exists():
        console.print(f"[red]Error: CSV file not found: {csv_file}[/red]")
        return
    
    console.print(f"[blue]Validating CSV file: {csv_file}[/blue]")
    
    try:
        validation_result = processor.validate_csv_file(csv_file)
        
        if validation_result['is_valid']:
            console.print("[bold green]✅ CSV file is valid![/bold green]")
            
            # Validation details table
            table = Table(title="Validation Details")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Rows", str(validation_result['total_rows']))
            table.add_row("File Size (MB)", f"{validation_result['file_size_mb']:.2f}")
            table.add_row("Columns Found", str(len(validation_result['columns_found'])))
            table.add_row("Relationship Types", ', '.join(validation_result['relationship_types_found']))
            
            console.print(table)
            
            # Show preview
            if validation_result['preview_rows']:
                console.print("\n[cyan]Preview (first 3 rows):[/cyan]")
                preview_table = Table()
                
                # Add columns
                if validation_result['preview_rows']:
                    for col in validation_result['preview_rows'][0].keys():
                        preview_table.add_column(col[:20], overflow="ellipsis")
                    
                    # Add rows
                    for row in validation_result['preview_rows']:
                        preview_table.add_row(*[str(v)[:50] for v in row.values()])
                
                console.print(preview_table)
        else:
            console.print("[bold red]❌ CSV validation failed![/bold red]")
            for error in validation_result['errors']:
                console.print(f"[red]• {error}[/red]")
                
    except Exception as e:
        console.print(f"[red]Error validating CSV file: {str(e)}[/red]")

def show_templates():
    """Show available CSV templates"""
    templates = LineageCSVTemplates()
    
    console.print("[bold blue]Available CSV Lineage Templates[/bold blue]\n")
    
    template_info = [
        templates.get_basic_template(),
        templates.get_etl_template(),
        templates.get_column_mapping_template()
    ]
    
    for template in template_info:
        console.print(f"[bold cyan]{template['name']}[/bold cyan]")
        console.print(f"[dim]{template['description']}[/dim]")
        console.print(f"[green]Columns: {', '.join(template['columns'])}[/green]")
        console.print()

if __name__ == '__main__':
    arguments = docopt(__doc__)
    
    # Initialize Purview client (this would typically come from config)
    profile = config_manager.get_active_profile()
    if not profile:
        console.print("[red]No active Purview profile found. Please configure a profile first.[/red]")
        sys.exit(1)
    
    client = EnhancedPurviewClient(profile.account_name, profile.get_credential())
    
    # Handle CSV lineage commands
    if arguments.get('csv'):
        asyncio.run(handle_csv_lineage_commands(arguments, client))
    else:
        # Handle traditional lineage commands (read, readNext)
        console.print("[yellow]Traditional lineage commands not yet implemented in enhanced CLI[/yellow]")
