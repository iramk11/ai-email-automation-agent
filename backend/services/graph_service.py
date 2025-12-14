"""
Graph service for relationship-based context retrieval.
Uses NetworkX for local graph operations.
Enhanced methodology: stores only replies, uses intersection search.
"""
import networkx as nx
from typing import List, Dict, Any, Set
import logging
from pathlib import Path
import uuid

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
        
        # NEW: Mapping email_id -> reply (for quick lookup)
        self.email_id_to_reply: Dict[str, str] = {}
        
        # NEW: Mapping node_name -> set of email_ids (for intersection search)
        self.node_to_email_ids: Dict[str, Set[str]] = {}
        
        if graph_path and Path(graph_path).exists():
            try:
                import pickle
                with open(graph_path, 'rb') as f:
                    data = pickle.load(f)
                    # Handle both old format (just graph) and new format (dict with graph and mappings)
                    if isinstance(data, dict):
                        self.graph = data.get('graph', nx.DiGraph())
                        self.email_id_to_reply = data.get('email_id_to_reply', {})
                        node_to_email_ids_raw = data.get('node_to_email_ids', {})
                        # Convert lists back to sets
                        self.node_to_email_ids = {k: set(v) if isinstance(v, list) else v for k, v in node_to_email_ids_raw.items()}
                    else:
                        # Old format: just the graph
                        self.graph = data
                        logger.info("Loaded old format graph (no email_id mappings)")
                logger.info(f"Loaded graph with {len(self.graph.nodes())} nodes, {len(self.graph.edges())} edges")
                logger.info(f"Loaded {len(self.email_id_to_reply)} email_id->reply mappings")
                logger.info(f"Loaded {len(self.node_to_email_ids)} node->email_id mappings")
            except Exception as e:
                logger.warning(f"Failed to load graph from {graph_path}: {e}")
                logger.info("Starting with empty graph")
    
    def build_from_labels(self, labels: List[Dict[str, Any]]):
        """
        Build graph from labeled email data.
        NEW METHODOLOGY: Stores only replies, creates email_id mappings.
        
        Args:
            labels: List of label dictionaries with topic, intents, artifacts, reply, id
        """
        ids_generated = 0
        ids_existing = 0
        
        logger.info("Building graph with enhanced methodology (replies only, email_id mappings)...")
        
        for item in labels:
            label_data = item.get("labels", {})
            topic = label_data.get("topic")
            intents = label_data.get("intents", [])
            artifacts = label_data.get("artifacts", [])
            
            # Get ONLY the reply (not full email context)
            reply = item.get("reply", "")
            
            # Get or generate email_id
            email_id = item.get("id")
            if not email_id or email_id == "":
                email_id = str(uuid.uuid4())
                ids_generated += 1
            else:
                ids_existing += 1
            
            # Store email_id -> reply mapping
            self.email_id_to_reply[email_id] = reply
            
            if not topic and not intents and not artifacts:
                continue
            
            # Add topic node
            if topic:
                self.graph.add_node(topic, type="topic")
                if topic not in self.node_to_email_ids:
                    self.node_to_email_ids[topic] = set()
                self.node_to_email_ids[topic].add(email_id)
            
            # Add intents as nodes and edges (with email_id)
            for intent in intents:
                self.graph.add_node(intent, type="intent")
                if topic:
                    # Store email_id on edge
                    self.graph.add_edge(topic, intent, relation="HAS_INTENT", email_id=email_id)
                
                if intent not in self.node_to_email_ids:
                    self.node_to_email_ids[intent] = set()
                self.node_to_email_ids[intent].add(email_id)
            
            # Add artifacts as nodes and edges (with email_id)
            for artifact in artifacts:
                self.graph.add_node(artifact, type="artifact")
                if topic:
                    # Store email_id on edge
                    self.graph.add_edge(topic, artifact, relation="USES_ARTIFACT", email_id=email_id)
                
                if artifact not in self.node_to_email_ids:
                    self.node_to_email_ids[artifact] = set()
                self.node_to_email_ids[artifact].add(email_id)
        
        logger.info(f"Built graph with {len(self.graph.nodes())} nodes, {len(self.graph.edges())} edges")
        logger.info(f"Email ID mappings: {len(self.email_id_to_reply)}")
        logger.info(f"Node->email_id mappings: {len(self.node_to_email_ids)}")
        logger.info(f"ID generation: {ids_existing} existing, {ids_generated} generated")
    
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
    
    def get_relationships(self, node_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get relationships (edges) for a node with their types.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Dictionary with 'outgoing' and 'incoming' relationships
            Each relationship includes: target/source node, relation type, and email_id if available
        """
        if node_name not in self.graph:
            return {"outgoing": [], "incoming": []}
        
        outgoing = []
        for successor in self.graph.successors(node_name):
            edge_data = self.graph.get_edge_data(node_name, successor, {})
            outgoing.append({
                "node": successor,
                "relation": edge_data.get("relation", "CONNECTED"),
                "email_id": edge_data.get("email_id")
            })
        
        incoming = []
        for predecessor in self.graph.predecessors(node_name):
            edge_data = self.graph.get_edge_data(predecessor, node_name, {})
            incoming.append({
                "node": predecessor,
                "relation": edge_data.get("relation", "CONNECTED"),
                "email_id": edge_data.get("email_id")
            })
        
        return {"outgoing": outgoing, "incoming": incoming}
    
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
        Save graph to disk (with email_id mappings).
        
        Args:
            path: Path to save the graph
        """
        try:
            import pickle
            # Save graph with mappings
            data = {
                'graph': self.graph,
                'email_id_to_reply': self.email_id_to_reply,
                'node_to_email_ids': {k: list(v) for k, v in self.node_to_email_ids.items()}  # Convert sets to lists for JSON compatibility
            }
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Saved graph with mappings to {path}")
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
    
    def get_node_info(self, node_name: str) -> Dict[str, Any]:
        """
        Get information about a specific node, including relationships.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Dictionary with node information including relationships
        """
        if node_name not in self.graph:
            return {}
        
        node_data = self.graph.nodes[node_name]
        relationships = self.get_relationships(node_name)
        
        return {
            "name": node_name,
            "type": node_data.get("type", "unknown"),
            "neighbors": self.get_neighbors(node_name),
            "relationships": relationships,  # NEW: Include relationship information
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
    
    def find_emails_by_intent_artifact_intersection(
        self,
        intents: List[str],
        artifacts: List[str],
        max_combinations: int = 100
    ) -> List[str]:
        """
        Find email IDs that exist in the intersection of intents and artifacts.
        NEW METHODOLOGY: Exhaustive P&C (permutations & combinations) intersection search.
        
        Args:
            intents: List of intent labels
            artifacts: List of artifact labels
            max_combinations: Maximum number of combinations to try (safety limit)
        
        Returns:
            List of email_ids that match the intersection criteria
        """
        if not intents or not artifacts:
            logger.warning("Need at least 1 intent AND 1 artifact for intersection search")
            return []
        
        # Check if node_to_email_ids is populated
        if not self.node_to_email_ids:
            logger.warning("⚠️ node_to_email_ids mapping is empty! Graph may need to be rebuilt from labels.")
            logger.warning("   The graph file might be in old format. Try deleting graph_data.gpickle to rebuild.")
            return []
        
        logger.info(f"🔍 Searching for emails with intents: {intents}, artifacts: {artifacts}")
        
        # Get email_ids for each intent
        intent_email_sets = []
        for intent in intents:
            if intent in self.node_to_email_ids:
                email_set = self.node_to_email_ids[intent]
                intent_email_sets.append(email_set)
                logger.info(f"   Intent '{intent}': {len(email_set)} emails")
            else:
                logger.warning(f"   ⚠️ Intent '{intent}' not found in graph")
        
        # Get email_ids for each artifact
        artifact_email_sets = []
        for artifact in artifacts:
            if artifact in self.node_to_email_ids:
                email_set = self.node_to_email_ids[artifact]
                artifact_email_sets.append(email_set)
                logger.info(f"   Artifact '{artifact}': {len(email_set)} emails")
            else:
                logger.warning(f"   ⚠️ Artifact '{artifact}' not found in graph")
        
        if not intent_email_sets or not artifact_email_sets:
            logger.warning("   ⚠️ No matching emails found (missing intents or artifacts)")
            return []
        
        # EXHAUSTIVE P&C APPROACH: Try all combinations of intent+artifact pairs
        # This is more precise than union intersection
        total_combinations = len(intents) * len(artifacts)
        
        if total_combinations > max_combinations:
            logger.warning(f"   ⚠️ Too many combinations ({total_combinations}), using union intersection instead")
            # Fallback to union intersection for very large combinations
            intent_union = set()
            for email_set in intent_email_sets:
                intent_union.update(email_set)
            
            artifact_union = set()
            for email_set in artifact_email_sets:
                artifact_union.update(email_set)
            
            matching_emails = intent_union.intersection(artifact_union)
            logger.info(f"   ✅ Found {len(matching_emails)} emails in union intersection")
            return list(matching_emails)
        
        # EXHAUSTIVE: Try all specific intent+artifact pairs
        logger.info(f"   🔍 Trying exhaustive P&C: {total_combinations} combinations...")
        specific_matches = []
        combination_details = []
        MAX_REPLIES_PER_COMBINATION = 3  # Limit to max 3 replies per combination
        
        for intent in intents:
            if intent not in self.node_to_email_ids:
                continue
            intent_emails = self.node_to_email_ids[intent]
            
            for artifact in artifacts:
                if artifact not in self.node_to_email_ids:
                    continue
                artifact_emails = self.node_to_email_ids[artifact]
                
                # Emails matching this specific intent+artifact pair
                pair_matches = intent_emails.intersection(artifact_emails)
                if pair_matches:
                    # Limit to max 3 emails per combination
                    pair_matches_list = list(pair_matches)[:MAX_REPLIES_PER_COMBINATION]
                    specific_matches.extend(pair_matches_list)
                    
                    combination_details.append({
                        'intent': intent,
                        'artifact': artifact,
                        'total_count': len(pair_matches),
                        'returned_count': len(pair_matches_list)
                    })
                    logger.info(f"      ✅ '{intent}' + '{artifact}': {len(pair_matches)} total, returning {len(pair_matches_list)} (max 3 per combo)")
        
        if specific_matches:
            # Remove duplicates while preserving order (first occurrence wins)
            seen = set()
            unique_matches = []
            for email_id in specific_matches:
                if email_id not in seen:
                    seen.add(email_id)
                    unique_matches.append(email_id)
            
            logger.info(f"   ✅ Exhaustive P&C found {len(unique_matches)} unique emails across {len(combination_details)} matching pairs")
            logger.info(f"   📊 Combination breakdown:")
            for detail in combination_details:
                logger.info(f"      - {detail['intent']} + {detail['artifact']}: {detail['returned_count']}/{detail['total_count']} emails")
            
            return unique_matches
        
        # Fallback: Union intersection if no specific pairs match
        logger.info("   ⚠️ No specific pairs matched, trying union intersection...")
        intent_union = set()
        for email_set in intent_email_sets:
            intent_union.update(email_set)
        
        artifact_union = set()
        for email_set in artifact_email_sets:
            artifact_union.update(email_set)
        
        matching_emails = intent_union.intersection(artifact_union)
        logger.info(f"   ✅ Found {len(matching_emails)} emails in union intersection")
        return list(matching_emails)
    
    def get_replies_by_email_ids(self, email_ids: List[str]) -> List[str]:
        """
        Get replies for given email IDs.
        
        Args:
            email_ids: List of email IDs
        
        Returns:
            List of replies (in order of email_ids)
        """
        replies = []
        for email_id in email_ids:
            reply = self.email_id_to_reply.get(email_id)
            if reply:
                replies.append(reply)
        return replies
    
    def health_check(self) -> bool:
        """
        Check if graph service is healthy.
        
        Returns:
            True if service is healthy
        """
        return len(self.graph.nodes()) > 0

