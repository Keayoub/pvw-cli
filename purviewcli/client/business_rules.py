"""
Business Rules Engine for Azure Purview
Provides automated governance policy enforcement and compliance checking
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Optional pandas dependency for report generation
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Report generation features will be limited.")

from .api_client import PurviewClient
from .config import PurviewConfig

console = Console()

class RuleType(Enum):
    """Types of business rules"""
    DATA_CLASSIFICATION = "data_classification"
    OWNERSHIP = "ownership"
    RETENTION = "retention"
    ACCESS_CONTROL = "access_control"
    DATA_QUALITY = "data_quality"
    LINEAGE = "lineage"
    COMPLIANCE = "compliance"
    NAMING_CONVENTION = "naming_convention"

class RuleSeverity(Enum):
    """Rule violation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class RuleAction(Enum):
    """Actions to take when rules are violated"""
    LOG = "log"
    NOTIFY = "notify"
    AUTO_FIX = "auto_fix"
    BLOCK = "block"
    ESCALATE = "escalate"

@dataclass
class BusinessRule:
    """Business rule definition"""
    id: str
    name: str
    description: str
    rule_type: RuleType
    severity: RuleSeverity
    actions: List[RuleAction]
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class RuleViolation:
    """Rule violation result"""
    rule_id: str
    rule_name: str
    entity_guid: str
    entity_name: str
    entity_type: str
    violation_message: str
    severity: RuleSeverity
    detected_at: datetime
    recommended_action: str
    additional_context: Dict[str, Any] = field(default_factory=dict)

