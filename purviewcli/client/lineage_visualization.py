"""
Advanced Lineage Visualization for Azure Purview
Provides comprehensive data lineage analysis, visualization, and impact assessment
"""

import asyncio
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

# Optional graph analysis dependencies - graceful fallback if not available
try:
    import pandas as pd
    import networkx as nx
    GRAPH_AVAILABLE = True
except ImportError as e:
    # Create mock classes for when graph dependencies are not available
    pd = None
    nx = None
    GRAPH_AVAILABLE = False
    print(f"Warning: Graph analysis dependencies not available ({e}). Advanced lineage features will be limited.")

from .api_client import EnhancedPurviewClient
from .config import PurviewConfig

console = Console()

class LineageDirection(Enum):
    """Lineage direction options"""
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    BOTH = "BOTH"

class LineageDepth(Enum):
    """Lineage depth levels"""
    IMMEDIATE = 1
    EXTENDED = 3
    DEEP = 5
    COMPLETE = -1

class ImpactLevel(Enum):
    """Impact assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class LineageNode:
    """Represents a node in the lineage graph"""
    guid: str
    name: str
    type_name: str
    qualified_name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    classifications: List[str] = field(default_factory=list)
    depth: int = 0
    direction: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LineageEdge:
    """Represents an edge/relationship in the lineage graph"""
    source_guid: str
    target_guid: str
    relationship_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    process_guid: Optional[str] = None

@dataclass
class LineageGraph:
    """Complete lineage graph structure"""
    nodes: Dict[str, LineageNode] = field(default_factory=dict)
    edges: List[LineageEdge] = field(default_factory=list)
    root_guid: str = ""
    depth: int = 0
    direction: str = ""

@dataclass
class ImpactAnalysis:
    """Impact analysis result"""
    affected_entities: List[str]
    impact_level: ImpactLevel
    impact_score: float
    downstream_count: int
    upstream_count: int
    critical_paths: List[List[str]]
    recommendations: List[str]

class AdvancedLineageAnalyzer:
    """Advanced data lineage analysis and visualization"""
    
    def __init__(self, client: EnhancedPurviewClient):
        self.client = client
        self.console = Console()
    
    async def get_comprehensive_lineage(
        self, 
        entity_guid: str, 
        direction: LineageDirection = LineageDirection.BOTH,
        depth: LineageDepth = LineageDepth.EXTENDED,
        include_processes: bool = True
    ) -> LineageGraph:
        """Get comprehensive lineage graph with enhanced analysis"""
        
        lineage_graph = LineageGraph(
            root_guid=entity_guid,
            depth=depth.value,
            direction=direction.value
        )
        
        visited_guids = set()
        
        try:
            # Get root entity information
            root_entity = await self.client.get_entity(entity_guid)
            root_node = self._create_lineage_node(root_entity, 0, "ROOT")
            lineage_graph.nodes[entity_guid] = root_node
            
            # Build lineage graph recursively
            await self._build_lineage_recursive(
                entity_guid, 
                lineage_graph, 
                visited_guids, 
                direction, 
                depth.value, 
                0,
                include_processes
            )
            
            # Enhance graph with additional analysis
            await self._enhance_lineage_graph(lineage_graph)
            
        except Exception as e:
            self.console.print(f"[red]Error building lineage graph: {e}[/red]")
        
        return lineage_graph
    
    async def _build_lineage_recursive(
        self,
        current_guid: str,
        graph: LineageGraph,
        visited: Set[str],
        direction: LineageDirection,
        max_depth: int,
        current_depth: int,
        include_processes: bool
    ):
        """Recursively build lineage graph"""
        
        if current_depth >= max_depth and max_depth != -1:
            return
        
        if current_guid in visited:
            return
        
        visited.add(current_guid)
        
        try:
            # Get lineage from Purview API
            lineage_response = await self.client._make_request('GET', f'/lineage/{current_guid}')
            
            # Process upstream lineage
            if direction in [LineageDirection.INPUT, LineageDirection.BOTH]:
                await self._process_lineage_direction(
                    lineage_response, graph, visited, direction, max_depth, 
                    current_depth, "INPUT", include_processes
                )
            
            # Process downstream lineage
            if direction in [LineageDirection.OUTPUT, LineageDirection.BOTH]:
                await self._process_lineage_direction(
                    lineage_response, graph, visited, direction, max_depth, 
                    current_depth, "OUTPUT", include_processes
                )
                
        except Exception as e:
            # Continue processing even if one entity fails
            pass
    
    async def _process_lineage_direction(
        self,
        lineage_response: Dict,
        graph: LineageGraph,
        visited: Set[str],
        direction: LineageDirection,
        max_depth: int,
        current_depth: int,
        lineage_direction: str,
        include_processes: bool
    ):
        """Process lineage in a specific direction"""
        
        relations = lineage_response.get('relations', [])
        
        for relation in relations:
            from_guid = relation.get('fromEntityId')
            to_guid = relation.get('toEntityId')
            
            if not from_guid or not to_guid:
                continue
            
            # Determine the next entity to process
            if lineage_direction == "INPUT":
                next_guid = from_guid
                current_is_target = to_guid
            else:
                next_guid = to_guid
                current_is_target = from_guid
            
            if next_guid not in graph.nodes:
                try:
                    # Get entity details
                    entity = await self.client.get_entity(next_guid)
                    node = self._create_lineage_node(
                        entity, 
                        current_depth + 1, 
                        lineage_direction
                    )
                    graph.nodes[next_guid] = node
                    
                    # Create edge
                    edge = LineageEdge(
                        source_guid=from_guid,
                        target_guid=to_guid,
                        relationship_type=relation.get('relationshipType', 'unknown')
                    )
                    graph.edges.append(edge)
                    
                    # Continue recursively
                    await self._build_lineage_recursive(
                        next_guid, graph, visited, direction, max_depth, 
                        current_depth + 1, include_processes
                    )
                    
                except Exception as e:
                    continue
    
    def _create_lineage_node(self, entity: Dict, depth: int, direction: str) -> LineageNode:
        """Create a lineage node from entity data"""
        attributes = entity.get('attributes', {})
        classifications = [
            c.get('typeName', '') for c in entity.get('classifications', [])
        ]
        
        return LineageNode(
            guid=entity.get('guid', ''),
            name=attributes.get('name', 'Unknown'),
            type_name=entity.get('typeName', 'Unknown'),
            qualified_name=attributes.get('qualifiedName', ''),
            attributes=attributes,
            classifications=classifications,
            depth=depth,
            direction=direction
        )
    
    async def _enhance_lineage_graph(self, graph: LineageGraph):
        """Enhance lineage graph with additional metadata and analysis"""
        
        # Add node metrics
        for node in graph.nodes.values():
            try:
                # Count incoming and outgoing edges
                incoming = len([e for e in graph.edges if e.target_guid == node.guid])
                outgoing = len([e for e in graph.edges if e.source_guid == node.guid])
                
                node.metadata.update({
                    'incoming_count': incoming,
                    'outgoing_count': outgoing,
                    'connection_count': incoming + outgoing
                })
                
                # Add additional entity metadata
                if node.guid != graph.root_guid:
                    node.metadata['distance_from_root'] = node.depth
                
            except Exception as e:
                continue
    
    def analyze_lineage_impact(self, graph: LineageGraph, change_entity_guid: str) -> ImpactAnalysis:
        """Analyze the impact of changes to a specific entity"""
        
        if change_entity_guid not in graph.nodes:
            return ImpactAnalysis(
                affected_entities=[],
                impact_level=ImpactLevel.LOW,
                impact_score=0.0,
                downstream_count=0,
                upstream_count=0,
                critical_paths=[],
                recommendations=[]
            )
        
        # Create NetworkX graph for analysis
        nx_graph = self._create_networkx_graph(graph)
        
        # Find downstream entities
        downstream_entities = []
        if change_entity_guid in nx_graph:
            try:
                downstream_entities = list(nx.descendants(nx_graph, change_entity_guid))
            except:
                pass
        
        # Find upstream entities
        upstream_entities = []
        if change_entity_guid in nx_graph:
            try:
                upstream_entities = list(nx.ancestors(nx_graph, change_entity_guid))
            except:
                pass
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(
            len(downstream_entities), 
            len(upstream_entities),
            graph.nodes
        )
        
        # Determine impact level
        impact_level = self._determine_impact_level(impact_score, downstream_entities, graph.nodes)
        
        # Find critical paths
        critical_paths = self._find_critical_paths(nx_graph, change_entity_guid, downstream_entities)
        
        # Generate recommendations
        recommendations = self._generate_impact_recommendations(
            impact_level, downstream_entities, upstream_entities, graph.nodes
        )
        
        return ImpactAnalysis(
            affected_entities=downstream_entities + upstream_entities,
            impact_level=impact_level,
            impact_score=impact_score,
            downstream_count=len(downstream_entities),
            upstream_count=len(upstream_entities),
            critical_paths=critical_paths,
            recommendations=recommendations
        )
    
    def _create_networkx_graph(self, graph: LineageGraph) -> nx.DiGraph:
        """Create NetworkX directed graph from lineage graph"""
        nx_graph = nx.DiGraph()
        
        # Add nodes
        for guid, node in graph.nodes.items():
            nx_graph.add_node(guid, **{
                'name': node.name,
                'type': node.type_name,
                'depth': node.depth
            })
        
        # Add edges
        for edge in graph.edges:
            nx_graph.add_edge(edge.source_guid, edge.target_guid, 
                            relationship_type=edge.relationship_type)
        
        return nx_graph
    
    def _calculate_impact_score(
        self, 
        downstream_count: int, 
        upstream_count: int, 
        nodes: Dict[str, LineageNode]
    ) -> float:
        """Calculate numerical impact score"""
        
        # Base score from affected entity counts
        base_score = (downstream_count * 2 + upstream_count) / max(len(nodes), 1)
        
        # Apply scaling and bounds
        impact_score = min(base_score * 100, 100.0)
        
        return impact_score
    
    def _determine_impact_level(
        self, 
        impact_score: float, 
        downstream_entities: List[str], 
        nodes: Dict[str, LineageNode]
    ) -> ImpactLevel:
        """Determine qualitative impact level"""
        
        # Check for critical entities in downstream
        has_critical = any(
            'critical' in nodes.get(guid, LineageNode('', '', '', '')).classifications
            for guid in downstream_entities
        )
        
        if has_critical or impact_score >= 80:
            return ImpactLevel.CRITICAL
        elif impact_score >= 60:
            return ImpactLevel.HIGH
        elif impact_score >= 30:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _find_critical_paths(
        self, 
        nx_graph: nx.DiGraph, 
        source_guid: str, 
        downstream_entities: List[str]
    ) -> List[List[str]]:
        """Find critical paths from source to important downstream entities"""
        
        critical_paths = []
        
        # Find paths to entities with many connections (hubs)
        important_entities = [
            guid for guid in downstream_entities
            if nx_graph.out_degree(guid) + nx_graph.in_degree(guid) > 2
        ]
        
        for target_guid in important_entities[:5]:  # Limit to top 5
            try:
                if nx.has_path(nx_graph, source_guid, target_guid):
                    path = nx.shortest_path(nx_graph, source_guid, target_guid)
                    if len(path) > 2:  # Only include non-trivial paths
                        critical_paths.append(path)
            except:
                continue
        
        return critical_paths
    
    def _generate_impact_recommendations(
        self,
        impact_level: ImpactLevel,
        downstream_entities: List[str],
        upstream_entities: List[str],
        nodes: Dict[str, LineageNode]
    ) -> List[str]:
        """Generate recommendations based on impact analysis"""
        
        recommendations = []
        
        if impact_level == ImpactLevel.CRITICAL:
            recommendations.extend([
                "⚠️  CRITICAL IMPACT: Coordinate changes with all stakeholders",
                "Implement comprehensive testing before deployment",
                "Consider phased rollout approach",
                "Set up monitoring for downstream systems"
            ])
        elif impact_level == ImpactLevel.HIGH:
            recommendations.extend([
                "High impact detected - notify downstream data owners",
                "Perform thorough testing of affected systems",
                "Plan maintenance window for changes"
            ])
        elif impact_level == ImpactLevel.MEDIUM:
            recommendations.extend([
                "Medium impact - review affected entities",
                "Test downstream dependencies",
                "Communicate changes to relevant teams"
            ])
        else:
            recommendations.append("Low impact - standard change management applies")
        
        if len(downstream_entities) > 10:
            recommendations.append(f"Large downstream impact ({len(downstream_entities)} entities)")
        
        if len(upstream_entities) > 5:
            recommendations.append(f"Consider upstream dependencies ({len(upstream_entities)} entities)")
        
        return recommendations
    
    def visualize_lineage_tree(self, graph: LineageGraph, max_depth: int = 3) -> Tree:
        """Create a Rich tree visualization of lineage"""
        
        if not graph.nodes:
            return Tree("No lineage data available")
        
        root_guid = graph.root_guid
        root_node = graph.nodes.get(root_guid)
        
        if not root_node:
            return Tree("Invalid root entity")
        
        # Create root tree
        tree = Tree(
            f"🏠 [bold blue]{root_node.name}[/bold blue] ({root_node.type_name})",
            guide_style="bold bright_blue"
        )
        
        # Add upstream section
        upstream_nodes = [n for n in graph.nodes.values() if n.direction == "INPUT"]
        if upstream_nodes:
            upstream_branch = tree.add("⬅️  [bold green]Upstream Dependencies[/bold green]")
            self._add_nodes_to_tree(upstream_branch, upstream_nodes, graph.edges, max_depth)
        
        # Add downstream section
        downstream_nodes = [n for n in graph.nodes.values() if n.direction == "OUTPUT"]
        if downstream_nodes:
            downstream_branch = tree.add("➡️  [bold yellow]Downstream Impact[/bold yellow]")
            self._add_nodes_to_tree(downstream_branch, downstream_nodes, graph.edges, max_depth)
        
        return tree
    
    def _add_nodes_to_tree(
        self, 
        parent_branch: Tree, 
        nodes: List[LineageNode], 
        edges: List[LineageEdge],
        max_depth: int
    ):
        """Add nodes to tree branch"""
        
        # Group nodes by depth
        nodes_by_depth = {}
        for node in nodes:
            if node.depth <= max_depth:
                if node.depth not in nodes_by_depth:
                    nodes_by_depth[node.depth] = []
                nodes_by_depth[node.depth].append(node)
        
        # Add nodes level by level
        for depth in sorted(nodes_by_depth.keys()):
            depth_nodes = nodes_by_depth[depth]
            
            for node in depth_nodes[:10]:  # Limit display
                # Create node label with metadata
                classifications_str = ", ".join(node.classifications[:3]) if node.classifications else "None"
                
                node_label = f"📊 {node.name} ({node.type_name})"
                if node.classifications:
                    node_label += f" | 🏷️  {classifications_str}"
                
                # Add connection count if available
                if 'connection_count' in node.metadata:
                    conn_count = node.metadata['connection_count']
                    node_label += f" | 🔗 {conn_count} connections"
                
                parent_branch.add(node_label)
    
    def create_lineage_summary_table(self, graph: LineageGraph) -> Table:
        """Create a summary table of lineage information"""
        
        table = Table(title="Lineage Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Details", style="yellow")
        
        # Basic statistics
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        
        upstream_nodes = len([n for n in graph.nodes.values() if n.direction == "INPUT"])
        downstream_nodes = len([n for n in graph.nodes.values() if n.direction == "OUTPUT"])
        
        # Entity types
        type_counts = {}
        for node in graph.nodes.values():
            type_name = node.type_name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        most_common_type = max(type_counts.keys(), key=lambda k: type_counts[k]) if type_counts else "N/A"
        
        # Depth statistics
        max_depth = max([n.depth for n in graph.nodes.values()], default=0)
        
        # Add rows
        table.add_row("Total Entities", str(total_nodes), f"Root + {total_nodes - 1} related")
        table.add_row("Total Relationships", str(total_edges), "Direct connections")
        table.add_row("Upstream Dependencies", str(upstream_nodes), "Input sources")
        table.add_row("Downstream Impact", str(downstream_nodes), "Output targets")
        table.add_row("Maximum Depth", str(max_depth), "Levels from root")
        table.add_row("Most Common Type", most_common_type, f"{type_counts.get(most_common_type, 0)} entities")
        
        # Classifications summary
        all_classifications = set()
        for node in graph.nodes.values():
            all_classifications.update(node.classifications)
        
        table.add_row("Unique Classifications", str(len(all_classifications)), ", ".join(list(all_classifications)[:3]))
        
        return table
    
    async def export_lineage_graph(
        self, 
        graph: LineageGraph, 
        output_path: str, 
        format: str = 'json'
    ):
        """Export lineage graph to file"""
        
        if format.lower() == 'json':
            graph_data = {
                'metadata': {
                    'root_guid': graph.root_guid,
                    'depth': graph.depth,
                    'direction': graph.direction,
                    'exported_at': datetime.now().isoformat(),
                    'total_nodes': len(graph.nodes),
                    'total_edges': len(graph.edges)
                },
                'nodes': [
                    {
                        'guid': node.guid,
                        'name': node.name,
                        'type_name': node.type_name,
                        'qualified_name': node.qualified_name,
                        'classifications': node.classifications,
                        'depth': node.depth,
                        'direction': node.direction,
                        'metadata': node.metadata
                    }
                    for node in graph.nodes.values()
                ],
                'edges': [
                    {
                        'source_guid': edge.source_guid,
                        'target_guid': edge.target_guid,
                        'relationship_type': edge.relationship_type,
                        'attributes': edge.attributes
                    }
                    for edge in graph.edges
                ]
            }
            
            with open(output_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
        
        elif format.lower() == 'csv':
            # Export nodes
            nodes_df = pd.DataFrame([
                {
                    'guid': node.guid,
                    'name': node.name,
                    'type_name': node.type_name,
                    'qualified_name': node.qualified_name,
                    'classifications': ', '.join(node.classifications),
                    'depth': node.depth,
                    'direction': node.direction
                }
                for node in graph.nodes.values()
            ])
            
            nodes_path = output_path.replace('.csv', '_nodes.csv')
            nodes_df.to_csv(nodes_path, index=False)
            
            # Export edges
            edges_df = pd.DataFrame([
                {
                    'source_guid': edge.source_guid,
                    'target_guid': edge.target_guid,
                    'relationship_type': edge.relationship_type
                }
                for edge in graph.edges
            ])
            
            edges_path = output_path.replace('.csv', '_edges.csv')
            edges_df.to_csv(edges_path, index=False)
        
        self.console.print(f"[green]Lineage graph exported to {output_path}[/green]")
    
    async def find_lineage_gaps(self, graph: LineageGraph) -> List[Dict]:
        """Identify potential gaps in lineage documentation"""
        
        gaps = []
        
        # Find nodes with no upstream or downstream connections
        isolated_nodes = []
        for node in graph.nodes.values():
            if node.guid == graph.root_guid:
                continue
                
            has_upstream = any(e.target_guid == node.guid for e in graph.edges)
            has_downstream = any(e.source_guid == node.guid for e in graph.edges)
            
            if not has_upstream and not has_downstream:
                isolated_nodes.append(node)
        
        if isolated_nodes:
            gaps.append({
                'type': 'isolated_entities',
                'description': f'Found {len(isolated_nodes)} entities with no lineage connections',
                'entities': [node.guid for node in isolated_nodes],
                'severity': 'medium'
            })
        
        # Find potential missing relationships (entities that should be connected)
        # This is a simplified heuristic based on naming patterns
        potential_connections = []
        for node1 in graph.nodes.values():
            for node2 in graph.nodes.values():
                if node1.guid != node2.guid:
                    similarity_score = self._calculate_name_similarity(node1.name, node2.name)
                    if similarity_score > 0.7:  # High similarity
                        # Check if they're already connected
                        connected = any(
                            (e.source_guid == node1.guid and e.target_guid == node2.guid) or
                            (e.source_guid == node2.guid and e.target_guid == node1.guid)
                            for e in graph.edges
                        )
                        
                        if not connected:
                            potential_connections.append({
                                'entity1': node1.guid,
                                'entity2': node2.guid,
                                'similarity_score': similarity_score
                            })
        
        if potential_connections:
            gaps.append({
                'type': 'potential_missing_connections',
                'description': f'Found {len(potential_connections)} potential missing connections',
                'connections': potential_connections[:10],  # Limit results
                'severity': 'low'
            })
        
        return gaps
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two entity names"""
        # Simple similarity based on common words and structure
        words1 = set(name1.lower().split('_'))
        words2 = set(name2.lower().split('_'))
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1.intersection(words2)
        total_words = words1.union(words2)
        
        return len(common_words) / len(total_words) if total_words else 0.0

