"""
Automation Scripts for Common Purview Operations
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import pandas as pd
from typing import Dict, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from purviewcli.client.api_client import PurviewClient, PurviewConfig
from purviewcli.client.csv_operations import CSVBatchProcessor, CSVExporter, ENTITY_TEMPLATES

class PurviewAutomation:
    """Automated Purview operations for common scenarios"""
    
    def __init__(self, account_name: str, region: str = None):
        self.config = PurviewConfig(
            account_name=account_name,
            azure_region=region,
            batch_size=50,
            max_retries=3
        )
    
    async def bulk_entity_import(self, csv_file: str, entity_type: str = 'dataset'):
        """Import entities from CSV with progress tracking"""
        
        async with PurviewClient(self.config) as client:
            processor = CSVBatchProcessor(client)
            
            if entity_type not in ENTITY_TEMPLATES:
                raise ValueError(f"Unsupported entity type: {entity_type}")
            
            template = ENTITY_TEMPLATES[entity_type]
            
            def progress_callback(current, total):
                percentage = (current / total) * 100
                print(f"Progress: {current}/{total} ({percentage:.1f}%)")
            
            print(f"Starting bulk import from {csv_file}")
            results = await processor.process_csv_file(
                csv_file,
                'create_entities',
                template,
                progress_callback
            )
            
            print(f"\nImport completed:")
            print(f"  - Total: {results['summary']['total']}")
            print(f"  - Success: {results['summary']['created']}")
            print(f"  - Failed: {results['summary']['failed']}")
            
            if results['errors']:
                print(f"\nFirst 5 errors:")
                for error in results['errors'][:5]:
                    print(f"  - {error}")
            
            return results
    
    async def bulk_glossary_setup(self, terms_csv: str, assignments_csv: str = None):
        """Setup glossary terms and optionally assign them to entities"""
        
        async with PurviewClient(self.config) as client:
            processor = CSVBatchProcessor(client)
            
            # Import terms
            print(f"Importing glossary terms from {terms_csv}")
            template = ENTITY_TEMPLATES['glossary_term']
            
            terms_results = await processor.process_csv_file(
                terms_csv,
                'create_glossary_terms',
                template
            )
            
            print(f"Terms import completed:")
            print(f"  - Created: {terms_results['summary']['created']}")
            print(f"  - Failed: {terms_results['summary']['failed']}")
            
            # Assign terms if assignments file provided
            if assignments_csv and os.path.exists(assignments_csv):
                print(f"\nAssigning terms from {assignments_csv}")
                
                assignment_results = await processor.process_csv_file(
                    assignments_csv,
                    'assign_glossary_terms', 
                    template  # Template not used for assignments
                )
                
                print(f"Term assignments completed:")
                print(f"  - Successful: {assignment_results['summary']['successful_assignments']}")
                print(f"  - Failed: {assignment_results['summary']['failed_assignments']}")
            
            return terms_results
    
    async def data_estate_export(self, output_dir: str):
        """Export comprehensive data estate information"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        async with PurviewClient(self.config) as client:
            exporter = CSVExporter(client)
            
            exports = [
                ('entities_all.csv', '*'),
                ('datasets.csv', 'typeName:DataSet'),
                ('tables.csv', 'typeName:hive_table'),
                ('databases.csv', 'typeName:hive_db'),
            ]
            
            for filename, query in exports:
                print(f"Exporting {filename}...")
                output_file = output_path / filename
                
                result = await exporter.export_entities(
                    query,
                    str(output_file)
                )
                
                if result['status'] == 'success':
                    print(f"  ✓ {result['message']}")
                else:
                    print(f"  ✗ {result['message']}")
            
            # Export glossary terms
            print("Exporting glossary terms...")
            glossary_result = await exporter.export_glossary_terms(
                None,  # All glossaries
                str(output_path / 'glossary_terms.csv')
            )
            
            if glossary_result['status'] == 'success':
                print(f"  ✓ {glossary_result['message']}")
            else:
                print(f"  ✗ {glossary_result['message']}")
    
    async def lineage_analysis(self, root_entity_guid: str, output_file: str):
        """Analyze and export lineage information"""
        
        async with PurviewClient(self.config) as client:
            print(f"Analyzing lineage for entity {root_entity_guid}")
            
            lineage = await client.get_lineage(root_entity_guid, 'BOTH', 5)
            
            # Extract lineage information
            lineage_data = []
            
            relations = lineage.get('relations', [])
            entities = lineage.get('guidEntityMap', {})
            
            for relation in relations:
                from_guid = relation.get('fromEntityId')
                to_guid = relation.get('toEntityId')
                
                from_entity = entities.get(from_guid, {})
                to_entity = entities.get(to_guid, {})
                
                lineage_data.append({
                    'from_guid': from_guid,
                    'from_name': from_entity.get('attributes', {}).get('name', 'Unknown'),
                    'from_type': from_entity.get('typeName', 'Unknown'),
                    'to_guid': to_guid,
                    'to_name': to_entity.get('attributes', {}).get('name', 'Unknown'),
                    'to_type': to_entity.get('typeName', 'Unknown'),
                    'relationship_type': relation.get('relationshipType', 'Unknown')
                })
            
            # Save to CSV
            df = pd.DataFrame(lineage_data)
            df.to_csv(output_file, index=False)
            
            print(f"Lineage analysis saved to {output_file}")
            print(f"Found {len(lineage_data)} lineage relationships")
            
            return lineage_data

async def main():
    """Example usage of automation scripts"""
    
    # Get configuration from environment
    account_name = os.environ.get('PURVIEW_ACCOUNT_NAME')
    if not account_name:
        print("Please set PURVIEW_ACCOUNT_NAME environment variable")
        return
    
    region = os.environ.get('AZURE_REGION')
    
    automation = PurviewAutomation(account_name, region)
    
    # Example operations
    print("=== Purview Automation Demo ===\n")
    
    # 1. Bulk entity import
    sample_csv = Path(__file__).parent.parent / 'samples' / 'csv' / 'dataset_import_sample.csv'
    if sample_csv.exists():
        print("1. Bulk Entity Import")
        try:
            await automation.bulk_entity_import(str(sample_csv), 'dataset')
        except Exception as e:
            print(f"Error in bulk import: {e}")
        print()
    
    # 2. Data estate export
    print("2. Data Estate Export")
    try:
        await automation.data_estate_export('./exports')
    except Exception as e:
        print(f"Error in data export: {e}")
    print()
    
    # 3. Glossary setup
    terms_csv = Path(__file__).parent.parent / 'samples' / 'csv' / 'glossary_terms_sample.csv'
    assignments_csv = Path(__file__).parent.parent / 'samples' / 'csv' / 'term_assignments_sample.csv'
    
    if terms_csv.exists():
        print("3. Glossary Setup")
        try:
            await automation.bulk_glossary_setup(
                str(terms_csv),
                str(assignments_csv) if assignments_csv.exists() else None
            )
        except Exception as e:
            print(f"Error in glossary setup: {e}")

if __name__ == '__main__':
    asyncio.run(main())
