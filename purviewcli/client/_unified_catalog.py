"""
Microsoft Purview Unified Catalog API Client
Implements comprehensive Unified Catalog functionality
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator


class UnifiedCatalogClient(Endpoint):
    """Client for Microsoft Purview Unified Catalog API."""

    def __init__(self):
        """Initialize the Unified Catalog client."""
        Endpoint.__init__(self)
        self.app = "datagovernance"  # Use datagovernance app for UC endpoints

    # ========================================
    # GOVERNANCE DOMAINS
    # ========================================
    @decorator
    def get_governance_domains(self, args):
        """Get all governance domains."""
        self.method = "GET"
        self.endpoint = "/datagovernance/catalog/businessdomains"
        self.params = {}

    @decorator
    def get_governance_domain_by_id(self, args):
        """Get a governance domain by ID."""
        domain_id = args.get("--domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/businessdomains/{domain_id}"
        self.params = {}

    @decorator
    def create_governance_domain(self, args):
        """Create a new governance domain."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/businessdomains"
        self.payload = get_json(args, "--payloadFile") or {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "type": args.get("--type", ["FunctionalUnit"])[0],
            "status": args.get("--status", ["Draft"])[0],
        }

    @decorator
    def update_governance_domain(self, args):
        """Update a governance domain."""
        domain_id = args.get("--domain-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/businessdomains/{domain_id}"
        self.payload = get_json(args, "--payloadFile") or {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "type": args.get("--type", [""])[0],
            "status": args.get("--status", [""])[0],
        }

    @decorator
    def delete_governance_domain(self, args):
        """Delete a governance domain."""
        domain_id = args.get("--domain-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/businessdomains/{domain_id}"
        self.params = {}

    # ========================================
    # DATA PRODUCTS
    # ========================================
    @decorator
    def get_data_products(self, args):
        """Get all data products."""
        self.method = "GET"
        self.endpoint = "/datagovernance/dataProducts"
        self.params = {}

        # Add optional filters
        if args.get("--domain-id"):
            self.params["domainId"] = args["--domain-id"][0]
        if args.get("--status"):
            self.params["status"] = args["--status"][0]

    @decorator
    def get_data_product_by_id(self, args):
        """Get a data product by ID."""
        product_id = args.get("--product-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/dataProducts/{product_id}"
        self.params = {}

    @decorator
    def create_data_product(self, args):
        """Create a new data product."""
        self.method = "POST"
        self.endpoint = "/datagovernance/dataProducts"
        self.payload = get_json(args, "--payloadFile") or {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "domainId": args.get("--domain-id", [""])[0],
            "status": args.get("--status", ["Draft"])[0],
        }

    @decorator
    def update_data_product(self, args):
        """Update a data product."""
        product_id = args.get("--product-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/dataProducts/{product_id}"
        self.payload = get_json(args, "--payloadFile") or {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "domainId": args.get("--domain-id", [""])[0],
            "status": args.get("--status", [""])[0],
        }

    @decorator
    def delete_data_product(self, args):
        """Delete a data product."""
        product_id = args.get("--product-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/dataProducts/{product_id}"
        self.params = {}

    # ========================================
    # GLOSSARY TERMS
    # ========================================

    @decorator
    def get_terms(self, args):
        """Get all glossary terms in a governance domain."""
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/businessdomains/{domain_id}/glossaryterms"
        self.params = {}

    @decorator
    def get_term_by_id(self, args):
        """Get a glossary term by ID."""
        term_id = args.get("--term-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/glossaryterms/{term_id}"
        self.params = {}

    @decorator
    def create_term(self, args):
        """Create a new glossary term."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/glossaryterms"

        # Build payload
        payload = {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "governanceDomainId": args.get("--governance-domain-id", [""])[0],
            "status": args.get("--status", ["Draft"])[0],
        }

        # Add optional fields
        if args.get("--acronyms"):
            payload["acronyms"] = args["--acronyms"]
        if args.get("--owner-id"):
            payload["ownerIds"] = args["--owner-id"]
        if args.get("--resource-name") and args.get("--resource-url"):
            payload["resources"] = [
                {"name": args["--resource-name"][0], "url": args["--resource-url"][0]}
            ]

        self.payload = payload

    # ========================================
    # OBJECTIVES AND KEY RESULTS (OKRs)
    # ========================================

    @decorator
    def get_objectives(self, args):
        """Get all objectives in a governance domain."""
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/businessdomains/{domain_id}/objectives"
        self.params = {}

    @decorator
    def get_objective_by_id(self, args):
        """Get an objective by ID."""
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}"
        self.params = {}

    @decorator
    def create_objective(self, args):
        """Create a new objective."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/objectives"

        payload = {
            "definition": args.get("--definition", [""])[0],
            "governanceDomainId": args.get("--governance-domain-id", [""])[0],
            "status": args.get("--status", ["Draft"])[0],
        }

        if args.get("--owner-id"):
            payload["ownerIds"] = args["--owner-id"]
        if args.get("--target-date"):
            payload["targetDate"] = args["--target-date"][0]

        self.payload = payload

    # ========================================
    # CRITICAL DATA ELEMENTS (CDEs)
    # ========================================

    @decorator
    def get_critical_data_elements(self, args):
        """Get all critical data elements in a governance domain."""
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/businessdomains/{domain_id}/criticaldataelements"
        self.params = {}

    @decorator
    def get_critical_data_element_by_id(self, args):
        """Get a critical data element by ID."""
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/criticaldataelements/{cde_id}"
        self.params = {}

    @decorator
    def create_critical_data_element(self, args):
        """Create a new critical data element."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/criticaldataelements"

        payload = {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "governanceDomainId": args.get("--governance-domain-id", [""])[0],
            "dataType": args.get("--data-type", ["String"])[0],
            "status": args.get("--status", ["Draft"])[0],
        }

        if args.get("--owner-id"):
            payload["ownerIds"] = args["--owner-id"]

        self.payload = payload

    # ========================================
    # UTILITY METHODS
    # ========================================

    @no_api_call_decorator
    def help(self, args):
        """Display help information for Unified Catalog operations."""
        help_text = """
Microsoft Purview Unified Catalog Client

Available Operations:
- Governance Domains: list, get, create, update, delete
- Data Products: list, get, create, update, delete
- Glossary Terms: list, get, create
- Objectives (OKRs): list, get, create  
- Critical Data Elements: list, get, create

Use --payloadFile to provide JSON payload for create/update operations.
Use individual flags like --name, --description for simple operations.
"""
        return {"message": help_text}
