from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import structlog

from app.core.logging import get_logger
from app.services.analytics_service import AnalyticsService

logger = get_logger(__name__)
router = APIRouter()

class MetricValue(BaseModel):
    name: str
    value: float
    unit: Optional[str] = None
    trend: Optional[float] = None  # percentage change
    timestamp: datetime

class ChartDataPoint(BaseModel):
    x: str  # x-axis value (date, category, etc.)
    y: float  # y-axis value
    label: Optional[str] = None

class ChartData(BaseModel):
    title: str
    type: str  # line, bar, pie, area, etc.
    data: List[ChartDataPoint]
    metadata: Optional[Dict[str, Any]] = {}

class DashboardMetrics(BaseModel):
    total_entities: MetricValue
    total_scans: MetricValue
    scan_success_rate: MetricValue
    data_quality_score: MetricValue
    governance_compliance: MetricValue

class ReportRequest(BaseModel):
    report_type: str
    date_range: Dict[str, str]  # start_date, end_date
    filters: Optional[Dict[str, Any]] = {}
    format: str = "json"  # json, csv, pdf

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    analytics_service: AnalyticsService = Depends()
):
    """Get key metrics for the dashboard"""
    try:
        metrics = await analytics_service.get_dashboard_metrics()
        return metrics
        
    except Exception as e:
        logger.error("Failed to get dashboard metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )

@router.get("/charts/{chart_type}", response_model=ChartData)
async def get_chart_data(
    chart_type: str,
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d, 1y"),
    entity_type: Optional[str] = None,
    analytics_service: AnalyticsService = Depends()
):
    """Get data for specific chart types"""
    try:
        valid_chart_types = [
            "entities_over_time", "scans_by_status", "data_sources_distribution",
            "classification_usage", "lineage_depth", "scan_performance",
            "data_quality_trends", "governance_metrics"
        ]
        
        if chart_type not in valid_chart_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid chart type. Valid types: {valid_chart_types}"
            )
            
        chart_data = await analytics_service.get_chart_data(
            chart_type=chart_type,
            time_range=time_range,
            entity_type=entity_type
        )
        
        return chart_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get chart data", chart_type=chart_type, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chart data: {str(e)}"
        )

@router.get("/metrics/entities")
async def get_entity_metrics(
    time_range: str = Query("30d", description="Time range: 1d, 7d, 30d, 90d, 1y"),
    entity_type: Optional[str] = None,
    analytics_service: AnalyticsService = Depends()
):
    """Get detailed entity metrics"""
    try:
        metrics = await analytics_service.get_entity_metrics(
            time_range=time_range,
            entity_type=entity_type
        )
        return metrics
        
    except Exception as e:
        logger.error("Failed to get entity metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity metrics: {str(e)}"
        )

@router.get("/metrics/scans")
async def get_scan_metrics(
    time_range: str = Query("30d", description="Time range: 1d, 7d, 30d, 90d, 1y"),
    data_source_type: Optional[str] = None,
    analytics_service: AnalyticsService = Depends()
):
    """Get detailed scan metrics"""
    try:
        metrics = await analytics_service.get_scan_metrics(
            time_range=time_range,
            data_source_type=data_source_type
        )
        return metrics
        
    except Exception as e:
        logger.error("Failed to get scan metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan metrics: {str(e)}"
        )

@router.get("/metrics/data-quality")
async def get_data_quality_metrics(
    time_range: str = Query("30d", description="Time range: 1d, 7d, 30d, 90d, 1y"),
    analytics_service: AnalyticsService = Depends()
):
    """Get data quality metrics"""
    try:
        metrics = await analytics_service.get_data_quality_metrics(time_range)
        return metrics
        
    except Exception as e:
        logger.error("Failed to get data quality metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data quality metrics: {str(e)}"
        )

@router.get("/metrics/governance")
async def get_governance_metrics(
    time_range: str = Query("30d", description="Time range: 1d, 7d, 30d, 90d, 1y"),
    analytics_service: AnalyticsService = Depends()
):
    """Get governance and compliance metrics"""
    try:
        metrics = await analytics_service.get_governance_metrics(time_range)
        return metrics
        
    except Exception as e:
        logger.error("Failed to get governance metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get governance metrics: {str(e)}"
        )

@router.post("/reports")
async def generate_report(
    report_request: ReportRequest,
    analytics_service: AnalyticsService = Depends()
):
    """Generate custom analytics report"""
    try:
        valid_report_types = [
            "entity_summary", "scan_summary", "lineage_analysis",
            "data_quality_report", "governance_report", "usage_report"
        ]
        
        if report_request.report_type not in valid_report_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid report type. Valid types: {valid_report_types}"
            )
            
        report = await analytics_service.generate_report(report_request)
        
        logger.info("Report generated", report_type=report_request.report_type)
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate report", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.get("/reports")
async def get_available_reports(
    analytics_service: AnalyticsService = Depends()
):
    """Get list of available report types and templates"""
    try:
        reports = await analytics_service.get_available_reports()
        return reports
        
    except Exception as e:
        logger.error("Failed to get available reports", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available reports: {str(e)}"
        )

@router.get("/trends/entities")
async def get_entity_trends(
    time_range: str = Query("90d", description="Time range: 7d, 30d, 90d, 1y"),
    granularity: str = Query("day", description="Granularity: hour, day, week, month"),
    analytics_service: AnalyticsService = Depends()
):
    """Get entity creation and modification trends"""
    try:
        trends = await analytics_service.get_entity_trends(
            time_range=time_range,
            granularity=granularity
        )
        return trends
        
    except Exception as e:
        logger.error("Failed to get entity trends", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entity trends: {str(e)}"
        )

@router.get("/insights/recommendations")
async def get_recommendations(
    analytics_service: AnalyticsService = Depends()
):
    """Get AI-powered recommendations for data governance"""
    try:
        recommendations = await analytics_service.get_recommendations()
        return recommendations
        
    except Exception as e:
        logger.error("Failed to get recommendations", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.get("/health-score")
async def get_data_health_score(
    analytics_service: AnalyticsService = Depends()
):
    """Get overall data health score and breakdown"""
    try:
        health_score = await analytics_service.get_data_health_score()
        return health_score
        
    except Exception as e:
        logger.error("Failed to get data health score", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data health score: {str(e)}"
        )
