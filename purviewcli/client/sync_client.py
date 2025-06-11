"""
Synchronous Purview Client for CLI compatibility
"""

import requests
import os
import json
from typing import Dict, Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError


class SyncPurviewConfig:
    """Simple synchronous config"""

    def __init__(self, account_name: str, azure_region: str = "public"):
        self.account_name = account_name
        self.azure_region = azure_region


class SyncPurviewClient:
    """Synchronous client for CLI operations with real Azure authentication"""

    def __init__(self, config: SyncPurviewConfig):
        self.config = config

        # Set up endpoints based on Azure region
        if config.azure_region and config.azure_region.lower() == "china":
            self.base_url = f"https://{config.account_name}.purview.azure.cn"
            self.auth_scope = "https://purview.azure.cn/.default"
        elif config.azure_region and config.azure_region.lower() == "usgov":
            self.base_url = f"https://{config.account_name}.purview.azure.us"
            self.auth_scope = "https://purview.azure.us/.default"
        else:
            self.base_url = f"https://{config.account_name}.purview.azure.com"
            self.auth_scope = "https://purview.azure.net/.default"

        self._token = None
        self._credential = None

    def _get_authentication_token(self):
        """Get Azure authentication token"""
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

            # Get the token
            token = self._credential.get_token(self.auth_scope)
            self._token = token.token
            return self._token

        except ClientAuthenticationError as e:
            raise Exception(f"Azure authentication failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get authentication token: {str(e)}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make actual HTTP request to Azure Purview"""
        try:
            # Get authentication token
            if not self._token:
                self._get_authentication_token()            # Prepare the request
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "User-Agent": "purviewcli/2.0",
            }

            # Make the actual HTTP request
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=kwargs.get("params"),
                json=kwargs.get("json"),
                timeout=30,
            )
            # Handle the response
            if response.status_code == 200:
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
                self._token = None
                self._get_authentication_token()
                headers["Authorization"] = f"Bearer {self._token}"

                # Retry the request
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=kwargs.get("params"),
                    json=kwargs.get("json"),
                    timeout=30,
                )

                if response.status_code == 200:
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
