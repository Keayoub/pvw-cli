"""
Health API Client for Microsoft Purview Unified Catalog
Provides governance health monitoring and recommendations
"""

from .endpoint import Endpoint, decorator, no_api_call_decorator


class Health(Endpoint):
    """Health API operations for governance monitoring.
    
    API Version: 2024-02-01-preview
    Base Path: /datagovernance/health
    """

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "datagovernance"

    # ========================================
    # HEALTH ACTIONS
    # ========================================

    @decorator
    def query_health_actions(self, args):
        """Query health actions (findings and recommendations).
        
        Returns governance health findings including:
        - Missing metadata
        - Incomplete governance
        - Data quality issues
        - Compliance gaps
        
        Filter by domain, severity, status, etc.
        """
        self.method = "POST"
        self.endpoint = "/datagovernance/health/actions/query"
        self.params = {"api-version": "2024-02-01-preview"}
        
        # Build filter payload
        payload = {}
        
        domain_id = args.get("--domain-id", [""])[0]
        if domain_id:
            payload["domainId"] = domain_id
        
        severity = args.get("--severity", [""])[0]
        if severity:
            payload["severity"] = severity
        
        status = args.get("--status", [""])[0]
        if status:
            payload["status"] = status
        
        finding_type = args.get("--finding-type", [""])[0]
        if finding_type:
            payload["findingType"] = finding_type
        
        target_type = args.get("--target-entity-type", [""])[0]
        if target_type:
            payload["targetEntityType"] = target_type
        
        self.payload = payload

    @decorator
    def get_health_action(self, args):
        """Get details of a specific health action by ID."""
        action_id = args.get("--action-id", [""])[0]
        
        self.method = "GET"
        self.endpoint = f"/datagovernance/health/actions/{action_id}"
        self.params = {"api-version": "2024-02-01-preview"}

    @decorator
    def update_health_action(self, args):
        """Update a health action (change status, assignment, etc.)."""
        action_id = args.get("--action-id", [""])[0]
        
        self.method = "PUT"
        self.endpoint = f"/datagovernance/health/actions/{action_id}"
        self.params = {"api-version": "2024-02-01-preview"}
        
        payload = {}
        
        status = args.get("--status", [""])[0]
        if status:
            payload["status"] = status
        
        assigned_to = args.get("--assigned-to", [""])[0]
        if assigned_to:
            payload["assignedTo"] = [assigned_to] if assigned_to else []
        
        reason = args.get("--reason", [""])[0]
        if reason:
            payload["reason"] = reason
        
        self.payload = payload

    @decorator
    def delete_health_action(self, args):
        """Delete a health action."""
        action_id = args.get("--action-id", [""])[0]
        
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/health/actions/{action_id}"
        self.params = {"api-version": "2024-02-01-preview"}

    # ========================================
    # STATISTICS & SUMMARIES
    # ========================================

    @decorator
    def get_health_summary(self, args):
        """Get health summary statistics for a domain."""
        domain_id = args.get("--domain-id", [""])[0]
        
        self.method = "GET"
        self.endpoint = "/datagovernance/health/summary"
        self.params = {
            "api-version": "2024-02-01-preview",
            "domainId": domain_id
        }

    # ========================================
    # UTILITY METHODS
    # ========================================

    @no_api_call_decorator
    def help(self, args):
        """Display help information for Health API operations."""
        help_text = """
Microsoft Purview Health API Client

OVERVIEW:
The Health API provides automated governance monitoring and recommendations.
It identifies gaps in metadata, governance policies, and data quality.

OPERATIONS:
- query_health_actions: List all health findings with filters
- get_health_action: Get details of a specific finding
- update_health_action: Update status or assignment
- delete_health_action: Delete a finding
- get_health_summary: Get health statistics for a domain

HEALTH FINDING TYPES:
- Estate Curation: Critical data identification, classification
- Access and Use: Terms of use, compliant data use
- Discoverability: Data cataloging, term assignment
- Trusted Data: Data quality enablement
- Value Creation: Business OKRs alignment
- Metadata Quality Management: Description quality, completeness

SEVERITY LEVELS:
- High: Critical governance gaps
- Medium: Important improvements needed
- Low: Nice-to-have enhancements

STATUS VALUES:
- NotStarted: No action taken
- InProgress: Being addressed
- Resolved: Completed
- Dismissed: Acknowledged but not acting

FILTERS:
--domain-id: Filter by governance domain
--severity: High, Medium, Low
--status: NotStarted, InProgress, Resolved, Dismissed
--finding-type: Estate Curation, Access and Use, etc.
--target-entity-type: BusinessDomain, DataProduct, Term, etc.

EXAMPLES:
# List all health actions
pvcli health query

# List high severity issues
pvcli health query --severity High

# List actions for a specific domain
pvcli health query --domain-id xxx

# Get details of a specific action
pvcli health show --action-id xxx

# Mark action as in progress
pvcli health update --action-id xxx --status InProgress

# Assign action to a user
pvcli health update --action-id xxx --assigned-to user@domain.com

API VERSION: 2024-02-01-preview
"""
        return {"message": help_text}
