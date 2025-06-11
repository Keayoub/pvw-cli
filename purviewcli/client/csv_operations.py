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

from ._lineage import CSVLineageProcessor, LineageRelationship

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
            'update_classifications',
            'create_lineage_relationships',
            'update_lineage_relationships',
            'bulk_create_lineage'
        ]
    
    # Predefined templates for lineage operations
    LINEAGE_TEMPLATES = {
        'basic_lineage': EntityTemplate(
            type_name='DataFlow',
            attribute_mappings=[
                ColumnMapping('source_entity_guid', 'source_guid', required=True),
                ColumnMapping('target_entity_guid', 'target_guid', required=True),
                ColumnMapping('relationship_type', 'type', required=True),
                ColumnMapping('process_name', 'process'),
                ColumnMapping('description', 'description'),
                ColumnMapping('confidence_score', 'confidence', data_type='float'),
            ]
        ),
        'etl_lineage': EntityTemplate(
            type_name='Process',
            attribute_mappings=[
                ColumnMapping('source_entity_guid', 'source_guid', required=True),
                ColumnMapping('target_entity_guid', 'target_guid', required=True),
                ColumnMapping('process_name', 'process_name', required=True),
                ColumnMapping('transformation_type', 'transformation'),
                ColumnMapping('owner', 'owner'),
                ColumnMapping('schedule', 'schedule'),
                ColumnMapping('metadata', 'metadata', data_type='json'),
            ]
        ),
        'column_lineage': EntityTemplate(
            type_name='ColumnMapping',
            attribute_mappings=[
                ColumnMapping('source_entity_guid', 'source_table_guid', required=True),
                ColumnMapping('target_entity_guid', 'target_table_guid', required=True),
                ColumnMapping('source_column', 'source_column', required=True),
                ColumnMapping('target_column', 'target_column', required=True),
                ColumnMapping('transformation_logic', 'transformation'),
                ColumnMapping('confidence_score', 'confidence', data_type='float'),
            ]
        )
    }    # Add lineage templates to existing templates
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
        ),
        # Lineage templates
        'basic_lineage': EntityTemplate(
            type_name='DataFlow',
            attribute_mappings=[
                ColumnMapping('source_entity_guid', 'source_guid', required=True),
                ColumnMapping('target_entity_guid', 'target_guid', required=True),
                ColumnMapping('relationship_type', 'type', required=True),
                ColumnMapping('process_name', 'process'),
                ColumnMapping('description', 'description'),
                ColumnMapping('confidence_score', 'confidence', data_type='float'),
            ]
        ),
        'etl_lineage': EntityTemplate(
            type_name='Process',
            attribute_mappings=[
                ColumnMapping('source_entity_guid', 'source_guid', required=True),
                ColumnMapping('target_entity_guid', 'target_guid', required=True),
                ColumnMapping('process_name', 'process_name', required=True),
                ColumnMapping('transformation_type', 'transformation'),
                ColumnMapping('owner', 'owner'),
                ColumnMapping('schedule', 'schedule'),
                ColumnMapping('metadata', 'metadata', data_type='json'),
            ]
        ),
        'column_lineage': EntityTemplate(
            type_name='ColumnMapping',
            attribute_mappings=[
                ColumnMapping('source_entity_guid', 'source_table_guid', required=True),
                ColumnMapping('target_entity_guid', 'target_table_guid', required=True),
                ColumnMapping('source_column', 'source_column', required=True),
                ColumnMapping('target_column', 'target_column', required=True),
                ColumnMapping('transformation_logic', 'transformation'),
                ColumnMapping('confidence_score', 'confidence', data_type='float'),
            ]
        )
    }

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
        elif operation == 'create_lineage_relationships':
            results = await self._create_lineage_from_csv(df, template, progress_callback)
        elif operation == 'update_lineage_relationships':
            results = await self._update_lineage_from_csv(df, template, progress_callback)
        elif operation == 'bulk_create_lineage':
            results = await self._bulk_create_lineage_from_csv(df, template, progress_callback)
        
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

    async def _create_lineage_from_csv(self, 
                                     df: pd.DataFrame, 
                                     template: EntityTemplate,
                                     progress_callback: Optional[Callable] = None) -> Dict:
        """Create lineage relationships from CSV data"""
        
        # Initialize lineage processor
        lineage_processor = CSVLineageProcessor(self.client)
        
        # Required columns for lineage
        required_columns = ['source_entity_guid', 'target_entity_guid', 'relationship_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'success': [], 
                'errors': [f"Missing required columns: {', '.join(missing_columns)}"],
                'summary': {'total': 0, 'created': 0, 'failed': 1}
            }
        
        relationships = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                relationship = LineageRelationship(
                    source_guid=row['source_entity_guid'],
                    target_guid=row['target_entity_guid'],
                    relationship_type=row['relationship_type'],
                    process_name=row.get('process_name', f'Process_{index}'),
                    process_guid=row.get('process_guid'),
                    confidence_score=float(row.get('confidence_score', 1.0)),
                    metadata=json.loads(row['metadata']) if pd.notna(row.get('metadata')) else {},
                    description=row.get('description', ''),
                    owner=row.get('owner', ''),
                    tags=row.get('tags', '').split(',') if pd.notna(row.get('tags')) else []
                )
                relationships.append(relationship)
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        if not relationships:
            return {'success': [], 'errors': errors, 'summary': {'total': 0, 'created': 0, 'failed': len(errors)}}
        
        # Create lineage relationships in batches
        created_count = 0
        for i, relationship in enumerate(relationships):
            try:
                result = await self.client.create_lineage_relationship(relationship)
                created_count += 1
                if progress_callback:
                    progress_callback(f"Created lineage relationship {i+1}/{len(relationships)}")
            except Exception as e:
                errors.append(f"Failed to create relationship {i+1}: {str(e)}")
        
        return {
            'success': list(range(created_count)),
            'errors': errors,
            'summary': {
                'total': len(df),
                'created': created_count,
                'failed': len(errors)
            }
        }

    async def _update_lineage_from_csv(self, 
                                     df: pd.DataFrame, 
                                     template: EntityTemplate,
                                     progress_callback: Optional[Callable] = None) -> Dict:
        """Update lineage relationships from CSV data"""
        
        # Required columns for lineage updates
        required_columns = ['relationship_guid', 'source_entity_guid', 'target_entity_guid', 'relationship_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'success': [], 
                'errors': [f"Missing required columns: {', '.join(missing_columns)}"],
                'summary': {'total': 0, 'updated': 0, 'failed': 1}
            }
        
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                relationship_data = {
                    'guid': row['relationship_guid'],
                    'typeName': row['relationship_type'],
                    'end1': {'guid': row['source_entity_guid']},
                    'end2': {'guid': row['target_entity_guid']},
                    'attributes': {}
                }
                
                # Add optional attributes
                if pd.notna(row.get('process_name')):
                    relationship_data['attributes']['process'] = row['process_name']
                if pd.notna(row.get('confidence_score')):
                    relationship_data['attributes']['confidence'] = float(row['confidence_score'])
                if pd.notna(row.get('description')):
                    relationship_data['attributes']['description'] = row['description']
                
                result = await self.client.update_lineage_relationship(relationship_data)
                updated_count += 1
                
                if progress_callback:
                    progress_callback(f"Updated lineage relationship {index+1}/{len(df)}")
                    
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return {
            'success': list(range(updated_count)),
            'errors': errors,
            'summary': {
                'total': len(df),
                'updated': updated_count,
                'failed': len(errors)
            }
        }

    async def _bulk_create_lineage_from_csv(self, 
                                          df: pd.DataFrame, 
                                          template: EntityTemplate,
                                          progress_callback: Optional[Callable] = None) -> Dict:
        """Bulk create lineage relationships from CSV data"""
        
        # Required columns for bulk lineage creation
        required_columns = ['source_entity_guid', 'target_entity_guid', 'relationship_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'success': [], 
                'errors': [f"Missing required columns: {', '.join(missing_columns)}"],
                'summary': {'total': 0, 'created': 0, 'failed': 1}
            }
        
        # Prepare bulk lineage payload
        lineage_entities = []
        relationships = []
        errors = []
        
        # Group relationships by process
        process_groups = df.groupby('process_name') if 'process_name' in df.columns else {'default_process': df}
        
        for process_name, group in process_groups:
            try:
                # Create process entity
                process_entity = {
                    'typeName': 'Process',
                    'attributes': {
                        'name': process_name if isinstance(process_name, str) else 'Default_Process',
                        'qualifiedName': f"{process_name}@{self.client.config.account_name if hasattr(self.client, 'config') else 'default'}",
                        'description': group.iloc[0].get('description', '') if 'description' in group.columns else ''
                    }
                }
                lineage_entities.append(process_entity)
                
                # Create relationships for this process
                for index, row in group.iterrows():
                    relationship = {
                        'typeName': 'DataFlow',
                        'end1': {'guid': row['source_entity_guid']},
                        'end2': {'guid': row['target_entity_guid']},
                        'attributes': {
                            'process': process_name if isinstance(process_name, str) else 'Default_Process',
                            'confidence': float(row.get('confidence_score', 1.0)) if pd.notna(row.get('confidence_score')) else 1.0
                        }
                    }
                    
                    # Add metadata if available
                    if pd.notna(row.get('metadata')):
                        try:
                            metadata = json.loads(row['metadata'])
                            relationship['attributes'].update(metadata)
                        except json.JSONDecodeError:
                            pass
                    
                    relationships.append(relationship)
                    
            except Exception as e:
                errors.append(f"Process {process_name}: {str(e)}")
        
        if not relationships:
            return {'success': [], 'errors': errors, 'summary': {'total': 0, 'created': 0, 'failed': len(errors)}}
        
        # Execute bulk creation
        try:
            bulk_payload = {
                'entities': lineage_entities,
                'relationships': relationships
            }
            
            result = await self.client.bulk_create_lineage(bulk_payload)
            created_count = len(relationships)
            
            if progress_callback:
                progress_callback(f"Bulk created {created_count} lineage relationships")
            
            return {
                'success': result,
                'errors': errors,
                'summary': {
                    'total': len(df),
                    'created': created_count,
                    'failed': len(errors)
                }
            }
            
        except Exception as e:
            errors.append(f"Bulk creation failed: {str(e)}")
            return {
                'success': [],
                'errors': errors,
                'summary': {
                    'total': len(df),
                    'created': 0,
                    'failed': len(errors)
                }
            }


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
    
    async def _update_classifications_from_csv(self, 
                                             df: pd.DataFrame, 
                                             template: EntityTemplate,
                                             progress_callback: Optional[Callable] = None) -> Dict:
        """Update entity classifications from CSV data"""
        
        results = {'success': [], 'errors': [], 'summary': {}}
        
        # Required columns for classification updates
        required_columns = ['entity_guid', 'classification_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            results['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
            return results
        
        # Group by entity_guid for batch processing
        entity_groups = df.groupby('entity_guid')
        
        for entity_guid, group in entity_groups:
            try:
                classifications = []
                
                for index, row in group.iterrows():
                    classification = {
                        'typeName': row['classification_name']
                    }
                    
                    # Add classification attributes
                    attributes = {}
                    for col in df.columns:
                        if col.startswith('attr_') and pd.notna(row[col]):
                            attr_name = col.replace('attr_', '')
                            attributes[attr_name] = self._convert_data_type(row[col], 'string')
                    
                    if attributes:
                        classification['attributes'] = attributes
                    
                    # Add propagation settings if specified
                    if 'propagate' in row and pd.notna(row['propagate']):
                        classification['propagate'] = str(row['propagate']).lower() in ('true', '1', 'yes')
                    
                    # Add validity periods if specified
                    if 'valid_from' in row and pd.notna(row['valid_from']):
                        classification['validityPeriods'] = [{
                            'start': row['valid_from'],
                            'end': row.get('valid_to', None)
                        }]
                    
                    classifications.append(classification)
                
                if classifications:
                    # Determine operation type
                    operation = group.iloc[0].get('operation', 'add').lower()
                    
                    if operation == 'add':
                        result = await self.client.add_classifications_to_entity(entity_guid, classifications)
                    elif operation == 'update':
                        result = await self.client.update_entity_classifications(entity_guid, classifications)
                    elif operation == 'remove':
                        # For remove operations, only classification names are needed
                        classification_names = [c['typeName'] for c in classifications]
                        result = await self.client.remove_classifications_from_entity(entity_guid, classification_names)
                    else:
                        raise ValueError(f"Unsupported operation: {operation}")
                    
                    results['success'].append({
                        'entity_guid': entity_guid,
                        'operation': operation,
                        'classifications_count': len(classifications),
                        'result': result
                    })
                    
                    if progress_callback:
                        progress_callback(f"Updated classifications for entity {entity_guid}")
                        
            except Exception as e:
                results['errors'].append(f"Failed to update classifications for entity {entity_guid}: {str(e)}")
        
        results['summary'] = {
            'entities_processed': len(entity_groups),
            'successful_updates': len(results['success']),
            'failed_updates': len(results['errors'])
        }
        
        return results

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
                account_name=self.client.config.account_name if hasattr(self.client, 'config') else 'default'
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


def generate_lineage_sample_csv(output_path: str, template_type: str = 'basic_lineage', num_samples: int = 10) -> None:
    """Generate sample CSV file for lineage operations"""
    
    template = CSVBatchProcessor.LINEAGE_TEMPLATES.get(template_type)
    if not template:
        raise ValueError(f"Unknown template type: {template_type}. Available: {list(CSVBatchProcessor.LINEAGE_TEMPLATES.keys())}")
    
    # Sample data based on template type
    if template_type == 'basic_lineage':
        data = []
        for i in range(num_samples):
            data.append({
                'source_entity_guid': f'source-guid-{i:03d}',
                'target_entity_guid': f'target-guid-{i:03d}',
                'relationship_type': 'DataFlow',
                'process_name': f'ETL_Process_{i}',
                'description': f'Data transformation process {i}',
                'confidence_score': round(0.8 + (i % 3) * 0.1, 2),
                'owner': 'data-engineering-team',
                'metadata': f'{{"tool": "spark", "job_id": "job_{i}", "run_date": "2025-06-10"}}'
            })
    
    elif template_type == 'etl_lineage':
        data = []
        for i in range(num_samples):
            data.append({
                'source_entity_guid': f'source-table-{i:03d}',
                'target_entity_guid': f'target-table-{i:03d}',
                'process_name': f'Daily_ETL_Job_{i}',
                'transformation_type': ['aggregation', 'filter', 'join'][i % 3],
                'owner': 'data-team',
                'schedule': 'daily',
                'metadata': f'{{"tool": "spark", "cluster": "prod", "sla_hours": 4}}'
            })
    
    elif template_type == 'column_lineage':
        data = []
        for i in range(num_samples):
            data.append({
                'source_entity_guid': f'source-table-{i:03d}',
                'target_entity_guid': f'target-table-{i:03d}',
                'source_column': f'col_{i}_source',
                'target_column': f'col_{i}_target',
                'transformation_logic': ['DIRECT', 'UPPER(source)', 'CONCAT(a,b)'][i % 3],
                'confidence_score': round(0.85 + (i % 2) * 0.1, 2)
            })
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(data)} sample lineage records in {output_path}")


