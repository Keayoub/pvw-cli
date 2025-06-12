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
from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

logger = logging.getLogger(__name__)


@dataclass
class LineageRelationship:
    """Represents a lineage relationship between entities"""

    source_entity_guid: str
    target_entity_guid: str
    source_entity_name: str = ""
    target_entity_name: str = ""
    relationship_type: str = "DataFlow"
    process_name: Optional[str] = None
    process_guid: Optional[str] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    tags: Optional[List[str]] = None

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


class CSVLineageProcessor:
    """
    CSV processor for creating custom lineage relationships in Azure Purview

    Usage:
        lineage csv process <csv_file> [--batch-size=<val> --validate-entities --create-missing-entities --progress]
        lineage csv validate <csv_file>
        lineage csv sample <output_file> [--num-samples=<val> --template=<val>]
        lineage csv templates
    """

    # Supported relationship types
    RELATIONSHIP_TYPES = [
        "DataFlow",
        "ColumnMapping",
        "Process",
        "Derivation",
        "Custom",
        "Transformation",
        "Copy",
        "Join",
        "Filter",
    ]

    # Required CSV columns
    REQUIRED_COLUMNS = [
        "source_entity_guid",
        "target_entity_guid",
        "source_entity_name",
        "target_entity_name",
        "relationship_type",
    ]

    # Optional CSV columns
    OPTIONAL_COLUMNS = [
        "process_name",
        "process_guid",
        "confidence_score",
        "metadata",
        "description",
        "owner",
        "tags",
    ]

    def __init__(self, purview_client):
        """Initialize the CSV lineage processor"""
        self.client = purview_client
        self.account_name = (
            purview_client.account_name if hasattr(purview_client, "account_name") else None
        )


