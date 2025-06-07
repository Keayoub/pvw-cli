"""
CSV Batch Operations Module
Provides comprehensive CSV import/export functionality for Purview entities
"""

import csv
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ColumnMapping:
    """Maps CSV columns to Purview entity attributes"""
    csv_column: str
    purview_attribute: str
    data_type: str = "string"
    required: bool = False
    transformer: Optional[Callable] = None
    default_value: Any = None

@dataclass
class EntityTemplate:
    """Template for creating Purview entities from CSV data"""
    type_name: str
    attribute_mappings: List[ColumnMapping] = field(default_factory=list)
    qualified_name_template: str = "{name}@{account_name}"
    collection_name: Optional[str] = None
    default_attributes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def required_fields(self) -> List[str]:
        """Get list of required CSV column names"""
        return [mapping.csv_column for mapping in self.attribute_mappings if mapping.required]
    
    @property
    def optional_fields(self) -> List[str]:
        """Get list of optional CSV column names"""
        return [mapping.csv_column for mapping in self.attribute_mappings if not mapping.required]

class CSVBatchProcessor:
    """Handles batch processing of CSV files for Purview operations"""
    
    def __init__(self, purview_client):
        self.client = purview_client
        self.supported_operations = [
            'create_entities',
            'update_entities', 
            'assign_glossary_terms',
            'create_glossary_terms',
            'update_classifications'
        ]
    
    async def process_csv_file(self, 
                              csv_path: str, 
                              operation: str, 
                              template: EntityTemplate,
                              progress_callback: Optional[Callable] = None) -> Dict:
        """Process CSV file with specified operation"""
        
        if operation not in self.supported_operations:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Read and validate CSV
        df = pd.read_csv(csv_path)
        results = {'success': [], 'errors': [], 'summary': {}}
        
        # Validate required columns
        validation_errors = self._validate_csv_structure(df, template)
        if validation_errors:
            results['errors'] = validation_errors
            return results
        
        # Process based on operation type
        if operation == 'create_entities':
            results = await self._create_entities_from_csv(df, template, progress_callback)
        elif operation == 'update_entities':
            results = await self._update_entities_from_csv(df, template, progress_callback)
        elif operation == 'assign_glossary_terms':
            results = await self._assign_terms_from_csv(df, template, progress_callback)
        elif operation == 'create_glossary_terms':
            results = await self._create_terms_from_csv(df, template, progress_callback)
        elif operation == 'update_classifications':
            results = await self._update_classifications_from_csv(df, template, progress_callback)
        
        return results
    
    def _validate_csv_structure(self, df: pd.DataFrame, template: EntityTemplate) -> List[str]:
        """Validate CSV structure against template"""
        errors = []
        
        # Check required columns
        required_columns = [mapping.csv_column for mapping in template.attribute_mappings if mapping.required]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for empty required values
        for mapping in template.attribute_mappings:
            if mapping.required and mapping.csv_column in df.columns:
                empty_rows = df[df[mapping.csv_column].isnull()].index.tolist()
                if empty_rows:
                    errors.append(f"Required column '{mapping.csv_column}' has empty values in rows: {empty_rows}")
        
        return errors
    
    async def _create_entities_from_csv(self, 
                                       df: pd.DataFrame, 
                                       template: EntityTemplate,
                                       progress_callback: Optional[Callable] = None) -> Dict:
        """Create entities from CSV data"""
        
        entities = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                entity = self._create_entity_from_row(row, template)
                entities.append(entity)
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        if not entities:
            return {'success': [], 'errors': errors, 'summary': {'total': 0, 'created': 0, 'failed': len(errors)}}
        
        # Create entities in batches
        created_entities = await self.client.batch_create_entities(entities, progress_callback)
        
        return {
            'success': created_entities,
            'errors': errors,
            'summary': {
                'total': len(df),
                'created': len(created_entities),
                'failed': len(errors)
            }
        }
    
    async def _update_entities_from_csv(self, 
                                       df: pd.DataFrame, 
                                       template: EntityTemplate,
                                       progress_callback: Optional[Callable] = None) -> Dict:
        """Update entities from CSV data"""
        
        entities = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Require GUID for updates
                if 'guid' not in row or pd.isna(row['guid']):
                    errors.append(f"Row {index + 1}: GUID is required for entity updates")
                    continue
                
                entity = self._create_entity_from_row(row, template)
                entity['guid'] = row['guid']
                entities.append(entity)
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        if not entities:
            return {'success': [], 'errors': errors, 'summary': {'total': 0, 'updated': 0, 'failed': len(errors)}}
        
        # Update entities in batches
        updated_entities = await self.client.batch_update_entities(entities, progress_callback)
        
        return {
            'success': updated_entities,
            'errors': errors,
            'summary': {
                'total': len(df),
                'updated': len(updated_entities),
                'failed': len(errors)
            }
        }
    
    async def _assign_terms_from_csv(self, 
                                    df: pd.DataFrame, 
                                    template: EntityTemplate,
                                    progress_callback: Optional[Callable] = None) -> Dict:
        """Assign glossary terms to entities from CSV"""
        
        results = {'success': [], 'errors': [], 'summary': {}}
        
        # Group by term_guid for batch assignment
        if 'term_guid' not in df.columns or 'entity_guid' not in df.columns:
            results['errors'].append("Required columns 'term_guid' and 'entity_guid' not found")
            return results
        
        term_groups = df.groupby('term_guid')
        
        for term_guid, group in term_groups:
            try:
                entity_guids = group['entity_guid'].dropna().tolist()
                if entity_guids:
                    result = await self.client.assign_term_to_entities(term_guid, entity_guids)
                    results['success'].append({
                        'term_guid': term_guid,
                        'assigned_entities': len(entity_guids),
                        'result': result
                    })
            except Exception as e:
                results['errors'].append(f"Failed to assign term {term_guid}: {str(e)}")
        
        results['summary'] = {
            'terms_processed': len(term_groups),
            'successful_assignments': len(results['success']),
            'failed_assignments': len(results['errors'])
        }
        
        return results
    
    async def _create_terms_from_csv(self, 
                                    df: pd.DataFrame, 
                                    template: EntityTemplate,
                                    progress_callback: Optional[Callable] = None) -> Dict:
        """Create glossary terms from CSV"""
        
        terms = []
        errors = []
        
        required_columns = ['name', 'glossary_guid']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'success': [], 
                'errors': [f"Missing required columns: {', '.join(missing_columns)}"],
                'summary': {'total': 0, 'created': 0, 'failed': 1}
            }
        
        for index, row in df.iterrows():
            try:
                term = {
                    'name': row['name'],
                    'glossaryGuid': row['glossary_guid'],
                    'longDescription': row.get('description', ''),
                    'shortDescription': row.get('short_description', ''),
                    'status': row.get('status', 'Draft')
                }
                
                # Add custom attributes
                for col in df.columns:
                    if col.startswith('attr_') and pd.notna(row[col]):
                        attr_name = col.replace('attr_', '')
                        term[attr_name] = row[col]
                
                terms.append(term)
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Create terms
        created_terms = []
        for term in terms:
            try:
                result = await self.client.create_glossary_term(term)
                created_terms.append(result)
            except Exception as e:
                errors.append(f"Failed to create term '{term['name']}': {str(e)}")
        
        return {
            'success': created_terms,
            'errors': errors,
            'summary': {
                'total': len(df),
                'created': len(created_terms),
                'failed': len(errors)
            }
        }
    
    def _create_entity_from_row(self, row: pd.Series, template: EntityTemplate) -> Dict:
        """Create Purview entity from CSV row"""
        
        entity = {
            'typeName': template.type_name,
            'attributes': template.default_attributes.copy()
        }
        
        # Apply column mappings
        for mapping in template.attribute_mappings:
            if mapping.csv_column in row:
                value = row[mapping.csv_column]
                
                # Handle null values
                if pd.isna(value):
                    if mapping.required:
                        raise ValueError(f"Required attribute '{mapping.purview_attribute}' is empty")
                    elif mapping.default_value is not None:
                        value = mapping.default_value
                    else:
                        continue
                
                # Apply data type conversion
                value = self._convert_data_type(value, mapping.data_type)
                
                # Apply transformer if provided
                if mapping.transformer:
                    value = mapping.transformer(value)
                
                entity['attributes'][mapping.purview_attribute] = value
        
        # Generate qualified name if not provided
        if 'qualifiedName' not in entity['attributes']:
            qualified_name = template.qualified_name_template.format(
                **entity['attributes'],
                account_name=self.client.config.account_name
            )
            entity['attributes']['qualifiedName'] = qualified_name
        
        # Set collection if specified
        if template.collection_name:
            entity['collections'] = [{'uniqueAttributes': {'name': template.collection_name}}]
        
        return entity
    
    def _convert_data_type(self, value: Any, data_type: str) -> Any:
        """Convert value to specified data type"""
        
        if data_type == 'string':
            return str(value)
        elif data_type == 'int':
            return int(float(value))
        elif data_type == 'float':  
            return float(value)
        elif data_type == 'bool':
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif data_type == 'json':
            return json.loads(value) if isinstance(value, str) else value
        elif data_type == 'list':
            return value.split(',') if isinstance(value, str) else [value] if not isinstance(value, list) else value
        else:
            return value