def validate_lineage_csv(csv_path: str, template_type: str = 'basic_lineage') -> Dict[str, Any]:
    """Validate lineage CSV file format"""
    
    template = CSVBatchProcessor.LINEAGE_TEMPLATES.get(template_type)
    if not template:
        return {'valid': False, 'errors': [f"Unknown template type: {template_type}"]}
    
    try:
        df = pd.read_csv(csv_path)
        errors = []
        warnings = []
        
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
        
        # Validate GUID formats (basic check)
        guid_columns = [col for col in df.columns if 'guid' in col.lower()]
        for col in guid_columns:
            if col in df.columns:
                invalid_guids = []
                for idx, guid in df[col].iteritems():
                    if pd.notna(guid) and len(str(guid)) < 10:  # Basic validation
                        invalid_guids.append(idx)
                if invalid_guids:
                    warnings.append(f"Column '{col}' has potentially invalid GUIDs in rows: {invalid_guids}")
        
        # Check confidence scores
        if 'confidence_score' in df.columns:
            invalid_scores = df[(df['confidence_score'] < 0) | (df['confidence_score'] > 1)].index.tolist()
            if invalid_scores:
                errors.append(f"Confidence scores must be between 0 and 1. Invalid rows: {invalid_scores}")
        
        # Validate JSON metadata
        if 'metadata' in df.columns:
            invalid_json_rows = []
            for idx, metadata in df['metadata'].iteritems():
                if pd.notna(metadata):
                    try:
                        json.loads(metadata)
                    except json.JSONDecodeError:
                        invalid_json_rows.append(idx)
            if invalid_json_rows:
                errors.append(f"Invalid JSON in metadata column, rows: {invalid_json_rows}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_rows': len(df),
            'columns': list(df.columns)
        }
        
    except Exception as e:
        return {'valid': False, 'errors': [f"Failed to read CSV: {str(e)}"]}


