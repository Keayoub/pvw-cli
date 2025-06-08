"""
PurviewClient: Advanced Azure Purview API Client

This module provides the PurviewClient class, enabling comprehensive automation and programmatic access to all major Azure Purview REST APIs. It is the core client used by the PVW CLI and can be used directly in Python scripts, notebooks, and automation workflows.

Key Features:
- Full support for Azure Purview data plane and control plane APIs
- Async and sync HTTP methods for high-performance automation
- Built-in retry logic, rate limiting, and error diagnostics
- Bulk operation helpers for parallel processing
- Detailed logging and error reporting
- Region and cloud support (public, China, US Gov, Germany)

Typical Use Cases:
- Automating data catalog, lineage, and governance operations
- Bulk import/export of entities, relationships, and glossary terms
- Integrating Purview with ETL, CI/CD, and data engineering workflows
- Advanced diagnostics and health checks

Example Usage:

Synchronous:
    from purviewcli.client.client import PurviewClient
    client = PurviewClient()
    client.set_region('catalog')
    client.set_account('catalog')
    client.set_token('catalog')
    result = client.http_request('catalog', 'GET', '/api/atlas/v2/entity/bulk?typeName=DataSet')
    print(result)

Asynchronous:
    import asyncio
    from purviewcli.client.client import PurviewClient
    async def main():
        client = PurviewClient()
        client.set_region('catalog')
        client.set_account('catalog')
        client.set_token('catalog')
        result = await client.http_request_async('catalog', 'GET', '/api/atlas/v2/entity/bulk?typeName=DataSet')
        print(result)
    asyncio.run(main())

For CLI usage and advanced documentation, see the PVW CLI README and docs/PVW_and_PurviewClient.md.
"""

import jwt
import sys
import os
import logging
import requests
import time
import asyncio
import aiohttp
from http.client import responses
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureAuthorityHosts
from typing import Dict, List, Optional, Union, Any
from . import settings
from .exceptions import PurviewClientError, PurviewAuthenticationError, PurviewAPIError
from .retry_handler import RetryHandler
from .rate_limiter import RateLimiter
from .. import __version__


logging.getLogger("azure.identity").setLevel(logging.ERROR)

