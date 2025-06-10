"""
Comprehensive Lineage Module for Azure Purview
Supports both traditional lineage operations and CSV-based bulk lineage creation
"""

import pandas as pd
import asyncio
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
import logging

from .api_client import PurviewClient
from .endpoint import Endpoint, decorator
from .endpoints import PurviewEndpoints

logger = logging.getLogger(__name__)

@dataclass
class LineageRelationship:
    """Represents a lineage relationship between entities"""
    source_entity_guid: str
    target_entity_guid: str
    source_entity_name: str
    target_entity_name: str
    relationship_type: str = "DataFlow"
    process_name: Optional[str] = None
    process_guid: Optional[str] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Generate process GUID if not provided"""
        if not self.process_guid:
            self.process_guid = f"process_{self.source_entity_guid}_{self.target_entity_guid}_{uuid.uuid4().hex[:8]}"
        
        if not self.process_name:
            self.process_name = f"Process_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

@dataclass 
class LineageProcessingResult:
    """Result of lineage processing operation"""
    success: bool
    total_rows: int = 0
    processed: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    processing_time: float = 0.0

class LineageCSVTemplates:
    """Predefined templates for common lineage scenarios"""
    
    @staticmethod
    def get_basic_template() -> Dict[str, Any]:
        """Basic lineage template"""
        return {
            'name': 'Basic Lineage',
            'description': 'Simple source-to-target lineage relationships',
            'columns': CSVLineageProcessor.REQUIRED_COLUMNS + ['process_name', 'description'],
            'sample_data': [
                {
                    'source_entity_guid': 'source-guid-001',
                    'target_entity_guid': 'target-guid-001',
                    'source_entity_name': 'Source_Table_A',
                    'target_entity_name': 'Target_Table_A',
                    'relationship_type': 'DataFlow',
                    'process_name': 'Basic_ETL_Process',
                    'description': 'Basic data transformation'
                }
            ]
        }
    
    @staticmethod
    def get_etl_template() -> Dict[str, Any]:
        """ETL process lineage template"""
        return {
            'name': 'ETL Process Lineage',
            'description': 'Comprehensive ETL transformation lineage with metadata',
            'columns': CSVLineageProcessor.REQUIRED_COLUMNS + [
                'process_name', 'confidence_score', 'metadata', 'owner', 'tags'
            ],
            'sample_data': [
                {
                    'source_entity_guid': 'source-guid-001',
                    'target_entity_guid': 'target-guid-001',
                    'source_entity_name': 'Raw_Customer_Data',
                    'target_entity_name': 'Processed_Customer_Data',
                    'relationship_type': 'Transformation',
                    'process_name': 'Customer_Data_ETL',
                    'confidence_score': 0.95,
                    'metadata': '{"transformation": "aggregation", "tool": "spark", "schedule": "daily", "sla_hours": 4}',
                    'owner': 'data-engineering-team',
                    'tags': 'customer,pii,daily'
                }
            ],
            'sample_metadata': {
                "transformation": "aggregation",
                "tool": "spark", 
                "schedule": "daily",
                "sla_hours": 4
            }
        }
    
    @staticmethod 
    def get_column_mapping_template() -> Dict[str, Any]:
        """Column-level lineage template"""
        return {
            'name': 'Column Mapping Lineage',
            'description': 'Fine-grained column-level lineage with transformation logic',
            'columns': CSVLineageProcessor.REQUIRED_COLUMNS + [
                'source_column', 'target_column', 'transformation_logic', 'confidence_score'
            ],
            'sample_data': [
                {
                    'source_entity_guid': 'source-table-guid-001',
                    'target_entity_guid': 'target-table-guid-001',
                    'source_entity_name': 'customer_raw',
                    'target_entity_name': 'customer_processed',
                    'relationship_type': 'ColumnMapping',
                    'source_column': 'first_name',
                    'target_column': 'full_name',
                    'transformation_logic': 'CONCAT(first_name, \' \', last_name)',
                    'confidence_score': 1.0
                }
            ]
        }

    @staticmethod
    def get_all_templates() -> List[Dict[str, Any]]:
        """Get all available templates"""
        return [
            LineageCSVTemplates.get_basic_template(),
            LineageCSVTemplates.get_etl_template(),
            LineageCSVTemplates.get_column_mapping_template()
        ]

    @staticmethod
    def get_template_by_name(name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name"""
        template_map = {
            'basic': LineageCSVTemplates.get_basic_template(),
            'etl': LineageCSVTemplates.get_etl_template(),
            'column-mapping': LineageCSVTemplates.get_column_mapping_template()
        }
        return template_map.get(name.lower())

    @staticmethod
    def generate_template_csv(template_name: str, output_path: str, num_samples: int = 5) -> str:
        """Generate a CSV file from a template"""
        template = LineageCSVTemplates.get_template_by_name(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Create sample data based on template
        sample_data = []
        base_sample = template.get('sample_data', [{}])[0]
        
        for i in range(num_samples):
            sample_row = base_sample.copy()
            # Modify identifiers to make them unique
            for key, value in sample_row.items():
                if isinstance(value, str) and ('guid' in key or 'name' in key):
                    if 'guid' in key:
                        sample_row[key] = f"{value.split('-')[0]}-{i:03d}"
                    else:
                        sample_row[key] = f"{value}_{i}"
            
            sample_data.append(sample_row)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False)
        
        return output_path