# Additional templates for common lineage scenarios
CSVBatchProcessor.LINEAGE_TEMPLATES.update({
    'data_pipeline': EntityTemplate(
        type_name='DataPipeline',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_guid', required=True),
            ColumnMapping('pipeline_name', 'pipeline_name', required=True),
            ColumnMapping('pipeline_type', 'pipeline_type'),
            ColumnMapping('schedule', 'schedule'),
            ColumnMapping('owner', 'owner'),
            ColumnMapping('status', 'status'),
            ColumnMapping('metadata', 'metadata', data_type='json'),
        ]
    ),
    'copy_activity': EntityTemplate(
        type_name='CopyActivity',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_guid', required=True),
            ColumnMapping('copy_activity_name', 'activity_name', required=True),
            ColumnMapping('copy_type', 'copy_type'),
            ColumnMapping('rows_copied', 'rows_copied', data_type='int'),
            ColumnMapping('bytes_copied', 'bytes_copied', data_type='int'),
            ColumnMapping('duration_seconds', 'duration', data_type='int'),
        ]
    )
})


# Predefined templates for lineage operations
LINEAGE_TEMPLATES = {
    'basic_lineage': EntityTemplate(
        type_name='DataFlow',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_guid', required=True),
            ColumnMapping('relationship_type', 'type', required=True),
            ColumnMapping('process_name', 'process'),
            ColumnMapping('description', 'description'),
            ColumnMapping('confidence_score', 'confidence', data_type='float'),
        ]
    ),
    'etl_lineage': EntityTemplate(
        type_name='Process',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_guid', required=True),
            ColumnMapping('process_name', 'process_name', required=True),
            ColumnMapping('transformation_type', 'transformation'),
            ColumnMapping('owner', 'owner'),
            ColumnMapping('schedule', 'schedule'),
            ColumnMapping('metadata', 'metadata', data_type='json'),
        ]
    ),
    'column_lineage': EntityTemplate(
        type_name='ColumnMapping',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_table_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_table_guid', required=True),
            ColumnMapping('source_column', 'source_column', required=True),
            ColumnMapping('target_column', 'target_column', required=True),
            ColumnMapping('transformation_logic', 'transformation'),
            ColumnMapping('confidence_score', 'confidence', data_type='float'),
        ]
    ),
    'data_pipeline': EntityTemplate(
        type_name='DataPipeline',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_guid', required=True),
            ColumnMapping('pipeline_name', 'pipeline_name', required=True),
            ColumnMapping('pipeline_type', 'pipeline_type'),
            ColumnMapping('schedule', 'schedule'),
            ColumnMapping('owner', 'owner'),
            ColumnMapping('status', 'status'),
            ColumnMapping('metadata', 'metadata', data_type='json'),
        ]
    ),
    'copy_activity': EntityTemplate(
        type_name='CopyActivity',
        attribute_mappings=[
            ColumnMapping('source_entity_guid', 'source_guid', required=True),
            ColumnMapping('target_entity_guid', 'target_guid', required=True),
            ColumnMapping('copy_activity_name', 'activity_name', required=True),
            ColumnMapping('copy_type', 'copy_type'),
            ColumnMapping('rows_copied', 'rows_copied', data_type='int'),
            ColumnMapping('bytes_copied', 'bytes_copied', data_type='int'),
            ColumnMapping('duration_seconds', 'duration', data_type='int'),
        ]
    )
}