class BusinessRulesEngine:
    """Advanced business rules engine for data governance"""
    
    def __init__(self, client: PurviewClient):
        self.client = client
        self.console = Console()
        self.rules: Dict[str, BusinessRule] = {}
        self.load_default_rules()
    
    def load_default_rules(self):
        """Load default business rules"""
        default_rules = [
            BusinessRule(
                id="ownership_required",
                name="Ownership Required",
                description="All datasets must have an assigned owner",
                rule_type=RuleType.OWNERSHIP,
                severity=RuleSeverity.ERROR,
                actions=[RuleAction.NOTIFY, RuleAction.LOG],
                conditions={"entity_types": ["DataSet", "hive_table", "azure_datalake_gen2_path"]},
                parameters={"required_attributes": ["owner"], "grace_period_days": 7}
            ),
            BusinessRule(
                id="pii_classification_required",
                name="PII Classification Required",
                description="Entities containing PII data must be properly classified",
                rule_type=RuleType.DATA_CLASSIFICATION,
                severity=RuleSeverity.CRITICAL,
                actions=[RuleAction.BLOCK, RuleAction.ESCALATE],
                conditions={"contains_pii_patterns": True},
                parameters={"required_classifications": ["Microsoft.PersonalData.PII"]}
            ),
            BusinessRule(
                id="retention_policy_set",
                name="Retention Policy Required",
                description="All business-critical datasets must have retention policies",
                rule_type=RuleType.RETENTION,
                severity=RuleSeverity.WARNING,
                actions=[RuleAction.NOTIFY],
                conditions={"business_critical": True},
                parameters={"required_metadata": ["retention_period", "retention_policy"]}
            ),
            BusinessRule(
                id="naming_convention_compliance",
                name="Naming Convention Compliance",
                description="Entity names must follow organizational naming conventions",
                rule_type=RuleType.NAMING_CONVENTION,
                severity=RuleSeverity.WARNING,
                actions=[RuleAction.LOG, RuleAction.AUTO_FIX],
                conditions={"entity_types": ["DataSet", "hive_table"]},
                parameters={
                    "patterns": {
                        "DataSet": r"^[a-z]+_[a-z]+_[a-z]+$",  # env_domain_name
                        "hive_table": r"^[a-z]+_[a-z0-9_]+$"   # domain_tablename
                    }
                }
            ),
            BusinessRule(
                id="lineage_documentation",
                name="Lineage Documentation Required",
                description="Critical data assets must have documented lineage",
                rule_type=RuleType.LINEAGE,
                severity=RuleSeverity.ERROR,
                actions=[RuleAction.NOTIFY],
                conditions={"criticality": "high"},
                parameters={"min_upstream_entities": 1}
            ),
            BusinessRule(
                id="gdpr_compliance_check",
                name="GDPR Compliance Check",
                description="EU personal data must comply with GDPR requirements",
                rule_type=RuleType.COMPLIANCE,
                severity=RuleSeverity.CRITICAL,
                actions=[RuleAction.BLOCK, RuleAction.ESCALATE],
                conditions={"contains_eu_personal_data": True},
                parameters={
                    "required_classifications": ["Microsoft.PersonalData.GDPR"],
                    "required_metadata": ["data_subject_rights", "lawful_basis"]
                }
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def add_rule(self, rule: BusinessRule):
        """Add a new business rule"""
        self.rules[rule.id] = rule
    
    def remove_rule(self, rule_id: str):
        """Remove a business rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def enable_rule(self, rule_id: str):
        """Enable a business rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
    
    def disable_rule(self, rule_id: str):
        """Disable a business rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
    
    async def validate_entity(self, entity_guid: str) -> List[RuleViolation]:
        """Validate a single entity against all applicable rules"""
        violations = []
        
        try:
            # Get entity details
            entity = await self.client.get_entity(entity_guid)
            entity_attrs = entity.get('entity', {}).get('attributes', {})
            entity_type = entity.get('entity', {}).get('typeName', '')
            entity_name = entity_attrs.get('name', 'Unknown')
            
            # Check each enabled rule
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                if self._rule_applies_to_entity(rule, entity):
                    violation = await self._check_rule_compliance(rule, entity)
                    if violation:
                        violations.append(RuleViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            entity_guid=entity_guid,
                            entity_name=entity_name,
                            entity_type=entity_type,
                            violation_message=violation['message'],
                            severity=rule.severity,
                            detected_at=datetime.now(),
                            recommended_action=violation['recommended_action'],
                            additional_context=violation.get('context', {})
                        ))
        
        except Exception as e:
            self.console.print(f"[red]Error validating entity {entity_guid}: {str(e)}[/red]")
        
        return violations
    
    async def validate_entities_bulk(self, entity_guids: List[str], 
                                   progress_callback: Optional[Callable] = None) -> Dict[str, List[RuleViolation]]:
        """Validate multiple entities against business rules"""
        results = {}
        
        for i, guid in enumerate(entity_guids):
            violations = await self.validate_entity(guid)
            if violations:
                results[guid] = violations
            
            if progress_callback:
                progress_callback(i + 1, len(entity_guids))
        
        return results
    
    async def validate_collection(self, collection_name: str = None) -> Dict[str, List[RuleViolation]]:
        """Validate all entities in a collection"""
        self.console.print(f"[blue]Validating collection: {collection_name or 'default'}[/blue]")
        
        # Search for entities in the collection
        search_query = f"collection:{collection_name}" if collection_name else "*"
        search_results = await self.client.search_entities(search_query, limit=1000)
        
        entities = search_results.get('value', [])
        entity_guids = [entity.get('id') for entity in entities if entity.get('id')]
        
        self.console.print(f"[blue]Found {len(entity_guids)} entities to validate[/blue]")
        
        return await self.validate_entities_bulk(entity_guids)
    
    def _rule_applies_to_entity(self, rule: BusinessRule, entity: Dict) -> bool:
        """Check if a rule applies to the given entity"""
        entity_data = entity.get('entity', {})
        entity_type = entity_data.get('typeName', '')
        entity_attrs = entity_data.get('attributes', {})
        
        conditions = rule.conditions
        
        # Check entity type filter
        if 'entity_types' in conditions:
            if entity_type not in conditions['entity_types']:
                return False
        
        # Check business criticality
        if 'business_critical' in conditions:
            is_critical = self._is_business_critical(entity_attrs)
            if conditions['business_critical'] != is_critical:
                return False
        
        # Check PII patterns
        if 'contains_pii_patterns' in conditions:
            contains_pii = self._contains_pii_patterns(entity_attrs)
            if conditions['contains_pii_patterns'] != contains_pii:
                return False
        
        # Check GDPR applicability
        if 'contains_eu_personal_data' in conditions:
            contains_eu_data = self._contains_eu_personal_data(entity_attrs)
            if conditions['contains_eu_personal_data'] != contains_eu_data:
                return False
        
        return True
    
    async def _check_rule_compliance(self, rule: BusinessRule, entity: Dict) -> Optional[Dict]:
        """Check if entity complies with the specific rule"""
        entity_data = entity.get('entity', {})
        entity_attrs = entity_data.get('attributes', {})
        entity_guid = entity_data.get('guid', '')
        
        if rule.rule_type == RuleType.OWNERSHIP:
            return await self._check_ownership_rule(rule, entity_attrs)
        
        elif rule.rule_type == RuleType.DATA_CLASSIFICATION:
            return await self._check_classification_rule(rule, entity)
        
        elif rule.rule_type == RuleType.RETENTION:
            return await self._check_retention_rule(rule, entity_attrs)
        
        elif rule.rule_type == RuleType.NAMING_CONVENTION:
            return await self._check_naming_convention_rule(rule, entity_attrs)
        
        elif rule.rule_type == RuleType.LINEAGE:
            return await self._check_lineage_rule(rule, entity_guid)
        
        elif rule.rule_type == RuleType.COMPLIANCE:
            return await self._check_compliance_rule(rule, entity)
        
        return None
    
    async def _check_ownership_rule(self, rule: BusinessRule, entity_attrs: Dict) -> Optional[Dict]:
        """Check ownership rule compliance"""
        required_attrs = rule.parameters.get('required_attributes', ['owner'])
        
        for attr in required_attrs:
            if not entity_attrs.get(attr):
                return {
                    'message': f"Missing required ownership attribute: {attr}",
                    'recommended_action': f"Assign a value to the '{attr}' attribute",
                    'context': {'missing_attributes': [attr]}
                }
        
        return None
    
    async def _check_classification_rule(self, rule: BusinessRule, entity: Dict) -> Optional[Dict]:
        """Check data classification rule compliance"""
        entity_data = entity.get('entity', {})
        classifications = entity_data.get('classifications', [])
        required_classifications = rule.parameters.get('required_classifications', [])
        
        existing_classification_names = [c.get('typeName', '') for c in classifications]
        
        for required_class in required_classifications:
            if required_class not in existing_classification_names:
                return {
                    'message': f"Missing required classification: {required_class}",
                    'recommended_action': f"Apply the '{required_class}' classification",
                    'context': {
                        'required_classifications': required_classifications,
                        'existing_classifications': existing_classification_names
                    }
                }
        
        return None
    
    async def _check_retention_rule(self, rule: BusinessRule, entity_attrs: Dict) -> Optional[Dict]:
        """Check retention policy rule compliance"""
        required_metadata = rule.parameters.get('required_metadata', [])
        
        for metadata_field in required_metadata:
            if not entity_attrs.get(metadata_field):
                return {
                    'message': f"Missing retention metadata: {metadata_field}",
                    'recommended_action': f"Set the '{metadata_field}' attribute with appropriate retention information",
                    'context': {'missing_metadata': [metadata_field]}
                }
        
        return None
    
    async def _check_naming_convention_rule(self, rule: BusinessRule, entity_attrs: Dict) -> Optional[Dict]:
        """Check naming convention rule compliance"""
        entity_name = entity_attrs.get('name', '')
        entity_type = entity_attrs.get('typeName', '')
        
        patterns = rule.parameters.get('patterns', {})
        
        if entity_type in patterns:
            pattern = patterns[entity_type]
            if not re.match(pattern, entity_name):
                return {
                    'message': f"Entity name '{entity_name}' does not match required pattern: {pattern}",
                    'recommended_action': f"Rename entity to follow the pattern: {pattern}",
                    'context': {
                        'current_name': entity_name,
                        'required_pattern': pattern,
                        'entity_type': entity_type
                    }
                }
        
        return None
    
    async def _check_lineage_rule(self, rule: BusinessRule, entity_guid: str) -> Optional[Dict]:
        """Check lineage documentation rule compliance"""
        try:
            lineage = await self.client.get_lineage(entity_guid, 'INPUT', 1)
            relations = lineage.get('relations', [])
            
            min_upstream = rule.parameters.get('min_upstream_entities', 1)
            
            if len(relations) < min_upstream:
                return {
                    'message': f"Insufficient lineage documentation. Found {len(relations)} upstream entities, required {min_upstream}",
                    'recommended_action': "Document data lineage by creating relationships to source entities",
                    'context': {
                        'current_upstream_count': len(relations),
                        'required_minimum': min_upstream
                    }
                }
        
        except Exception as e:
            return {
                'message': f"Unable to verify lineage: {str(e)}",
                'recommended_action': "Ensure lineage information is properly configured",
                'context': {'error': str(e)}
            }
        
        return None
    
    async def _check_compliance_rule(self, rule: BusinessRule, entity: Dict) -> Optional[Dict]:
        """Check compliance rule (e.g., GDPR)"""
        # Check for required classifications
        classification_violation = await self._check_classification_rule(rule, entity)
        if classification_violation:
            return classification_violation
        
        # Check for required metadata
        entity_attrs = entity.get('entity', {}).get('attributes', {})
        required_metadata = rule.parameters.get('required_metadata', [])
        
        for metadata_field in required_metadata:
            if not entity_attrs.get(metadata_field):
                return {
                    'message': f"Missing compliance metadata: {metadata_field}",
                    'recommended_action': f"Add the required '{metadata_field}' compliance attribute",
                    'context': {'missing_compliance_metadata': [metadata_field]}
                }
        
        return None
    
    def _is_business_critical(self, entity_attrs: Dict) -> bool:
        """Determine if entity is business critical"""
        # Check for business criticality indicators
        criticality_indicators = [
            'business_critical',
            'criticality',
            'importance',
            'tier'
        ]
        
        for indicator in criticality_indicators:
            value = entity_attrs.get(indicator, '').lower()
            if value in ['critical', 'high', 'tier1', 'production', 'true']:
                return True
        
        # Check tags for criticality indicators
        tags = entity_attrs.get('tags', [])
        critical_tags = ['critical', 'production', 'business-critical', 'tier1']
        
        return any(tag.lower() in critical_tags for tag in tags)
    
    def _contains_pii_patterns(self, entity_attrs: Dict) -> bool:
        """Check if entity contains PII patterns"""
        pii_indicators = [
            'personal', 'pii', 'gdpr', 'privacy',
            'email', 'phone', 'ssn', 'social_security',
            'credit_card', 'passport', 'driver_license'
        ]
        
        # Check in name, description, and other text fields
        text_fields = [
            entity_attrs.get('name', ''),
            entity_attrs.get('description', ''),
            entity_attrs.get('qualifiedName', '')
        ]
        
        for text in text_fields:
            text_lower = text.lower()
            if any(indicator in text_lower for indicator in pii_indicators):
                return True
        
        return False
    
    def _contains_eu_personal_data(self, entity_attrs: Dict) -> bool:
        """Check if entity contains EU personal data"""
        eu_indicators = [
            'eu', 'europe', 'european', 'gdpr',
            'france', 'germany', 'spain', 'italy', 'uk'
        ]
        
        # Check location, region, or other geographic indicators
        location_fields = [
            entity_attrs.get('location', ''),
            entity_attrs.get('region', ''),
            entity_attrs.get('country', ''),
            entity_attrs.get('qualifiedName', '')
        ]
        
        for location in location_fields:
            location_lower = location.lower()
            if any(indicator in location_lower for indicator in eu_indicators):
                return True
        
        return False
    
    async def generate_compliance_report(self, output_file: str, 
                                       collection_name: str = None) -> Dict:
        """Generate comprehensive compliance report"""
        self.console.print("[blue]Generating compliance report...[/blue]")
        
        # Validate entities
        violations_by_entity = await self.validate_collection(collection_name)
        
        # Aggregate violations by rule and severity
        report_data = []
        rule_summary = {}
        severity_summary = {severity.value: 0 for severity in RuleSeverity}
        
        for entity_guid, violations in violations_by_entity.items():
            for violation in violations:
                report_data.append({
                    'entity_guid': entity_guid,
                    'entity_name': violation.entity_name,
                    'entity_type': violation.entity_type,
                    'rule_id': violation.rule_id,
                    'rule_name': violation.rule_name,
                    'severity': violation.severity.value,
                    'violation_message': violation.violation_message,
                    'recommended_action': violation.recommended_action,
                    'detected_at': violation.detected_at.isoformat(),
                    'additional_context': json.dumps(violation.additional_context)
                })
                
                # Update summaries
                if violation.rule_id not in rule_summary:
                    rule_summary[violation.rule_id] = {
                        'rule_name': violation.rule_name,
                        'violation_count': 0,
                        'severity': violation.severity.value
                    }
                rule_summary[violation.rule_id]['violation_count'] += 1
                severity_summary[violation.severity.value] += 1
        
        # Save detailed report
        if report_data:
            df = pd.DataFrame(report_data)
            df.to_csv(output_file, index=False)
        else:
            # Create empty report
            pd.DataFrame(columns=[
                'entity_guid', 'entity_name', 'entity_type', 'rule_id', 'rule_name',
                'severity', 'violation_message', 'recommended_action', 'detected_at',
                'additional_context'
            ]).to_csv(output_file, index=False)
        
        # Generate summary
        summary = {
            'report_file': output_file,
            'generated_at': datetime.now().isoformat(),
            'collection': collection_name or 'all',
            'total_violations': len(report_data),
            'entities_with_violations': len(violations_by_entity),
            'violations_by_severity': severity_summary,
            'violations_by_rule': rule_summary
        }
        
        # Display summary
        self._display_compliance_summary(summary)
        
        return summary
    
    def _display_compliance_summary(self, summary: Dict):
        """Display compliance report summary"""
        # Main summary panel
        summary_text = f"""
[bold green]Compliance Report Generated[/bold green]

📊 [cyan]Report Statistics:[/cyan]
   • Total Violations: {summary['total_violations']}
   • Entities Affected: {summary['entities_with_violations']}
   • Collection: {summary['collection']}

🚨 [yellow]Violations by Severity:[/yellow]
"""
        
        for severity, count in summary['violations_by_severity'].items():
            if count > 0:
                color = {
                    'critical': 'red',
                    'error': 'red',
                    'warning': 'yellow',
                    'info': 'blue'
                }.get(severity, 'white')
                summary_text += f"   • {severity.title()}: [{color}]{count}[/{color}]\n"
        
        self.console.print(Panel(summary_text, title="Compliance Report Summary"))
        
        # Top violations table
        if summary['violations_by_rule']:
            table = Table(title="Top Rule Violations", show_header=True, header_style="bold magenta")
            table.add_column("Rule Name", style="cyan")
            table.add_column("Violations", style="red", justify="right")
            table.add_column("Severity", style="yellow")
            
            # Sort by violation count
            sorted_rules = sorted(
                summary['violations_by_rule'].items(),
                key=lambda x: x[1]['violation_count'],
                reverse=True
            )
            
            for rule_id, rule_data in sorted_rules[:10]:  # Top 10
                table.add_row(
                    rule_data['rule_name'],
                    str(rule_data['violation_count']),
                    rule_data['severity'].title()
                )
            
            self.console.print(table)
    
    def export_rules_config(self, output_file: str):
        """Export rules configuration to file"""
        rules_config = {}
        for rule_id, rule in self.rules.items():
            rules_config[rule_id] = {
                'name': rule.name,
                'description': rule.description,
                'rule_type': rule.rule_type.value,
                'severity': rule.severity.value,
                'actions': [action.value for action in rule.actions],
                'enabled': rule.enabled,
                'conditions': rule.conditions,
                'parameters': rule.parameters,
                'created_by': rule.created_by,
                'tags': rule.tags
            }
        
        with open(output_file, 'w') as f:
            json.dump(rules_config, f, indent=2)
        
        self.console.print(f"[green]✓ Rules configuration exported to {output_file}[/green]")
    
    def import_rules_config(self, config_file: str):
        """Import rules configuration from file"""
        with open(config_file, 'r') as f:
            rules_config = json.load(f)
        
        imported_count = 0
        for rule_id, rule_data in rules_config.items():
            try:
                rule = BusinessRule(
                    id=rule_id,
                    name=rule_data['name'],
                    description=rule_data['description'],
                    rule_type=RuleType(rule_data['rule_type']),
                    severity=RuleSeverity(rule_data['severity']),
                    actions=[RuleAction(action) for action in rule_data['actions']],
                    enabled=rule_data.get('enabled', True),
                    conditions=rule_data.get('conditions', {}),
                    parameters=rule_data.get('parameters', {}),
                    created_by=rule_data.get('created_by', ''),
                    tags=rule_data.get('tags', [])
                )
                
                self.rules[rule_id] = rule
                imported_count += 1
                
            except Exception as e:
                self.console.print(f"[red]Failed to import rule {rule_id}: {str(e)}[/red]")
        
        self.console.print(f"[green]✓ Imported {imported_count} rules from {config_file}[/green]")

# Export the main classes
__all__ = [
    'BusinessRulesEngine',
    'BusinessRule',
    'RuleViolation',
    'RuleType',
    'RuleSeverity',
    'RuleAction'
]
