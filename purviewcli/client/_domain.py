"""
Governance Domain Management Client for Microsoft Purview

NOTE: Governance Domains are currently not available in the public Microsoft Purview REST API.
This feature may be in preview, portal-only, or planned for future release.

This client provides a foundation for when the API becomes available and includes
alternative approaches for domain-like organization.
"""

from .endpoint import Endpoint
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION


class Domain(Endpoint):
    """Client for managing governance domains in Microsoft Purview."""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"  # Use catalog app as fallback

    def domainsList(self, args):
        """List all governance domains - Currently not available in public API"""
        result = {
            "status": "not_available",
            "message": "Governance Domains are not currently available in the public Microsoft Purview REST API. Please use the Azure portal to manage governance domains, or use collections as an alternative organizational structure.",
            "alternatives": [
                "Use collections to organize assets hierarchically",
                "Use custom entity attributes to tag assets with domain information",
                "Use glossary terms to create domain vocabularies",
            ],
        }
        return result

    def domainsCreate(self, args):
        """Create a new governance domain - Currently not available in public API"""
        result = {
            "status": "not_available",
            "message": "Governance Domain creation is not currently available in the public Microsoft Purview REST API. Please use the Azure portal or consider using collections as an alternative.",
            "suggested_action": f"Consider creating a collection named '{args.get('--name', 'unknown')}' instead using: pvw collections create --collection-name {args.get('--name', 'domain-name')}",
        }
        return result

    def domainsGet(self, args):
        """Get a governance domain by name - Currently not available in public API"""
        domain_name = args.get("--domainName", "unknown")
        result = {
            "status": "not_available",
            "message": f"Cannot retrieve governance domain '{domain_name}' - feature not available in public API",
            "suggested_action": f"Try: pvw collections get --collection-name {domain_name}",
        }
        return result

    def domainsUpdate(self, args):
        """Update a governance domain - Currently not available in public API"""
        domain_name = args.get("--domainName", "unknown")
        result = {
            "status": "not_available",
            "message": f"Cannot update governance domain '{domain_name}' - feature not available in public API",
        }
        return result

    def domainsDelete(self, args):
        """Delete a governance domain by name - Currently not available in public API"""
        domain_name = args.get("--domainName", "unknown")
        result = {
            "status": "not_available",
            "message": f"Cannot delete governance domain '{domain_name}' - feature not available in public API",
        }
        return result

    def get_api_version(self):
        """Return the current API version for the domain (datamap) endpoint."""
        return DATAMAP_API_VERSION

    def get_api_version_params(self):
        """Return the current API version params for the domain (datamap) endpoint."""
        return {"api-version": DATAMAP_API_VERSION}

    # Example usage in a real API call (when available):
    # version = self.get_api_version()
    # params = self.get_api_version_params()
    # ... use version/params in requests ...
