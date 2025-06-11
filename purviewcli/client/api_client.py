"""
 Azure Purview API Client
Supports the latest Azure Purview REST API specifications with comprehensive automation capabilities
"""

import json
import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
import logging
from datetime import datetime
import os
import sys
from .endpoints import PurviewEndpoints

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

        for attempt in range(self.config.max_retries):
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        # Token might be expired, refresh it
                        await self._refresh_token()
                        continue
                    else:
                        response.raise_for_status()
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def _refresh_token(self):
        """Refresh authentication token"""
        token = await self._credential.get_token(self.auth_scope)
        self._token = token.token
        self._session.headers.update(
            {"Authorization": f"Bearer {self._token}"}
        )  # Data Map API Methods

    async def get_entity(self, guid: str, **kwargs) -> Dict:
        """Get entity by GUID"""
        params = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["guid"], guid=guid)
        return await self._make_request("GET", endpoint, params=params)

    async def create_entity(self, entity_data: Dict) -> Dict:
        """Create new entity"""
        return await self._make_request("POST", PurviewEndpoints.ENTITY["base"], json=entity_data)

    async def update_entity(self, entity_data: Dict) -> Dict:
        """Update existing entity"""
        return await self._make_request("PUT", PurviewEndpoints.ENTITY["base"], json=entity_data)

    async def delete_entity(self, guid: str) -> Dict:
        """Delete entity by GUID"""
        endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["guid"], guid=guid)
        return await self._make_request("DELETE", endpoint)

    async def search_entities(self, query: str, **kwargs) -> Dict:
        """Search entities with advanced filters"""
        search_request = {
            "keywords": query,
            "filter": kwargs.get("filter"),
            "facets": kwargs.get("facets"),
            "limit": kwargs.get("limit", 50),
            "offset": kwargs.get("offset", 0),
        }
        return await self._make_request(
            "POST", PurviewEndpoints.SEARCH["query"], json=search_request
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
                    "POST", PurviewEndpoints.ENTITY["bulk"], json=batch_data
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
                    "PUT", PurviewEndpoints.ENTITY["bulk"], json=batch_data
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
        """Get all glossary terms"""
        if glossary_guid:
            endpoint = PurviewEndpoints.format_endpoint(
                PurviewEndpoints.GLOSSARY["terms"], glossaryGuid=glossary_guid
            )
        else:
            endpoint = PurviewEndpoints.GLOSSARY["base"]
        return await self._make_request("GET", endpoint)

    async def create_glossary_term(self, term_data: Dict) -> Dict:
        """Create glossary term"""
        return await self._make_request("POST", PurviewEndpoints.GLOSSARY["term"], json=term_data)

    async def assign_term_to_entities(self, term_guid: str, entity_guids: List[str]) -> Dict:
        """Assign glossary term to multiple entities"""
        assignment_data = {"termGuid": term_guid, "entityGuids": entity_guids}
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.GLOSSARY["term_assigned_entities"], termGuid=term_guid
        )
        return await self._make_request("POST", endpoint, json=assignment_data)

    # Data Estate Insights
    async def get_asset_distribution(self) -> Dict:
        """Get asset distribution insights"""
        return await self._make_request("GET", "/mapanddiscover/api/browse")

    # === ACCOUNT MANAGEMENT (Official API Operations) ===

    async def get_account_properties(self) -> Dict:
        """Get Account Properties - Official API Operation"""
        params = PurviewEndpoints.get_api_version_params("account")
        return await self._make_request("GET", PurviewEndpoints.ACCOUNT["account"], params=params)

    async def update_account_properties(self, account_data: Dict) -> Dict:
        """Update Account Properties - Official API Operation"""
        params = PurviewEndpoints.get_api_version_params("account")
        return await self._make_request(
            "PATCH", PurviewEndpoints.ACCOUNT["account_update"], json=account_data, params=params
        )

    async def get_access_keys(self) -> Dict:
        """Get Access Keys - Official API Operation"""
        params = PurviewEndpoints.get_api_version_params("account")
        return await self._make_request(
            "POST", PurviewEndpoints.ACCOUNT["access_keys"], params=params
        )

    async def regenerate_access_key(self, key_data: Dict) -> Dict:
        """Regenerate Access Key - Official API Operation"""
        params = PurviewEndpoints.get_api_version_params("account")
        return await self._make_request(
            "POST", PurviewEndpoints.ACCOUNT["regenerate_access_key"], json=key_data, params=params
        )

    # === COLLECTIONS MANAGEMENT (Official API Operations) ===

    async def list_collections(self) -> List[Dict]:
        """List Collections - Official API Operation"""
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("GET", PurviewEndpoints.COLLECTIONS["base"], params=params)

    async def get_collection(self, collection_name: str) -> Dict:
        """Get Collection - Official API Operation"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("GET", endpoint, params=params)

    async def create_collection(self, collection_name: str, collection_data: Dict) -> Dict:
        """Create Collection - Official API Operation"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("PUT", endpoint, json=collection_data, params=params)

    async def update_collection(self, collection_name: str, collection_data: Dict) -> Dict:
        """Update Collection - Official API Operation"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("PUT", endpoint, json=collection_data, params=params)

    async def create_or_update_collection(
        self, collection_name: str, collection_data: Dict
    ) -> Dict:
        """Create Or Update Collection - Official API Operation (Backward Compatibility)"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("PUT", endpoint, json=collection_data, params=params)

    async def delete_collection(self, collection_name: str) -> Dict:
        """Delete Collection - Official API Operation"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("DELETE", endpoint, params=params)

    async def get_collection_path(self, collection_name: str) -> Dict:
        """Get Collection Path - Official API Operation"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection_path"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("GET", endpoint, params=params)

    async def get_child_collection_names(self, collection_name: str) -> List[str]:
        """List Child Collection Names - Official API Operation"""
        endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["child_collection_names"], collectionName=collection_name
        )
        params = PurviewEndpoints.get_api_version_params("collections")
        return await self._make_request("GET", endpoint, params=params)

    # Lineage Operations
    async def get_lineage(self, guid: str, direction: str = "BOTH", depth: int = 3) -> Dict:
        """Get entity lineage"""
        params = {"direction": direction, "depth": depth}
        endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.LINEAGE["lineage"], guid=guid)
        return await self._make_request("GET", endpoint, params=params)

    async def create_lineage(self, lineage_data: Dict) -> Dict:
        """Create lineage relationship"""
        return await self._make_request(
            "POST", PurviewEndpoints.LINEAGE["lineage"], json=lineage_data
        )

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