class PurviewClient:
    """Purview client with comprehensive API coverage and automation features"""
    
    def __init__(self, 
                 retry_config: Optional[Dict] = None,
                 rate_limit_config: Optional[Dict] = None,
                 enable_logging: bool = True,
                 retry_after_default: float = 5.0):
        """
        Initialize the Purview Client
        
        Args:
            retry_config: Configuration for retry logic
            rate_limit_config: Configuration for rate limiting
            enable_logging: Enable detailed logging
            retry_after_default: Default wait time (seconds) if Retry-After header is not a float
        """
        self.access_token = None
        self.account_name = None
        self.azure_region = None
        self.management_endpoint = None
        self.purview_endpoint = None
        
        #  features
        self.retry_handler = RetryHandler(retry_config or {})
        self.rate_limiter = RateLimiter(rate_limit_config or {})
        self.session = requests.Session()
        self.enable_logging = enable_logging
        self.retry_after_default = retry_after_default
        
        # API endpoint mappings
        self.api_endpoints = {
            'management': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Purview/accounts/{account_name}',
            'catalog': '/catalog',
            'scan': '/scan',
            'account': '/account',
            'policystore': '/policystore',
            'share': '/share',
            'mapanddiscover': '/mapanddiscover',
            'guardian': '',
            'datamap': '/datamap',
            'workflow': '/workflow',
            'lineage': '/lineage',
            'insights': '/insights',
            'governance': '/governance',
            'classification': '/classification',
            'sensitivity': '/sensitivity'
        }
        
        if enable_logging:
            self._setup_logging()

    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('purview_client.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def set_region(self, app: str):
        """Set Azure region configuration with enhanced cloud support"""
        self.azure_region = os.environ.get("AZURE_REGION")
        
        region_configs = {
            None: {
                'management': "https://management.azure.com",
                'purview': "purview.azure.com"
            },
            'china': {
                'management': "https://management.chinacloudapi.cn",
                'purview': "purview.azure.cn"
            },
            'usgov': {
                'management': "https://management.usgovcloudapi.net",
                'purview': "purview.azure.us"
            },
            'germany': {
                'management': "https://management.microsoftazure.de",
                'purview': "purview.azure.de"
            }
        }
        
        if self.azure_region and self.azure_region.lower() in region_configs:
            config = region_configs[self.azure_region.lower()]
            self.management_endpoint = config['management']
            self.purview_endpoint = config['purview']
        elif self.azure_region is None:
            config = region_configs[None]
            self.management_endpoint = config['management']
            self.purview_endpoint = config['purview']
        else:
            raise PurviewClientError(f"Unsupported Azure region: {self.azure_region}")

    def set_account(self, app: str):
        """Set Purview account with enhanced validation"""
        if app == "management":
            self.account_name = None
        else:
            self.account_name = (settings.PURVIEW_NAME if settings.PURVIEW_NAME 
                               else os.environ.get("PURVIEW_NAME"))
            
            if not self.account_name:
                raise PurviewClientError("""
Environment variable PURVIEW_NAME is missing.

Configure PURVIEW_NAME environment variable:
    Windows (Command Prompt):   set PURVIEW_NAME=value
    macOS (Terminal):           export PURVIEW_NAME=value
    Python:                     os.environ["PURVIEW_NAME"] = "value"
    PowerShell:                 $env:PURVIEW_NAME = "value"
    Jupyter Notebook:           %env PURVIEW_NAME=value

Alternatively, provide --purviewName=<val> argument.
""")

    def set_token(self, app: str):
        """ token management with better error handling"""
        credential_config = {
            'china': {
                'authority': "https://login.partner.microsoftonline.cn",
                'exclude_shared_token_cache_credential': True
            },
            'usgov': {
                'authority': AzureAuthorityHosts.AZURE_GOVERNMENT
            },
            'germany': {
                'authority': "https://login.microsoftonline.de"
            }
        }
        
        if self.azure_region and self.azure_region.lower() in credential_config:
            config = credential_config[self.azure_region.lower()]
            credential = DefaultAzureCredential(**config)
        else:
            credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        
        resource = (f"{self.management_endpoint}/.default" if app == "management" 
                   else "https://purview.azure.net/.default")
        
        try:
            token = credential.get_token(resource)
            self.access_token = token.token
            
            if self.enable_logging:
                self.logger.info(f"Successfully obtained token for {app}")
                
        except ClientAuthenticationError as e:
            raise PurviewAuthenticationError(f"Authentication failed: {e}")

    def get_base_url(self, app: str) -> str:
        """Get base URL for different API surfaces"""
        url_patterns = {
            'management': f"{self.management_endpoint}",
            'catalog': f"https://{self.account_name}.{self.purview_endpoint}/catalog",
            'scan': f"https://{self.account_name}.{self.purview_endpoint}/scan",
            'account': f"https://{self.account_name}.{self.purview_endpoint}/account",
            'policystore': f"https://{self.account_name}.{self.purview_endpoint}/policystore",
            'share': f"https://{self.account_name}.{self.purview_endpoint}/share",
            'mapanddiscover': f"https://{self.account_name}.{self.purview_endpoint}/mapanddiscover",
            'guardian': f"https://{self.account_name}.{app}.{self.purview_endpoint}",
            'datamap': f"https://{self.account_name}.{self.purview_endpoint}/datamap",
            'workflow': f"https://{self.account_name}.{self.purview_endpoint}/workflow",
            'lineage': f"https://{self.account_name}.{self.purview_endpoint}/lineage",
            'insights': f"https://{self.account_name}.{self.purview_endpoint}/insights",
            'governance': f"https://{self.account_name}.{self.purview_endpoint}/governance",
            'classification': f"https://{self.account_name}.{self.purview_endpoint}/classification",
            'sensitivity': f"https://{self.account_name}.{self.purview_endpoint}/sensitivity"
        }
        
        if app in url_patterns:
            return url_patterns[app]
        else:
            return f"https://{self.account_name}.{app}.{self.purview_endpoint}"

    async def http_request_async(self, 
                                app: str, 
                                method: str, 
                                endpoint: str,
                                params: Optional[Dict] = None,
                                payload: Optional[Dict] = None,
                                files: Optional[Dict] = None,
                                headers: Optional[Dict] = None) -> Dict:
        """Asynchronous HTTP request for parallel operations"""
        uri = f"{self.get_base_url(app)}{endpoint}"
        headers = headers or {}
        
        auth_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": f"purviewcli/{__version__} {requests.utils.default_headers().get('User-Agent')}"
        }
        headers.update(auth_headers)
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, uri, params=params, json=payload, headers=headers) as response:
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return {'status_code': response.status, 'content': await response.text()}

    def http_request(self, 
                    app: str, 
                    method: str, 
                    endpoint: str,
                    params: Optional[Dict] = None,
                    payload: Optional[Dict] = None,
                    files: Optional[Dict] = None,
                    headers: Optional[Dict] = None,
                    timeout: Optional[int] = None) -> Dict:
        """ HTTP request with retry logic and rate limiting"""
        
        def _make_request():
            uri = f"{self.get_base_url(app)}{endpoint}"
            headers = headers or {}
            
            auth_headers = {
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": f"purviewcli/{__version__} {requests.utils.default_headers().get('User-Agent')}"
            }
            headers.update(auth_headers)
            
            # Apply rate limiting
            self.rate_limiter.wait()
            
            try:
                response = self.session.request(
                    method, uri, 
                    params=params, 
                    json=payload, 
                    files=files, 
                    headers=headers,
                    timeout=timeout or 30
                )
                
                if response.status_code == 429:
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                        except ValueError:
                            # Retry-After can be a date, fallback to parameterized seconds
                            wait_time = self.retry_after_default
                        if self.enable_logging:
                            self.logger.warning(f"Received 429 Too Many Requests. Retrying after {wait_time} seconds.")
                        time.sleep(wait_time)
                        return _make_request()
                
                if self.enable_logging:
                    self.logger.info(f"{method} {uri} - Status: {response.status_code}")
                
                return self._process_response(response, method, uri)
                
            except requests.exceptions.RequestException as e:
                if self.enable_logging:
                    self.logger.error(f"Request failed: {e}")
                raise PurviewAPIError(f"Request failed: {e}")
        
        return self.retry_handler.execute(_make_request)

    def _process_response(self, response: requests.Response, method: str, uri: str) -> Dict:
        """Process HTTP response with enhanced error handling"""
        status_code = response.status_code
        
        if status_code == 204:
            return {
                'operation': f'[{method}] {uri}',
                'status': 'The server successfully processed the request'
            }
        
        if status_code == 403:
            self._handle_forbidden_error(response, method, uri)
            return {}
        
        if status_code >= 400:
            error_msg = f"HTTP {status_code}: {response.reason}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            
            raise PurviewAPIError(error_msg)
        
        # Handle different content types
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            try:
                return response.json()
            except ValueError:
                return {
                    'url': response.url,
                    'status_code': status_code,
                    'content': response.text
                }
        
        elif 'text/csv' in content_type or 'application/octet-stream' in content_type:
            return self._handle_file_response(response, status_code)
        
        else:
            return {
                'url': response.url,
                'status_code': status_code,
                'content': response.text
            }

    def _handle_forbidden_error(self, response: requests.Response, method: str, uri: str):
        """Handle 403 Forbidden errors with detailed diagnostics"""
        print('[Error] Access to the requested resource is forbidden (HTTP status code 403).')
        print(f'\n[Resource] [{method}] {uri}')
        
        try:
            error_detail = response.json()
            print(f'\n[Response] {error_detail}')
        except:
            print(f'\n[Response] {response.text}')
        
        if self.access_token:
            try:
                claimset = jwt.decode(self.access_token, options={"verify_signature": False})
                print('\n[Credentials]')
                print(f"Application ID: {claimset.get('appid', 'N/A')}")
                print(f"Object ID: {claimset.get('oid', 'N/A')}")
                print(f"Tenant ID: {claimset.get('tid', 'N/A')}")
            except Exception as e:
                print(f'\n[Token Decode Error] {e}')

    def _handle_file_response(self, response: requests.Response, status_code: int) -> Dict:
        """Handle file download responses"""
        filepath = os.path.join(os.getcwd(), 'export.csv')
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return {
            'status_code': status_code,
            'export': filepath,
            'size': len(response.content)
        }

    # Bulk operation helpers
    async def bulk_operation(self, operations: List[Dict]) -> List[Dict]:
        """Execute bulk operations in parallel"""
        tasks = []
        for operation in operations:
            task = self.http_request_async(
                operation['app'],
                operation['method'], 
                operation['endpoint'],
                operation.get('params'),
                operation.get('payload'),
                operation.get('files'),
                operation.get('headers')
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_health_status(self) -> Dict:
        """Get Purview service health status"""
        try:
            response = self.http_request('account', 'GET', '/health')
            return {'status': 'healthy', 'details': response}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    def validate_connection(self) -> bool:
        """Validate connection to Purview services"""
        try:
            self.get_health_status()
            return True
        except:
            return False

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()
