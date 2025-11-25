"""
Graph service for relationship-based context retrieval.
Uses NetworkX for local graph operations.
"""
import networkx as nx
from typing import List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GraphService:
    """Service for graph-based context retrieval."""
    
    def __init__(self, graph_path: str = None):
        """
        Initialize graph service.
        
        Args:
            graph_path: Path to serialized graph file (optional)
        """
        self.graph = nx.DiGraph()
        
        if graph_path and Path(graph_path).exists():
            try:
                import pickle
                with open(graph_path, 'rb') as f:
                    self.graph = pickle.load(f)
                logger.info(f"Loaded graph with {len(self.graph.nodes())} nodes, {len(self.graph.edges())} edges")
            except Exception as e:
                logger.warning(f"Failed to load graph from {graph_path}: {e}")
                logger.info("Starting with empty graph")
    
    def build_from_labels(self, labels: List[Dict[str, Any]]):
        """
        Build graph from labeled email data.
        
        Args:
            labels: List of label dictionaries with topic, intents, artifacts
        """
        for item in labels:
            label_data = item.get("labels", {})
            topic = label_data.get("topic")
            intents = label_data.get("intents", [])
            artifacts = label_data.get("artifacts", [])
            
            if not topic and not intents and not artifacts:
                continue
            
            # Add topic node
            if topic:
                self.graph.add_node(topic, type="topic")
            
            # Add intents as nodes and edges
            for intent in intents:
                self.graph.add_node(intent, type="intent")
                if topic:
                    self.graph.add_edge(topic, intent, relation="HAS_INTENT")
            
            # Add artifacts as nodes and edges
            for artifact in artifacts:
                self.graph.add_node(artifact, type="artifact")
                if topic:
                    self.graph.add_edge(topic, artifact, relation="USES_ARTIFACT")
        
        logger.info(f"Built graph with {len(self.graph.nodes())} nodes, {len(self.graph.edges())} edges")
    
    def get_neighbors(self, node_name: str) -> List[str]:
        """
        Get all neighbors (predecessors and successors) of a node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            List of neighbor node names
        """
        if node_name not in self.graph:
            return []
        
        successors = list(self.graph.successors(node_name))
        predecessors = list(self.graph.predecessors(node_name))
        
        return list(set(successors + predecessors))
    
    def expand_graph_hits(self, graph_hits: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Expand graph hits by retrieving neighbors for context enrichment.
        
        Args:
            graph_hits: List of graph node hits from vector search
            
        Returns:
            Dictionary mapping node names to their neighbors
        """
        expanded = {}
        
        for hit in graph_hits:
            node_name = hit.get("node_name")
            if node_name:
                neighbors = self.get_neighbors(node_name)
                expanded[node_name] = neighbors
        
        return expanded
    
    def save_graph(self, path: str):
        """
        Save graph to disk.
        
        Args:
            path: Path to save the graph
        """
        try:
            import pickle
            with open(path, 'wb') as f:
                pickle.dump(self.graph, f)
            logger.info(f"Saved graph to {path}")
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
    
    def get_node_info(self, node_name: str) -> Dict[str, Any]:
        """
        Get information about a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Dictionary with node information
        """
        if node_name not in self.graph:
            return {}
        
        node_data = self.graph.nodes[node_name]
        return {
            "name": node_name,
            "type": node_data.get("type", "unknown"),
            "neighbors": self.get_neighbors(node_name),
            "in_degree": self.graph.in_degree(node_name),
            "out_degree": self.graph.out_degree(node_name)
        }
    
    def get_nodes_by_intents(self, intents: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve graph nodes related to multiple intents.
        This is used for intent-based retrieval as a complement to vector search.
        
        Args:
            intents: List of detected intents (e.g., ["send_materials", "schedule"])
            limit: Maximum number of nodes to return
            
        Returns:
            List of node information dictionaries
        """
        nodes = []
        seen_names = set()
        
        for intent in intents:
            # Check if the intent itself is a node
            if intent in self.graph and intent not in seen_names:
                node_info = self.get_node_info(intent)
                if node_info:
                    nodes.append(node_info)
                    seen_names.add(intent)
            
            # Find nodes connected to this intent
            if intent in self.graph:
                neighbors = self.get_neighbors(intent)
                for neighbor in neighbors:
                    if neighbor not in seen_names and len(nodes) < limit:
                        node_info = self.get_node_info(neighbor)
                        if node_info:
                            nodes.append(node_info)
                            seen_names.add(neighbor)
        
        logger.info(f"Retrieved {len(nodes)} graph nodes for intents {intents}")
        return nodes[:limit]
    
    def health_check(self) -> bool:
        """
        Check if graph service is healthy.
        
        Returns:
            True if service is healthy
        """
        return len(self.graph.nodes()) > 0

