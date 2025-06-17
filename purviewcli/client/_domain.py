"""
Governance Domain Management Client for Microsoft Purview
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/catalogdataplane/domains
API Version: 2024-03-01-preview

Implements:
- Create, list, get, update, and delete governance domains
- Uses endpoints from purviewcli.client.endpoints (PurviewEndpoints)
- Compatible with CLI global endpoint/token options
"""

from purviewcli.client.endpoints import PurviewEndpoints
import os
import requests

class Domain:
    """Client for managing governance domains in Microsoft Purview."""
    def __init__(self, endpoint=None, token=None):
        """
        Initialize the Domain client with endpoint and token.
        If not provided, will try to use environment variables.
        """
        self.endpoint = endpoint or os.environ.get("PURVIEW_ENDPOINT", "")
        self.token = token or os.environ.get("PURVIEW_TOKEN", "")
        self.endpoint = self.endpoint.rstrip("/") if self.endpoint else ""
        
        # Define domain API endpoints if not in PurviewEndpoints yet
        if not hasattr(PurviewEndpoints, "DOMAIN"):
            PurviewEndpoints.DOMAIN = {
                "base": f"{PurviewEndpoints.CATALOG_BASE}/domains",
                "domain": f"{PurviewEndpoints.CATALOG_BASE}/domains/{{name}}"
            }

    def create_domain(self, name, friendly_name=None, description=None):
        """Create a new governance domain using the official Purview API."""
        if not self.endpoint or not self.token:
            raise ValueError("Endpoint and token must be provided")
            
        url = self.endpoint + PurviewEndpoints.DOMAIN["base"]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        params = PurviewEndpoints.get_api_version_params("catalog")
        payload = {
            "name": name,
            "friendlyName": friendly_name or name,
            "description": description or ""
        }
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()
        return response.json()

    def list_domains(self):
        """List all governance domains."""
        if not self.endpoint or not self.token:
            raise ValueError("Endpoint and token must be provided")
            
        url = self.endpoint + PurviewEndpoints.DOMAIN["base"]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        params = PurviewEndpoints.get_api_version_params("catalog")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_domain(self, name):
        """Get a governance domain by name."""
        if not self.endpoint or not self.token:
            raise ValueError("Endpoint and token must be provided")
            
        url = self.endpoint + PurviewEndpoints.format_endpoint(
            PurviewEndpoints.DOMAIN["domain"], name=name
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        params = PurviewEndpoints.get_api_version_params("catalog")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def update_domain(self, name, friendly_name=None, description=None):
        """Update a governance domain's friendlyName and/or description."""
        if not self.endpoint or not self.token:
            raise ValueError("Endpoint and token must be provided")
            
        url = self.endpoint + PurviewEndpoints.format_endpoint(
            PurviewEndpoints.DOMAIN["domain"], name=name
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        params = PurviewEndpoints.get_api_version_params("catalog")
        payload = {}
        if friendly_name is not None:
            payload["friendlyName"] = friendly_name
        if description is not None:
            payload["description"] = description
        response = requests.patch(url, headers=headers, params=params, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_domain(self, name):
        """Delete a governance domain by name."""
        if not self.endpoint or not self.token:
            raise ValueError("Endpoint and token must be provided")
            
        url = self.endpoint + PurviewEndpoints.format_endpoint(
            PurviewEndpoints.DOMAIN["domain"], name=name
        )
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        params = PurviewEndpoints.get_api_version_params("catalog")
        response = requests.delete(url, headers=headers, params=params)
        response.raise_for_status()
        return {"status": "deleted", "name": name}
