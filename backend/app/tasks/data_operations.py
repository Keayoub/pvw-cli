"""
Celery tasks for data operations and analytics.
Handles background data processing, analytics updates, and reporting.
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from celery import current_task
import structlog

from app.core.celery_app import celery_app, BaseTask
from app.core.logging import get_logger
from app.services.analytics_service import AnalyticsService
from app.services.entities_service import EntitiesService
from app.services.lineage_service import LineageService
from app.services.governance_service import GovernanceService
from app.services.cache_service import CacheService
from app.database.connection import get_db_session

logger = get_logger(__name__)

class DataOperationsTask(BaseTask):
    """Base class for data operations tasks."""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.entities_service = EntitiesService()
        self.lineage_service = LineageService()
        self.governance_service = GovernanceService()
        self.cache_service = CacheService()
    
    def update_progress(self, progress: int, message: str = None):
        """Update task progress."""
        current_task.update_state(
            state="PROGRESS",
            meta={
                "progress": progress,
                "message": message or f"Processing... {progress}%"
            }
        )

@celery_app.task(bind=True, base=DataOperationsTask, name="update_analytics_cache")
def update_analytics_cache_task(self):
    """
    Update analytics cache with latest data.
    Runs periodically to keep dashboard data fresh.
    """
    try:
        logger.info("Starting analytics cache update")
        
        self.update_progress(10, "Initializing analytics cache update...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Update dashboard metrics
            self.update_progress(20, "Updating dashboard metrics...")
            dashboard_metrics = loop.run_until_complete(
                self.analytics_service.get_dashboard_metrics()
            )
            
            # Cache dashboard metrics
            loop.run_until_complete(
                self.cache_service.set("analytics:dashboard_metrics", dashboard_metrics, ttl=900)
            )
            
            # Update scan analytics
            self.update_progress(40, "Updating scan analytics...")
            scan_analytics = loop.run_until_complete(
                self.analytics_service.get_scan_analytics({})
            )
            
            loop.run_until_complete(
                self.cache_service.set("analytics:scan_analytics", scan_analytics, ttl=900)
            )
            
            # Update classification analytics
            self.update_progress(60, "Updating classification analytics...")
            classification_analytics = loop.run_until_complete(
                self.analytics_service.get_classification_analytics({})
            )
            
            loop.run_until_complete(
                self.cache_service.set("analytics:classification_analytics", classification_analytics, ttl=900)
            )
            
            # Update data quality metrics
            self.update_progress(80, "Updating data quality metrics...")
            quality_metrics = loop.run_until_complete(
                self.analytics_service.get_data_quality_metrics({})
            )
            
            loop.run_until_complete(
                self.cache_service.set("analytics:quality_metrics", quality_metrics, ttl=900)
            )
            
            self.update_progress(100, "Analytics cache update completed")
            
            logger.info("Analytics cache update completed successfully")
            return {"status": "completed", "updated_at": datetime.utcnow().isoformat()}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Analytics cache update failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=DataOperationsTask, name="generate_data_lineage")
def generate_data_lineage_task(self, entity_guid: str):
    """
    Generate comprehensive data lineage for an entity.
    """
    try:
        logger.info("Starting data lineage generation", entity_guid=entity_guid)
        
        self.update_progress(10, "Initializing lineage generation...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get entity lineage
            self.update_progress(30, "Discovering upstream lineage...")
            upstream_lineage = loop.run_until_complete(
                self.lineage_service.get_lineage(entity_guid, direction="upstream", depth=3)
            )
            
            self.update_progress(60, "Discovering downstream lineage...")
            downstream_lineage = loop.run_until_complete(
                self.lineage_service.get_lineage(entity_guid, direction="downstream", depth=3)
            )
            
            # Perform impact analysis
            self.update_progress(80, "Performing impact analysis...")
            impact_analysis = loop.run_until_complete(
                self.lineage_service.analyze_impact(entity_guid)
            )
            
            # Generate lineage report
            lineage_report = {
                "entity_guid": entity_guid,
                "upstream_lineage": upstream_lineage,
                "downstream_lineage": downstream_lineage,
                "impact_analysis": impact_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache the lineage report
            loop.run_until_complete(
                self.cache_service.set(
                    f"lineage:entity:{entity_guid}", 
                    lineage_report, 
                    ttl=3600
                )
            )
            
            self.update_progress(100, "Lineage generation completed")
            
            logger.info("Data lineage generation completed", entity_guid=entity_guid)
            return lineage_report
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Data lineage generation failed", entity_guid=entity_guid, error=str(exc))
        raise exc

@celery_app.task(bind=True, base=DataOperationsTask, name="bulk_classification_update")
def bulk_classification_update_task(self, classification_updates: List[Dict[str, Any]]):
    """
    Apply classification updates in bulk.
    """
    try:
        logger.info("Starting bulk classification update", updates_count=len(classification_updates))
        
        self.update_progress(10, "Initializing bulk classification update...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            total_updates = len(classification_updates)
            successful_updates = []
            failed_updates = []
            
            for i, update in enumerate(classification_updates):
                try:
                    progress = int((i / total_updates) * 80) + 10
                    self.update_progress(
                        progress, 
                        f"Processing classification {i+1}/{total_updates}..."
                    )
                    
                    # Apply classification
                    result = loop.run_until_complete(
                        self.governance_service.apply_classification(
                            update["entity_guid"],
                            update["classification"]
                        )
                    )
                    
                    successful_updates.append({
                        "entity_guid": update["entity_guid"],
                        "classification": update["classification"],
                        "result": result
                    })
                    
                except Exception as e:
                    failed_updates.append({
                        "entity_guid": update["entity_guid"],
                        "classification": update["classification"],
                        "error": str(e)
                    })
            
            self.update_progress(100, "Bulk classification update completed")
            
            result = {
                "total_updates": total_updates,
                "successful_updates": len(successful_updates),
                "failed_updates": len(failed_updates),
                "success_details": successful_updates,
                "failure_details": failed_updates,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                "Bulk classification update completed",
                total=total_updates,
                successful=len(successful_updates),
                failed=len(failed_updates)
            )
            
            return result
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Bulk classification update failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=DataOperationsTask, name="data_quality_assessment")
def data_quality_assessment_task(self, entity_guids: List[str]):
    """
    Perform comprehensive data quality assessment for multiple entities.
    """
    try:
        logger.info("Starting data quality assessment", entities_count=len(entity_guids))
        
        self.update_progress(10, "Initializing data quality assessment...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            total_entities = len(entity_guids)
            quality_results = []
            
            for i, entity_guid in enumerate(entity_guids):
                progress = int((i / total_entities) * 80) + 10
                self.update_progress(
                    progress, 
                    f"Assessing entity {i+1}/{total_entities}..."
                )
                
                try:
                    # Get entity details
                    entity = loop.run_until_complete(
                        self.entities_service.get_entity(entity_guid)
                    )
                    
                    if entity:
                        # Perform quality assessment
                        quality_metrics = await self._assess_entity_quality(entity)
                        
                        quality_results.append({
                            "entity_guid": entity_guid,
                            "entity_name": entity.get("attributes", {}).get("name", "Unknown"),
                            "quality_metrics": quality_metrics,
                            "assessed_at": datetime.utcnow().isoformat()
                        })
                    
                except Exception as e:
                    logger.warning("Failed to assess entity quality", entity_guid=entity_guid, error=str(e))
                    quality_results.append({
                        "entity_guid": entity_guid,
                        "error": str(e),
                        "assessed_at": datetime.utcnow().isoformat()
                    })
            
            # Generate overall quality report
            overall_report = self._generate_quality_report(quality_results)
            
            self.update_progress(100, "Data quality assessment completed")
            
            result = {
                "total_entities": total_entities,
                "assessed_entities": len([r for r in quality_results if "quality_metrics" in r]),
                "failed_assessments": len([r for r in quality_results if "error" in r]),
                "quality_results": quality_results,
                "overall_report": overall_report,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Data quality assessment completed", entities_assessed=len(quality_results))
            return result
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Data quality assessment failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=DataOperationsTask, name="governance_compliance_check")
def governance_compliance_check_task(self, policy_ids: List[str]):
    """
    Check governance compliance for specified policies.
    """
    try:
        logger.info("Starting governance compliance check", policies_count=len(policy_ids))
        
        self.update_progress(10, "Initializing compliance check...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            total_policies = len(policy_ids)
            compliance_results = []
            
            for i, policy_id in enumerate(policy_ids):
                progress = int((i / total_policies) * 80) + 10
                self.update_progress(
                    progress, 
                    f"Checking policy {i+1}/{total_policies}..."
                )
                
                try:
                    # Check policy compliance
                    compliance_result = loop.run_until_complete(
                        self.governance_service.check_compliance(policy_id)
                    )
                    
                    compliance_results.append({
                        "policy_id": policy_id,
                        "compliance_result": compliance_result,
                        "checked_at": datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning("Failed to check policy compliance", policy_id=policy_id, error=str(e))
                    compliance_results.append({
                        "policy_id": policy_id,
                        "error": str(e),
                        "checked_at": datetime.utcnow().isoformat()
                    })
            
            # Generate compliance summary
            compliance_summary = self._generate_compliance_summary(compliance_results)
            
            self.update_progress(100, "Governance compliance check completed")
            
            result = {
                "total_policies": total_policies,
                "checked_policies": len([r for r in compliance_results if "compliance_result" in r]),
                "failed_checks": len([r for r in compliance_results if "error" in r]),
                "compliance_results": compliance_results,
                "compliance_summary": compliance_summary,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Governance compliance check completed", policies_checked=len(compliance_results))
            return result
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Governance compliance check failed", error=str(exc))
        raise exc

@celery_app.task(bind=True, base=DataOperationsTask, name="entity_relationship_discovery")
def entity_relationship_discovery_task(self, entity_guid: str, discovery_depth: int = 2):
    """
    Discover relationships for an entity using various algorithms.
    """
    try:
        logger.info("Starting entity relationship discovery", entity_guid=entity_guid)
        
        self.update_progress(10, "Initializing relationship discovery...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get entity details
            self.update_progress(20, "Loading entity details...")
            entity = loop.run_until_complete(
                self.entities_service.get_entity(entity_guid)
            )
            
            if not entity:
                raise ValueError(f"Entity not found: {entity_guid}")
            
            # Discover different types of relationships
            relationships = {}
            
            # Schema relationships
            self.update_progress(40, "Discovering schema relationships...")
            relationships["schema"] = await self._discover_schema_relationships(entity)
            
            # Data lineage relationships
            self.update_progress(60, "Discovering lineage relationships...")
            relationships["lineage"] = loop.run_until_complete(
                self.lineage_service.get_lineage(entity_guid, depth=discovery_depth)
            )
            
            # Semantic relationships
            self.update_progress(80, "Discovering semantic relationships...")
            relationships["semantic"] = await self._discover_semantic_relationships(entity)
            
            # Generate relationship report
            relationship_report = {
                "entity_guid": entity_guid,
                "entity_name": entity.get("attributes", {}).get("name", "Unknown"),
                "discovery_depth": discovery_depth,
                "relationships": relationships,
                "relationship_count": sum(len(rels) for rels in relationships.values() if isinstance(rels, list)),
                "discovered_at": datetime.utcnow().isoformat()
            }
            
            # Cache the relationship report
            loop.run_until_complete(
                self.cache_service.set(
                    f"relationships:entity:{entity_guid}", 
                    relationship_report, 
                    ttl=1800
                )
            )
            
            self.update_progress(100, "Relationship discovery completed")
            
            logger.info("Entity relationship discovery completed", entity_guid=entity_guid)
            return relationship_report
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error("Entity relationship discovery failed", entity_guid=entity_guid, error=str(exc))
        raise exc

# Helper methods
async def _assess_entity_quality(self, entity: Dict[str, Any]) -> Dict[str, Any]:
    """Assess quality metrics for an entity."""
    quality_metrics = {
        "completeness": 0,
        "accuracy": 0,
        "consistency": 0,
        "timeliness": 0,
        "validity": 0
    }
    
    attributes = entity.get("attributes", {})
    
    # Completeness check
    required_fields = ["name", "qualified_name", "description"]
    filled_fields = sum(1 for field in required_fields if attributes.get(field))
    quality_metrics["completeness"] = (filled_fields / len(required_fields)) * 100
    
    # Validity check (basic)
    if attributes.get("qualified_name"):
        quality_metrics["validity"] = 90 if "@" in attributes["qualified_name"] else 60
    
    # Timeliness check
    if entity.get("last_scanned"):
        last_scan = datetime.fromisoformat(entity["last_scanned"].replace("Z", "+00:00"))
        days_since_scan = (datetime.utcnow() - last_scan.replace(tzinfo=None)).days
        quality_metrics["timeliness"] = max(0, 100 - (days_since_scan * 5))
    
    # Calculate overall score
    quality_metrics["overall_score"] = sum(quality_metrics.values()) / len(quality_metrics)
    
    return quality_metrics

def _generate_quality_report(self, quality_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate overall quality report from individual results."""
    successful_results = [r for r in quality_results if "quality_metrics" in r]
    
    if not successful_results:
        return {"status": "no_data", "message": "No successful quality assessments"}
    
    # Calculate averages
    avg_metrics = {}
    for metric in ["completeness", "accuracy", "consistency", "timeliness", "validity", "overall_score"]:
        values = [r["quality_metrics"][metric] for r in successful_results if metric in r["quality_metrics"]]
        avg_metrics[f"avg_{metric}"] = sum(values) / len(values) if values else 0
    
    # Categorize entities by quality
    high_quality = len([r for r in successful_results if r["quality_metrics"]["overall_score"] >= 80])
    medium_quality = len([r for r in successful_results if 60 <= r["quality_metrics"]["overall_score"] < 80])
    low_quality = len([r for r in successful_results if r["quality_metrics"]["overall_score"] < 60])
    
    return {
        "total_entities": len(successful_results),
        "average_metrics": avg_metrics,
        "quality_distribution": {
            "high_quality": high_quality,
            "medium_quality": medium_quality,
            "low_quality": low_quality
        },
        "recommendations": self._generate_quality_recommendations(avg_metrics)
    }