class LineageCSVTemplates:
    """
    Predefined templates for common lineage scenarios

    Usage:
        lineage csv templates
        lineage csv sample <output_file> [--num-samples=<val> --template=<val>]
    """

    @staticmethod
    def get_basic_template() -> Dict[str, Any]:
        """Basic lineage template"""
        return {
            "name": "Basic Lineage",
            "description": "Simple source-to-target lineage relationships",
            "columns": CSVLineageProcessor.REQUIRED_COLUMNS + ["process_name", "description"],
            "sample_data": [
                {
                    "source_entity_guid": "source-guid-001",
                    "target_entity_guid": "target-guid-001",
                    "source_entity_name": "Source_Table_A",
                    "target_entity_name": "Target_Table_A",
                    "relationship_type": "DataFlow",
                    "process_name": "Basic_ETL_Process",
                    "description": "Basic data transformation",
                }
            ],
        }

    @staticmethod
    def get_etl_template() -> Dict[str, Any]:
        """ETL process lineage template"""
        return {
            "name": "ETL Process Lineage",
            "description": "Comprehensive ETL transformation lineage with metadata",
            "columns": CSVLineageProcessor.REQUIRED_COLUMNS
            + ["process_name", "confidence_score", "metadata", "owner", "tags"],
            "sample_data": [
                {
                    "source_entity_guid": "source-guid-001",
                    "target_entity_guid": "target-guid-001",
                    "source_entity_name": "Raw_Customer_Data",
                    "target_entity_name": "Processed_Customer_Data",
                    "relationship_type": "Transformation",
                    "process_name": "Customer_Data_ETL",
                    "confidence_score": 0.95,
                    "metadata": '{"transformation": "aggregation", "tool": "spark", "schedule": "daily", "sla_hours": 4}',
                    "owner": "data-engineering-team",
                    "tags": "customer,pii,daily",
                }
            ],
            "sample_metadata": {
                "transformation": "aggregation",
                "tool": "spark",
                "schedule": "daily",
                "sla_hours": 4,
            },
        }

    @staticmethod
    def get_column_mapping_template() -> Dict[str, Any]:
        """Column-level lineage template"""
        return {
            "name": "Column Mapping Lineage",
            "description": "Fine-grained column-level lineage with transformation logic",
            "columns": CSVLineageProcessor.REQUIRED_COLUMNS
            + ["source_column", "target_column", "transformation_logic", "confidence_score"],
            "sample_data": [
                {
                    "source_entity_guid": "source-table-guid-001",
                    "target_entity_guid": "target-table-guid-001",
                    "source_entity_name": "customer_raw",
                    "target_entity_name": "customer_processed",
                    "relationship_type": "ColumnMapping",
                    "source_column": "first_name",
                    "target_column": "full_name",
                    "transformation_logic": "CONCAT(first_name, ' ', last_name)",
                    "confidence_score": 1.0,
                }
            ],
        }

    @staticmethod
    def get_all_templates() -> List[Dict[str, Any]]:
        """Get all available templates"""
        return [
            LineageCSVTemplates.get_basic_template(),
            LineageCSVTemplates.get_etl_template(),
            LineageCSVTemplates.get_column_mapping_template(),
        ]

    @staticmethod
    def get_template_by_name(name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name"""
        template_map = {
            "basic": LineageCSVTemplates.get_basic_template(),
            "etl": LineageCSVTemplates.get_etl_template(),
            "column-mapping": LineageCSVTemplates.get_column_mapping_template(),
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
        base_sample = template.get("sample_data", [{}])[0]

        for i in range(num_samples):
            sample_row = base_sample.copy()
            # Modify identifiers to make them unique
            for key, value in sample_row.items():
                if isinstance(value, str) and ("guid" in key or "name" in key):
                    if "guid" in key:
                        sample_row[key] = f"{value.split('-')[0]}-{i:03d}"
                    else:
                        sample_row[key] = f"{value}_{i}"

            sample_data.append(sample_row)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False)

        return output_path


class Lineage(Endpoint):
    """
    Original lineage endpoint class with traditional lineage operations

    Usage:
        lineage read --guid=<val> [--depth=<val> --width=<val> --direction=<val>]
        lineage analyze --guid=<val> [--depth=<val> --direction=<val>]
        lineage impact --guid=<val> [--depth=<val>]
        lineage csv process <csv_file> [--batch-size=<val> ...]
        lineage csv validate <csv_file>
        lineage csv sample <output_file> [--num-samples=<val> --template=<val>]
        lineage csv templates
    """

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    @decorator
    def lineageRead(self, args):
        """Read lineage information for an entity"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"]
        )
        self.params = {
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 6),
            "direction": args.get("--direction", "BOTH"),
            "forceNewApi": "true",
            "includeParent": "true",
            "getDerivedLineage": "true",
        }

    @decorator
    def lineageReadNext(self, args):
        """Read next page of lineage results"""
        self.method = "GET"
        self.endpoint = f'/catalog/api/lineage/{args["--guid"]}/next/'
        self.params = {
            "direction": args["--direction"],
            "getDerivedLineage": "true",
            "offset": args["--offset"],
            "limit": args["--limit"],
            "api-version": "2021-05-01-preview",
        }

    @decorator
    def lineageAnalyze(self, args):
        """Advanced lineage analysis endpoint"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"])}/analyze'
        self.params = {
            "depth": args.get("--depth", 3),
            "direction": args.get("--direction", "BOTH"),
            "includeImpactAnalysis": "true",
        }

    @decorator
    def lineageImpact(self, args):
        """Impact analysis endpoint"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"])}/impact'
        self.params = {
            "direction": args.get("--direction", "OUTPUT"),
            "maxDepth": args.get("--depth", 5),
        }

    @decorator
    def lineageCSVProcess(self, args):
        """Parse CSV, convert to JSON (Atlas relationship format), and call lineageBulkCreate (official bulk API)."""
        import os
        import tempfile

        csv_file = args.get("<csv_file>") or args.get("csv_file") or args.get("csv")
        if not csv_file or not os.path.exists(csv_file):
            raise ValueError(f"CSV file not found: {csv_file}")

        # Read CSV and convert to Atlas relationship format
        df = pd.read_csv(csv_file)
        entities = []
        for _, row in df.iterrows():
            rel = {
                "typeName": row.get("relationship_type", "DataFlow"),
                "end1": {"guid": row["source_entity_guid"]},
                "end2": {"guid": row["target_entity_guid"]},
                "attributes": {},
            }
            # Optional attributes
            if "process_name" in row and not pd.isna(row["process_name"]):
                rel["attributes"]["process"] = row["process_name"]
            if "confidence_score" in row and not pd.isna(row["confidence_score"]):
                rel["attributes"]["confidence"] = float(row["confidence_score"])
            if "description" in row and not pd.isna(row["description"]):
                rel["attributes"]["description"] = row["description"]
            if "metadata" in row and not pd.isna(row["metadata"]):
                try:
                    rel["attributes"]["metadata"] = json.loads(row["metadata"])
                except Exception:
                    rel["attributes"]["metadata"] = row["metadata"]
            if "owner" in row and not pd.isna(row["owner"]):
                rel["attributes"]["owner"] = row["owner"]
            if "tags" in row and not pd.isna(row["tags"]):
                rel["attributes"]["tags"] = [
                    t.strip() for t in str(row["tags"]).split(",") if t.strip()
                ]
            entities.append(rel)
        payload = {"entities": entities}
        # Write to a temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
            json.dump(payload, tmpf, indent=2)
            tmpf.flush()
            payload_file = tmpf.name

        # Call the official bulk creation endpoint
        bulk_args = {
            "--payloadFile": payload_file,
            "--ignoreRelationships": args.get("--ignoreRelationships", False),
            "--minExtInfo": args.get("--minExtInfo", False),
        }
        
        result = self.lineageBulkCreate(bulk_args)
        os.remove(payload_file)
        return result

    @decorator
    def lineageCSVValidate(self, args):
        """Validate CSV lineage file format"""
        self.method = "POST"
        self.endpoint = (
            f"{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/validate"
        )
        self.params = {}

    @decorator
    def lineageCSVSample(self, args):
        """Generate sample CSV lineage file"""
        self.method = "GET"
        self.endpoint = (
            f"{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/sample"
        )
        self.params = {
            "num-samples": args.get("--num-samples", 10),
            "template": args.get("--template", "basic"),
        }

    @decorator
    def lineageCSVTemplates(self, args):
        """Get available CSV lineage templates"""
        self.method = "GET"
        self.endpoint = (
            f"{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/csv/templates"
        )
        self.params = {}

    @decorator
    def lineageReadUniqueAttribute(self, args):
        """Read lineage information for an entity by unique attribute"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.LINEAGE["unique_attribute"], typeName=args["--typeName"]
        )
        self.params = {
            "attr:qualifiedName": args["--qualifiedName"],
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 6),
            "direction": args.get("--direction", "BOTH"),
            "forceNewApi": "true",
            "includeParent": "true",
            "getDerivedLineage": "true",
        }

    @decorator
    def lineageBulkCreate(self, args):
        """Create multiple lineage relationships in bulk (Official API)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.LINEAGE["bulk"]
        self.payload = get_json(args, "--payloadFile")
        self.params = {
            "ignoreRelationships": str(args.get("--ignoreRelationships", False)).lower(),
            "minExtInfo": str(args.get("--minExtInfo", False)).lower(),
        }

    @decorator
    def lineageBulkUpdate(self, args):
        """Update multiple lineage relationships in bulk"""
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.LINEAGE["bulk_update"]
        self.payload = get_json(args, "--payloadFile")
        self.params = {
            "ignoreRelationships": str(args.get("--ignoreRelationships", False)).lower(),
            "minExtInfo": str(args.get("--minExtInfo", False)).lower(),
        }

    @decorator
    def lineageReadDownstream(self, args):
        """Get downstream lineage for an entity"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.LINEAGE["downstream"], guid=args["--guid"]
        )
        self.params = {
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 6),
            "includeParent": "true",
            "getDerivedLineage": "true",
        }

    @decorator
    def lineageReadUpstream(self, args):
        """Get upstream lineage for an entity"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.LINEAGE["upstream"], guid=args["--guid"]
        )
        self.params = {
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 6),
            "includeParent": "true",
            "getDerivedLineage": "true",
        }

    @decorator
    def lineageCreateRelationship(self, args):
        """Create a new lineage relationship"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.LINEAGE["guid"].replace("/{guid}", "")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def lineageUpdateRelationship(self, args):
        """Update an existing lineage relationship"""
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"]
        )
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def lineageDeleteRelationship(self, args):
        """Delete a lineage relationship"""
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"]
        )
        self.params = {"cascade": str(args.get("--cascade", False)).lower()}

    # === ENHANCED LINEAGE ANALYSIS METHODS ===

    @decorator
    def lineageAnalyzeColumn(self, args):
        """Analyze column-level lineage"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"])}/columns'
        self.params = {
            "columnName": args.get("--columnName"),
            "direction": args.get("--direction", "BOTH"),
            "depth": args.get("--depth", 3),
        }

    @decorator
    def lineageAnalyzeDataflow(self, args):
        """Analyze data flow patterns"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["guid"], guid=args["--guid"])}/dataflow'
        self.params = {
            "includeProcesses": "true",
            "includeTransformations": "true",
            "direction": args.get("--direction", "BOTH"),
        }

    @decorator
    def lineageGetMetrics(self, args):
        """Get lineage metrics and statistics"""
        self.method = "GET"
        self.endpoint = (
            f"{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/lineage/metrics"
        )
        self.params = {
            "entityGuid": args.get("--guid"),
            "includeColumnLineage": "true",
            "includeDerivedLineage": "true",
        }

    # ...existing CSV processing methods...
