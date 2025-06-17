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
import requests

class Domain:
    """Client for managing governance domains in Microsoft Purview."""
    def __init__(self, endpoint, token):
        self.endpoint = endpoint.rstrip("/")
        self.token = token

    def create_domain(self, name, friendly_name=None, description=None):
        """Create a new governance domain using the official Purview API."""
        url = self.endpoint + PurviewEndpoints.CATALOG_BASE + "/domains"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": name,
            "friendlyName": friendly_name or name,
            "description": description or ""
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def list_domains(self):
        """List all governance domains."""
        url = self.endpoint + PurviewEndpoints.CATALOG_BASE + "/domains"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_domain(self, name):
        """Get a governance domain by name."""
        url = self.endpoint + PurviewEndpoints.CATALOG_BASE + f"/domains/{name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def update_domain(self, name, friendly_name=None, description=None):
        """Update a governance domain's friendlyName and/or description."""
        url = self.endpoint + PurviewEndpoints.CATALOG_BASE + f"/domains/{name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {}
        if friendly_name is not None:
            payload["friendlyName"] = friendly_name
        if description is not None:
            payload["description"] = description
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_domain(self, name):
        """Delete a governance domain by name."""
        url = self.endpoint + PurviewEndpoints.CATALOG_BASE + f"/domains/{name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return {"status": "deleted", "name": name}
