"""
Synchronous Purview Client for CLI compatibility
"""

import requests
import os
import json
from typing import Dict, Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ssl
import urllib3


class SyncPurviewConfig:
    """Simple synchronous config"""

    def __init__(self, account_name: str, azure_region: str = "public", account_id: Optional[str] = None):
        self.account_name = account_name
        self.azure_region = azure_region
        self.account_id = account_id  # Optional Purview account ID for UC endpoints


class SyncPurviewClient:
    """Synchronous client for CLI operations with real Azure authentication"""

    def __init__(self, config: SyncPurviewConfig):
        self.config = config

        # Set up regular Purview API endpoints based on Azure region, using account name in the URL
        if config.azure_region and config.azure_region.lower() == "china":
            self.base_url = f"https://{config.account_name}.purview.azure.cn"
            self.auth_scope = "https://purview.azure.cn/.default"
        elif config.azure_region and config.azure_region.lower() == "usgov":
            self.base_url = f"https://{config.account_name}.purview.azure.us"
            self.auth_scope = "https://purview.azure.us/.default"
        else:
            self.base_url = f"https://{config.account_name}.purview.azure.com"
            self.auth_scope = "https://purview.azure.net/.default"

        # Set up Unified Catalog endpoint using Purview account ID format
        self.account_id = config.account_id or self._get_purview_account_id()
        self.uc_base_url = f"https://{self.account_id}-api.purview-service.microsoft.com"
        self.uc_auth_scope = "73c2949e-da2d-457a-9607-fcc665198967/.default"

        self._token = None
        self._uc_token = None
        self._credential = None
        
        # Configure session with retry strategy for Azure Front Door SSL issues
        self._session = self._create_session_with_retries()

    def _create_session_with_retries(self):
        """Create a requests session with retry strategy and SSL workarounds for Azure Front Door"""
        session = requests.Session()
        
        # Retry strategy for transient errors and SSL issues
        retry_strategy = Retry(
            total=5,  # Total number of retries
            backoff_factor=1,  # Wait 1, 2, 4, 8, 16 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]  # Retry on all methods
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # Workaround for Azure Front Door SSL issues (TLS inspection, protocol mismatch)
        # Disable SSL verification warnings (only if needed in corporate environments)
        if os.getenv("PURVIEW_DISABLE_SSL_VERIFY", "false").lower() == "true":
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            session.verify = False
        
        return session

    def _get_purview_account_id(self):
        """Get Purview account ID from Atlas endpoint URL"""
        account_id = os.getenv("PURVIEW_ACCOUNT_ID")
        if not account_id:
            import subprocess
            try:
                # Get the Atlas catalog endpoint and extract account ID from it
                result = subprocess.run([
                    "az", "purview", "account", "show", 
                    "--name", self.config.account_name,
                    "--resource-group", os.getenv("PURVIEW_RESOURCE_GROUP", "fabric-artifacts"),
                    "--query", "endpoints.catalog", 
                    "-o", "tsv"
                ], capture_output=True, text=True, check=True)
                atlas_url = result.stdout.strip()
                
                if atlas_url and "-api.purview-service.microsoft.com" in atlas_url:
                    account_id = atlas_url.split("://")[1].split("-api.purview-service.microsoft.com")[0]
                else:
                    raise Exception(f"Could not extract account ID from Atlas URL: {atlas_url}")
            except Exception as e:
                # For Unified Catalog, the account ID is typically the Azure Tenant ID
                try:
                    tenant_result = subprocess.run([
                        "az", "account", "show", "--query", "tenantId", "-o", "tsv"
                    ], capture_output=True, text=True, check=True)
                    account_id = tenant_result.stdout.strip()
                    print(f"Info: Using Tenant ID as Purview Account ID for Unified Catalog: {account_id}")
                except Exception:
                    raise Exception(f"Could not determine Purview account ID. For Unified Catalog, this is typically your Azure Tenant ID. Please set PURVIEW_ACCOUNT_ID environment variable. Error: {e}")
        return account_id

    def _get_authentication_token(self, for_unified_catalog=False):
        """Get Azure authentication token for regular Purview or Unified Catalog APIs"""
        try:
            # Try different authentication methods in order of preference

            # 1. Try client credentials if available
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            tenant_id = os.getenv("AZURE_TENANT_ID")

            if client_id and client_secret and tenant_id:
                self._credential = ClientSecretCredential(
                    tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
                )
            else:
                # 2. Use default credential (managed identity, VS Code, CLI, etc.)
                self._credential = DefaultAzureCredential()

            # Get the appropriate token based on the API type
            if for_unified_catalog:
                token = self._credential.get_token(self.uc_auth_scope)
                self._uc_token = token.token
                return self._uc_token
            else:
                token = self._credential.get_token(self.auth_scope)
                self._token = token.token
                return self._token

        except ClientAuthenticationError as e:
            raise Exception(f"Azure authentication failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get authentication token: {str(e)}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make actual HTTP request to Microsoft Purview"""
        try:
            # Determine if this is a Unified Catalog / Data Map (Atlas) request
            # Several endpoints use '/catalog' or '/datamap' prefixes (Atlas/DataMap APIs)
            is_unified_catalog = (
                endpoint.startswith('/datagovernance/catalog')
                or endpoint.startswith('/catalog')
                or endpoint.startswith('/datamap')
            )
            
            # Get the appropriate authentication token and base URL
            if is_unified_catalog:
                if not self._uc_token:
                    self._get_authentication_token(for_unified_catalog=True)
                token = self._uc_token
                base_url = self.uc_base_url
            else:
                if not self._token:
                    self._get_authentication_token(for_unified_catalog=False)
                token = self._token
                base_url = self.base_url
            
            # Prepare the request
            url = f"{base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "purviewcli/2.0",
            }
            
            # Handle file uploads vs JSON payload
            files = kwargs.get("files")
            custom_headers = kwargs.get("headers", {})
            
            if files:
                # For multipart/form-data uploads, don't set Content-Type
                # Let requests library handle it automatically
                headers.update(custom_headers)
            else:
                # For JSON payloads
                headers["Content-Type"] = "application/json"
                headers.update(custom_headers)

            # Make the actual HTTP request using session with retries
            response = self._session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=kwargs.get("params"),
                json=kwargs.get("json") if not files else None,
                files=files,
                timeout=60,  # Increased timeout for Azure Front Door
            )
            # Handle the response
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    return {"status": "success", "data": data, "status_code": response.status_code}
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "data": response.text,
                        "status_code": response.status_code,
                    }
            elif response.status_code == 401:
                # Token might be expired, try to refresh
                if is_unified_catalog:
                    self._uc_token = None
                    self._get_authentication_token(for_unified_catalog=True)
                    token = self._uc_token
                else:
                    self._token = None
                    self._get_authentication_token(for_unified_catalog=False)
                    token = self._token
                    
                headers["Authorization"] = f"Bearer {token}"

                # Retry the request with session
                response = self._session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=kwargs.get("params"),
                    json=kwargs.get("json") if not files else None,
                    files=files,
                    timeout=60,
                )

                if response.status_code in [200, 201]:
                    try:
                        data = response.json()
                        return {
                            "status": "success",
                            "data": data,
                            "status_code": response.status_code,
                        }
                    except json.JSONDecodeError:
                        return {
                            "status": "success",
                            "data": response.text,
                            "status_code": response.status_code,
                        }
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status_code}: {response.text}",
                        "status_code": response.status_code,
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Request timed out after 30 seconds"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"Failed to connect to {self.base_url}"}
        except Exception as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}
