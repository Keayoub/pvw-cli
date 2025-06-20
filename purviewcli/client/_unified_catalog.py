import json
import requests
import os
from .endpoint import Endpoint, get_data
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION


class UnifiedCatalogDataProduct:
    """
    Microsoft Purview Unified Catalog Data Product client
    Based on the actual Microsoft Purview Unified Catalog API structure
    """

    def __init__(self):
        """Initialize the unified catalog data product client"""
        pass

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request through the existing infrastructure"""
        try:
            # Unified Catalog uses the Data Governance base path
            base_path = "/datagovernance/catalog"
            full_endpoint = base_path + endpoint
            
            http_dict = {
                "method": method,
                "endpoint": full_endpoint,
                "params": params or {},
                "payload": data
            }
            
            # Add Unified Catalog API version to params
            if "api-version" not in http_dict["params"]:
                http_dict["params"]["api-version"] = DATAMAP_API_VERSION
            
            return get_data(http_dict)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "status_code": getattr(e, 'response', {}).get('status_code', 500) if hasattr(e, 'response') else 500
            }

    # === DATA PRODUCT OPERATIONS ===

    def dataProductList(self, args):
        """List data products with optional filtering"""
        params = {}
        if args.get("--limit"):
            params["$top"] = args["--limit"]
        if args.get("--skip"):
            params["$skip"] = args["--skip"]
        if args.get("--governanceDomain"):
            params["domainId"] = args["--governanceDomain"]
            
        return self._make_request("GET", "/dataproducts", params=params)

    def dataProductCreate(self, args):
        """Create a new data product"""
        payload = self._get_payload_from_args(args)
        return self._make_request("POST", "/dataproducts", data=payload)

    def dataProductRead(self, args):
        """Get a data product by ID"""
        data_product_id = args.get("--dataProductId")
        if not data_product_id:
            return {"status": "error", "message": "dataProductId is required"}
        
        endpoint = f"/dataproducts/{data_product_id}"
        return self._make_request("GET", endpoint)

    def dataProductUpdate(self, args):
        """Update a data product"""
        data_product_id = args.get("--dataProductId")
        if not data_product_id:
            return {"status": "error", "message": "dataProductId is required"}
        
        payload = self._get_payload_from_args(args)
        endpoint = f"/dataproducts/{data_product_id}"
        return self._make_request("PUT", endpoint, data=payload)

    def dataProductDelete(self, args):
        """Delete a data product"""
        data_product_id = args.get("--dataProductId")
        if not data_product_id:
            return {"status": "error", "message": "dataProductId is required"}
        
        endpoint = f"/dataproducts/{data_product_id}"
        return self._make_request("DELETE", endpoint)

    # === GLOSSARY OPERATIONS ===

    def glossaryTermsList(self, args):
        """List glossary terms"""
        params = {}
        if args.get("--governanceDomain"):
            params["domainId"] = args["--governanceDomain"]
        
        return self._make_request("GET", "/terms", params=params)

    def glossaryTermCreate(self, args):
        """Create a glossary term"""
        payload = self._get_payload_from_args(args)
        return self._make_request("POST", "/terms", data=payload)

    def glossaryTermRead(self, args):
        """Get a glossary term by ID"""
        term_id = args.get("--termId")
        if not term_id:
            return {"status": "error", "message": "termId is required"}
        
        endpoint = f"/terms/{term_id}"
        return self._make_request("GET", endpoint)

    def glossaryTermUpdate(self, args):
        """Update a glossary term"""
        term_id = args.get("--termId")
        if not term_id:
            return {"status": "error", "message": "termId is required"}
        
        payload = self._get_payload_from_args(args)
        endpoint = f"/terms/{term_id}"
        return self._make_request("PUT", endpoint, data=payload)

    def glossaryTermDelete(self, args):
        """Delete a glossary term"""
        term_id = args.get("--termId")
        if not term_id:
            return {"status": "error", "message": "termId is required"}
        
        endpoint = f"/terms/{term_id}"
        return self._make_request("DELETE", endpoint)

    # === BUSINESS DOMAIN OPERATIONS ===

    def businessDomainsList(self, args):
        """List business domains"""
        return self._make_request("GET", "/businessdomains")

    def businessDomainCreate(self, args):
        """Create a business domain"""
        payload = self._get_payload_from_args(args)
        return self._make_request("POST", "/businessdomains", data=payload)

    def businessDomainRead(self, args):
        """Get a business domain by ID"""
        domain_id = args.get("--domainId")
        if not domain_id:
            return {"status": "error", "message": "domainId is required"}
        
        endpoint = f"/businessdomains/{domain_id}"
        return self._make_request("GET", endpoint)

    def businessDomainUpdate(self, args):
        """Update a business domain"""
        domain_id = args.get("--domainId")
        if not domain_id:
            return {"status": "error", "message": "domainId is required"}
        
        payload = self._get_payload_from_args(args)
        endpoint = f"/businessdomains/{domain_id}"
        return self._make_request("PUT", endpoint, data=payload)

    def businessDomainDelete(self, args):
        """Delete a business domain"""
        domain_id = args.get("--domainId")
        if not domain_id:
            return {"status": "error", "message": "domainId is required"}
        
        endpoint = f"/businessdomains/{domain_id}"
        return self._make_request("DELETE", endpoint)

    # === RELATIONSHIP OPERATIONS ===

    def relationshipCreate(self, args):
        """Create a relationship between entities"""
        entity_type = args.get("--entityType")
        entity_id = args.get("--entityId")
        
        if not entity_type or not entity_id:
            return {"status": "error", "message": "entityType and entityId are required"}
        
        endpoint_map = {
            "DataProduct": "dataproducts",
            "Term": "terms",
        }
        
        if entity_type not in endpoint_map:
            return {"status": "error", "message": f"Unsupported entity type: {entity_type}"}
        
        endpoint = f"/{endpoint_map[entity_type]}/{entity_id}/relationships"
        payload = self._get_payload_from_args(args)
        params = {"entityType": entity_type}
        
        return self._make_request("POST", endpoint, data=payload, params=params)

    def relationshipDelete(self, args):
        """Delete a relationship between entities"""
        entity_type = args.get("--entityType")
        entity_id = args.get("--entityId")
        target_entity_id = args.get("--targetEntityId")
        relationship_type = args.get("--relationshipType")
        
        if not all([entity_type, entity_id, target_entity_id, relationship_type]):
            return {"status": "error", "message": "entityType, entityId, targetEntityId, and relationshipType are required"}
        
        endpoint_map = {
            "DataProduct": "dataproducts",
            "Term": "terms",
        }
        
        if entity_type not in endpoint_map:
            return {"status": "error", "message": f"Unsupported entity type: {entity_type}"}
        
        endpoint = f"/{endpoint_map[entity_type]}/{entity_id}/relationships"
        params = {
            "entityId": target_entity_id,
            "entityType": entity_type,
            "relationshipType": relationship_type
        }
        
        return self._make_request("DELETE", endpoint, params=params)

    # === HELPER METHODS ===

    def _get_payload_from_args(self, args):
        """Extract payload from args, either from --payloadFile or construct from individual args"""
        if args.get("--payloadFile"):
            # Load from file
            with open(args["--payloadFile"], 'r') as f:
                return json.load(f)
        
        # Construct from individual arguments
        payload = {}
        
        # Common fields
        if args.get("--name"):
            payload["name"] = args["--name"]
        if args.get("--description"):
            payload["description"] = args["--description"]
        if args.get("--governanceDomain"):
            payload["domain"] = args["--governanceDomain"]
        if args.get("--type"):
            payload["type"] = args["--type"]
        if args.get("--businessUse"):
            payload["businessUse"] = args["--businessUse"]
        if args.get("--status"):
            payload["status"] = args["--status"]
        if args.get("--endorsed"):
            payload["endorsed"] = args["--endorsed"] == "true"
        
        # Relationships
        if args.get("--entityId"):
            payload["entityId"] = args["--entityId"]
        if args.get("--relationshipType"):
            payload["relationshipType"] = args["--relationshipType"]
        
        return payload

    # === HIGH-LEVEL CONVENIENCE METHODS ===
    # These methods provide a simpler interface for common operations

    def create_data_product(self, name, description=None, domain_guid=None):
        """Create a data product with simple parameters"""
        args = {
            "--name": name,
            "--description": description or "",
            "--governanceDomain": domain_guid,
            "--type": "Dataset",  # Default type
            "--status": "Draft"   # Default status
        }
        return self.dataProductCreate(args)

    def get_data_product(self, data_product_id):
        """Get a data product by ID"""
        args = {"--dataProductId": data_product_id}
        return self.dataProductRead(args)

    def update_data_product(self, data_product_id, updates):
        """Update a data product with a dictionary of updates"""
        args = {"--dataProductId": data_product_id}
        args.update({f"--{k}": v for k, v in updates.items()})
        return self.dataProductUpdate(args)

    def delete_data_product(self, data_product_id):
        """Delete a data product by ID"""
        args = {"--dataProductId": data_product_id}
        return self.dataProductDelete(args)

    def list_data_products(self, limit=50, offset=0, domain_id=None):
        """List data products with pagination"""
        args = {
            "--limit": str(limit),
            "--skip": str(offset)
        }
        if domain_id:
            args["--governanceDomain"] = domain_id
        return self.dataProductList(args)

    def create_glossary_term(self, name, description, domain_id):
        """Create a glossary term"""
        args = {
            "--name": name,
            "--description": description,
            "--governanceDomain": domain_id,
            "--status": "Draft"
        }
        return self.glossaryTermCreate(args)

    def link_term_to_data_product(self, data_product_id, term_id):
        """Link a glossary term to a data product"""
        args = {
            "--entityType": "DataProduct",
            "--entityId": data_product_id,
            "--entityId": term_id,
            "--relationshipType": "Related"
        }
        return self.relationshipCreate(args)
