#!/usr/bin/env python3
"""
Cytoscape.js Data Generator for KJV Sources Project
==================================================

This script generates network data for Cytoscape.js visualization from KJV sources data.
It extracts person names, cities, locations, directional coordinates, and source relationships.

Author: KJV Sources Project
License: MIT
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CytoscapeDataGenerator:
    """Generates Cytoscape.js network data from KJV sources"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.nodes = []
        self.edges = []
        self.node_ids = set()
        self.edge_ids = set()
        
        # Source color mapping
        self.source_colors = {
            "J": "#000088",  # Navy Blue - Jahwist
            "E": "#008888",  # Teal - Elohist  
            "P": "#888800",  # Olive Yellow - Priestly
            "D": "#000000",  # Black - Deuteronomist
            "R": "#880000",  # Maroon Red - Redactor
        }
        
        # Entity type colors
        self.entity_colors = {
            "person": "#3498db",
            "city": "#e74c3c", 
            "location": "#f39c12",
            "source": "#9b59b6",
            "book": "#1abc9c",
            "tribe": "#34495e",
            "direction": "#95a5a6"
        }
        
        # Biblical person names (common names from the text)
        self.person_names = {
            "Adam", "Eve", "Cain", "Abel", "Seth", "Noah", "Abraham", "Sarah", 
            "Isaac", "Rebekah", "Jacob", "Esau", "Joseph", "Moses", "Aaron",
            "Joshua", "Caleb", "David", "Solomon", "Samuel", "Saul", "Ruth",
            "Esther", "Daniel", "Isaiah", "Jeremiah", "Ezekiel", "Jonah",
            "Job", "Elijah", "Elisha", "John", "Jesus", "Peter", "Paul",
            "Mary", "Elizabeth", "Zechariah", "Gabriel", "Michael"
        }
        
        # Directional terms
        self.directional_terms = {
            "east", "west", "north", "south", "eastward", "westward", 
            "northward", "southward", "rising", "setting", "toward"
        }
        
        # Common city/location names
        self.location_names = {
            "Jerusalem", "Bethlehem", "Nazareth", "Capernaum", "Jericho",
            "Eden", "Canaan", "Egypt", "Assyria", "Babylon", "Moab",
            "Sinai", "Horeb", "Jordan", "Red Sea", "Dead Sea", "Galilee",
            "Samaria", "Judea", "Gilead", "Bashan", "Lebanon", "Damascus",
            "Tyre", "Sidon", "Nineveh", "Ur", "Haran", "Beersheba",
            "Hebron", "Shiloh", "Gilgal", "Bethel", "Ai", "Gibeon"
        }
        
        # Tribe names
        self.tribe_names = {
            "Judah", "Reuben", "Simeon", "Levi", "Dan", "Naphtali", 
            "Gad", "Asher", "Issachar", "Zebulun", "Joseph", "Benjamin",
            "Ephraim", "Manasseh"
        }
    
    def extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from biblical text"""
        entities = {
            "persons": [],
            "cities": [],
            "locations": [],
            "directions": [],
            "tribes": []
        }
        
        # Extract person names
        for name in self.person_names:
            if re.search(rf'\b{name}\b', text, re.IGNORECASE):
                entities["persons"].append(name)
        
        # Extract city/location names
        for location in self.location_names:
            if re.search(rf'\b{location}\b', text, re.IGNORECASE):
                entities["cities"].append(location)
        
        # Extract directional terms
        for direction in self.directional_terms:
            if re.search(rf'\b{direction}\b', text, re.IGNORECASE):
                entities["directions"].append(direction)
        
        # Extract tribe names
        for tribe in self.tribe_names:
            if re.search(rf'\b{tribe}\b', text, re.IGNORECASE):
                entities["tribes"].append(tribe)
        
        # Extract additional locations (geographic terms)
        location_patterns = [
            r'\b(?:land of|city of|town of|village of)\s+([A-Z][a-z]+)\b',
            r'\b([A-Z][a-z]+)\s+(?:river|mountain|valley|plain|wilderness)\b',
            r'\b(?:mount|mt\.)\s+([A-Z][a-z]+)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["locations"].extend(matches)
        
        return entities
    
    def add_node(self, node_id: str, label: str, node_type: str, 
                 attributes: Dict[str, Any] = None) -> bool:
        """Add a node to the network if it doesn't exist"""
        if node_id in self.node_ids:
            return False
        
        node = {
            "data": {
                "id": node_id,
                "label": label,
                "type": node_type,
                "color": self.entity_colors.get(node_type, "#95a5a6")
            }
        }
        
        if attributes:
            node["data"].update(attributes)
        
        self.nodes.append(node)
        self.node_ids.add(node_id)
        return True
    
    def add_edge(self, source_id: str, target_id: str, relationship: str,
                 attributes: Dict[str, Any] = None) -> bool:
        """Add an edge to the network"""
        # Validate that both source and target nodes exist
        if source_id not in self.node_ids:
            logger.warning(f"Source node {source_id} does not exist, skipping edge")
            return False
            
        if target_id not in self.node_ids:
            logger.warning(f"Target node {target_id} does not exist, skipping edge")
            return False
        
        edge_id = f"{source_id}_{relationship}_{target_id}"
        
        if edge_id in self.edge_ids:
            return False
        
        edge = {
            "data": {
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "relationship": relationship
            }
        }
        
        if attributes:
            edge["data"].update(attributes)
        
        self.edges.append(edge)
        self.edge_ids.add(edge_id)
        return True
    
    def process_csv_file(self, csv_path: Path) -> Dict[str, Any]:
        """Process a single CSV file and extract network data"""
        logger.info(f"Processing {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                # Extract entities from the verse text
                entities = self.extract_entities_from_text(row['full_text'])
                
                # First, create all nodes for this verse
                verse_id = f"verse_{row['verse_id']}"
                self.add_node(
                    verse_id,
                    f"{row['canonical_reference']}",
                    "verse",
                    {
                        "book": row['book'],
                        "chapter": row['chapter'],
                        "verse": row['verse'],
                        "text": row['full_text'][:100] + "..." if len(row['full_text']) > 100 else row['full_text'],
                        "sources": row['sources'].split(';') if pd.notna(row['sources']) else [],
                        "primary_source": row['primary_source'],
                        "source_count": row['source_count'],
                        "word_count": row['word_count']
                    }
                )
                
                # Add source nodes
                sources = row['sources'].split(';') if pd.notna(row['sources']) else []
                for source in sources:
                    if source.strip():
                        source_id = f"source_{source.strip()}"
                        self.add_node(
                            source_id,
                            f"Source {source.strip()}",
                            "source",
                            {
                                "color": self.source_colors.get(source.strip(), "#95a5a6"),
                                "description": self.get_source_description(source.strip())
                            }
                        )
                
                # Add book node
                book_id = f"book_{row['book']}"
                self.add_node(
                    book_id,
                    row['book'],
                    "book",
                    {"type": "narrative" if row['book'] in ["Genesis", "Exodus", "Numbers"] else "legal"}
                )
                
                # Add person nodes
                for person in entities["persons"]:
                    person_id = f"person_{person}"
                    self.add_node(person_id, person, "person")
                
                # Add city/location nodes
                for city in entities["cities"]:
                    city_id = f"city_{city}"
                    self.add_node(city_id, city, "city")
                
                # Add location nodes
                for location in entities["locations"]:
                    location_id = f"location_{location}"
                    self.add_node(location_id, location, "location")
                
                # Add tribe nodes
                for tribe in entities["tribes"]:
                    tribe_id = f"tribe_{tribe}"
                    self.add_node(tribe_id, tribe, "tribe")
                
                # Add directional nodes
                for direction in entities["directions"]:
                    direction_id = f"direction_{direction}"
                    self.add_node(direction_id, direction, "direction")
                
                # Now create all edges (after all nodes are created)
                # Connect sources to verses
                for source in sources:
                    if source.strip():
                        source_id = f"source_{source.strip()}"
                        self.add_edge(source_id, verse_id, "contains")
                
                # Connect book to verse
                self.add_edge(book_id, verse_id, "contains")
                
                # Connect entities to verses
                for person in entities["persons"]:
                    person_id = f"person_{person}"
                    self.add_edge(person_id, verse_id, "appears_in")
                
                for city in entities["cities"]:
                    city_id = f"city_{city}"
                    self.add_edge(city_id, verse_id, "mentioned_in")
                
                for location in entities["locations"]:
                    location_id = f"location_{location}"
                    self.add_edge(location_id, verse_id, "mentioned_in")
                
                for tribe in entities["tribes"]:
                    tribe_id = f"tribe_{tribe}"
                    self.add_edge(tribe_id, verse_id, "mentioned_in")
                
                for direction in entities["directions"]:
                    direction_id = f"direction_{direction}"
                    self.add_edge(direction_id, verse_id, "mentioned_in")
            
            logger.info(f"Processed {len(df)} verses from {csv_path.name}")
            
        except Exception as e:
            logger.error(f"Error processing {csv_path}: {e}")
    
    def get_source_description(self, source: str) -> str:
        """Get description for source"""
        descriptions = {
            "J": "Jahwist - Early narrative source with anthropomorphic God",
            "E": "Elohist - Northern source emphasizing divine communication",
            "P": "Priestly - Ritual and genealogical source",
            "D": "Deuteronomist - Deuteronomy-focused source",
            "R": "Redactor - Editorial additions and connections"
        }
        return descriptions.get(source, "Unknown source")
    
    def generate_network_data(self) -> Dict[str, Any]:
        """Generate complete network data for Cytoscape.js"""
        logger.info("Generating network data...")
        
        # Process all CSV files
        csv_files = list(self.output_dir.glob("**/*.csv"))
        
        for csv_file in csv_files:
            if csv_file.name.endswith('.csv') and not csv_file.name.startswith('.'):
                self.process_csv_file(csv_file)
        
        # Create network data structure
        network_data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "metadata": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": Counter(node["data"]["type"] for node in self.nodes),
                "relationship_types": Counter(edge["data"]["relationship"] for edge in self.edges)
            }
        }
        
        logger.info(f"Generated network with {len(self.nodes)} nodes and {len(self.edges)} edges")
        return network_data
    
    def save_network_data(self, output_path: str = "cytoscape_network_data.json"):
        """Save network data to JSON file"""
        network_data = self.generate_network_data()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Network data saved to {output_path}")
        return output_path
    
    def generate_filtered_networks(self) -> Dict[str, Dict[str, Any]]:
        """Generate filtered network views"""
        network_data = self.generate_network_data()
        
        filtered_networks = {}
        
        # Source-focused network
        source_nodes = [n for n in self.nodes if n["data"]["type"] == "source"]
        source_edges = [e for e in self.edges if e["data"]["source"].startswith("source_") or e["data"]["target"].startswith("source_")]
        filtered_networks["source_network"] = {
            "nodes": source_nodes,
            "edges": source_edges,
            "name": "Source Analysis Network"
        }
        
        # Person-focused network
        person_nodes = [n for n in self.nodes if n["data"]["type"] == "person"]
        person_edges = [e for e in self.edges if e["data"]["source"].startswith("person_") or e["data"]["target"].startswith("person_")]
        filtered_networks["person_network"] = {
            "nodes": person_nodes,
            "edges": person_edges,
            "name": "Person Network"
        }
        
        # Geographic network
        geo_nodes = [n for n in self.nodes if n["data"]["type"] in ["city", "location", "direction"]]
        geo_edges = [e for e in self.edges if any(e["data"]["source"].startswith(prefix) or e["data"]["target"].startswith(prefix) 
                                                 for prefix in ["city_", "location_", "direction_"])]
        filtered_networks["geographic_network"] = {
            "nodes": geo_nodes,
            "edges": geo_edges,
            "name": "Geographic Network"
        }
        
        return filtered_networks

def main():
    """Main function to generate Cytoscape.js data"""
    generator = CytoscapeDataGenerator()
    
    # Generate main network data
    output_file = generator.save_network_data()
    
    # Generate filtered networks
    filtered_networks = generator.generate_filtered_networks()
    
    # Save filtered networks
    for network_name, network_data in filtered_networks.items():
        output_file = f"cytoscape_{network_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Filtered network saved to {output_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("CYTOSCAPE.JS DATA GENERATION COMPLETE")
    print("="*50)
    print(f"Main network: cytoscape_network_data.json")
    print(f"Source network: cytoscape_source_network.json")
    print(f"Person network: cytoscape_person_network.json")
    print(f"Geographic network: cytoscape_geographic_network.json")
    print("\nUse these files with the Cytoscape.js visualization interface.")

if __name__ == "__main__":
    main()