class LineageReporting:
    """Generate comprehensive lineage reports"""
    
    def __init__(self, analyzer: AdvancedLineageAnalyzer):
        self.analyzer = analyzer
        self.console = Console()
    
    async def generate_impact_report(
        self, 
        entity_guid: str, 
        output_path: str
    ) -> Dict:
        """Generate comprehensive impact analysis report"""
        
        # Get comprehensive lineage
        lineage_graph = await self.analyzer.get_comprehensive_lineage(
            entity_guid, 
            LineageDirection.BOTH, 
            LineageDepth.DEEP
        )
        
        # Perform impact analysis
        impact_analysis = self.analyzer.analyze_lineage_impact(lineage_graph, entity_guid)
        
        # Create report
        report = {
            'report_metadata': {
                'entity_guid': entity_guid,
                'entity_name': lineage_graph.nodes.get(entity_guid, LineageNode('', '', '', '')).name,
                'generated_at': datetime.now().isoformat(),
                'analysis_depth': lineage_graph.depth
            },
            'impact_summary': {
                'impact_level': impact_analysis.impact_level.value,
                'impact_score': impact_analysis.impact_score,
                'affected_entities_count': len(impact_analysis.affected_entities),
                'downstream_count': impact_analysis.downstream_count,
                'upstream_count': impact_analysis.upstream_count
            },
            'affected_entities': [
                {
                    'guid': guid,
                    'name': lineage_graph.nodes.get(guid, LineageNode('', '', '', '')).name,
                    'type': lineage_graph.nodes.get(guid, LineageNode('', '', '', '')).type_name
                }
                for guid in impact_analysis.affected_entities
            ],
            'critical_paths': impact_analysis.critical_paths,
            'recommendations': impact_analysis.recommendations,
            'lineage_statistics': {
                'total_nodes': len(lineage_graph.nodes),
                'total_edges': len(lineage_graph.edges),
                'max_depth': max([n.depth for n in lineage_graph.nodes.values()], default=0)
            }
        }
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.console.print(f"[green]Impact report generated: {output_path}[/green]")
        return report
