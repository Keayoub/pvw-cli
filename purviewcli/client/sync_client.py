"""
Synchronous Purview Client for CLI compatibility
"""

import requests
import os
import json
import subprocess
import logging
from typing import Dict, Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ssl
import urllib3

# Configure logging
logger = logging.getLogger(__name__)


# Custom Authentication Exceptions
class PurviewAuthenticationError(Exception):
    """Base exception for Purview authentication errors"""
    pass


class AzureCliNotFoundError(PurviewAuthenticationError):
    """Raised when Azure CLI is not installed or not available"""
    pass


class AzureCliAuthenticationError(PurviewAuthenticationError):
    """Raised when Azure CLI authentication fails"""
    pass


class AzureCredentialsError(PurviewAuthenticationError):
    """Raised when Azure credentials are not properly configured"""
    pass


class InvalidServicePrincipalError(PurviewAuthenticationError):
    """Raised when service principal is not registered in the tenant"""
    pass


class TokenExpirationError(PurviewAuthenticationError):
    """Raised when token expiration cannot be parsed"""
    pass


class AzureCliCredentialFixed:
    """Custom Azure CLI credential that properly handles Purview scope"""
    
    def get_token(self, *scopes, **kwargs):
        """Get token using az account get-access-token with correct scope"""
        try:
            # Extract the resource from scope (e.g., "https://purview.azure.net/.default" -> "https://purview.azure.net")
            scope = scopes[0] if scopes else ""
            resource = scope.replace("/.default", "")
            
            logger.debug(f"Attempting Azure CLI authentication for resource: {resource}")
            
            # Use az account get-access-token with the correct resource
            # Try 'az' and 'az.cmd' (Windows)
            result = None
            last_error = None
            
            for az_cmd in ["az", "az.cmd"]:
                try:
                    result = subprocess.run(
                        [az_cmd, "account", "get-access-token", "--resource", resource, "--output", "json"],
                        capture_output=True,
                        text=True,
                        check=False,  # Don't raise, we handle errors manually
                        shell=True  # Use shell on Windows
                    )
                    
                    if result.returncode == 0:
                        logger.debug("Successfully obtained token from Azure CLI")
                        break
                    else:
                        last_error = result.stderr
                        logger.debug(f"Azure CLI ({az_cmd}) returned code {result.returncode}: {result.stderr[:200]}")
                        
                except (FileNotFoundError, OSError) as e:
                    logger.debug(f"Azure CLI command '{az_cmd}' not found: {e}")
                    last_error = str(e)
                    continue
            
            if not result or result.returncode != 0:
                error_msg = last_error or "Unknown error"
                
                # Check for specific error patterns
                if "not found in the tenant" in error_msg or "AADSTS500011" in error_msg:
                    raise InvalidServicePrincipalError(
                        f"The Purview service principal is not registered in your Azure AD tenant. "
                        f"Your Azure AD administrator must register it. Error: {error_msg[:200]}"
                    )
                elif "Authentication failed" in error_msg or "AADSTS" in error_msg:
                    raise AzureCliAuthenticationError(
                        f"Azure CLI authentication failed. Please ensure you are logged in with 'az login' "
                        f"and have the necessary permissions. Error: {error_msg[:200]}"
                    )
                else:
                    raise AzureCliAuthenticationError(f"Azure CLI error: {error_msg[:300]}")
            
            try:
                token_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Azure CLI response: {result.stdout[:100]}")
                raise AzureCliAuthenticationError(f"Invalid JSON response from Azure CLI: {str(e)}")
            
            if "accessToken" not in token_data:
                raise AzureCliAuthenticationError("No access token in Azure CLI response")
            
            # Parse expiresOn - can be either timestamp or datetime string
            from datetime import datetime
            expires_on_str = str(token_data.get("expiresOn", "0"))
            
            try:
                # Try as timestamp first
                expires_on = int(expires_on_str)
            except ValueError:
                # Try parsing as datetime string (e.g., "2026-01-26 10:59:31.000000")
                try:
                    dt = datetime.strptime(expires_on_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
                    expires_on = int(dt.timestamp())
                except Exception as e:
                    logger.warning(f"Could not parse token expiration time '{expires_on_str}': {e}")
                    raise TokenExpirationError(f"Failed to parse token expiration: {expires_on_str}")
            
            logger.debug(f"Token obtained successfully, expires in ~{(expires_on - int(datetime.now().timestamp())) // 3600} hours")
            return AccessToken(token=token_data["accessToken"], expires_on=expires_on)
            
        except PurviewAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AzureCliCredentialFixed: {e}")
            raise AzureCliAuthenticationError(f"Unexpected authentication error: {str(e)}")


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
            # Allow override via environment variable for special tenants using legacy service principal
            self.auth_scope = os.environ.get("PURVIEW_AUTH_SCOPE", "https://purview.azure.net/.default")

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
        api_type = "Unified Catalog" if for_unified_catalog else "Purview"
        auth_scope = self.uc_auth_scope if for_unified_catalog else self.auth_scope
        
        try:
            # 1. Try client credentials from environment if available
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            tenant_id = os.getenv("AZURE_TENANT_ID")

            if client_id and client_secret and tenant_id:
                try:
                    logger.debug(f"Attempting authentication with service principal: {client_id}")
                    self._credential = ClientSecretCredential(
                        tenant_id=tenant_id, 
                        client_id=client_id, 
                        client_secret=client_secret
                    )
                    token = self._credential.get_token(auth_scope)
                    logger.info(f"Successfully authenticated using service principal for {api_type} API")
                    return token.token
                except ClientAuthenticationError as e:
                    error_msg = str(e)
                    if "not found in the tenant" in error_msg or "AADSTS500011" in error_msg:
                        raise InvalidServicePrincipalError(
                            f"The Purview service principal is not registered in tenant {tenant_id}. "
                            f"Your Azure AD administrator must register the service principal. "
                            f"Ask them to run: New-AzureADServicePrincipal -AppId 73c2949e-da2d-457a-9607-fcc665198967"
                        )
                    else:
                        raise AzureCredentialsError(f"Service principal authentication failed: {error_msg[:300]}")
                except Exception as e:
                    logger.error(f"Service principal authentication error: {e}")
                    raise AzureCredentialsError(f"Unexpected error with service principal: {str(e)}")
            
            # 2. Try Azure CLI credential (handles az login)
            logger.debug("Attempting authentication with Azure CLI")
            try:
                self._credential = AzureCliCredentialFixed()
                token = self._credential.get_token(auth_scope)
                logger.info(f"Successfully authenticated using Azure CLI for {api_type} API")
                return token.token
            except InvalidServicePrincipalError as e:
                logger.error(f"Service principal not registered: {e}")
                raise
            except AzureCliAuthenticationError as e:
                logger.debug(f"Azure CLI authentication failed, will try default credential: {e}")
            except AzureCliNotFoundError as e:
                logger.debug(f"Azure CLI not found: {e}")
            
            # 3. Fall back to DefaultAzureCredential (managed identity, VS Code, etc.)
            logger.debug("Attempting authentication with DefaultAzureCredential (managed identity, VS Code, etc.)")
            try:
                self._credential = DefaultAzureCredential()
                token = self._credential.get_token(auth_scope)
                logger.info(f"Successfully authenticated using system credentials for {api_type} API")
                return token.token
            except ClientAuthenticationError as e:
                error_msg = str(e)
                if "not found in the tenant" in error_msg or "AADSTS500011" in error_msg:
                    raise InvalidServicePrincipalError(
                        f"The Purview service principal is not registered in your Azure AD tenant. "
                        f"Your Azure AD administrator must register it. "
                        f"Command: New-AzureADServicePrincipal -AppId 73c2949e-da2d-457a-9607-fcc665198967"
                    )
                else:
                    raise AzureCredentialsError(f"Default credential authentication failed: {error_msg[:300]}")

        except InvalidServicePrincipalError:
            # Re-raise service principal errors as-is
            raise
        except PurviewAuthenticationError:
            # Re-raise specific Purview auth errors
            raise
        except ClientAuthenticationError as e:
            logger.error(f"Azure authentication error: {e}")
            raise AzureCredentialsError(
                f"Azure AD authentication failed. "
                f"Please ensure you are logged in with 'az login' and have the necessary permissions to access Purview. "
                f"Error: {str(e)[:300]}"
            )
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}", exc_info=True)
            raise PurviewAuthenticationError(
                f"Failed to authenticate to {api_type} API. "
                f"Please ensure you have configured Azure credentials properly. "
                f"Use 'az login' or set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID. "
                f"Error: {str(e)[:300]}"
            )

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make actual HTTP request to Microsoft Purview"""
        try:
            # Determine if this is a Unified Catalog / Data Map (Atlas) request
            is_unified_catalog = (
                endpoint.startswith('/datagovernance/catalog')
                or endpoint.startswith('/catalog')
                or endpoint.startswith('/datamap')
            )
            
            # Get the appropriate authentication token and base URL
            if is_unified_catalog:
                if not self._uc_token:
                    self._uc_token = self._get_authentication_token(for_unified_catalog=True)
                token = self._uc_token
                base_url = self.uc_base_url
            else:
                if not self._token:
                    self._token = self._get_authentication_token(for_unified_catalog=False)
                token = self._token
                base_url = self.base_url
            
            # Verify we got a token
            if not token:
                api_type = "Unified Catalog" if is_unified_catalog else "Purview"
                logger.error(f"Failed to get authentication token for {api_type} API")
                return {
                    "status": "error",
                    "message": f"Failed to authenticate to {api_type} API. Token is None.",
                    "status_code": 401,
                }
            
            # Prepare the request
            url = f"{base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "purviewcli/1.6.0",
            }
            
            # Handle file uploads vs JSON payload
            files = kwargs.get("files")
            custom_headers = kwargs.get("headers", {})
            
            if files:
                headers.update(custom_headers)
            else:
                headers["Content-Type"] = "application/json"
                headers.update(custom_headers)

            logger.debug(f"Making {method.upper()} request to {url}")
            logger.debug(f"Using {'Unified Catalog' if is_unified_catalog else 'Purview'} API")
            logger.debug(f"Token (first 20 chars): {token[:20]}...")
            
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
                    logger.debug(f"Response received: {response.status_code}")
                    return {"status": "success", "data": data, "status_code": response.status_code}
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "data": response.text,
                        "status_code": response.status_code,
                    }
            elif response.status_code == 401:
                # Unauthorized - token expired or insufficient permissions
                logger.warning(f"Received 401 Unauthorized: {response.text}")
                logger.debug(f"Attempting to refresh token for {'Unified Catalog' if is_unified_catalog else 'Purview'} API")
                try:
                    if is_unified_catalog:
                        self._uc_token = None
                        self._credential = None  # Force re-authentication
                        self._uc_token = self._get_authentication_token(for_unified_catalog=True)
                        token = self._uc_token
                        logger.debug("Unified Catalog token refreshed")
                    else:
                        self._token = None
                        self._credential = None  # Force re-authentication
                        self._token = self._get_authentication_token(for_unified_catalog=False)
                        token = self._token
                        logger.debug("Purview token refreshed")
                        
                    headers["Authorization"] = f"Bearer {token}"
                    logger.debug(f"New token (first 20 chars): {token[:20] if token else 'None'}...")

                    # Retry the request with session
                    logger.debug(f"Retrying request to {url} with refreshed token")
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
                        logger.info(f"Request succeeded after token refresh: {response.status_code}")
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
                except PurviewAuthenticationError as e:
                    logger.error(f"Authentication error on token refresh: {e}")
                    return {
                        "status": "error",
                        "message": f"Authentication failed: {str(e)}",
                        "status_code": 401,
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code,
                }

        except PurviewAuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return {
                "status": "error",
                "message": f"Authentication failed: {str(e)}",
                "status_code": 401,
            }
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return {"status": "error", "message": "Request timed out after 60 seconds"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return {"status": "error", "message": f"Failed to connect to {self.base_url}"}

        except Exception as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}
