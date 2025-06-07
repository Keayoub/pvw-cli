"""
Governance Service for managing data governance policies, classifications, and compliance.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class PolicyStatus(Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    DISABLED = "disabled"
    ARCHIVED = "archived"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    UNDER_REVIEW = "under_review"

class GovernanceService:
    """Service for handling data governance operations."""
    
    def __init__(self):
        self.cache = {}
        self.mock_data = self._generate_mock_governance_data()
    
    def _generate_mock_governance_data(self) -> Dict[str, Any]:
        """Generate mock governance data for demonstration."""
        return {
            "policies": [
                {
                    "id": "pol_001",
                    "name": "PII Data Protection Policy",
                    "description": "Ensures PII data is properly classified and protected",
                    "status": PolicyStatus.ACTIVE.value,
                    "type": "classification",
                    "rules": [
                        "All PII fields must be classified as 'Confidential'",
                        "PII data must be encrypted at rest and in transit",
                        "Access to PII requires approval from data steward"
                    ],
                    "created_date": "2024-01-01T00:00:00Z",
                    "updated_date": "2024-01-15T10:30:00Z",
                    "created_by": "admin@company.com"
                },
                {
                    "id": "pol_002",
                    "name": "Data Retention Policy",
                    "description": "Defines data retention periods for different data types",
                    "status": PolicyStatus.ACTIVE.value,
                    "type": "retention",
                    "rules": [
                        "Customer data: 7 years retention",
                        "Transaction data: 10 years retention",
                        "Log data: 2 years retention"
                    ],
                    "created_date": "2024-01-05T00:00:00Z",
                    "updated_date": "2024-01-10T14:20:00Z",
                    "created_by": "data.officer@company.com"
                }
            ],
            "classifications": [
                {
                    "name": "Confidential",
                    "description": "Highly sensitive data requiring strict access controls",
                    "level": 4,
                    "color": "#ff4757",
                    "rules": [
                        "Encrypt at rest and in transit",
                        "Multi-factor authentication required",
                        "Audit all access"
                    ]
                },
                {
                    "name": "Internal",
                    "description": "Internal company data not for external sharing",
                    "level": 3,
                    "color": "#ffa502",
                    "rules": [
                        "Company employees only",
                        "Log access attempts"
                    ]
                },
                {
                    "name": "Public",
                    "description": "Publicly available information",
                    "level": 1,
                    "color": "#2ed573",
                    "rules": [
                        "Can be shared externally",
                        "No special restrictions"
                    ]
                }
            ]
        }
    
    async def get_policies(
        self,
        status: Optional[str] = None,
        policy_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get governance policies with optional filtering.
        
        Args:
            status: Filter by policy status
            policy_type: Filter by policy type
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            Dictionary containing policies and metadata
        """
        logger.info(f"Getting policies with filters: status={status}, type={policy_type}")
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        policies = self.mock_data["policies"].copy()
        
        # Apply filters
        if status:
            policies = [p for p in policies if p["status"] == status]
        if policy_type:
            policies = [p for p in policies if p["type"] == policy_type]
        
        # Apply pagination
        total = len(policies)
        policies = policies[offset:offset + limit]
        
        return {
            "policies": policies,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new governance policy.
        
        Args:
            policy_data: Policy information
        
        Returns:
            Dictionary containing created policy
        """
        logger.info(f"Creating new policy: {policy_data.get('name')}")
        
        # Simulate creation delay
        await asyncio.sleep(0.3)
        
        # Generate new policy ID
        policy_id = f"pol_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        new_policy = {
            "id": policy_id,
            "name": policy_data["name"],
            "description": policy_data.get("description", ""),
            "status": PolicyStatus.DRAFT.value,
            "type": policy_data.get("type", "general"),
            "rules": policy_data.get("rules", []),
            "created_date": datetime.utcnow().isoformat(),
            "updated_date": datetime.utcnow().isoformat(),
            "created_by": policy_data.get("created_by", "system")
        }
        
        return new_policy
    
    async def update_policy(
        self,
        policy_id: str,
        policy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing governance policy.
        
        Args:
            policy_id: ID of the policy to update
            policy_data: Updated policy information
        
        Returns:
            Dictionary containing updated policy
        """
        logger.info(f"Updating policy: {policy_id}")
        
        # Simulate update delay
        await asyncio.sleep(0.2)
        
        # Find existing policy (mock)
        existing_policy = next(
            (p for p in self.mock_data["policies"] if p["id"] == policy_id),
            None
        )
        
        if not existing_policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        # Update policy
        updated_policy = existing_policy.copy()
        updated_policy.update(policy_data)
        updated_policy["updated_date"] = datetime.utcnow().isoformat()
        
        return updated_policy
    
    async def get_compliance_status(
        self,
        entity_id: Optional[str] = None,
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get compliance status for entities or policies.
        
        Args:
            entity_id: Specific entity to check (optional)
            policy_id: Specific policy to check (optional)
        
        Returns:
            Dictionary containing compliance status
        """
        logger.info(f"Getting compliance status for entity={entity_id}, policy={policy_id}")
        
        # Simulate compliance check delay
        await asyncio.sleep(0.4)
        
        if entity_id:
            # Compliance status for specific entity
            compliance_data = {
                "entity_id": entity_id,
                "overall_status": ComplianceStatus.PARTIAL.value,
                "compliance_score": 78.5,
                "policy_results": [
                    {
                        "policy_id": "pol_001",
                        "policy_name": "PII Data Protection Policy",
                        "status": ComplianceStatus.COMPLIANT.value,
                        "score": 95.0,
                        "issues": []
                    },
                    {
                        "policy_id": "pol_002",
                        "policy_name": "Data Retention Policy",
                        "status": ComplianceStatus.NON_COMPLIANT.value,
                        "score": 62.0,
                        "issues": [
                            "Retention period not configured",
                            "Missing archival process"
                        ]
                    }
                ],
                "recommendations": [
                    "Configure data retention settings",
                    "Implement automated archival process"
                ]
            }
        else:
            # Overall compliance status
            compliance_data = {
                "overall_compliance": {
                    "score": 84.2,
                    "status": ComplianceStatus.PARTIAL.value,
                    "total_entities": 15750,
                    "compliant_entities": 13265,
                    "non_compliant_entities": 2485
                },
                "by_policy": [
                    {
                        "policy_id": "pol_001",
                        "policy_name": "PII Data Protection Policy",
                        "compliance_rate": 89.5,
                        "compliant_entities": 4025,
                        "non_compliant_entities": 475
                    },
                    {
                        "policy_id": "pol_002",
                        "policy_name": "Data Retention Policy",
                        "compliance_rate": 76.8,
                        "compliant_entities": 3456,
                        "non_compliant_entities": 1044
                    }
                ],
                "trend": {
                    "direction": "improving",
                    "change_30d": 3.2,
                    "change_7d": 0.8
                }
            }
        
        compliance_data["generated_at"] = datetime.utcnow().isoformat()
        return compliance_data
    
    async def get_classifications(self) -> Dict[str, Any]:
        """
        Get available data classifications.
        
        Returns:
            Dictionary containing classification definitions
        """
        logger.info("Getting classification definitions")
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        classifications = self.mock_data["classifications"].copy()
        
        # Add usage statistics
        for classification in classifications:
            classification["usage_stats"] = {
                "total_assets": 1500 + hash(classification["name"]) % 2000,
                "recent_additions": 45 + hash(classification["name"]) % 50,
                "confidence_avg": 0.85 + (hash(classification["name"]) % 100) / 1000
            }
        
        return {
            "classifications": classifications,
            "total_count": len(classifications),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def create_classification(
        self,
        classification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new data classification.
        
        Args:
            classification_data: Classification information
        
        Returns:
            Dictionary containing created classification
        """
        logger.info(f"Creating new classification: {classification_data.get('name')}")
        
        # Simulate creation delay
        await asyncio.sleep(0.2)
        
        new_classification = {
            "name": classification_data["name"],
            "description": classification_data.get("description", ""),
            "level": classification_data.get("level", 2),
            "color": classification_data.get("color", "#666666"),
            "rules": classification_data.get("rules", []),
            "created_date": datetime.utcnow().isoformat(),
            "created_by": classification_data.get("created_by", "system"),
            "usage_stats": {
                "total_assets": 0,
                "recent_additions": 0,
                "confidence_avg": 0.0
            }
        }
        
        return new_classification
    
    async def get_data_stewards(self) -> Dict[str, Any]:
        """
        Get data stewards and their assignments.
        
        Returns:
            Dictionary containing data steward information
        """
        logger.info("Getting data steward information")
        
        # Simulate API delay
        await asyncio.sleep(0.2)
        
        stewards_data = {
            "stewards": [
                {
                    "id": "steward_001",
                    "name": "Alice Johnson",
                    "email": "alice.johnson@company.com",
                    "department": "Finance",
                    "role": "Senior Data Steward",
                    "assigned_assets": 234,
                    "domains": ["Financial Data", "Customer Data"],
                    "status": "active",
                    "last_activity": "2024-01-15T14:30:00Z"
                },
                {
                    "id": "steward_002",
                    "name": "Bob Smith",
                    "email": "bob.smith@company.com",
                    "department": "IT",
                    "role": "Technical Data Steward",
                    "assigned_assets": 567,
                    "domains": ["System Data", "Log Data"],
                    "status": "active",
                    "last_activity": "2024-01-15T16:45:00Z"
                },
                {
                    "id": "steward_003",
                    "name": "Carol Davis",
                    "email": "carol.davis@company.com",
                    "department": "Marketing",
                    "role": "Domain Data Steward",
                    "assigned_assets": 123,
                    "domains": ["Marketing Data", "Customer Analytics"],
                    "status": "active",
                    "last_activity": "2024-01-15T11:20:00Z"
                }
            ],
            "summary": {
                "total_stewards": 3,
                "active_stewards": 3,
                "total_assigned_assets": 924,
                "unassigned_assets": 234,
                "coverage_percentage": 79.8
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return stewards_data
    
    async def assign_steward(
        self,
        entity_id: str,
        steward_id: str,
        assignment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assign a data steward to an entity.
        
        Args:
            entity_id: ID of the entity
            steward_id: ID of the steward
            assignment_data: Assignment details
        
        Returns:
            Dictionary containing assignment result
        """
        logger.info(f"Assigning steward {steward_id} to entity {entity_id}")
        
        # Simulate assignment delay
        await asyncio.sleep(0.2)
        
        assignment = {
            "assignment_id": f"assign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "entity_id": entity_id,
            "steward_id": steward_id,
            "assigned_date": datetime.utcnow().isoformat(),
            "assigned_by": assignment_data.get("assigned_by", "system"),
            "responsibility_level": assignment_data.get("responsibility_level", "full"),
            "notes": assignment_data.get("notes", ""),
            "status": "active"
        }
        
        return assignment
    
    async def get_audit_log(
        self,
        days: int = 30,
        entity_id: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get governance audit log entries.
        
        Args:
            days: Number of days to retrieve
            entity_id: Filter by specific entity
            action_type: Filter by action type
            limit: Maximum number of entries
        
        Returns:
            Dictionary containing audit log entries
        """
        logger.info(f"Getting audit log for {days} days")
        
        # Simulate query delay
        await asyncio.sleep(0.3)
        
        # Mock audit log entries
        audit_entries = [
            {
                "id": "audit_001",
                "timestamp": "2024-01-15T16:30:00Z",
                "user": "alice.johnson@company.com",
                "action": "policy_created",
                "entity_type": "policy",
                "entity_id": "pol_003",
                "details": "Created new data retention policy",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            {
                "id": "audit_002",
                "timestamp": "2024-01-15T15:45:00Z",
                "user": "bob.smith@company.com",
                "action": "classification_applied",
                "entity_type": "table",
                "entity_id": "table_customer_data",
                "details": "Applied 'Confidential' classification",
                "ip_address": "192.168.1.105",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            {
                "id": "audit_003",
                "timestamp": "2024-01-15T14:20:00Z",
                "user": "carol.davis@company.com",
                "action": "steward_assigned",
                "entity_type": "dataset",
                "entity_id": "dataset_marketing_analytics",
                "details": "Assigned as data steward",
                "ip_address": "192.168.1.110",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        ]
        
        audit_data = {
            "entries": audit_entries,
            "total_entries": len(audit_entries),
            "period_days": days,
            "filters": {
                "entity_id": entity_id,
                "action_type": action_type
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return audit_data
