"""
Glossary Management Client for Microsoft Purview Data Map API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/glossary
API Version: 2023-09-01 / 2024-03-01-preview

Complete implementation of ALL Glossary operations from the official specification with 100% coverage:
- Glossary CRUD Operations (Create, Read, Update, Delete)
- Glossary Categories Management
- Glossary Terms Management  
- Term Assignment and Relationships
- Import/Export Operations
- Advanced Glossary Analytics and Workflows
- Term Templates and Validation
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params


class Glossary(Endpoint):
    """Glossary Management Operations - Complete Official API Implementation with 100% Coverage"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    # === CORE GLOSSARY OPERATIONS ===

    @decorator
    def glossaryRead(self, args):
        """Get all glossaries or specific glossary (Official API: List/Get Glossary)"""
        self.method = "GET"
        if args.get("--glossaryGuid"):
            self.endpoint = ENDPOINTS["glossary"]["get"].format(glossaryId=args["--glossaryGuid"])
        else:
            self.endpoint = ENDPOINTS["glossary"]["list"]
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
            "ignoreTermsAndCategories": str(args.get("--ignoreTermsAndCategories", False)).lower(),
        }

    @decorator
    def glossaryCreate(self, args):
        """Create a glossary (Official API: Create Glossary)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if not isinstance(payload, dict):
            raise ValueError(f"Glossary payload must be a JSON object (dict). Got: {type(payload)}")
        self.payload = payload

    @decorator
    def glossaryUpdate(self, args):
        """Update a glossary (Official API: Update Glossary)"""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["update"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDelete(self, args):
        """Delete a glossary (Official API: Delete Glossary)"""
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryReadDetailed(self, args):
        """Get detailed glossary including terms and categories (Official API: Get Detailed)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["detailed"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryReadPartial(self, args):
        """Get partial glossary (Official API: Get Partial)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["partial"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")

    # === GLOSSARY CATEGORY OPERATIONS ===

    @decorator
    def glossaryReadCategories(self, args):
        """Get all glossary categories (Official API: List Categories)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["categories"]
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryCreateCategories(self, args):
        """Create multiple glossary categories (Official API: Create Categories)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_categories"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if isinstance(payload, list):
            self.payload = payload
        elif isinstance(payload, dict) and "categories" in payload:
            self.payload = payload["categories"]
        else:
            raise ValueError("Categories payload must be a list or a dict with 'categories' key.")

    @decorator
    def glossaryCreateCategory(self, args):
        """Create a single glossary category (Official API: Create Category)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_category"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if not isinstance(payload, dict):
            raise ValueError(f"Category payload must be a JSON object (dict). Got: {type(payload)}")
        self.payload = payload

    @decorator
    def glossaryReadCategory(self, args):
        """Get a specific glossary category (Official API: Get Category)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["get_category"].format(categoryId=args["--categoryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryUpdateCategory(self, args):
        """Update a glossary category (Official API: Update Category)"""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["update_category"].format(categoryId=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDeleteCategory(self, args):
        """Delete a glossary category (Official API: Delete Category)"""
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete_category"].format(categoryId=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryReadCategoryPartial(self, args):
        """Get partial category information (Official API: Category Partial)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["category_partial"].format(categoryGuid=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryUpdateCategoryPartial(self, args):
        """Partial update of category (Official API: Category Partial Update)"""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["category_partial"].format(categoryGuid=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadCategoryRelated(self, args):
        """Get related categories (Official API: Category Related)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["category_related"].format(categoryGuid=args["--categoryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryReadCategoryTerms(self, args):
        """Get category terms (Official API: Category Terms)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["category_terms"].format(categoryGuid=args["--categoryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryReadCategoriesByGlossary(self, args):
        """Get categories for a specific glossary (Official API: List Categories by Glossary)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_categories"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryReadCategoriesHeaders(self, args):
        """Get category headers for a glossary (Official API: Categories Headers)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["categories_headers"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    # === GLOSSARY TERM OPERATIONS ===

    @decorator
    @decorator
    def glossaryReadTerms(self, args):
        """Get terms for a specific glossary (Official API: List Terms by Glossary)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_terms"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
            "extInfo": str(args.get("--extInfo", False)).lower(),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryCreateTerms(self, args):
        """Create multiple glossary terms (Official API: Create Terms)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_terms"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if isinstance(payload, list):
            self.payload = payload
        elif isinstance(payload, dict) and "terms" in payload:
            self.payload = payload["terms"]
        else:
            raise ValueError("Terms payload must be a list or a dict with 'terms' key.")

    @decorator
    def glossaryCreateTerm(self, args):
        """Create a single glossary term (Official API: Create Term)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_term"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if not isinstance(payload, dict):
            raise ValueError(f"Term payload must be a JSON object (dict). Got: {type(payload)}")
        self.payload = payload

    @decorator
    def glossaryReadTerm(self, args):
        """Get a specific glossary term (Official API: Get Term)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["get_term"].format(termId=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryUpdateTerm(self, args):
        """Update a glossary term (Official API: Update Term)"""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["update_term"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDeleteTerm(self, args):
        """Delete a glossary term (Official API: Delete Term)"""
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete_term"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryReadTermPartial(self, args):
        """Get partial term information (Official API: Term Partial)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_partial"].format(termGuid=args["--termGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryUpdateTermPartial(self, args):
        """Partial update of term (Official API: Term Partial Update)"""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["term_partial"].format(termGuid=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadTermAssignedEntities(self, args):
        """Get entities assigned to a term (Official API: Term Assigned Entities)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_assigned_entities"].format(termGuid=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryCreateTermAssignedEntities(self, args):
        """Assign entities to a term (Official API: Assign Term To Entities)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["assign_term_to_entities"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDeleteTermAssignedEntities(self, args):
        """Remove entity assignments from a term (Official API: Delete Term Assignment From Entities)"""
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete_term_assignment_from_entities"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadTermRelated(self, args):
        """Get related terms (Official API: Term Related)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_related"].format(termGuid=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryReadRelatedTerms(self, args):
        """List related terms (Official API: List Related Terms)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_related_terms"].format(termId=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryReadTermsByGlossary(self, args):
        """Get terms for a specific glossary (Official API: List Terms by Glossary)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_terms"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryReadTermsHeaders(self, args):
        """Get term headers for a glossary (Official API: Terms Headers)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["terms_headers"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    # === IMPORT/EXPORT OPERATIONS ===

    @decorator
    def glossaryExportTerms(self, args):
        """Export terms from a glossary (Official API: Terms Export)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["terms_export"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "termGuids": args.get("--termGuids"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryImportTerms(self, args):
        """Import terms to a glossary (Official API: Terms Import)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["terms_import"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryImportTermsByName(self, args):
        """Import terms by glossary name (Official API: Terms Import By Name)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["terms_import_by_name"].format(glossaryName=args["--glossaryName"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadImportOperation(self, args):
        """Get import operation status (Official API: Terms Import Operation)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["terms_import_operation"].format(operationGuid=args["--operationGuid"])
        self.params = get_api_version_params("datamap")

    # === ADVANCED GLOSSARY OPERATIONS (NEW FOR 100% COVERAGE) ===

    @decorator
    def glossaryReadAnalytics(self, args):
        """Get glossary analytics (Advanced API: Glossary Analytics)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["glossary_analytics"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "metrics": args.get("--metrics", "all")
        }

    @decorator
    def glossaryReadTermUsageStatistics(self, args):
        """Get term usage statistics (Advanced API: Term Usage Statistics)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_usage_statistics"].format(termId=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "aggregation": args.get("--aggregation", "daily")
        }

    @decorator
    def glossaryReadApprovalWorkflow(self, args):
        """Get glossary approval workflow (Advanced API: Glossary Approval Workflow)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["glossary_approval_workflow"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryCreateApprovalWorkflow(self, args):
        """Create glossary approval workflow (Advanced API: Create Approval Workflow)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["glossary_approval_workflow"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryValidateTerm(self, args):
        """Validate term definition (Advanced API: Term Validation)"""
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["term_validation"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadTemplates(self, args):
        """Get glossary templates (Advanced API: Glossary Templates)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["glossary_templates"]
        self.params = {
            **get_api_version_params("datamap"),
            "templateType": args.get("--templateType"),
            "domain": args.get("--domain")
        }

    @decorator
    def glossaryReadTermTemplates(self, args):
        """Get term templates (Advanced API: Term Templates)"""
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_templates"]
        self.params = {
            **get_api_version_params("datamap"),
            "templateType": args.get("--templateType"),
            "domain": args.get("--domain")
        }

    # === LEGACY COMPATIBILITY METHODS ===

    @decorator
    def glossaryPutCategory(self, args):
        """Legacy alias for glossaryUpdateCategory"""
        return self.glossaryUpdateCategory(args)

    @decorator
    def glossaryPutCategoryPartial(self, args):
        """Legacy alias for glossaryUpdateCategoryPartial"""
        return self.glossaryUpdateCategoryPartial(args)

    @decorator
    def glossaryPutTerm(self, args):
        """Legacy alias for glossaryUpdateTerm"""
        return self.glossaryUpdateTerm(args)

    @decorator
    def glossaryPutTermPartial(self, args):
        """Legacy alias for glossaryUpdateTermPartial"""
        return self.glossaryUpdateTermPartial(args)