def validate_lineage_csv(csv_path: str, template_name: str = 'basic_lineage') -> Dict:
    """
    Validate a lineage CSV file against a template
    
    Args:
        csv_path: Path to the CSV file
        template_name: Name of the template to validate against
        
    Returns:
        Dictionary with validation results
    """
    try:
        if template_name not in LINEAGE_TEMPLATES:
            return {
                'valid': False, 
                'errors': [f"Unknown template: {template_name}. Available templates: {list(LINEAGE_TEMPLATES.keys())}"]
            }
        
        template = LINEAGE_TEMPLATES[template_name]
        df = pd.read_csv(csv_path)
        
        errors = []
        warnings = []
        
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
        
        # Check data types
        for mapping in template.attribute_mappings:
            if mapping.csv_column in df.columns:
                if mapping.data_type == 'float':
                    non_numeric = df[~pd.to_numeric(df[mapping.csv_column], errors='coerce').notnull()].index.tolist()
                    if non_numeric:
                        warnings.append(f"Column '{mapping.csv_column}' has non-numeric values in rows: {non_numeric}")
                elif mapping.data_type == 'int':
                    non_integer = df[~df[mapping.csv_column].astype(str).str.isdigit()].index.tolist()
                    if non_integer:
                        warnings.append(f"Column '{mapping.csv_column}' has non-integer values in rows: {non_integer}")
        
        # Special validation for lineage-specific columns
        if 'metadata' in df.columns:
            invalid_json_rows = []
            for idx, row in df.iterrows():
                if pd.notna(row['metadata']):
                    try:
                        json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        invalid_json_rows.append(idx)
            if invalid_json_rows:
                errors.append(f"Invalid JSON in metadata column, rows: {invalid_json_rows}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_rows': len(df),
            'columns': list(df.columns)
        }
        
    except Exception as e:
        return {'valid': False, 'errors': [f"Failed to read CSV: {str(e)}"]}


def get_lineage_csv_template_info(template_name: str = None) -> Dict:
    """
    Get information about lineage CSV templates
    
    Args:
        template_name: Specific template name, or None for all templates
        
    Returns:
        Dictionary with template information
    """
    if template_name:
        if template_name not in LINEAGE_TEMPLATES:
            return {'error': f"Unknown template: {template_name}"}
        
        template = LINEAGE_TEMPLATES[template_name]
        return {
            'name': template_name,
            'type_name': template.type_name,
            'required_columns': [m.csv_column for m in template.attribute_mappings if m.required],
            'optional_columns': [m.csv_column for m in template.attribute_mappings if not m.required],
            'all_mappings': [(m.csv_column, m.purview_attribute, m.data_type) for m in template.attribute_mappings]
        }
    
    # Return information about all templates
    return {
        'available_templates': list(LINEAGE_TEMPLATES.keys()),
        'templates': {
            name: {
                'type_name': template.type_name,
                'required_columns': [m.csv_column for m in template.attribute_mappings if m.required],
                'optional_columns': [m.csv_column for m in template.attribute_mappings if not m.required]
            }
            for name, template in LINEAGE_TEMPLATES.items()
        }
    }