def _generate_compliance_summary(self, compliance_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate compliance summary from check results."""
    successful_checks = [r for r in compliance_results if "compliance_result" in r]
    
    if not successful_checks:
        return {"status": "no_data", "message": "No successful compliance checks"}
    
    # Count compliance status
    compliant = len([r for r in successful_checks if r["compliance_result"].get("compliant", False)])
    non_compliant = len(successful_checks) - compliant
    
    # Identify common violations
    violations = []
    for result in successful_checks:
        if not result["compliance_result"].get("compliant", False):
            violations.extend(result["compliance_result"].get("violations", []))
    
    return {
        "total_policies_checked": len(successful_checks),
        "compliant_policies": compliant,
        "non_compliant_policies": non_compliant,
        "compliance_rate": (compliant / len(successful_checks)) * 100 if successful_checks else 0,
        "common_violations": list(set(violations))[:10],  # Top 10 most common
        "recommendations": self._generate_compliance_recommendations(violations)
    }

async def _discover_schema_relationships(self, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Discover schema-based relationships."""
    # Placeholder for schema relationship discovery
    return []

async def _discover_semantic_relationships(self, entity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Discover semantic relationships based on naming and metadata."""
    # Placeholder for semantic relationship discovery
    return []

def _generate_quality_recommendations(self, avg_metrics: Dict[str, float]) -> List[str]:
    """Generate quality improvement recommendations."""
    recommendations = []
    
    if avg_metrics.get("avg_completeness", 0) < 80:
        recommendations.append("Improve data completeness by implementing validation rules")
    
    if avg_metrics.get("avg_timeliness", 0) < 80:
        recommendations.append("Increase scan frequency to improve data timeliness")
    
    if avg_metrics.get("avg_validity", 0) < 80:
        recommendations.append("Implement data validation to improve validity scores")
    
    return recommendations

def _generate_compliance_recommendations(self, violations: List[str]) -> List[str]:
    """Generate compliance improvement recommendations."""
    recommendations = []
    
    violation_counts = {}
    for violation in violations:
        violation_counts[violation] = violation_counts.get(violation, 0) + 1
    
    # Top violations
    top_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for violation, count in top_violations:
        recommendations.append(f"Address recurring violation: {violation} (occurs {count} times)")
    
    return recommendations
