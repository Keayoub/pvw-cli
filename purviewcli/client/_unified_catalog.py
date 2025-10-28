"""
Microsoft Purview Unified Catalog API Client
Implements comprehensive Unified Catalog functionality
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
import os
import json


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
        # Allow payload file to fully control creation; otherwise build payload from flags
        payload = get_json(args, "--payloadFile")
        if not payload:
            payload = {
                "name": args.get("--name", [""])[0],
                "description": args.get("--description", [""])[0],
                "type": args.get("--type", ["FunctionalUnit"])[0],
                "status": args.get("--status", ["Draft"])[0],
            }
            # Support parent domain ID passed via CLI as --parent-domain-id
            parent_id = args.get("--parent-domain-id", [""])[0]
            if parent_id:
                payload["parentId"] = parent_id

        # If payload file contains parentId or parentDomainId, keep it as-is
        self.payload = payload

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
        self.endpoint = "/datagovernance/catalog/dataproducts"
        
        # Add optional filters
        domain_id = args.get("--governance-domain-id", [""])[0] or args.get("--domain-id", [""])[0]
        self.params = {"domainId": domain_id} if domain_id else {}
        
        if args.get("--status"):
            self.params["status"] = args["--status"][0]

    @decorator
    def get_data_product_by_id(self, args):
        """Get a data product by ID."""
        product_id = args.get("--product-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/dataproducts/{product_id}"
        self.params = {}

    @decorator
    def create_data_product(self, args):
        """Create a new data product."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/dataproducts"
        
        # Get domain ID
        domain_id = args.get("--governance-domain-id", [""])[0] or args.get("--domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        business_use = args.get("--business-use", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Type mapping for data products
        dp_type = args.get("--type", ["Dataset"])[0]
        
        # Build contacts field
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id, "description": ""})
        
        payload = {
            "name": name,
            "description": description,
            "domain": domain_id,
            "type": dp_type,
            "businessUse": business_use,
            "status": status,
        }
        
        if owners:
            payload["contacts"] = {"owner": owners}
        
        # Optional fields
        if args.get("--audience"):
            payload["audience"] = args["--audience"]
        if args.get("--terms-of-use"):
            payload["termsOfUse"] = args["--terms-of-use"]
        if args.get("--documentation"):
            payload["documentation"] = args["--documentation"]
        if args.get("--update-frequency"):
            payload["updateFrequency"] = args["--update-frequency"][0]
        if args.get("--endorsed"):
            payload["endorsed"] = args["--endorsed"][0]
        
        self.payload = payload

    @decorator
    def update_data_product(self, args):
        """Update a data product - fetches current state first, then applies updates."""
        product_id = args.get("--product-id", [""])[0]
        
        # First, get the current data product
        get_args = {"--product-id": [product_id]}
        current_product = self.get_data_product_by_id(get_args)
        
        if not current_product or (isinstance(current_product, dict) and current_product.get("error")):
            raise ValueError(f"Failed to retrieve data product {product_id} for update")
        
        # Start with current product as base
        payload = dict(current_product)
        
        # Update only the fields that were provided
        if args.get("--name"):
            payload["name"] = args.get("--name")[0]
        if "--description" in args:
            payload["description"] = args.get("--description")[0]
        if args.get("--domain-id") or args.get("--governance-domain-id"):
            payload["domain"] = args.get("--governance-domain-id", [""])[0] or args.get("--domain-id", [""])[0]
        if args.get("--type"):
            payload["type"] = args.get("--type")[0]
        if args.get("--status"):
            payload["status"] = args.get("--status")[0]
        if "--business-use" in args:
            payload["businessUse"] = args.get("--business-use")[0]
        if args.get("--update-frequency"):
            payload["updateFrequency"] = args.get("--update-frequency")[0]
        if args.get("--endorsed"):
            payload["endorsed"] = args.get("--endorsed")[0] == "true"
        
        # Handle owner updates
        owner_ids = args.get("--owner-id", [])
        if owner_ids:
            owners = [{"id": owner_id, "description": "Owner"} for owner_id in owner_ids]
            if "contacts" not in payload:
                payload["contacts"] = {}
            payload["contacts"]["owner"] = owners
        
        # Now perform the PUT request
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/dataproducts/{product_id}"
        self.payload = payload

    @decorator
    def delete_data_product(self, args):
        """Delete a data product."""
        product_id = args.get("--product-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/dataproducts/{product_id}"
        self.params = {}

    # ========================================
    # GLOSSARY TERMS
    # ========================================

    @decorator
    def get_terms(self, args):
        """Get all Unified Catalog terms in a governance domain.
        
        Uses the Unified Catalog /terms endpoint which is separate from
        Data Map glossary terms. These are business terms managed through
        the Governance Domains interface.
        """
        domain_id = args.get("--governance-domain-id", [""])[0]
        
        self.method = "GET"
        
        if domain_id:
            # Use Unified Catalog terms API with domainId filter
            self.endpoint = "/datagovernance/catalog/terms"
            self.params = {"domainId": domain_id}
        else:
            # List all UC terms
            self.endpoint = "/datagovernance/catalog/terms"
            self.params = {}

    # Keeping old Data Map glossary-based implementation for reference/fallback
    def get_terms_from_glossary(self, args):
        """Get glossary terms from Data Map API (Classic Types view).
        
        This is the OLD implementation that queries Data Map glossaries.
        Use get_terms() for Unified Catalog (Governance Domain) terms.
        """
        domain_id = args.get("--governance-domain-id", [""])[0]

        # If no domain provided, list all glossaries via the Glossary client
        from ._glossary import Glossary

        gclient = Glossary()

        # Helper to normalize glossary list responses
        def _normalize_glossary_list(resp):
            if isinstance(resp, dict):
                return resp.get("value", []) or []
            elif isinstance(resp, (list, tuple)):
                return resp
            return []

        try:
            if not domain_id:
                glossaries = gclient.glossaryRead({})
                normalized = _normalize_glossary_list(glossaries)
                if os.getenv("PURVIEWCLI_DEBUG"):
                    try:
                        print("[PURVIEWCLI DEBUG] get_terms returning (no domain_id):", json.dumps(normalized, default=str, indent=2))
                    except Exception:
                        print("[PURVIEWCLI DEBUG] get_terms returning (no domain_id): (could not serialize)")
                return normalized

            # 1) Get governance domain info to obtain a human-readable name
            # Note: Nested domains may not be directly fetchable via /businessdomains/{id}
            # If fetch fails, we'll match by domain_id in qualifiedName
            domain_info = None
            domain_name = None
            try:
                domain_info = self.get_governance_domain_by_id({"--domain-id": [domain_id]})
                if isinstance(domain_info, dict):
                    domain_name = domain_info.get("name") or domain_info.get("displayName") or domain_info.get("qualifiedName")
            except Exception as e:
                if os.getenv("PURVIEWCLI_DEBUG"):
                    print(f"[PURVIEWCLI DEBUG] Could not fetch domain by ID (may be nested): {e}")
                # Continue without domain_name; will match by domain_id in qualifiedName

            # If explicit glossary GUID provided, fetch that glossary directly
            explicit_guid_list = args.get("--glossary-guid")
            if explicit_guid_list:
                # Extract the GUID string from the list
                explicit_guid = explicit_guid_list[0] if isinstance(explicit_guid_list, list) else explicit_guid_list
                if os.getenv("PURVIEWCLI_DEBUG"):
                    print(f"[PURVIEWCLI DEBUG] get_terms: Using explicit glossary GUID: {explicit_guid}")
                # Pass as string, not list, to glossary client
                detailed = gclient.glossaryReadDetailed({"--glossaryGuid": explicit_guid})
                if isinstance(detailed, dict):
                    return [{
                        "guid": explicit_guid,
                        "name": detailed.get("name") or detailed.get("qualifiedName"),
                        "terms": detailed.get("terms") or [],
                    }]
                return []

            # 2) List all glossaries and try to find ones that look associated
            all_glossaries_resp = gclient.glossaryRead({})
            all_glossaries = _normalize_glossary_list(all_glossaries_resp)

            if os.getenv("PURVIEWCLI_DEBUG"):
                try:
                    print("[PURVIEWCLI DEBUG] get_terms: domain_id=", domain_id, "domain_name=", domain_name)
                    print("[PURVIEWCLI DEBUG] all_glossaries:", json.dumps(all_glossaries, default=str, indent=2))
                except Exception:
                    print("[PURVIEWCLI DEBUG] get_terms: (could not serialize glossary list)")

            matched = []
            for g in all_glossaries:
                if not isinstance(g, dict):
                    continue
                g_name = g.get("name") or g.get("qualifiedName") or ""
                g_guid = g.get("guid") or g.get("id") or g.get("glossaryGuid")
                qn = str(g.get("qualifiedName", ""))
                
                # For nested domains, look for domain_id in qualifiedName
                # Pattern: "Domain Name@domain-id" or similar
                if domain_id and domain_id in qn:
                    matched.append((g_guid, g))
                    continue
                
                # Match by exact name if we have domain_name
                if domain_name and domain_name.lower() == str(g_name).lower():
                    matched.append((g_guid, g))
                    continue
                    
                # Match if domain_name appears in qualifiedName
                if domain_name and domain_name.lower() in qn.lower():
                    matched.append((g_guid, g))
                    continue

            # 3) For matched glossaries, fetch detailed glossary (which contains terms)
            results = []
            for guid, base_g in matched:
                if not guid:
                    continue
                detailed = gclient.glossaryReadDetailed({"--glossaryGuid": [guid]})
                # glossaryReadDetailed should return a dict representing the glossary
                if isinstance(detailed, dict):
                    # some endpoints return the glossary inside 'data' or as raw dict
                    glossary_obj = detailed
                else:
                    glossary_obj = None

                # Ensure 'terms' key exists and is a list of term objects
                terms = []
                if isinstance(glossary_obj, dict):
                    terms = glossary_obj.get("terms") or []
                results.append({
                    "guid": guid,
                    "name": base_g.get("name") or base_g.get("qualifiedName"),
                    "terms": terms,
                })

            if os.getenv("PURVIEWCLI_DEBUG"):
                try:
                    print("[PURVIEWCLI DEBUG] get_terms matched results:", json.dumps(results, default=str, indent=2))
                except Exception:
                    print("[PURVIEWCLI DEBUG] get_terms matched results: (could not serialize)")
            return results

        except Exception as e:
            # If anything fails, return an empty list rather than crashing
            print(f"Warning: failed to list glossaries/terms for domain {domain_id}: {e}")
            return []

    @decorator
    def get_term_by_id(self, args):
        """Get a Unified Catalog term by ID."""
        term_id = args.get("--term-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/terms/{term_id}"
        self.params = {}

    @decorator
    def create_term(self, args):
        """Create a new Unified Catalog term (Governance Domain term)."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/terms"

        # Build Unified Catalog term payload
        domain_id = args.get("--governance-domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})
        
        # Get acronyms if provided
        acronyms = args.get("--acronym", [])
        
        # Get resources if provided
        resources = []
        resource_names = args.get("--resource-name", [])
        resource_urls = args.get("--resource-url", [])
        if resource_names and resource_urls:
            for i in range(min(len(resource_names), len(resource_urls))):
                resources.append({
                    "name": resource_names[i],
                    "url": resource_urls[i]
                })
        
        payload = {
            "name": name,
            "description": description,
            "domain": domain_id,
            "status": status,
        }
        
        # Add parent_id if provided
        parent_id = args.get("--parent-id", [""])[0]
        if parent_id:
            payload["parentId"] = parent_id
        
        # Add optional fields
        if owners:
            payload["contacts"] = {"owner": owners}
        if acronyms:
            payload["acronyms"] = acronyms
        if resources:
            payload["resources"] = resources

        self.payload = payload

    def update_term(self, args):
        """Update an existing Unified Catalog term (supports partial updates)."""
        from purviewcli.client.endpoint import get_data
        
        term_id = args.get("--term-id", [""])[0]
        
        # First, fetch the existing term to get current values
        fetch_client = UnifiedCatalogClient()
        existing_term = fetch_client.get_term_by_id({"--term-id": [term_id]})
        
        if not existing_term or (isinstance(existing_term, dict) and existing_term.get("error")):
            return {"error": f"Could not fetch existing term {term_id}"}
        
        # Start with existing term data
        payload = {
            "id": term_id,
            "name": existing_term.get("name", ""),
            "description": existing_term.get("description", ""),
            "domain": existing_term.get("domain", ""),
            "status": existing_term.get("status", "Draft"),
        }
        
        # Update with provided values (only if explicitly provided)
        if args.get("--name"):
            payload["name"] = args["--name"][0]
        if "--description" in args:  # Allow empty string
            payload["description"] = args.get("--description", [""])[0]
        if args.get("--governance-domain-id"):
            payload["domain"] = args["--governance-domain-id"][0]
        if args.get("--parent-id"):
            payload["parentId"] = args["--parent-id"][0]
        if args.get("--status"):
            payload["status"] = args["--status"][0]
        
        # Handle owners - replace or add to existing
        contacts = existing_term.get("contacts") or {}
        existing_owners = contacts.get("owner", []) if isinstance(contacts, dict) else []
        if args.get("--owner-id"):
            # Replace owners
            owners = [{"id": oid} for oid in args["--owner-id"]]
            payload["contacts"] = {"owner": owners}
        elif args.get("--add-owner-id"):
            # Add to existing owners
            existing_owner_ids = set()
            if isinstance(existing_owners, list):
                for o in existing_owners:
                    if isinstance(o, dict) and o.get("id"):
                        existing_owner_ids.add(o.get("id"))
            new_owner_ids = args["--add-owner-id"]
            combined_owner_ids = existing_owner_ids.union(set(new_owner_ids))
            owners = [{"id": oid} for oid in combined_owner_ids]
            payload["contacts"] = {"owner": owners}
        elif existing_owners:
            # Keep existing owners
            payload["contacts"] = {"owner": existing_owners}
        
        # Handle acronyms - replace or add to existing
        existing_acronyms = existing_term.get("acronyms", []) or []
        if args.get("--acronym"):
            # Replace acronyms
            payload["acronyms"] = list(args["--acronym"])
        elif args.get("--add-acronym"):
            # Add to existing acronyms
            combined_acronyms = list(set(existing_acronyms + list(args["--add-acronym"])))
            payload["acronyms"] = combined_acronyms
        elif existing_acronyms:
            # Keep existing acronyms
            payload["acronyms"] = existing_acronyms
        
        # Handle resources - replace with new ones if provided
        existing_resources = existing_term.get("resources", []) or []
        resource_names = args.get("--resource-name", [])
        resource_urls = args.get("--resource-url", [])
        if resource_names and resource_urls:
            # Replace resources
            resources = []
            for i in range(min(len(resource_names), len(resource_urls))):
                resources.append({
                    "name": resource_names[i],
                    "url": resource_urls[i]
                })
            payload["resources"] = resources
        elif existing_resources:
            # Keep existing resources
            payload["resources"] = existing_resources

        # Now make the actual PUT request
        http_dict = {
            "app": "datagovernance",
            "method": "PUT",
            "endpoint": f"/datagovernance/catalog/terms/{term_id}",
            "params": {},
            "payload": payload,
            "files": None,
            "headers": {},
        }
        
        return get_data(http_dict)

    @decorator
    def delete_term(self, args):
        """Delete a Unified Catalog term."""
        term_id = args.get("--term-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/terms/{term_id}"
        self.params = {}

    def _get_or_create_glossary_for_domain(self, domain_id):
        """Get or create a default glossary for the domain."""
        # Improved implementation:
        # 1. Try to find existing glossaries associated with the domain using get_terms()
        # 2. If none found, attempt to create a new glossary (using the Glossary client) and return its GUID
        # 3. If anything fails, return None so callers don't send an invalid GUID to the API
        if not domain_id:
            return None

        try:
            # Try to list glossaries for this domain using the existing get_terms API
            glossaries = self.get_terms({"--governance-domain-id": [domain_id]})

            # Normalize response to a list of glossary objects
            if isinstance(glossaries, dict):
                candidates = glossaries.get("value", []) or []
            elif isinstance(glossaries, (list, tuple)):
                candidates = glossaries
            else:
                candidates = []

            # If we have candidate glossaries, prefer the first valid GUID we find
            for g in candidates:
                if not isinstance(g, dict):
                    continue
                guid = g.get("guid") or g.get("glossaryGuid") or g.get("id")
                if guid:
                    return guid

            # Nothing found -> attempt to create a glossary for this domain.
            # Try to fetch domain metadata to produce a sensible glossary name.
            # Note: For nested domains, the direct fetch may fail with 404
            domain_info = None
            domain_name = None
            try:
                domain_info = self.get_governance_domain_by_id({"--domain-id": [domain_id]})
                if isinstance(domain_info, dict):
                    domain_name = domain_info.get("name") or domain_info.get("displayName")
            except Exception as e:
                if os.getenv("PURVIEWCLI_DEBUG"):
                    print(f"[PURVIEWCLI DEBUG] Could not fetch domain for glossary creation (may be nested): {e}")
                # Continue without domain_name

            glossary_name = domain_name or f"Glossary for domain {domain_id[:8]}"
            payload = {
                "name": glossary_name,
                "qualifiedName": f"{glossary_name}@{domain_id}",
                "shortDescription": f"Auto-created glossary for governance domain {domain_name or domain_id}",
            }

            # Import Glossary client lazily to avoid circular imports
            from ._glossary import Glossary

            gclient = Glossary()
            created = gclient.glossaryCreate({"--payloadFile": payload})

            # Attempt to extract GUID from the created response
            if isinstance(created, dict):
                new_guid = created.get("guid") or created.get("id") or created.get("glossaryGuid")
                if new_guid:
                    return new_guid

        except Exception as e:
            # Log a helpful warning and continue to safe fallback
            print(f"Warning: error looking up/creating glossary for domain {domain_id}: {e}")

        # Final safe fallback: return None so create_term doesn't send an invalid GUID
        print(f"Warning: No glossary found or created for domain {domain_id}")
        return None

    # ========================================
    # OBJECTIVES AND KEY RESULTS (OKRs)
    # ========================================

    @decorator
    def get_objectives(self, args):
        """Get all objectives in a governance domain."""
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = "/datagovernance/catalog/objectives"
        self.params = {"domainId": domain_id} if domain_id else {}

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

        domain_id = args.get("--governance-domain-id", [""])[0]
        definition = args.get("--definition", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "domain": domain_id,
            "definition": definition,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}
        if args.get("--target-date"):
            payload["targetDate"] = args["--target-date"][0]

        self.payload = payload

    @decorator
    def update_objective(self, args):
        """Update an existing objective."""
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}"

        domain_id = args.get("--governance-domain-id", [""])[0]
        definition = args.get("--definition", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "id": objective_id,
            "domain": domain_id,
            "definition": definition,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}
        if args.get("--target-date"):
            payload["targetDate"] = args["--target-date"][0]

        self.payload = payload

    @decorator
    def delete_objective(self, args):
        """Delete an objective."""
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}"
        self.params = {}

    # ========================================
    # KEY RESULTS (Part of OKRs)
    # ========================================

    @decorator
    def get_key_results(self, args):
        """Get all key results for an objective."""
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}/keyResults"
        self.params = {}

    @decorator
    def get_key_result_by_id(self, args):
        """Get a key result by ID."""
        objective_id = args.get("--objective-id", [""])[0]
        key_result_id = args.get("--key-result-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}/keyResults/{key_result_id}"
        self.params = {}

    @decorator
    def create_key_result(self, args):
        """Create a new key result."""
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "POST"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}/keyResults"

        domain_id = args.get("--governance-domain-id", [""])[0]
        progress = int(args.get("--progress", ["0"])[0])
        goal = int(args.get("--goal", ["100"])[0])
        max_value = int(args.get("--max", ["100"])[0])
        status = args.get("--status", ["OnTrack"])[0]
        definition = args.get("--definition", [""])[0]

        payload = {
            "progress": progress,
            "goal": goal,
            "max": max_value,
            "status": status,
            "definition": definition,
            "domainId": domain_id,
        }

        self.payload = payload

    @decorator
    def update_key_result(self, args):
        """Update an existing key result."""
        objective_id = args.get("--objective-id", [""])[0]
        key_result_id = args.get("--key-result-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}/keyResults/{key_result_id}"

        domain_id = args.get("--governance-domain-id", [""])[0]
        progress = int(args.get("--progress", ["0"])[0])
        goal = int(args.get("--goal", ["100"])[0])
        max_value = int(args.get("--max", ["100"])[0])
        status = args.get("--status", ["OnTrack"])[0]
        definition = args.get("--definition", [""])[0]

        payload = {
            "id": key_result_id,
            "progress": progress,
            "goal": goal,
            "max": max_value,
            "status": status,
            "definition": definition,
            "domainId": domain_id,
        }

        self.payload = payload

    @decorator
    def delete_key_result(self, args):
        """Delete a key result."""
        objective_id = args.get("--objective-id", [""])[0]
        key_result_id = args.get("--key-result-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/objectives/{objective_id}/keyResults/{key_result_id}"
        self.params = {}

    # ========================================
    # CRITICAL DATA ELEMENTS (CDEs)
    # ========================================

    @decorator
    def get_critical_data_elements(self, args):
        """Get all critical data elements in a governance domain."""
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = "/datagovernance/catalog/criticalDataElements"
        self.params = {"domainId": domain_id} if domain_id else {}

    @decorator
    def get_critical_data_element_by_id(self, args):
        """Get a critical data element by ID."""
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/criticalDataElements/{cde_id}"
        self.params = {}

    @decorator
    def create_critical_data_element(self, args):
        """Create a new critical data element."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/criticalDataElements"

        domain_id = args.get("--governance-domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--data-type", ["Number"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "name": name,
            "description": description,
            "domain": domain_id,
            "dataType": data_type,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}

        self.payload = payload

    @decorator
    def update_critical_data_element(self, args):
        """Update an existing critical data element."""
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/criticalDataElements/{cde_id}"

        domain_id = args.get("--governance-domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--data-type", ["Number"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "id": cde_id,
            "name": name,
            "description": description,
            "domain": domain_id,
            "dataType": data_type,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}

        self.payload = payload

    @decorator
    def delete_critical_data_element(self, args):
        """Delete a critical data element."""
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/criticalDataElements/{cde_id}"
        self.params = {}

    # ========================================
    # RELATIONSHIPS
    # ========================================
    
    @decorator
    def get_relationships(self, args):
        """Get all relationships for an entity (term, data product, or CDE).
        
        Supported entity types for filtering:
        - CustomMetadata: Custom attributes attached to the entity
        - DataAsset: Data assets (tables, columns) linked to the entity
        - DataProduct: Data products related to the entity
        - CriticalDataColumn: Critical data columns related to the entity
        - CriticalDataElement: Critical data elements related to the entity
        - Term: Other terms related to this entity
        """
        entity_type = args.get("--entity-type", [""])[0]  # Term, DataProduct, CriticalDataElement
        entity_id = args.get("--entity-id", [""])[0]
        filter_type = args.get("--filter-type", [""])[0]  # Optional: CustomMetadata, DataAsset, DataProduct, etc.
        
        # Map entity type to endpoint
        endpoint_map = {
            "Term": "terms",
            "DataProduct": "dataproducts", 
            "CriticalDataElement": "criticalDataElements",
        }
        
        endpoint_base = endpoint_map.get(entity_type)
        if not endpoint_base:
            raise ValueError(f"Invalid entity type: {entity_type}. Must be Term, DataProduct, or CriticalDataElement")
        
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/{endpoint_base}/{entity_id}/relationships"
        
        # Add optional entity type filter
        if filter_type:
            valid_filters = ["CustomMetadata", "DataAsset", "DataProduct", "CriticalDataColumn", "CriticalDataElement", "Term"]
            if filter_type not in valid_filters:
                raise ValueError(f"Invalid filter type: {filter_type}. Must be one of: {', '.join(valid_filters)}")
            self.params = {"entityType": filter_type}
        else:
            self.params = {}

    @decorator
    def create_relationship(self, args):
        """Create a relationship between entities (terms, data products, CDEs)."""
        entity_type = args.get("--entity-type", [""])[0]  # Term, DataProduct, CriticalDataElement
        entity_id = args.get("--entity-id", [""])[0]
        target_entity_id = args.get("--target-entity-id", [""])[0]
        relationship_type = args.get("--relationship-type", ["Related"])[0]  # Synonym, Related
        description = args.get("--description", [""])[0]
        
        # Map entity type to endpoint
        endpoint_map = {
            "Term": "terms",
            "DataProduct": "dataproducts",
            "CriticalDataElement": "criticalDataElements",
        }
        
        endpoint_base = endpoint_map.get(entity_type)
        if not endpoint_base:
            raise ValueError(f"Invalid entity type: {entity_type}. Must be Term, DataProduct, or CriticalDataElement")
        
        self.method = "POST"
        self.endpoint = f"/datagovernance/catalog/{endpoint_base}/{entity_id}/relationships"
        self.params = {"entityType": entity_type}
        
        self.payload = {
            "entityId": target_entity_id,
            "relationshipType": relationship_type,
            "description": description,
        }

    @decorator
    def delete_relationship(self, args):
        """Delete a relationship between entities."""
        entity_type = args.get("--entity-type", [""])[0]
        entity_id = args.get("--entity-id", [""])[0]
        target_entity_id = args.get("--target-entity-id", [""])[0]
        relationship_type = args.get("--relationship-type", ["Related"])[0]
        
        # Map entity type to endpoint
        endpoint_map = {
            "Term": "terms",
            "DataProduct": "dataproducts",
            "CriticalDataElement": "criticalDataElements",
        }
        
        endpoint_base = endpoint_map.get(entity_type)
        if not endpoint_base:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/{endpoint_base}/{entity_id}/relationships"
        self.params = {
            "entityId": target_entity_id,
            "entityType": entity_type,
            "relationshipType": relationship_type,
        }

    # ========================================
    # DATA POLICIES (NEW)
    # ========================================

    @decorator
    def list_policies(self, args):
        """List all data policies."""
        self.method = "GET"
        self.endpoint = "/datagovernance/catalog/policies"
        self.params = {}

    @decorator
    def get_policy(self, args):
        """Get a specific data policy by ID."""
        policy_id = args.get("--policy-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/policies/{policy_id}"
        self.params = {}

    @decorator
    def create_policy(self, args):
        """Create a new data policy."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/policies"
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        policy_type = args.get("--type", ["Access"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        payload = {
            "name": name,
            "description": description,
            "policyType": policy_type,
            "status": status,
        }
        
        self.payload = payload

    @decorator
    def update_policy(self, args):
        """Update an existing data policy."""
        policy_id = args.get("--policy-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/policies/{policy_id}"
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        policy_type = args.get("--type", ["Access"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        payload = {
            "name": name,
            "description": description,
            "policyType": policy_type,
            "status": status,
        }
        
        self.payload = payload

    @decorator
    def delete_policy(self, args):
        """Delete a data policy."""
        policy_id = args.get("--policy-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/policies/{policy_id}"
        self.params = {}

    # ========================================
    # CUSTOM METADATA (NEW)
    # ========================================

    @decorator
    def list_custom_metadata(self, args):
        """List all custom metadata definitions with UC term template filter.
        
        Uses Atlas API with includeTermTemplate=true to get UC Custom Metadata.
        This is the same API used by Purview UI for UC metadata.
        """
        self.method = "GET"
        self.endpoint = "/catalog/api/atlas/v2/types/typedefs"
        self.params = {
            "type": "business_metadata",
            "includeTermTemplate": "true",
            "api-version": "2022-11-03"
        }

    @decorator
    def get_custom_metadata(self, args):
        """Get custom metadata (business metadata) for a specific asset.
        
        Uses Entity API to get business metadata attached to a GUID.
        This returns all business metadata groups attached to the entity.
        """
        asset_id = args.get("--asset-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datamap/api/atlas/v2/entity/guid/{asset_id}"
        self.params = {
            "api-version": "2023-09-01",
            "minExtInfo": "false",
            "ignoreRelationships": "true"
        }

    @decorator
    def add_custom_metadata(self, args):
        """Add custom metadata (business metadata) to an asset.
        
        Uses Entity API to add business metadata to a GUID.
        Format: { "GroupName": { "attribute1": "value1", "attribute2": "value2" } }
        """
        asset_id = args.get("--asset-id", [""])[0]
        self.method = "POST"
        self.endpoint = f"/datamap/api/atlas/v2/entity/guid/{asset_id}/businessmetadata"
        self.params = {"api-version": "2023-09-01"}
        
        # Build payload based on parameters
        key = args.get("--key", [""])[0]
        value = args.get("--value", [""])[0]
        group = args.get("--group", ["Custom"])[0]  # Default group name
        
        # Format: { "GroupName": { "attributeName": "value" } }
        payload = {
            group: {
                key: value
            }
        }
        
        self.payload = payload

    @decorator
    def update_custom_metadata(self, args):
        """Update custom metadata (business metadata) for an asset.
        
        Uses Entity API to update business metadata on a GUID.
        POST method overwrites existing values for the specified attributes.
        Format: { "GroupName": { "attribute1": "newValue" } }
        """
        asset_id = args.get("--asset-id", [""])[0]
        self.method = "POST"
        self.endpoint = f"/datamap/api/atlas/v2/entity/guid/{asset_id}/businessmetadata"
        self.params = {"api-version": "2023-09-01"}
        
        key = args.get("--key", [""])[0]
        value = args.get("--value", [""])[0]
        group = args.get("--group", ["Custom"])[0]
        
        payload = {
            group: {
                key: value
            }
        }
        
        self.payload = payload

    @decorator
    def delete_custom_metadata(self, args):
        """Delete custom metadata (business metadata) from an asset.
        
        Uses Entity API to remove business metadata from a GUID.
        Removes entire business metadata group by passing it in params + empty payload.
        """
        asset_id = args.get("--asset-id", [""])[0]
        group = args.get("--group", [""])[0]
        
        if not group:
            raise ValueError("--group parameter is required to delete business metadata")
        
        self.method = "DELETE"
        self.endpoint = f"/datamap/api/atlas/v2/entity/guid/{asset_id}/businessmetadata"
        self.params = {
            "api-version": "2023-09-01"
        }
        # Payload must contain the group with empty dict to delete entire group
        self.payload = {
            group: {}
        }

    # ========================================
    # CUSTOM ATTRIBUTES (NEW)
    # ========================================

    @decorator
    def list_custom_attributes(self, args):
        """List all custom attribute definitions."""
        self.method = "GET"
        self.endpoint = "/datagovernance/catalog/attributes"
        self.params = {}

    @decorator
    def get_custom_attribute(self, args):
        """Get a specific custom attribute definition."""
        attribute_id = args.get("--attribute-id", [""])[0]
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/attributes/{attribute_id}"
        self.params = {}

    @decorator
    def create_custom_attribute(self, args):
        """Create a new custom attribute definition."""
        self.method = "POST"
        self.endpoint = "/datagovernance/catalog/attributes"
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--type", ["string"])[0]
        required = args.get("--required", ["false"])[0].lower() == "true"
        
        payload = {
            "name": name,
            "description": description,
            "dataType": data_type,
            "required": required,
        }
        
        self.payload = payload

    @decorator
    def update_custom_attribute(self, args):
        """Update a custom attribute definition."""
        attribute_id = args.get("--attribute-id", [""])[0]
        self.method = "PUT"
        self.endpoint = f"/datagovernance/catalog/attributes/{attribute_id}"
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--type", ["string"])[0]
        required = args.get("--required", ["false"])[0].lower() == "true"
        
        payload = {
            "name": name,
            "description": description,
            "dataType": data_type,
            "required": required,
        }
        
        self.payload = payload

    @decorator
    def delete_custom_attribute(self, args):
        """Delete a custom attribute definition."""
        attribute_id = args.get("--attribute-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/attributes/{attribute_id}"
        self.params = {}

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
- Terms: list, get, create, update, delete
- Objectives (OKRs): list, get, create, update, delete
- Key Results: list, get, create, update, delete
- Critical Data Elements: list, get, create, update, delete
- Data Policies: list, get, create, update, delete (NEW)
- Custom Metadata: list, get, add, update, delete (NEW)
- Custom Attributes: list, get, create, update, delete (NEW)
- Relationships: create, delete (between terms, data products, CDEs)

Use --payloadFile to provide JSON payload for create/update operations.
Use individual flags like --name, --description for simple operations.

Note: This client uses the Unified Catalog API (/datagovernance/catalog/*)
which is separate from the Data Map API (/catalog/api/atlas/*).
"""
        return {"message": help_text}