class Lineage(Endpoint):
    """Original lineage endpoint class with traditional lineage operations"""
    
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def lineageRead(self, args):
        """Read lineage information for an entity"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE['guid'], guid=args["--guid"])
        self.params = {
            'depth': args.get('--depth', 3),
            'width': args.get('--width', 6),
            'direction': args.get('--direction', 'BOTH'),
            'forceNewApi': 'true',
            'includeParent': 'true',
            'getDerivedLineage': 'true'
        }
    
    @decorator
    def lineageReadNext(self, args):
        """Read next page of lineage results"""
        self.method = 'GET'
        self.endpoint = f'/catalog/api/lineage/{args["--guid"]}/next/'
        self.params = {
          'direction': args['--direction'],
          'getDerivedLineage': 'true',
          'offset': args['--offset'],
          'limit': args['--limit'],
          'api-version': '2021-05-01-preview'
        }

    @decorator  
    def lineageAnalyze(self, args):
        """Advanced lineage analysis endpoint"""
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"])}/analyze'
        self.params = {
            'depth': args.get('--depth', 3),
            'direction': args.get('--direction', 'BOTH'),
            'includeImpactAnalysis': 'true'
        }

    @decorator
    def lineageImpact(self, args):
        """Impact analysis endpoint"""
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"])}/impact'
        self.params = {
            'direction': args.get('--direction', 'OUTPUT'),
            'maxDepth': args.get('--depth', 5)
        }

    @decorator
    def lineageCSVProcess(self, args):
        """Process CSV lineage relationships"""
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/process'
        self.params = {
            'batch-size': args.get('--batch-size', 100),
            'validate-entities': args.get('--validate-entities', False),
            'create-missing-entities': args.get('--create-missing-entities', False),
            'progress': args.get('--progress', False)
        }

    @decorator
    def lineageCSVValidate(self, args):
        """Validate CSV lineage file format"""
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/validate'
        self.params = {}

    @decorator
    def lineageCSVSample(self, args):
        """Generate sample CSV lineage file"""
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/sample'
        self.params = {
            'num-samples': args.get('--num-samples', 10),
            'template': args.get('--template', 'basic')
        }

    @decorator
    def lineageCSVTemplates(self, args):
        """Get available CSV lineage templates"""
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/templates'
        self.params = {}


class CSVLineageProcessor:
    """ CSV processor for creating custom lineage relationships in Azure Purview"""
    
    # Supported relationship types
    RELATIONSHIP_TYPES = [
        'DataFlow', 'ColumnMapping', 'Process', 'Derivation', 
        'Custom', 'Transformation', 'Copy', 'Join', 'Filter'
    ]
    
    # Required CSV columns
    REQUIRED_COLUMNS = [
        'source_entity_guid', 'target_entity_guid', 
        'source_entity_name', 'target_entity_name',
        'relationship_type'
    ]
    
    # Optional CSV columns
    OPTIONAL_COLUMNS = [
        'process_name', 'process_guid', 'confidence_score', 
        'metadata', 'description', 'owner', 'tags'
    ]
    
    def __init__(self, purview_client):
        """Initialize the CSV lineage processor"""
        from .api_client import PurviewClient
        self.client = purview_client
        self.account_name = purview_client.account_name
        
    async def process_lineage_csv(
        self, 
        csv_file_path: str, 
        batch_size: int = 100,
        validate_entities: bool = True,
        create_missing_entities: bool = False,
        progress_callback: Optional[callable] = None
    ) -> LineageProcessingResult:
        """
        Process CSV file to create custom lineage relationships.
        
        Args:
            csv_file_path: Path to CSV file
            batch_size: Number of relationships to process in each batch
            validate_entities: Whether to validate that entities exist
            create_missing_entities: Whether to create missing entities
            progress_callback: Optional callback function for progress updates
            
        Returns:
            LineageProcessingResult with processing statistics
        """
        start_time = datetime.now()
        
        try:
            # Read and validate CSV
            df = pd.read_csv(csv_file_path)
            validation_result = self._validate_csv_format(df)
            
            if not validation_result['is_valid']:
                return LineageProcessingResult(
                    success=False,
                    errors=[f"CSV validation failed: {'; '.join(validation_result['errors'])}"]
                )
            
            # Convert DataFrame to LineageRelationship objects
            relationships = self._create_relationships_from_df(df)
            total_rows = len(relationships)
            
            logger.info(f"Processing {total_rows} lineage relationships from {csv_file_path}")
            
            # Process in batches
            processed = 0
            failed = 0
            errors = []
            
            for i in range(0, total_rows, batch_size):
                batch_relationships = relationships[i:i + batch_size]
                batch_result = await self._process_lineage_batch(
                    batch_relationships, 
                    validate_entities,
                    create_missing_entities
                )
                
                processed += batch_result['processed']
                failed += batch_result['failed']
                errors.extend(batch_result['errors'])
                
                # Progress update
                if progress_callback:
                    progress = ((i + batch_size) / total_rows) * 100
                    progress_callback(min(progress, 100), processed, failed)
                
                logger.info(f"Batch {i//batch_size + 1}: {batch_result['processed']} processed, {batch_result['failed']} failed")
            
            # Calculate results
            processing_time = (datetime.now() - start_time).total_seconds()
            success_rate = (processed / total_rows) * 100 if total_rows > 0 else 0
            
            return LineageProcessingResult(
                success=True,
                total_rows=total_rows,
                processed=processed,
                failed=failed,
                errors=errors,
                success_rate=success_rate,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing lineage CSV: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            return LineageProcessingResult(
                success=False,
                errors=[str(e)],
                processing_time=processing_time
            )
    
    def _validate_csv_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate CSV format and required columns"""
        errors = []
        
        # Check required columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty required fields
        for col in self.REQUIRED_COLUMNS:
            if col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    errors.append(f"Column '{col}' has {empty_count} empty values")
        
        # Validate relationship types
        if 'relationship_type' in df.columns:
            invalid_types = df[~df['relationship_type'].isin(self.RELATIONSHIP_TYPES)]['relationship_type'].unique()
            if len(invalid_types) > 0:
                errors.append(f"Invalid relationship types found: {list(invalid_types)}. Valid types: {self.RELATIONSHIP_TYPES}")
        
        # Validate confidence scores
        if 'confidence_score' in df.columns:
            invalid_scores = df[
                (df['confidence_score'].notna()) & 
                ((df['confidence_score'] < 0) | (df['confidence_score'] > 1))
            ]
            if len(invalid_scores) > 0:
                errors.append(f"Confidence scores must be between 0.0 and 1.0. Found {len(invalid_scores)} invalid values")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'total_rows': len(df),
            'columns_found': list(df.columns)
        }
    
    def _create_relationships_from_df(self, df: pd.DataFrame) -> List[LineageRelationship]:
        """Convert DataFrame rows to LineageRelationship objects"""
        relationships = []
        
        for _, row in df.iterrows():
            # Parse metadata if it's a JSON string
            metadata = None
            if pd.notna(row.get('metadata')):
                try:
                    metadata = json.loads(row['metadata'])
                except json.JSONDecodeError:
                    metadata = {'raw_metadata': str(row['metadata'])}
            
            relationship = LineageRelationship(
                source_entity_guid=row['source_entity_guid'],
                target_entity_guid=row['target_entity_guid'],
                source_entity_name=row['source_entity_name'],
                target_entity_name=row['target_entity_name'],
                relationship_type=row['relationship_type'],
                process_name=row.get('process_name'),
                process_guid=row.get('process_guid'),
                confidence_score=row.get('confidence_score') if pd.notna(row.get('confidence_score')) else None,
                metadata=metadata
            )
            relationships.append(relationship)
        
        return relationships
    
    async def _process_lineage_batch(
        self, 
        relationships: List[LineageRelationship],
        validate_entities: bool,
        create_missing_entities: bool
    ) -> Dict[str, Any]:
        """Process a batch of lineage relationships"""
        processed = 0
        failed = 0
        errors = []
        
        for relationship in relationships:
            try:
                # Validate entities exist if requested
                if validate_entities:
                    source_exists = await self._entity_exists(relationship.source_entity_guid)
                    target_exists = await self._entity_exists(relationship.target_entity_guid)
                    
                    if not source_exists or not target_exists:
                        if create_missing_entities:
                            # Create missing entities
                            if not source_exists:
                                await self._create_placeholder_entity(
                                    relationship.source_entity_guid, 
                                    relationship.source_entity_name
                                )
                            if not target_exists:
                                await self._create_placeholder_entity(
                                    relationship.target_entity_guid, 
                                    relationship.target_entity_name
                                )
                        else:
                            errors.append(f"Entity validation failed for relationship: {relationship.source_entity_name} -> {relationship.target_entity_name}")
                            failed += 1
                            continue
                
                # Create lineage relationship
                success = await self._create_lineage_relationship(relationship)
                if success:
                    processed += 1
                    logger.debug(f"Created lineage: {relationship.source_entity_name} -> {relationship.target_entity_name}")
                else:
                    failed += 1
                    errors.append(f"Failed to create lineage: {relationship.source_entity_name} -> {relationship.target_entity_name}")
                    
            except Exception as e:
                failed += 1
                errors.append(f"Error processing relationship {relationship.source_entity_name} -> {relationship.target_entity_name}: {str(e)}")
                logger.error(f"Error processing relationship: {str(e)}")
        
        return {
            'processed': processed,
            'failed': failed,
            'errors': errors
        }
    
    async def _entity_exists(self, entity_guid: str) -> bool:
        """Check if an entity exists in Purview"""
        try:
            response = await self.client.make_request('GET', f'/catalog/api/atlas/v2/entity/guid/{entity_guid}')
            return response.get('entity') is not None
        except Exception as e:
            if "404" in str(e) or "EntityNotFound" in str(e):
                return False
            logger.warning(f"Error checking entity existence {entity_guid}: {str(e)}")
            return False
    
    async def _create_placeholder_entity(self, entity_guid: str, entity_name: str) -> bool:
        """Create a placeholder entity if it doesn't exist"""
        try:
            entity_data = {
                "entity": {
                    "guid": entity_guid,
                    "typeName": "DataSet",
                    "attributes": {
                        "name": entity_name,
                        "qualifiedName": f"{entity_name}@{self.account_name}",
                        "description": "Auto-created placeholder entity for lineage"
                    }
                }
            }
            
            response = await self.client.make_request('POST', '/catalog/api/atlas/v2/entity', json=entity_data)
            logger.info(f"Created placeholder entity: {entity_name} ({entity_guid})")
            return response is not None
            
        except Exception as e:
            logger.error(f"Failed to create placeholder entity {entity_guid}: {str(e)}")
            return False
    
    async def _create_lineage_relationship(self, relationship: LineageRelationship) -> bool:
        """Create a lineage relationship between two entities"""
        try:
            # Prepare process entity data
            process_attributes = {
                "name": relationship.process_name,
                "qualifiedName": f"{relationship.process_guid}@{self.account_name}",
                "inputs": [{"guid": relationship.source_entity_guid}],
                "outputs": [{"guid": relationship.target_entity_guid}]
            }
            
            # Add optional attributes
            if relationship.confidence_score is not None:
                process_attributes["confidence"] = relationship.confidence_score
            
            if relationship.metadata:
                process_attributes.update(relationship.metadata)
            
            # Create process entity that represents the lineage
            lineage_data = {
                "entity": {
                    "guid": relationship.process_guid,
                    "typeName": "Process",
                    "attributes": process_attributes
                }
            }
            
            # Create the lineage relationship via process entity
            response = await self.client.make_request('POST', '/catalog/api/atlas/v2/entity', json=lineage_data)
            return response is not None
            
        except Exception as e:
            logger.error(f"Failed to create lineage relationship: {str(e)}")
            return False
    
    def generate_sample_csv(self, output_path: str, num_samples: int = 10) -> str:
        """Generate a sample CSV file for lineage creation"""
        sample_data = []
        
        for i in range(num_samples):
            sample_data.append({
                'source_entity_guid': f'source-guid-{i:03d}',
                'target_entity_guid': f'target-guid-{i:03d}',
                'source_entity_name': f'Source_Table_{i}',
                'target_entity_name': f'Target_Table_{i}',
                'relationship_type': 'DataFlow',
                'process_name': f'ETL_Process_{i}',
                'process_guid': f'process-guid-{i:03d}',
                'confidence_score': 0.9,
                'metadata': json.dumps({"transformation": "aggregation", "tool": "spark", "schedule": "daily"})
            })
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Generated sample CSV with {num_samples} lineage relationships: {output_path}")
        return output_path
    
    def validate_csv_file(self, csv_file_path: str) -> Dict[str, Any]:
        """Validate a CSV file without processing it"""
        try:
            df = pd.read_csv(csv_file_path)
            validation_result = self._validate_csv_format(df)
            
            # Add additional statistics
            validation_result.update({
                'file_path': csv_file_path,
                'file_size_mb': Path(csv_file_path).stat().st_size / (1024 * 1024),
                'relationship_types_found': list(df['relationship_type'].unique()) if 'relationship_type' in df.columns else [],
                'preview_rows': df.head(3).to_dict('records') if len(df) > 0 else []
            })
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f"Error reading CSV file: {str(e)}"],
                'file_path': csv_file_path
            }