class CSVExporter:
    """Export Purview data to CSV format"""
    
    def __init__(self, purview_client):
        self.client = purview_client
    
    async def export_entities(self, 
                            search_query: str,
                            output_path: str,
                            columns: Optional[List[str]] = None,
                            flatten_attributes: bool = True) -> Dict:
        """Export entities to CSV"""
        
        try:
            # Search for entities
            search_results = await self.client.search_entities(search_query, limit=10000)
            entities = search_results.get('value', [])
            
            if not entities:
                return {'status': 'success', 'message': 'No entities found', 'count': 0}
            
            # Convert to DataFrame
            df_data = []
            for entity in entities:
                row = self._entity_to_row(entity, flatten_attributes)
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            
            # Filter columns if specified
            if columns:
                available_columns = [col for col in columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
            
            # Export to CSV
            df.to_csv(output_path, index=False)
            
            return {
                'status': 'success',
                'message': f'Exported {len(entities)} entities to {output_path}',
                'count': len(entities),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def export_glossary_terms(self, 
                                  glossary_guid: Optional[str],
                                  output_path: str) -> Dict:
        """Export glossary terms to CSV"""
        
        try:
            terms = await self.client.get_glossary_terms(glossary_guid)
            
            if not terms:
                return {'status': 'success', 'message': 'No terms found', 'count': 0}
            
            # Convert terms to DataFrame
            df = pd.DataFrame(terms)
            df.to_csv(output_path, index=False)
            
            return {
                'status': 'success',
                'message': f'Exported {len(terms)} glossary terms to {output_path}',
                'count': len(terms)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _entity_to_row(self, entity: Dict, flatten_attributes: bool = True) -> Dict:
        """Convert entity to CSV row format"""
        
        row = {
            'guid': entity.get('guid'),
            'typeName': entity.get('typeName'),
            'status': entity.get('status'),
            'createdBy': entity.get('createdBy'),
            'updatedBy': entity.get('updatedBy'),
            'createTime': entity.get('createTime'),
            'updateTime': entity.get('updateTime')
        }
        
        # Add attributes
        attributes = entity.get('attributes', {})
        if flatten_attributes:
            for key, value in attributes.items():
                if isinstance(value, (str, int, float, bool)):
                    row[f'attr_{key}'] = value
                elif isinstance(value, list) and value:
                    row[f'attr_{key}'] = ', '.join(str(v) for v in value)
                elif isinstance(value, dict):
                    row[f'attr_{key}'] = json.dumps(value)
        else:
            row['attributes'] = json.dumps(attributes)
        
        # Add classifications
        classifications = entity.get('classifications', [])
        if classifications:
            row['classifications'] = ', '.join([c.get('typeName', '') for c in classifications])
        
        return row

# Predefined templates for common entity types
ENTITY_TEMPLATES = {
    'dataset': EntityTemplate(
        type_name='DataSet',
        attribute_mappings=[
            ColumnMapping('name', 'name', required=True),
            ColumnMapping('description', 'description'),
            ColumnMapping('owner', 'owner'),
            ColumnMapping('schema', 'schema', data_type='json'),
        ]
    ),
    'table': EntityTemplate(
        type_name='hive_table',
        attribute_mappings=[
            ColumnMapping('name', 'name', required=True),
            ColumnMapping('database', 'db'),
            ColumnMapping('owner', 'owner'),
            ColumnMapping('table_type', 'tableType'),
        ]
    ),
    'glossary_term': EntityTemplate(
        type_name='AtlasGlossaryTerm',
        attribute_mappings=[
            ColumnMapping('name', 'name', required=True),
            ColumnMapping('description', 'longDescription'),
            ColumnMapping('short_description', 'shortDescription'),
            ColumnMapping('status', 'status', default_value='Draft'),
        ]
    )
}
