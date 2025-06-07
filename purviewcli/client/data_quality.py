"""
Data Quality and Validation Module
Provides data quality checks and validation for Purview operations
"""

import pandas as pd
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationRule:
    """Data validation rule definition"""
    name: str
    description: str
    severity: ValidationSeverity
    column: Optional[str] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required: bool = False
    allowed_values: Optional[List[str]] = None
    custom_validator: Optional[callable] = None

@dataclass
class ValidationResult:
    """Result of a validation check"""
    rule_name: str
    severity: ValidationSeverity
    message: str
    row_index: Optional[int] = None
    column: Optional[str] = None
    value: Any = None

class DataQualityValidator:
    """Validates data quality for Purview operations"""
    
    def __init__(self):
        self.rules = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules"""
        # GUID validation
        guid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.add_rule(ValidationRule(
            name="valid_guid",
            description="GUID format validation",
            severity=ValidationSeverity.ERROR,
            pattern=guid_pattern
        ))
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.add_rule(ValidationRule(
            name="valid_email",
            description="Email format validation",
            severity=ValidationSeverity.WARNING,
            pattern=email_pattern
        ))
        
        # Qualified name validation
        self.add_rule(ValidationRule(
            name="qualified_name_format",
            description="Qualified name should contain @ symbol",
            severity=ValidationSeverity.ERROR,
            custom_validator=lambda x: '@' in str(x) if x else False
        ))
        
        # Name length validation
        self.add_rule(ValidationRule(
            name="name_length",
            description="Name should be between 1 and 100 characters",
            severity=ValidationSeverity.ERROR,
            min_length=1,
            max_length=100
        ))
    
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """Remove a validation rule"""
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
    
    def validate_dataframe(self, df: pd.DataFrame, column_rules: Dict[str, List[str]] = None) -> List[ValidationResult]:
        """Validate entire DataFrame"""
        results = []
        
        # Global validations
        results.extend(self._validate_structure(df))
        
        # Column-specific validations
        if column_rules:
            for column, rule_names in column_rules.items():
                if column in df.columns:
                    for rule_name in rule_names:
                        rule = self._get_rule(rule_name)
                        if rule:
                            results.extend(self._validate_column(df, column, rule))
        
        return results
    
    def validate_entity_data(self, entity_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate entity data structure"""
        results = []
        
        # Check required fields
        required_fields = ['typeName']
        for field in required_fields:
            if field not in entity_data:
                results.append(ValidationResult(
                    rule_name="required_field",
                    severity=ValidationSeverity.ERROR,
                    message=f"Required field '{field}' is missing",
                    column=field
                ))
        
        # Validate attributes
        attributes = entity_data.get('attributes', {})
        if attributes:
            results.extend(self._validate_entity_attributes(attributes))
        
        return results
    
    def _validate_structure(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Validate DataFrame structure"""
        results = []
        
        # Check for empty DataFrame
        if df.empty:
            results.append(ValidationResult(
                rule_name="empty_dataframe",
                severity=ValidationSeverity.ERROR,
                message="DataFrame is empty"
            ))
        
        # Check for duplicate rows
        duplicates = df.duplicated()
        if duplicates.any():
            duplicate_indices = df[duplicates].index.tolist()
            results.append(ValidationResult(
                rule_name="duplicate_rows",
                severity=ValidationSeverity.WARNING,
                message=f"Found {len(duplicate_indices)} duplicate rows at indices: {duplicate_indices}"
            ))
        
        return results
    
    def _validate_column(self, df: pd.DataFrame, column: str, rule: ValidationRule) -> List[ValidationResult]:
        """Validate specific column against rule"""
        results = []
        
        for index, value in df[column].items():
            result = self._validate_value(value, rule, index, column)
            if result:
                results.append(result)
        
        return results
    
    def _validate_value(self, value: Any, rule: ValidationRule, row_index: int = None, column: str = None) -> Optional[ValidationResult]:
        """Validate single value against rule"""
        # Skip validation for null values unless required
        if pd.isna(value):
            if rule.required:
                return ValidationResult(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Required value is missing",
                    row_index=row_index,
                    column=column,
                    value=value
                )
            return None
        
        str_value = str(value)
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, str_value, re.IGNORECASE):
            return ValidationResult(
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Value '{value}' does not match pattern {rule.pattern}",
                row_index=row_index,
                column=column,
                value=value
            )
        
        # Length validation
        if rule.min_length and len(str_value) < rule.min_length:
            return ValidationResult(
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Value '{value}' is too short (minimum {rule.min_length} characters)",
                row_index=row_index,
                column=column,
                value=value
            )
        
        if rule.max_length and len(str_value) > rule.max_length:
            return ValidationResult(
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Value '{value}' is too long (maximum {rule.max_length} characters)",
                row_index=row_index,
                column=column,
                value=value
            )
        
        # Allowed values validation
        if rule.allowed_values and str_value not in rule.allowed_values:
            return ValidationResult(
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Value '{value}' is not in allowed values: {rule.allowed_values}",
                row_index=row_index,
                column=column,
                value=value
            )
        
        # Custom validator
        if rule.custom_validator:
            try:
                if not rule.custom_validator(value):
                    return ValidationResult(
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=f"Value '{value}' failed custom validation",
                        row_index=row_index,
                        column=column,
                        value=value
                    )
            except Exception as e:
                return ValidationResult(
                    rule_name=rule.name,
                    severity=ValidationSeverity.ERROR,
                    message=f"Custom validator error: {e}",
                    row_index=row_index,
                    column=column,
                    value=value
                )
        
        return None
    
    def _validate_entity_attributes(self, attributes: Dict[str, Any]) -> List[ValidationResult]:
        """Validate entity attributes"""
        results = []
        
        # Validate qualifiedName format
        qualified_name = attributes.get('qualifiedName')
        if qualified_name:
            rule = self._get_rule('qualified_name_format')
            if rule:
                result = self._validate_value(qualified_name, rule, column='qualifiedName')
                if result:
                    results.append(result)
        
        # Validate name length
        name = attributes.get('name')
        if name:
            rule = self._get_rule('name_length')
            if rule:
                result = self._validate_value(name, rule, column='name')
                if result:
                    results.append(result)
        
        return results
    
    def _get_rule(self, rule_name: str) -> Optional[ValidationRule]:
        """Get validation rule by name"""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None

class DataQualityReport:
    """Generate data quality reports"""
    
    @staticmethod
    def generate_report(validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate comprehensive data quality report"""
        
        # Categorize results by severity
        errors = [r for r in validation_results if r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in validation_results if r.severity == ValidationSeverity.WARNING]
        info = [r for r in validation_results if r.severity == ValidationSeverity.INFO]
        
        # Count issues by rule
        rule_counts = {}
        for result in validation_results:
            rule_counts[result.rule_name] = rule_counts.get(result.rule_name, 0) + 1
        
        # Count issues by column
        column_counts = {}
        for result in validation_results:
            if result.column:
                column_counts[result.column] = column_counts.get(result.column, 0) + 1
        
        return {
            'summary': {
                'total_issues': len(validation_results),
                'errors': len(errors),
                'warnings': len(warnings),
                'info': len(info),
                'data_quality_score': DataQualityReport._calculate_quality_score(validation_results)
            },
            'issues_by_rule': rule_counts,
            'issues_by_column': column_counts,
            'error_details': [
                {
                    'rule': r.rule_name,
                    'message': r.message,
                    'row': r.row_index,
                    'column': r.column,
                    'value': r.value
                } for r in errors
            ],
            'warning_details': [
                {
                    'rule': r.rule_name,
                    'message': r.message,
                    'row': r.row_index,
                    'column': r.column,
                    'value': r.value
                } for r in warnings
            ]
        }
    
    @staticmethod
    def _calculate_quality_score(validation_results: List[ValidationResult]) -> float:
        """Calculate data quality score (0-100)"""
        if not validation_results:
            return 100.0
        
        # Weight errors more heavily than warnings
        error_weight = 3
        warning_weight = 1
        
        total_score = sum(
            error_weight if r.severity == ValidationSeverity.ERROR else warning_weight
            for r in validation_results
        )
        
        # Assume base score and deduct for issues
        base_score = 100.0
        deduction_per_issue = 2.0
        
        final_score = max(0.0, base_score - (total_score * deduction_per_issue))
        return round(final_score, 1)
    
    @staticmethod
    def export_report_to_csv(report: Dict[str, Any], output_file: str):
        """Export validation report to CSV"""
        
        # Create detailed issues DataFrame
        issues_data = []
        
        for error in report.get('error_details', []):
            issues_data.append({
                'severity': 'ERROR',
                'rule': error['rule'],
                'message': error['message'],
                'row': error['row'],
                'column': error['column'],
                'value': error['value']
            })
        
        for warning in report.get('warning_details', []):
            issues_data.append({
                'severity': 'WARNING',
                'rule': warning['rule'],
                'message': warning['message'],
                'row': warning['row'],
                'column': warning['column'],
                'value': warning['value']
            })
        
        if issues_data:
            df = pd.DataFrame(issues_data)
            df.to_csv(output_file, index=False)
        else:
            # Create empty file with headers
            pd.DataFrame(columns=['severity', 'rule', 'message', 'row', 'column', 'value']).to_csv(output_file, index=False)

# Predefined validation rule sets for common scenarios
# Entity validation rules mapping - maps entity types to validation rule names
ENTITY_VALIDATION_RULES = {
    'dataset': [
        'name_length',
        'qualified_name_format', 
        'valid_email',
        'valid_guid'
    ],
    'table': [
        'name_length',
        'qualified_name_format',
        'valid_email'
    ],
    'glossary_term': [
        'name_length',
        'valid_guid'
    ]
}

# Legacy field-based validation rules (for backward compatibility)
LEGACY_VALIDATION_RULES = {
    'name': ['name_length'],
    'qualifiedName': ['qualified_name_format'],
    'owner': ['valid_email'],
    'guid': ['valid_guid']
}

GLOSSARY_TERM_VALIDATION_RULES = {
    'name': ['name_length'],
    'glossaryGuid': ['valid_guid']
}

TABLE_VALIDATION_RULES = {
    'name': ['name_length'],
    'qualifiedName': ['qualified_name_format'],
    'db': ['name_length'],
    'owner': ['valid_email']
}
