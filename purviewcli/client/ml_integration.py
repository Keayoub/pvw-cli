"""
Machine Learning Integration for Azure Purview
Provides intelligent data discovery, anomaly detection, and predictive analytics
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console

# Optional ML dependencies - graceful fallback if not available
try:
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    ML_AVAILABLE = True
except ImportError as e:
    # Create mock classes for when ML dependencies are not available
    pd = None
    np = None
    TfidfVectorizer = None
    KMeans = None
    cosine_similarity = None
    StandardScaler = None
    IsolationForest = None
    ML_AVAILABLE = False
    print(f"Warning: ML dependencies not available ({e}). ML features will be limited.")
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID

from .api_client import PurviewClient
from .config import PurviewProfile

console = Console()

class MLTaskType(Enum):
    """Types of ML tasks"""
    DATA_DISCOVERY = "data_discovery"
    ANOMALY_DETECTION = "anomaly_detection"
    CLASSIFICATION_PREDICTION = "classification_prediction"
    LINEAGE_INFERENCE = "lineage_inference"
    QUALITY_PREDICTION = "quality_prediction"
    USAGE_PREDICTION = "usage_prediction"

class ConfidenceLevel(Enum):
    """Confidence levels for ML predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class MLInsight:
    """Machine learning insight"""
    id: str
    task_type: MLTaskType
    title: str
    description: str
    confidence: ConfidenceLevel
    confidence_score: float  # 0.0 to 1.0
    evidence: List[str]
    recommendations: List[str]
    affected_entities: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataPattern:
    """Discovered data pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    entities: List[str]
    attributes: List[str]
    frequency: int
    confidence_score: float

@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    entity_id: str
    anomaly_type: str
    severity_score: float
    description: str
    normal_range: Tuple[float, float]
    actual_value: float
    detection_timestamp: datetime

class IntelligentDataDiscovery:
    """ML-powered data discovery and analysis"""
    
    def __init__(self, client: PurviewClient):
        self.client = client
        self.console = Console()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        
    async def discover_similar_datasets(self, reference_entity_guid: str, similarity_threshold: float = 0.7) -> List[Dict]:
        """Discover datasets similar to a reference dataset using ML"""
        
        try:
            # Get reference entity
            reference_entity = await self.client.get_entity(reference_entity_guid)
            
            # Search for all datasets
            search_payload = {
                "keywords": "*",
                "limit": 1000,
                "filter": {"entityType": "DataSet"}
            }
            
            search_response = await self.client._make_request('POST', '/search/query', json=search_payload)
            datasets = search_response.get('value', [])
            
            if not datasets:
                return []
            
            # Extract features for similarity comparison
            features = []
            entity_metadata = []
            
            # Process reference entity
            ref_features = self._extract_entity_features(reference_entity)
            
            # Process all datasets
            for dataset in datasets:
                if dataset.get('id') == reference_entity_guid:
                    continue
                
                try:
                    entity = await self.client.get_entity(dataset.get('id'))
                    dataset_features = self._extract_entity_features(entity)
                    features.append(dataset_features)
                    entity_metadata.append({
                        'guid': dataset.get('id'),
                        'name': entity.get('attributes', {}).get('name', 'Unknown'),
                        'entity': entity
                    })
                except:
                    continue
            
            if not features:
                return []
            
            # Calculate similarities
            all_features = [ref_features] + features
            feature_matrix = self._vectorize_features(all_features)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(feature_matrix[0:1], feature_matrix[1:])[0]
            
            # Filter and sort results
            similar_datasets = []
            for i, similarity in enumerate(similarities):
                if similarity >= similarity_threshold:
                    metadata = entity_metadata[i]
                    similar_datasets.append({
                        'guid': metadata['guid'],
                        'name': metadata['name'],
                        'similarity_score': float(similarity),
                        'entity': metadata['entity']
                    })
            
            # Sort by similarity score
            similar_datasets.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_datasets
            
        except Exception as e:
            self.console.print(f"[red]Error in similar dataset discovery: {e}[/red]")
            return []
    
    def _extract_entity_features(self, entity: Dict) -> str:
        """Extract textual features from an entity for similarity analysis"""
        features = []
        
        attributes = entity.get('attributes', {})
        
        # Basic attributes
        name = attributes.get('name', '')
        description = attributes.get('description', '')
        owner = attributes.get('owner', '')
        
        features.extend([name, description, owner])
        
        # Schema information
        schema = attributes.get('schema', [])
        if isinstance(schema, list):
            for column in schema:
                if isinstance(column, dict):
                    col_name = column.get('name', '')
                    col_type = column.get('type', '')
                    features.extend([col_name, col_type])
        
        # Classifications
        classifications = entity.get('classifications', [])
        for classification in classifications:
            if isinstance(classification, dict):
                features.append(classification.get('typeName', ''))
        
        # Custom attributes
        custom_attrs = attributes.get('customAttributes', {})
        if isinstance(custom_attrs, dict):
            for key, value in custom_attrs.items():
                features.extend([key, str(value)])
        
        return ' '.join(filter(None, features))
    
    def _vectorize_features(self, feature_texts: List[str]) -> np.ndarray:
        """Convert text features to numerical vectors"""
        try:
            return self.vectorizer.fit_transform(feature_texts).toarray()
        except:
            # Fallback for empty or invalid texts
            return np.zeros((len(feature_texts), 100))
    
    async def detect_schema_anomalies(self, entity_type: str = "DataSet") -> List[AnomalyResult]:
        """Detect schema anomalies using ML"""
        
        anomalies = []
        
        try:
            # Get all entities of specified type
            search_payload = {
                "keywords": "*",
                "limit": 1000,
                "filter": {"entityType": entity_type}
            }
            
            search_response = await self.client._make_request('POST', '/search/query', json=search_payload)
            entities = search_response.get('value', [])
            
            if len(entities) < 10:  # Need minimum entities for anomaly detection
                return anomalies
            
            # Extract schema features
            schema_features = []
            entity_metadata = []
            
            for entity_ref in entities:
                try:
                    entity = await self.client.get_entity(entity_ref.get('id'))
                    features = self._extract_schema_features(entity)
                    
                    if features is not None:
                        schema_features.append(features)
                        entity_metadata.append({
                            'guid': entity_ref.get('id'),
                            'name': entity.get('attributes', {}).get('name', 'Unknown')
                        })
                except:
                    continue
            
            if len(schema_features) < 10:
                return anomalies
            
            # Normalize features
            feature_matrix = np.array(schema_features)
            normalized_features = self.scaler.fit_transform(feature_matrix)
            
            # Detect anomalies using Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(normalized_features)
            anomaly_scores = iso_forest.score_samples(normalized_features)
            
            # Process results
            for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                if label == -1:  # Anomaly detected
                    metadata = entity_metadata[i]
                    
                    anomaly = AnomalyResult(
                        entity_id=metadata['guid'],
                        anomaly_type="schema_anomaly",
                        severity_score=abs(score),
                        description=f"Unusual schema pattern detected in {metadata['name']}",
                        normal_range=(-0.5, 0.5),  # Typical range for normalized scores
                        actual_value=score,
                        detection_timestamp=datetime.now()
                    )
                    anomalies.append(anomaly)
            
        except Exception as e:
            self.console.print(f"[red]Error in anomaly detection: {e}[/red]")
        
        return anomalies
    
    def _extract_schema_features(self, entity: Dict) -> Optional[List[float]]:
        """Extract numerical features from entity schema"""
        try:
            attributes = entity.get('attributes', {})
            schema = attributes.get('schema', [])
            
            if not isinstance(schema, list):
                return None
            
            features = []
            
            # Basic schema metrics
            features.append(len(schema))  # Number of columns
            
            # Column type distribution
            type_counts = {}
            for column in schema:
                if isinstance(column, dict):
                    col_type = column.get('type', 'unknown').lower()
                    type_counts[col_type] = type_counts.get(col_type, 0) + 1
            
            # Common types
            common_types = ['string', 'int', 'float', 'boolean', 'date', 'timestamp']
            for col_type in common_types:
                features.append(type_counts.get(col_type, 0))
            
            # Name pattern analysis
            column_names = [col.get('name', '') for col in schema if isinstance(col, dict)]
            avg_name_length = np.mean([len(name) for name in column_names]) if column_names else 0
            features.append(avg_name_length)
            
            # Naming convention patterns
            underscore_count = sum(1 for name in column_names if '_' in name)
            camel_case_count = sum(1 for name in column_names if re.search(r'[a-z][A-Z]', name))
            
            features.extend([underscore_count, camel_case_count])
            
            return features
            
        except Exception as e:
            return None
    
    async def predict_data_classifications(self, entity_guid: str) -> List[Dict]:
        """Predict potential classifications for an entity using ML"""
        
        predictions = []
        
        try:
            # Get entity
            entity = await self.client.get_entity(entity_guid)
            
            # Get existing classifications for training
            classification_samples = await self._get_classification_samples()
            
            if not classification_samples:
                return predictions
            
            # Extract features for the target entity
            target_features = self._extract_classification_features(entity)
            
            # Extract features for training samples
            training_features = []
            training_labels = []
            
            for sample in classification_samples:
                features = self._extract_classification_features(sample['entity'])
                if features:
                    training_features.append(features)
                    training_labels.extend(sample['classifications'])
            
            if not training_features:
                return predictions
            
            # Vectorize features
            all_features = training_features + [target_features]
            feature_matrix = self._vectorize_features(all_features)
            
            # Simple similarity-based prediction
            target_vector = feature_matrix[-1:, :]
            training_vectors = feature_matrix[:-1, :]
            
            similarities = cosine_similarity(target_vector, training_vectors)[0]
            
            # Get top similar entities and their classifications
            classification_scores = {}
            for i, similarity in enumerate(similarities):
                if similarity > 0.3:  # Minimum similarity threshold
                    for classification in training_labels:
                        if classification not in classification_scores:
                            classification_scores[classification] = []
                        classification_scores[classification].append(similarity)
            
            # Calculate average scores and create predictions
            for classification, scores in classification_scores.items():
                avg_score = np.mean(scores)
                confidence = self._score_to_confidence(avg_score)
                
                predictions.append({
                    'classification': classification,
                    'confidence_score': float(avg_score),
                    'confidence_level': confidence.value,
                    'supporting_entities': len(scores)
                })
            
            # Sort by confidence score
            predictions.sort(key=lambda x: x['confidence_score'], reverse=True)
            
        except Exception as e:
            self.console.print(f"[red]Error in classification prediction: {e}[/red]")
        
        return predictions
    
    async def _get_classification_samples(self) -> List[Dict]:
        """Get entities with existing classifications for training"""
        samples = []
        
        try:
            # Search for classified entities
            search_payload = {
                "keywords": "*",
                "limit": 500,
                "filter": {
                    "not": {"attributeName": "classifications", "operator": "eq", "attributeValue": None}
                }
            }
            
            search_response = await self.client._make_request('POST', '/search/query', json=search_payload)
            entities = search_response.get('value', [])
            
            for entity_ref in entities[:100]:  # Limit for performance
                try:
                    entity = await self.client.get_entity(entity_ref.get('id'))
                    classifications = entity.get('classifications', [])
                    
                    if classifications:
                        classification_names = [c.get('typeName') for c in classifications if c.get('typeName')]
                        if classification_names:
                            samples.append({
                                'entity': entity,
                                'classifications': classification_names
                            })
                except:
                    continue
                    
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not get classification samples: {e}[/yellow]")
        
        return samples
    
    def _extract_classification_features(self, entity: Dict) -> str:
        """Extract features relevant for classification prediction"""
        features = []
        
        attributes = entity.get('attributes', {})
        
        # Basic attributes
        name = attributes.get('name', '')
        description = attributes.get('description', '')
        
        # Schema column names and types
        schema = attributes.get('schema', [])
        column_info = []
        
        if isinstance(schema, list):
            for column in schema:
                if isinstance(column, dict):
                    col_name = column.get('name', '').lower()
                    col_type = column.get('type', '').lower()
                    column_info.extend([col_name, col_type])
        
        features.extend([name, description] + column_info)
        
        return ' '.join(filter(None, features))
    
    def _score_to_confidence(self, score: float) -> ConfidenceLevel:
        """Convert numerical score to confidence level"""
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.6:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    async def discover_data_patterns(self) -> List[DataPattern]:
        """Discover common patterns in data using clustering"""
        patterns = []
        
        try:
            # Get all entities
            search_payload = {"keywords": "*", "limit": 1000}
            search_response = await self.client._make_request('POST', '/search/query', json=search_payload)
            entities = search_response.get('value', [])
            
            if len(entities) < 20:
                return patterns
            
            # Extract features for clustering
            entity_features = []
            entity_metadata = []
            
            for entity_ref in entities:
                try:
                    entity = await self.client.get_entity(entity_ref.get('id'))
                    features = self._extract_entity_features(entity)
                    
                    entity_features.append(features)
                    entity_metadata.append({
                        'guid': entity_ref.get('id'),
                        'name': entity.get('attributes', {}).get('name', 'Unknown'),
                        'type': entity.get('typeName', 'Unknown')
                    })
                except:
                    continue
            
            if len(entity_features) < 20:
                return patterns
            
            # Vectorize features
            feature_matrix = self._vectorize_features(entity_features)
            
            # Perform clustering
            n_clusters = min(10, len(entity_features) // 5)  # Reasonable number of clusters
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(feature_matrix)
            
            # Analyze clusters to identify patterns
            for cluster_id in range(n_clusters):
                cluster_entities = [
                    entity_metadata[i] for i, label in enumerate(cluster_labels) 
                    if label == cluster_id
                ]
                
                if len(cluster_entities) >= 3:  # Minimum entities for a pattern
                    # Analyze common attributes
                    common_attributes = self._find_common_attributes(cluster_entities)
                    
                    pattern = DataPattern(
                        pattern_id=f"pattern_{cluster_id}",
                        pattern_type="entity_cluster",
                        description=f"Group of {len(cluster_entities)} entities with similar characteristics",
                        entities=[e['guid'] for e in cluster_entities],
                        attributes=common_attributes,
                        frequency=len(cluster_entities),
                        confidence_score=0.7  # Based on clustering quality
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            self.console.print(f"[red]Error in pattern discovery: {e}[/red]")
        
        return patterns
    
    def _find_common_attributes(self, entities: List[Dict]) -> List[str]:
        """Find common attributes among a group of entities"""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated pattern analysis
        
        entity_types = [e['type'] for e in entities]
        type_counts = {}
        for et in entity_types:
            type_counts[et] = type_counts.get(et, 0) + 1
        
        common_attributes = []
        most_common_type = max(type_counts.keys(), key=lambda k: type_counts[k])
        
        if type_counts[most_common_type] >= len(entities) * 0.7:
            common_attributes.append(f"entity_type:{most_common_type}")
        
        return common_attributes

class MLRecommendationEngine:
    """ML-powered recommendation engine for data governance"""
    
    def __init__(self, client: PurviewClient):
        self.client = client
        self.console = Console()
        self.discovery_engine = IntelligentDataDiscovery(client)
    
    async def generate_governance_recommendations(self, entity_guid: str) -> List[MLInsight]:
        """Generate ML-powered governance recommendations"""
        insights = []
        
        try:
            entity = await self.client.get_entity(entity_guid)
            entity_name = entity.get('attributes', {}).get('name', 'Unknown')
            
            # Classification recommendations
            classification_predictions = await self.discovery_engine.predict_data_classifications(entity_guid)
            if classification_predictions:
                top_prediction = classification_predictions[0]
                confidence = ConfidenceLevel(top_prediction['confidence_level'])
                
                insight = MLInsight(
                    id=f"classification_{entity_guid}_{int(datetime.now().timestamp())}",
                    task_type=MLTaskType.CLASSIFICATION_PREDICTION,
                    title=f"Recommended Classification: {top_prediction['classification']}",
                    description=f"ML analysis suggests '{entity_name}' should be classified as {top_prediction['classification']}",
                    confidence=confidence,
                    confidence_score=top_prediction['confidence_score'],
                    evidence=[
                        f"Similar entities with {top_prediction['supporting_entities']} examples",
                        f"Content analysis confidence: {top_prediction['confidence_score']:.2f}"
                    ],
                    recommendations=[
                        f"Apply '{top_prediction['classification']}' classification",
                        "Review and validate the suggested classification",
                        "Consider implementing auto-classification rules"
                    ],
                    affected_entities=[entity_guid],
                    timestamp=datetime.now()
                )
                insights.append(insight)
            
            # Similar datasets recommendations
            similar_datasets = await self.discovery_engine.discover_similar_datasets(entity_guid, 0.6)
            if similar_datasets:
                top_similar = similar_datasets[0]
                
                insight = MLInsight(
                    id=f"similar_{entity_guid}_{int(datetime.now().timestamp())}",
                    task_type=MLTaskType.DATA_DISCOVERY,
                    title=f"Similar Dataset Found: {top_similar['name']}",
                    description=f"Found dataset '{top_similar['name']}' with {top_similar['similarity_score']:.2f} similarity",
                    confidence=ConfidenceLevel.HIGH if top_similar['similarity_score'] > 0.8 else ConfidenceLevel.MEDIUM,
                    confidence_score=top_similar['similarity_score'],
                    evidence=[
                        f"Similarity score: {top_similar['similarity_score']:.2f}",
                        "Based on schema, naming, and metadata analysis"
                    ],
                    recommendations=[
                        "Review similar dataset for governance best practices",
                        "Consider standardizing metadata and classifications",
                        "Explore potential data lineage relationships"
                    ],
                    affected_entities=[entity_guid, top_similar['guid']],
                    timestamp=datetime.now()
                )
                insights.append(insight)
            
            # Data quality recommendations
            quality_insight = await self._generate_quality_recommendations(entity)
            if quality_insight:
                insights.append(quality_insight)
            
        except Exception as e:
            self.console.print(f"[red]Error generating recommendations: {e}[/red]")
        
        return insights
    
    async def _generate_quality_recommendations(self, entity: Dict) -> Optional[MLInsight]:
        """Generate data quality recommendations"""
        try:
            attributes = entity.get('attributes', {})
            schema = attributes.get('schema', [])
            
            if not isinstance(schema, list) or not schema:
                return None
            
            # Analyze schema for quality issues
            quality_issues = []
            recommendations = []
            
            # Check for missing descriptions
            columns_without_desc = [
                col.get('name', 'Unknown') for col in schema 
                if isinstance(col, dict) and not col.get('description')
            ]
            
            if columns_without_desc:
                quality_issues.append(f"{len(columns_without_desc)} columns lack descriptions")
                recommendations.append("Add descriptions to all columns for better discoverability")
            
            # Check naming conventions
            inconsistent_naming = []
            naming_patterns = {'underscore': 0, 'camelCase': 0, 'PascalCase': 0}
            
            for col in schema:
                if isinstance(col, dict):
                    name = col.get('name', '')
                    if '_' in name:
                        naming_patterns['underscore'] += 1
                    elif re.search(r'^[a-z][a-zA-Z0-9]*[A-Z]', name):
                        naming_patterns['camelCase'] += 1
                    elif re.search(r'^[A-Z][a-zA-Z0-9]*', name):
                        naming_patterns['PascalCase'] += 1
            
            # Check if naming is inconsistent
            max_pattern = max(naming_patterns.values())
            total_columns = len(schema)
            
            if max_pattern < total_columns * 0.8:  # Less than 80% consistent
                quality_issues.append("Inconsistent column naming conventions")
                recommendations.append("Standardize column naming conventions")
            
            if quality_issues:
                confidence_score = 0.8 if len(quality_issues) > 2 else 0.6
                
                return MLInsight(
                    id=f"quality_{entity.get('guid', 'unknown')}_{int(datetime.now().timestamp())}",
                    task_type=MLTaskType.QUALITY_PREDICTION,
                    title="Data Quality Improvement Opportunities",
                    description=f"Analysis identified {len(quality_issues)} potential quality improvements",
                    confidence=ConfidenceLevel.HIGH if confidence_score > 0.7 else ConfidenceLevel.MEDIUM,
                    confidence_score=confidence_score,
                    evidence=quality_issues,
                    recommendations=recommendations,
                    affected_entities=[entity.get('guid', '')],
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return None
        
        return None
    
    async def batch_analyze_entities(self, entity_guids: List[str]) -> Dict[str, List[MLInsight]]:
        """Perform batch ML analysis on multiple entities"""
        results = {}
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing entities...", total=len(entity_guids))
            
            for guid in entity_guids:
                try:
                    insights = await self.generate_governance_recommendations(guid)
                    results[guid] = insights
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not analyze {guid}: {e}[/yellow]")
                    results[guid] = []
                
                progress.advance(task)
        
        return results
    
    def export_insights(self, insights: List[MLInsight], output_path: str):
        """Export ML insights to file"""
        insights_data = []
        
        for insight in insights:
            insights_data.append({
                'id': insight.id,
                'task_type': insight.task_type.value,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence.value,
                'confidence_score': insight.confidence_score,
                'evidence': insight.evidence,
                'recommendations': insight.recommendations,
                'affected_entities': insight.affected_entities,
                'timestamp': insight.timestamp.isoformat(),
                'metadata': insight.metadata
            })
        
        with open(output_path, 'w') as f:
            json.dump(insights_data, f, indent=2)
        
        self.console.print(f"[green]ML insights exported to {output_path}[/green]")

class PredictiveAnalytics:
    """Predictive analytics for data governance trends"""
    
    def __init__(self, client: PurviewClient):
        self.client = client
        self.console = Console()
    
    async def predict_scan_failures(self, lookback_days: int = 30) -> List[Dict]:
        """Predict potential scan failures based on historical data"""
        predictions = []
        
        try:
            # This is a simplified implementation
            # In practice, you'd collect historical scan data and train a proper model
            
            # Get data sources
            data_sources = await self.client._make_request('GET', '/scan/datasources')
            
            for ds in data_sources.get('value', [])[:10]:  # Limit for demo
                ds_name = ds.get('name', '')
                
                # Simulate failure prediction based on naming patterns and metadata
                risk_score = self._calculate_failure_risk(ds)
                
                if risk_score > 0.5:
                    predictions.append({
                        'data_source': ds_name,
                        'failure_probability': risk_score,
                        'predicted_issues': self._predict_failure_causes(ds),
                        'recommendations': self._generate_prevention_recommendations(ds)
                    })
        
        except Exception as e:
            self.console.print(f"[red]Error in failure prediction: {e}[/red]")
        
        return predictions
    
    def _calculate_failure_risk(self, data_source: Dict) -> float:
        """Calculate failure risk score for a data source"""
        # Simplified risk calculation
        risk_factors = 0
        
        name = data_source.get('name', '').lower()
        
        # Risk factors (simplified)
        if 'test' in name or 'temp' in name:
            risk_factors += 0.3
        
        if not data_source.get('description'):
            risk_factors += 0.2
        
        # Connection string issues (simplified check)
        properties = data_source.get('properties', {})
        if not properties:
            risk_factors += 0.4
        
        return min(risk_factors, 1.0)
    
    def _predict_failure_causes(self, data_source: Dict) -> List[str]:
        """Predict potential failure causes"""
        causes = []
        
        name = data_source.get('name', '').lower()
        properties = data_source.get('properties', {})
        
        if 'test' in name:
            causes.append("Test data source may be unstable")
        
        if not properties:
            causes.append("Missing connection properties")
        
        if not data_source.get('description'):
            causes.append("Lack of documentation may indicate configuration issues")
        
        return causes or ["General connectivity issues"]
    
    def _generate_prevention_recommendations(self, data_source: Dict) -> List[str]:
        """Generate recommendations to prevent failures"""
        recommendations = []
        
        if not data_source.get('description'):
            recommendations.append("Add detailed description and documentation")
        
        recommendations.extend([
            "Verify connection parameters",
            "Test connectivity before scheduling scans",
            "Implement monitoring and alerting"
        ])
        
        return recommendations
