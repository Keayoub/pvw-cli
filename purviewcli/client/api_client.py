"""
 Microsoft Purview API Client
Supports the latest Microsoft Purview REST API specifications with comprehensive automation capabilities
"""

import json
import asyncio
try:
    import aiohttp
except Exception:
    aiohttp = None
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
import logging
from datetime import datetime
import os
import sys
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION, format_endpoint, get_api_version_params

logger = logging.getLogger(__name__)


@dataclass
class PurviewConfig:
    """Configuration for Purview API Client"""

    account_name: str
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    azure_region: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    batch_size: int = 100


class PurviewClient:
    """Purview API Client with comprehensive automation support"""

    def __init__(self, config: PurviewConfig):
        self.config = config
        self._token = None
        self._credential = None
        self._session = None
        self._setup_endpoints()

    def _setup_endpoints(self):
        """Setup API endpoints based on Azure region"""
        if self.config.azure_region and self.config.azure_region.lower() == "china":
            self.purview_endpoint = f"https://{self.config.account_name}.purview.azure.cn"
            self.management_endpoint = "https://management.chinacloudapi.cn"
            self.auth_scope = "https://purview.azure.cn/.default"
        elif self.config.azure_region and self.config.azure_region.lower() == "usgov":
            self.purview_endpoint = f"https://{self.config.account_name}.purview.azure.us"
            self.management_endpoint = "https://management.usgovcloudapi.net"
            self.auth_scope = "https://purview.azure.us/.default"
        else:
            self.purview_endpoint = f"https://{self.config.account_name}.purview.azure.com"
            self.management_endpoint = "https://management.azure.com"
            self.auth_scope = "https://purview.azure.net/.default"

    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
        if self._credential:
            await self._credential.close()

    async def _initialize_session(self):
        """Initialize HTTP session and authentication"""
        if aiohttp is None:
            raise RuntimeError(
                "The 'aiohttp' package is required for Purview async operations. "
                "Install it in your environment (e.g. '.venv\\Scripts\\pip.exe install aiohttp' or 'pip install aiohttp')."
            )
        self._credential = DefaultAzureCredential()

        try:
            token = await self._credential.get_token(self.auth_scope)
            self._token = token.token
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)

        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "User-Agent": f"pvw-cli/2.0",
            },
        )

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with retry logic"""
        url = f"{self.purview_endpoint}{endpoint}"
        params = kwargs.get("params", {})
        params["api-version"] = DATAMAP_API_VERSION
        kwargs["params"] = params

        for attempt in range(self.config.max_retries):
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    raise

    async def _refresh_token(self):
        """Refresh authentication token"""
        token = await self._credential.get_token(self.auth_scope)
        self._token = token.token
        self._session.headers.update({"Authorization": f"Bearer {self._token}"})

    # Data Map API Methods
    async def get_entity(self, guid: str, **kwargs) -> Dict:
        """
        Get a Purview entity by its unique GUID.
        
        Args:
            guid: The unique GUID identifier of the entity
            **kwargs: Additional query parameters (e.g., minExtInfo, ignoreRelationships)
            
        Returns:
            Dict containing entity details including:
                - guid: Entity unique identifier
                - typeName: Entity type (e.g., "azure_sql_table")
                - attributes: Entity attributes (name, qualifiedName, etc.)
                - classifications: Applied classifications/tags
                - relationshipAttributes: Related entities
                
        Raises:
            ClientAuthenticationError: If authentication fails
            ValueError: If guid is invalid or entity not found
            
        Example:
            entity = await client.get_entity("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
            print(entity["attributes"]["name"])
        """
        endpoint = format_endpoint(ENDPOINTS["entity"]["get"], guid=guid)
        return await self._make_request("GET", endpoint, params=kwargs)

    async def create_entity(self, entity_data: Dict) -> Dict:
        """
        Create a new entity in the Purview catalog.
        
        Args:
            entity_data: Dictionary containing entity information with required fields:
                - typeName (str): Entity type (e.g., "azure_sql_table", "DataSet")
                - attributes (dict): Entity attributes including:
                    - name (str): Display name
                    - qualifiedName (str): Unique qualified name
                    - Additional type-specific attributes
                - Optional: classifications, relationshipAttributes
                
        Returns:
            Dict containing created entity details with assigned GUID
            
        Raises:
            ValueError: If required fields are missing or invalid
            
        Example:
            entity = await client.create_entity({
                "typeName": "DataSet",
                "attributes": {
                    "name": "Sales Data",
                    "qualifiedName": "sales_data@tenant",
                    "description": "Monthly sales records"
                }
            })
        """
        return await self._make_request(
            "POST", ENDPOINTS["entity"]["create_or_update"], json=entity_data
        )

    async def update_entity(self, entity_data: Dict) -> Dict:
        """
        Update an existing entity in the Purview catalog.
        
        Args:
            entity_data: Dictionary containing entity update with:
                - guid (str): Entity GUID to update (required)
                - typeName (str): Entity type
                - attributes (dict): Updated attributes
                
        Returns:
            Dict containing updated entity details
            
        Raises:
            ValueError: If entity not found or update fails
            
        Example:
            updated = await client.update_entity({
                "guid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "typeName": "DataSet",
                "attributes": {"description": "Updated description"}
            })
        """
        return await self._make_request(
            "PUT", ENDPOINTS["entity"]["create_or_update"], json=entity_data
        )

    async def delete_entity(self, guid: str) -> Dict:
        """
        Delete an entity from the Purview catalog.
        
        Args:
            guid: The unique GUID of the entity to delete
            
        Returns:
            Dict containing deletion status
            
        Raises:
            ValueError: If entity not found
            
        Warning:
            This operation is irreversible. All relationships and lineage will be affected.
            
        Example:
            result = await client.delete_entity("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        """
        endpoint = format_endpoint(ENDPOINTS["entity"]["delete"], guid=guid)
        return await self._make_request("DELETE", endpoint)

    async def search_entities(self, query: str, **kwargs) -> Dict:
        """
        Search for entities in the Purview catalog with advanced filtering.
        
        Args:
            query: Search keywords or query string
            **kwargs: Optional search parameters:
                - filter (dict): Filter criteria (e.g., {"typeName": "DataSet"})
                - facets (list): Facets for aggregation
                - limit (int): Maximum results to return (default: 50, max: 1000)
                - offset (int): Pagination offset (default: 0)
                
        Returns:
            Dict containing:
                - value: List of matching entities
                - @search.count: Total number of matches
                - @search.facets: Facet aggregations if requested
                
        Example:
            results = await client.search_entities(
                "sales",
                filter={"typeName": "azure_sql_table"},
                limit=100
            )
            for entity in results["value"]:
                print(entity["name"])
        """
        search_request = {
            "keywords": query,
            "filter": kwargs.get("filter"),
            "facets": kwargs.get("facets"),
            "limit": kwargs.get("limit", 50),
            "offset": kwargs.get("offset", 0),
        }
        return await self._make_request(
            "POST", ENDPOINTS["discovery"]["query"], json=search_request
        )

    # Batch Operations
    async def batch_create_entities(
        self, entities: List[Dict], progress_callback=None
    ) -> List[Dict]:
        """Create multiple entities in batches"""
        results = []
        total = len(entities)

        for i in range(0, total, self.config.batch_size):
            batch = entities[i : i + self.config.batch_size]
            batch_data = {"entities": batch}

            try:
                result = await self._make_request(
                    "POST", ENDPOINTS["entity"]["bulk_create_or_update"], json=batch_data
                )
                results.extend(result.get("mutatedEntities", {}).get("CREATE", []))

                if progress_callback:
                    progress_callback(min(i + self.config.batch_size, total), total)

            except Exception as e:
                logger.error(f"Batch {i//self.config.batch_size + 1} failed: {e}")
                continue

        return results

    async def batch_update_entities(
        self, entities: List[Dict], progress_callback=None
    ) -> List[Dict]:
        """Update multiple entities in batches"""
        results = []
        total = len(entities)

        for i in range(0, total, self.config.batch_size):
            batch = entities[i : i + self.config.batch_size]
            batch_data = {"entities": batch}

            try:
                result = await self._make_request(
                    "PUT", ENDPOINTS["entity"]["bulk_create_or_update"], json=batch_data
                )
                results.extend(result.get("mutatedEntities", {}).get("UPDATE", []))

                if progress_callback:
                    progress_callback(min(i + self.config.batch_size, total), total)

            except Exception as e:
                logger.error(f"Batch {i//self.config.batch_size + 1} failed: {e}")
                continue

        return results

    # CSV Import/Export Methods
    async def import_entities_from_csv(self, csv_file_path: str, mapping_config: Dict) -> Dict:
        """Import entities from CSV file"""
        df = pd.read_csv(csv_file_path)
        entities = []

        for _, row in df.iterrows():
            entity = self._map_csv_row_to_entity(row, mapping_config)
            if entity:
                entities.append(entity)

        return await self.batch_create_entities(entities)

    async def export_entities_to_csv(
        self, query: str, csv_file_path: str, columns: List[str] = None
    ) -> str:
        """Export entities to CSV file"""
        search_results = await self.search_entities(query, limit=1000)
        entities = search_results.get("value", [])

        if not entities:
            return "No entities found"

        # Convert entities to DataFrame
        flattened_data = []
        for entity in entities:
            flat_entity = self._flatten_entity(entity)
            flattened_data.append(flat_entity)

        df = pd.DataFrame(flattened_data)

        if columns:
            df = df[columns] if all(col in df.columns for col in columns) else df

        df.to_csv(csv_file_path, index=False)
        return f"Exported {len(entities)} entities to {csv_file_path}"

    def _map_csv_row_to_entity(self, row: pd.Series, mapping_config: Dict) -> Dict:
        """Map CSV row to Purview entity format"""
        try:
            entity = {"typeName": mapping_config.get("typeName", "DataSet"), "attributes": {}}

            # Map CSV columns to entity attributes
            for csv_col, attr_name in mapping_config.get("attributes", {}).items():
                if csv_col in row and pd.notna(row[csv_col]):
                    entity["attributes"][attr_name] = row[csv_col]

            # Add required attributes if not present
            if "name" not in entity["attributes"] and "name" in row:
                entity["attributes"]["name"] = row["name"]

            if "qualifiedName" not in entity["attributes"]:
                entity["attributes"][
                    "qualifiedName"
                ] = f"{row.get('name', 'unnamed')}@{self.config.account_name}"

            return entity
        except Exception as e:
            logger.error(f"Failed to map row to entity: {e}")
            return None

    def _flatten_entity(self, entity: Dict) -> Dict:
        """Flatten entity structure for CSV export"""
        flat = {
            "guid": entity.get("guid"),
            "typeName": entity.get("typeName"),
            "status": entity.get("status"),
        }

        # Flatten attributes
        attributes = entity.get("attributes", {})
        for key, value in attributes.items():
            if isinstance(value, (str, int, float, bool)):
                flat[f"attr_{key}"] = value
            elif isinstance(value, list) and value:
                flat[f"attr_{key}"] = ", ".join(str(v) for v in value)

        return flat  # Glossary Operations

    async def get_glossary_terms(self, glossary_guid: str = None) -> List[Dict]:
        """
        Get all glossary terms or terms from a specific glossary.
        
        Args:
            glossary_guid: Optional GUID of a specific glossary to filter terms.
                          If None, returns all terms from all glossaries.
                          
        Returns:
            List of dictionaries, each containing term information:
                - guid: Term unique identifier
                - name: Term display name
                - qualifiedName: Fully qualified term name
                - glossaryGuid: Parent glossary GUID
                - status: Term status (Draft, Approved, etc.)
                - definition: Term definition/description
                - abbreviation: Optional abbreviation
                - examples: Optional usage examples
                - attributes: Custom attributes
                - assignedEntities: Entities tagged with this term
                
        Example:
            # Get all terms
            all_terms = await client.get_glossary_terms()
            
            # Get terms from specific glossary
            glossary_terms = await client.get_glossary_terms("glossary-guid-123")
            
            for term in all_terms:
                print(f"{term['name']}: {term.get('definition', 'No definition')}")
        """
        if glossary_guid:
            endpoint = f"{ENDPOINTS['glossary']['terms']}/{glossary_guid}"
        else:
            endpoint = ENDPOINTS["glossary"]["base"]
        return await self._make_request("GET", endpoint)

    async def create_glossary_term(self, term_data: Dict) -> Dict:
        """
        Create a new glossary term in Purview.
        
        Args:
            term_data: Dictionary containing term information with required fields:
                - name (str): Term display name (required)
                - glossaryGuid (str): Parent glossary GUID (required)
                - Optional fields:
                    - qualifiedName (str): Auto-generated if not provided
                    - definition (str): Term definition/description
                    - abbreviation (str): Short form
                    - status (str): "Draft", "Approved", "Alert", "Expired"
                    - nickName (str): Alternative name
                    - examples (list): Usage examples
                    - resources (list): Related resources/links
                    - contacts (dict): Experts, owners, stewards
                    - attributes (dict): Custom attributes
                    
        Returns:
            Dict containing created term with assigned GUID
            
        Raises:
            ValueError: If required fields are missing or glossary not found
            
        Example:
            term = await client.create_glossary_term({
                "name": "Customer",
                "glossaryGuid": "glossary-guid-123",
                "definition": "An individual or organization that purchases goods or services",
                "status": "Approved",
                "abbreviation": "CUST",
                "examples": ["Enterprise customer", "Retail customer"]
            })
            print(f"Created term: {term['guid']}")
        """
        return await self._make_request("POST", ENDPOINTS["glossary"]["term"], json=term_data)

    async def assign_term_to_entities(self, term_guid: str, entity_guids: List[str]) -> Dict:
        """
        Assign a glossary term to multiple entities for business context tagging.
        
        Args:
            term_guid: The unique GUID of the glossary term to assign
            entity_guids: List of entity GUIDs to tag with this term
            
        Returns:
            Dict containing assignment results with success/failure details
            
        Raises:
            ValueError: If term or entities not found
            
        Use Case:
            Tag data assets with business glossary terms to provide business context
            and enable business users to discover data using familiar terminology.
            
        Example:
            # Tag multiple tables with "Customer" term
            result = await client.assign_term_to_entities(
                term_guid="term-guid-abc",
                entity_guids=[
                    "table-guid-1",
                    "table-guid-2",
                    "table-guid-3"
                ]
            )
            print(f"Tagged {len(entity_guids)} entities")
        """
        assignment_data = {"termGuid": term_guid, "entityGuids": entity_guids}
        endpoint = f"{ENDPOINTS['glossary']['term_assigned_entities']}/{term_guid}"
        return await self._make_request("POST", endpoint, json=assignment_data)

    # Data Estate Insights
    async def get_asset_distribution(self) -> Dict:
        """Get asset distribution insights"""
        return await self._make_request("GET", "/mapanddiscover/api/browse")

        # === ACCOUNT MANAGEMENT (Official API Operations) ===    async def get_account_properties(self) -> Dict:
        """Get Account Properties - Official API Operation"""
        params = get_api_version_params("account")
        return await self._make_request("GET", ENDPOINTS["account"]["account"], params=params)

    async def update_account_properties(self, account_data: Dict) -> Dict:
        """Update Account Properties - Official API Operation"""
        params = get_api_version_params("account")
        return await self._make_request(
            "PATCH", ENDPOINTS["account"]["account_update"], json=account_data, params=params
        )

    async def get_access_keys(self) -> Dict:
        """Get Access Keys - Official API Operation"""
        params = get_api_version_params("account")
        return await self._make_request("POST", ENDPOINTS["account"]["access_keys"], params=params)

    async def regenerate_access_key(self, key_data: Dict) -> Dict:
        """Regenerate Access Key - Official API Operation"""
        params = get_api_version_params("account")
        return await self._make_request(
            "POST", ENDPOINTS["account"]["regenerate_access_key"], json=key_data, params=params
        )

        # === COLLECTIONS MANAGEMENT (Official API Operations) ===

    async def list_collections(self) -> List[Dict]:
        """
        List all collections in the Purview account.
        
        Collections organize data assets into logical hierarchies for access control
        and governance. They form a tree structure with parent-child relationships.
        
        Returns:
            List of dictionaries, each containing collection information:
                - name: Collection unique name/identifier
                - friendlyName: Human-readable display name
                - description: Collection description
                - collectionProvisioningState: State (e.g., "Succeeded")
                - parentCollection: Parent collection reference
                - systemData: Creation/modification metadata
                
        Example:
            collections = await client.list_collections()
            for col in collections:
                print(f"{col['friendlyName']} ({col['name']})")
                print(f"  Parent: {col.get('parentCollection', {}).get('referenceName', 'Root')}")
        """
        params = get_api_version_params("collections")
        return await self._make_request("GET", ENDPOINTS["collections"]["list"], params=params)

    async def get_collection(self, collection_name: str) -> Dict:
        """
        Get detailed information about a specific collection.
        
        Args:
            collection_name: The unique name (not friendlyName) of the collection
            
        Returns:
            Dict containing collection details including name, friendlyName, description,
            parent relationships, and provisioning state
            
        Raises:
            ValueError: If collection not found
            
        Example:
            collection = await client.get_collection("myorg-finance")
            print(f"Collection: {collection['friendlyName']}")
            print(f"Description: {collection.get('description', 'N/A')}")
        """
        endpoint = format_endpoint(ENDPOINTS["collections"]["get"], collectionName=collection_name)
        params = get_api_version_params("collections")
        return await self._make_request("GET", endpoint, params=params)

    async def create_collection(self, collection_name: str, collection_data: Dict) -> Dict:
        """Create Collection - Official API Operation"""
        endpoint = format_endpoint(
            ENDPOINTS["collections"]["create_or_update"], collectionName=collection_name
        )
        params = get_api_version_params("collections")
        return await self._make_request("PUT", endpoint, json=collection_data, params=params)

    async def update_collection(self, collection_name: str, collection_data: Dict) -> Dict:
        """Update Collection - Official API Operation"""
        endpoint = format_endpoint(
            ENDPOINTS["collections"]["create_or_update"], collectionName=collection_name
        )
        params = get_api_version_params("collections")
        return await self._make_request("PUT", endpoint, json=collection_data, params=params)

    async def create_or_update_collection(
        self, collection_name: str, collection_data: Dict
    ) -> Dict:
        """Create Or Update Collection - Official API Operation (Backward Compatibility)"""
        endpoint = format_endpoint(
            ENDPOINTS["collections"]["create_or_update"], collectionName=collection_name
        )
        params = get_api_version_params("collections")
        return await self._make_request("PUT", endpoint, json=collection_data, params=params)

    async def delete_collection(self, collection_name: str) -> Dict:
        """Delete Collection - Official API Operation"""
        endpoint = format_endpoint(
            ENDPOINTS["collections"]["delete"], collectionName=collection_name
        )
        params = get_api_version_params("collections")
        return await self._make_request("DELETE", endpoint, params=params)

    async def get_collection_path(self, collection_name: str) -> Dict:
        """Get Collection Path - Official API Operation"""
        endpoint = format_endpoint(
            ENDPOINTS["collections"]["get_collection_path"], collectionName=collection_name
        )
        params = get_api_version_params("collections")
        return await self._make_request("GET", endpoint, params=params)

    async def get_child_collection_names(self, collection_name: str) -> List[str]:
        """List Child Collection Names - Official API Operation"""
        endpoint = format_endpoint(
            ENDPOINTS["collections"]["get_child_collection_names"], collectionName=collection_name
        )
        params = get_api_version_params("collections")
        return await self._make_request("GET", endpoint, params=params)

    # Lineage Operations
    async def get_lineage(self, guid: str, direction: str = "BOTH", depth: int = 3) -> Dict:
        """
        Get data lineage for an entity showing upstream sources and downstream consumers.
        
        Data lineage tracks how data flows between systems, showing transformation paths
        and dependencies critical for impact analysis and compliance.
        
        Args:
            guid: The unique GUID of the entity to get lineage for
            direction: Lineage direction to retrieve:
                - "INPUT": Upstream sources (where data comes from)
                - "OUTPUT": Downstream consumers (where data goes to)
                - "BOTH": Both upstream and downstream (default)
            depth: How many levels deep to traverse (default: 3, max: 10)
                  Higher depths may return large result sets
                  
        Returns:
            Dict containing:
                - baseEntityGuid: Starting entity GUID
                - guidEntityMap: Map of all entities in the lineage graph
                - relations: List of lineage relationships showing data flow
                - widthCounts: Entity counts at each lineage level
                - lineageDirection: Requested direction
                - lineageDepth: Requested depth
                
        Use Cases:
            - Impact analysis: "What will break if I change this table?"
            - Data tracing: "Where does this report's data come from?"
            - Compliance: "Show the complete data flow for audit"
            
        Example:
            # Get full lineage for a table
            lineage = await client.get_lineage(
                guid="table-guid-abc",
                direction="BOTH",
                depth=5
            )
            
            # Analyze upstream sources
            for rel in lineage["relations"]:
                if rel["relationshipType"] == "UPSTREAM":
                    source = lineage["guidEntityMap"][rel["fromEntityId"]]
                    print(f"Source: {source['displayName']}")
        """
        params = {"direction": direction, "depth": depth}
        endpoint = f"{ENDPOINTS['lineage']['lineage']}/{guid}"
        return await self._make_request("GET", endpoint, params=params)

    async def create_lineage(self, lineage_data: Dict) -> Dict:
        """
        Create a data lineage relationship between entities.
        
        Use this to document custom data flows, ETL processes, or transformations
        not automatically discovered by Purview scanners.
        
        Args:
            lineage_data: Dictionary containing lineage relationship with:
                - typeName (str): Process type (e.g., "Process", "spark_process")
                - attributes (dict):
                    - name (str): Process name
                    - qualifiedName (str): Unique identifier
                    - inputs (list): List of input entity references
                    - outputs (list): List of output entity references
                    
        Returns:
            Dict containing created lineage process entity
            
        Example:
            # Document an ETL process
            lineage = await client.create_lineage({
                "typeName": "Process",
                "attributes": {
                    "name": "Daily Sales ETL",
                    "qualifiedName": "etl_sales_daily@tenant",
                    "inputs": [
                        {"guid": "source-table-guid"}
                    ],
                    "outputs": [
                        {"guid": "target-table-guid"}
                    ]
                }
            })
        """
        return await self._make_request("POST", ENDPOINTS["lineage"]["lineage"], json=lineage_data)

    # === CSV IMPORT/EXPORT OPERATIONS ===

    async def import_collections_from_csv(self, csv_file_path: str, progress_callback=None) -> Dict:
        """Import Collections from CSV file"""
        import pandas as pd

        if not os.path.exists(csv_file_path):
            raise ValueError(f"CSV file not found: {csv_file_path}")

        try:
            df = pd.read_csv(csv_file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")

        # Validate required columns
        required_columns = ["collectionName", "friendlyName"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. Required: {required_columns}"
            )

        results = []
        total_rows = len(df)

        for index, row in df.iterrows():
            try:
                collection_name = row["collectionName"]
                collection_data = {
                    "friendlyName": row.get("friendlyName", collection_name),
                    "description": row.get("description", ""),
                    "parentCollection": {"referenceName": row.get("parentCollection", "root")},
                }

                # Create the collection
                result = await self.create_collection(collection_name, collection_data)
                results.append(
                    {
                        "row": index + 1,
                        "collectionName": collection_name,
                        "status": "success",
                        "result": result,
                    }
                )

                if progress_callback:
                    progress_callback(index + 1, total_rows)

            except Exception as e:
                results.append(
                    {
                        "row": index + 1,
                        "collectionName": row.get("collectionName", "unknown"),
                        "status": "error",
                        "error": str(e),
                    }
                )

        return {
            "total_processed": len(results),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "details": results,
        }

    async def export_collections_to_csv(
        self, csv_file_path: str, include_hierarchy: bool = True, include_metadata: bool = True
    ) -> str:
        """Export Collections to CSV file"""
        import pandas as pd

        try:
            # Get all collections
            collections_data = await self.list_collections()

            if not collections_data or "value" not in collections_data:
                return "No collections found to export"

            collections = collections_data["value"]
            export_data = []

            for collection in collections:
                row_data = {
                    "collectionName": collection.get("name", ""),
                    "friendlyName": collection.get("friendlyName", ""),
                    "description": collection.get("description", ""),
                    "parentCollection": collection.get("parentCollection", {}).get(
                        "referenceName", "root"
                    ),
                }

                if include_hierarchy:
                    # Try to get collection path for hierarchy info
                    try:
                        if collection.get("name"):
                            path_data = await self.get_collection_path(collection["name"])
                            row_data["collectionPath"] = " > ".join(path_data.get("path", []))
                            row_data["level"] = len(path_data.get("path", [])) - 1
                    except:
                        row_data["collectionPath"] = ""
                        row_data["level"] = 0

                if include_metadata:
                    row_data["systemData_createdAt"] = collection.get("systemData", {}).get(
                        "createdAt", ""
                    )
                    row_data["systemData_lastModifiedAt"] = collection.get("systemData", {}).get(
                        "lastModifiedAt", ""
                    )
                    row_data["systemData_createdBy"] = collection.get("systemData", {}).get(
                        "createdBy", ""
                    )

                export_data.append(row_data)

            # Create DataFrame and export to CSV
            df = pd.DataFrame(export_data)
            df.to_csv(csv_file_path, index=False)

            return f"Successfully exported {len(export_data)} collections to {csv_file_path}"

        except Exception as e:
            raise Exception(f"Failed to export collections to CSV: {str(e)}")


class BatchOperationProgress:
    """Progress tracker for batch operations"""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.processed = 0
        self.description = description
        self.start_time = datetime.now()

    def update(self, processed: int, total: int):
        """Update progress"""
        self.processed = processed
        self.total = total
        percentage = (processed / total) * 100 if total > 0 else 0
        elapsed = datetime.now() - self.start_time

        print(
            f"\r{self.description}: {processed}/{total} ({percentage:.1f}%) - Elapsed: {elapsed}",
            end="",
            flush=True,
        )

        if processed >= total:
            print()  # New line when complete
