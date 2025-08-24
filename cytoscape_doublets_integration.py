#!/usr/bin/env python3
"""
Cytoscape Doublets Integration for KJV Sources Project
=====================================================

Enhances the existing Cytoscape visualization with doublet-specific nodes,
relationships, and network views. Creates specialized doublet network data
that integrates seamlessly with the current visualization system.

Author: KJV Sources Project
License: MIT
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CytoscapeDoubletsIntegration:
    """Integrates doublets into Cytoscape visualization system"""
    
    def __init__(self, doublets_file: str = "doublets_data.json", 
                 output_dir: str = "frontend"):
        self.doublets_file = Path(doublets_file)
        self.output_dir = Path(output_dir)
        self.doublets_data = self.load_doublets_data()
        
        # Network data structures
        self.nodes = []
        self.edges = []
        self.node_ids = set()
        self.edge_ids = set()
        
        # Color schemes (matching project standards)
        self.source_colors = {
            "J": "#000088",  # Navy Blue - Jahwist
            "E": "#008888",  # Teal - Elohist  
            "P": "#888800",  # Olive Yellow - Priestly
            "D": "#000000",  # Black - Deuteronomist
            "R": "#880000",  # Maroon Red - Redactor
            "J/E/R": "#440044"  # Mixed sources
        }
        
        # Doublet category colors (enhanced for network visualization)
        self.category_colors = {
            "cosmogony": "#e74c3c",        # Red - Creation stories
            "genealogy": "#f39c12",        # Orange - Family lineages
            "catastrophe": "#8e44ad",      # Purple - Divine judgment
            "deception": "#e67e22",        # Dark orange - Deception stories
            "covenant": "#2980b9",         # Blue - Covenant accounts
            "family_conflict": "#27ae60",  # Green - Family tensions
            "prophetic_calling": "#34495e", # Dark gray - Divine calling
            "law": "#16a085",              # Teal - Legal traditions
            "wilderness_miracle": "#d35400", # Red orange - Wilderness miracles
            "wilderness_provision": "#c0392b" # Dark red - Wilderness provision
        }
        
        # Node type configurations
        self.node_types = {
            "doublet": {"size": 60, "shape": "diamond", "border_width": 3},
            "passage": {"size": 40, "shape": "ellipse", "border_width": 2},
            "category": {"size": 50, "shape": "octagon", "border_width": 2},
            "source": {"size": 45, "shape": "square", "border_width": 3},
            "book": {"size": 70, "shape": "hexagon", "border_width": 4},
            "chapter": {"size": 30, "shape": "triangle", "border_width": 1}
        }
    
    def load_doublets_data(self) -> Dict[str, Any]:
        """Load doublets data from JSON file"""
        if not self.doublets_file.exists():
            raise FileNotFoundError(f"Doublets file not found: {self.doublets_file}")
        
        with open(self.doublets_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_biblical_reference(self, reference: str) -> Tuple[str, int, int]:
        """Parse biblical reference into components"""
        # Handle complex references, extract first clear reference
        pattern = r'([A-Za-z0-9\s]+)\s+(\d+):(\d+)'
        match = re.search(pattern, reference.strip())
        
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            return book, chapter, verse
        else:
            logger.warning(f"Could not parse reference: {reference}")
            return "Unknown", 1, 1
    
    def add_node(self, node_id: str, label: str, node_type: str, 
                 attributes: Dict[str, Any] = None) -> bool:
        """Add a node to the network if it doesn't exist"""
        if node_id in self.node_ids:
            return False
        
        type_config = self.node_types.get(node_type, self.node_types["passage"])
        
        node = {
            "data": {
                "id": node_id,
                "label": label,
                "type": node_type,
                "size": type_config["size"],
                "shape": type_config["shape"],
                "border_width": type_config["border_width"]
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
        if source_id not in self.node_ids or target_id not in self.node_ids:
            logger.warning(f"Edge skipped: {source_id} -> {target_id} (missing nodes)")
            return False
        
        edge_id = f"{source_id}_{relationship}_{target_id}"
        if edge_id in self.edge_ids:
            return False
        
        edge = {
            "data": {
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "relationship": relationship,
                "weight": 1
            }
        }
        
        if attributes:
            edge["data"].update(attributes)
        
        self.edges.append(edge)
        self.edge_ids.add(edge_id)
        return True
    
    def create_doublet_network(self) -> Dict[str, Any]:
        """Create a specialized network focused on doublets"""
        logger.info("Creating doublet-focused network...")
        
        # Process each doublet
        for doublet in self.doublets_data.get("doublets", []):
            doublet_id = f"doublet_{doublet['id']}"
            category = doublet["category"]
            
            # Add doublet node
            self.add_node(
                doublet_id,
                doublet["name"],
                "doublet",
                {
                    "color": self.category_colors.get(category, "#95a5a6"),
                    "description": doublet["description"],
                    "category": category,
                    "passage_count": len(doublet["passages"]),
                    "theological_differences": doublet.get("theological_differences", [])
                }
            )
            
            # Add category node
            category_id = f"category_{category}"
            category_name = self.doublets_data.get("categories", {}).get(category, category)
            self.add_node(
                category_id,
                category_name,
                "category",
                {
                    "color": self.category_colors.get(category, "#95a5a6"),
                    "description": category_name
                }
            )
            
            # Connect doublet to category
            self.add_edge(doublet_id, category_id, "belongs_to_category")
            
            # Process passages
            passage_nodes = []
            for i, passage in enumerate(doublet["passages"]):
                passage_id = f"passage_{doublet['id']}_{i}"
                source = passage.get("source", "Unknown")
                book, chapter, verse = self.parse_biblical_reference(passage["reference"])
                
                # Add passage node
                self.add_node(
                    passage_id,
                    f"{passage['reference']} ({source})",
                    "passage",
                    {
                        "color": self.source_colors.get(source, "#95a5a6"),
                        "source": source,
                        "book": book,
                        "chapter": chapter,
                        "verse": verse,
                        "reference": passage["reference"],
                        "themes": passage.get("themes", []),
                        "characteristics": passage.get("characteristics", [])
                    }
                )
                passage_nodes.append(passage_id)
                
                # Connect passage to doublet
                self.add_edge(doublet_id, passage_id, "contains_passage")
                
                # Add source node
                source_id = f"source_{source}"
                self.add_node(
                    source_id,
                    f"Source {source}",
                    "source",
                    {
                        "color": self.source_colors.get(source, "#95a5a6"),
                        "description": self.get_source_description(source)
                    }
                )
                
                # Connect passage to source
                self.add_edge(passage_id, source_id, "attributed_to_source")
                
                # Add book node
                book_id = f"book_{book}"
                self.add_node(
                    book_id,
                    book,
                    "book",
                    {
                        "color": "#1abc9c",
                        "testament": "Torah" if book in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"] else "Other"
                    }
                )
                
                # Connect passage to book
                self.add_edge(passage_id, book_id, "located_in_book")
                
                # Add chapter node
                chapter_id = f"chapter_{book}_{chapter}"
                self.add_node(
                    chapter_id,
                    f"{book} {chapter}",
                    "chapter",
                    {
                        "color": "#3498db",
                        "book": book,
                        "chapter_number": chapter
                    }
                )
                
                # Connect passage to chapter
                self.add_edge(passage_id, chapter_id, "located_in_chapter")
            
            # Create doublet similarity edges between passages
            for i, passage_id1 in enumerate(passage_nodes):
                for j, passage_id2 in enumerate(passage_nodes[i+1:], i+1):
                    self.add_edge(
                        passage_id1, 
                        passage_id2, 
                        "doublet_parallel",
                        {"style": "dashed", "weight": 2}
                    )
        
        # Create network data structure
        network_data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "metadata": {
                "type": "doublets_network",
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": Counter(node["data"]["type"] for node in self.nodes),
                "relationship_types": Counter(edge["data"]["relationship"] for edge in self.edges),
                "doublets_count": len(self.doublets_data.get("doublets", [])),
                "categories": list(self.category_colors.keys())
            }
        }
        
        logger.info(f"Created doublet network with {len(self.nodes)} nodes and {len(self.edges)} edges")
        return network_data
    
    def get_source_description(self, source: str) -> str:
        """Get description for documentary source"""
        descriptions = {
            "J": "Jahwist - Early narrative source with anthropomorphic God",
            "E": "Elohist - Northern source emphasizing divine communication",
            "P": "Priestly - Ritual and genealogical source",
            "D": "Deuteronomist - Deuteronomy-focused source",
            "R": "Redactor - Editorial additions and connections",
            "J/E/R": "Multiple sources - Complex redactional composition"
        }
        return descriptions.get(source, f"Documentary source: {source}")
    
    def create_enhanced_cytoscape_html(self, output_file: str = "doublets_cytoscape.html"):
        """Create enhanced Cytoscape HTML with doublet integration"""
        network_data = self.create_doublet_network()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biblical Doublets - Interactive Network Visualization</title>
    
    <!-- Cytoscape.js and Extensions -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape-dagre/2.5.0/cytoscape-dagre.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape-cose-bilkent/4.1.0/cytoscape-cose-bilkent.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape-panzoom/2.5.3/cytoscape-panzoom.min.js"></script>
    
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
        }}
        
        .sidebar {{
            width: 350px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 20px rgba(0,0,0,0.1);
        }}
        
        .main-content {{
            flex: 1;
            position: relative;
        }}
        
        #cy {{
            width: 100%;
            height: 100vh;
            background: radial-gradient(circle at center, #f8f9fa 0%, #e9ecef 100%);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #3498db;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin: 0 0 5px 0;
        }}
        
        .header p {{
            color: #7f8c8d;
            margin: 0;
            font-size: 0.9em;
        }}
        
        .controls {{
            margin-bottom: 20px;
        }}
        
        .control-group {{
            margin-bottom: 15px;
        }}
        
        .control-group label {{
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .control-group select, .control-group button {{
            width: 100%;
            padding: 8px 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            background: white;
        }}
        
        .control-group button {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        
        .control-group button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
        }}
        
        .legend {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .legend h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1em;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 0.85em;
        }}
        
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 3px;
            margin-right: 8px;
            border: 1px solid #ddd;
        }}
        
        .stats {{
            background: #e8f4f8;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .stats h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1em;
        }}
        
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin: 3px 0;
            font-size: 0.85em;
        }}
        
        .node-info {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            max-width: 300px;
            display: none;
        }}
        
        .floating-controls {{
            position: absolute;
            top: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
        }}
        
        .floating-btn {{
            background: rgba(255, 255, 255, 0.9);
            border: none;
            padding: 10px 15px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            color: #2c3e50;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }}
        
        .floating-btn:hover {{
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="header">
                <h1>📖 Biblical Doublets</h1>
                <p>Interactive Network Analysis</p>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label>Layout Algorithm</label>
                    <select id="layout-select">
                        <option value="cose-bilkent">Cose-Bilkent (Default)</option>
                        <option value="dagre">Dagre (Hierarchical)</option>
                        <option value="grid">Grid</option>
                        <option value="circle">Circle</option>
                        <option value="concentric">Concentric</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Filter by Category</label>
                    <select id="category-filter">
                        <option value="all">All Categories</option>
                        <option value="cosmogony">Creation Stories</option>
                        <option value="genealogy">Family Lineages</option>
                        <option value="catastrophe">Divine Judgment</option>
                        <option value="deception">Deception Stories</option>
                        <option value="covenant">Covenant Accounts</option>
                        <option value="family_conflict">Family Tensions</option>
                        <option value="prophetic_calling">Divine Calling</option>
                        <option value="law">Legal Traditions</option>
                        <option value="wilderness_miracle">Wilderness Miracles</option>
                        <option value="wilderness_provision">Wilderness Provision</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Filter by Source</label>
                    <select id="source-filter">
                        <option value="all">All Sources</option>
                        <option value="J">Jahwist (J)</option>
                        <option value="E">Elohist (E)</option>
                        <option value="P">Priestly (P)</option>
                        <option value="D">Deuteronomist (D)</option>
                        <option value="R">Redactor (R)</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <button id="reset-view">🔄 Reset View</button>
                </div>
                
                <div class="control-group">
                    <button id="center-doublets">🎯 Center on Doublets</button>
                </div>
            </div>
            
            <div class="legend">
                <h3>🎨 Node Types</h3>
                <div class="legend-item">
                    <div class="legend-color" style="background: #e74c3c; clip-path: polygon(50% 0%, 0% 100%, 100% 100%);"></div>
                    <span>Doublets</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3498db; border-radius: 50%;"></div>
                    <span>Passages</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #27ae60;"></div>
                    <span>Sources</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #1abc9c; clip-path: polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%);"></div>
                    <span>Books</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #f39c12; clip-path: polygon(50% 0%, 80% 10%, 100% 35%, 100% 70%, 80% 90%, 50% 100%, 20% 90%, 0% 70%, 0% 35%, 20% 10%);"></div>
                    <span>Categories</span>
                </div>
            </div>
            
            <div class="stats">
                <h3>📊 Network Statistics</h3>
                <div class="stat-item">
                    <span>Total Nodes:</span>
                    <span id="total-nodes">{network_data['metadata']['total_nodes']}</span>
                </div>
                <div class="stat-item">
                    <span>Total Edges:</span>
                    <span id="total-edges">{network_data['metadata']['total_edges']}</span>
                </div>
                <div class="stat-item">
                    <span>Doublets:</span>
                    <span id="doublets-count">{network_data['metadata']['doublets_count']}</span>
                </div>
                <div class="stat-item">
                    <span>Categories:</span>
                    <span id="categories-count">{len(network_data['metadata']['categories'])}</span>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="floating-controls">
                <button class="floating-btn" id="export-png">📸 Export PNG</button>
                <button class="floating-btn" id="export-json">💾 Export JSON</button>
                <button class="floating-btn" id="fullscreen">🔍 Fullscreen</button>
            </div>
            
            <div id="cy"></div>
            
            <div class="node-info" id="node-info">
                <h4 id="node-title">Node Information</h4>
                <div id="node-details"></div>
            </div>
        </div>
    </div>

    <script>
        // Network data
        const networkData = {json.dumps(network_data, indent=8)};
        
        // Initialize Cytoscape
        document.addEventListener('DOMContentLoaded', function() {{
            // Register extensions
            if (typeof cytoscapeDagre !== 'undefined') cytoscape.use(cytoscapeDagre);
            if (typeof cytoscapeCoseBilkent !== 'undefined') cytoscape.use(cytoscapeCoseBilkent);
            if (typeof cytoscapePanzoom !== 'undefined') cytoscape.use(cytoscapePanzoom);
            
            const cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: [
                    ...networkData.nodes,
                    ...networkData.edges
                ],
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'width': 'data(size)',
                            'height': 'data(size)',
                            'background-color': 'data(color)',
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'font-size': '10px',
                            'font-weight': 'bold',
                            'text-outline-width': 2,
                            'text-outline-color': '#ffffff',
                            'border-width': 'data(border_width)',
                            'border-color': '#2c3e50',
                            'border-opacity': 0.8
                        }}
                    }},
                    {{
                        selector: 'node[type="doublet"]',
                        style: {{
                            'shape': 'diamond',
                            'font-size': '12px'
                        }}
                    }},
                    {{
                        selector: 'node[type="passage"]',
                        style: {{
                            'shape': 'ellipse',
                            'font-size': '8px'
                        }}
                    }},
                    {{
                        selector: 'node[type="source"]',
                        style: {{
                            'shape': 'square'
                        }}
                    }},
                    {{
                        selector: 'node[type="book"]',
                        style: {{
                            'shape': 'hexagon',
                            'font-size': '14px'
                        }}
                    }},
                    {{
                        selector: 'node[type="category"]',
                        style: {{
                            'shape': 'octagon'
                        }}
                    }},
                    {{
                        selector: 'node[type="chapter"]',
                        style: {{
                            'shape': 'triangle'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 2,
                            'line-color': '#7f8c8d',
                            'target-arrow-color': '#7f8c8d',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'opacity': 0.7
                        }}
                    }},
                    {{
                        selector: 'edge[relationship="doublet_parallel"]',
                        style: {{
                            'line-style': 'dashed',
                            'line-color': '#e74c3c',
                            'width': 3,
                            'opacity': 0.8
                        }}
                    }},
                    {{
                        selector: 'node:selected',
                        style: {{
                            'border-width': 4,
                            'border-color': '#f39c12',
                            'background-blacken': 0.1
                        }}
                    }},
                    {{
                        selector: 'node.highlighted',
                        style: {{
                            'border-width': 6,
                            'border-color': '#e74c3c',
                            'z-index': 999
                        }}
                    }},
                    {{
                        selector: 'node.dimmed',
                        style: {{
                            'opacity': 0.3
                        }}
                    }},
                    {{
                        selector: 'edge.dimmed',
                        style: {{
                            'opacity': 0.1
                        }}
                    }}
                ],
                layout: {{
                    name: 'cose-bilkent',
                    nodeRepulsion: 8000,
                    idealEdgeLength: 100,
                    edgeElasticity: 0.1,
                    nestingFactor: 0.1,
                    gravity: 0.1,
                    numIter: 2500,
                    tile: true,
                    animate: true,
                    randomize: false
                }}
            }});
            
            // Add panzoom if available
            if (cy.panzoom) {{
                cy.panzoom({{
                    zoomFactor: 0.05,
                    zoomDelay: 45,
                    minZoom: 0.1,
                    maxZoom: 10,
                    fitPadding: 50,
                    panSpeed: 10,
                    panDistance: 10,
                    panDragAreaSize: 75,
                    panMinPercentSpeed: 0.25,
                    panMaxPercentSpeed: 2.0,
                    panInactiveArea: 8,
                    panIndicatorMinOpacity: 0.5,
                    zoomOnly: false,
                    fitSelector: undefined,
                    animateOnFit: function() {{ return false; }},
                    fitAnimationDuration: 1000
                }});
            }}
            
            // Event handlers
            cy.on('tap', 'node', function(evt) {{
                const node = evt.target;
                const nodeInfo = document.getElementById('node-info');
                const nodeTitle = document.getElementById('node-title');
                const nodeDetails = document.getElementById('node-details');
                
                nodeTitle.textContent = node.data('label');
                
                let details = `<p><strong>Type:</strong> ${{node.data('type')}}</p>`;
                
                if (node.data('description')) {{
                    details += `<p><strong>Description:</strong> ${{node.data('description')}}</p>`;
                }}
                
                if (node.data('source')) {{
                    details += `<p><strong>Source:</strong> ${{node.data('source')}}</p>`;
                }}
                
                if (node.data('category')) {{
                    details += `<p><strong>Category:</strong> ${{node.data('category')}}</p>`;
                }}
                
                if (node.data('themes')) {{
                    details += `<p><strong>Themes:</strong> ${{node.data('themes').join(', ')}}</p>`;
                }}
                
                if (node.data('characteristics')) {{
                    details += `<p><strong>Characteristics:</strong> ${{node.data('characteristics').join(', ')}}</p>`;
                }}
                
                if (node.data('theological_differences')) {{
                    details += `<p><strong>Theological Differences:</strong></p><ul>`;
                    node.data('theological_differences').forEach(diff => {{
                        details += `<li>${{diff}}</li>`;
                    }});
                    details += `</ul>`;
                }}
                
                nodeDetails.innerHTML = details;
                nodeInfo.style.display = 'block';
                
                // Highlight connected nodes
                const connectedNodes = node.neighborhood().add(node);
                cy.elements().addClass('dimmed');
                connectedNodes.removeClass('dimmed').addClass('highlighted');
            }});
            
            cy.on('tap', function(evt) {{
                if (evt.target === cy) {{
                    document.getElementById('node-info').style.display = 'none';
                    cy.elements().removeClass('dimmed highlighted');
                }}
            }});
            
            // Control handlers
            document.getElementById('layout-select').addEventListener('change', function(e) {{
                const layoutName = e.target.value;
                let layout;
                
                switch(layoutName) {{
                    case 'dagre':
                        layout = {{ name: 'dagre', rankDir: 'TB', spacingFactor: 1.5 }};
                        break;
                    case 'grid':
                        layout = {{ name: 'grid', rows: 5 }};
                        break;
                    case 'circle':
                        layout = {{ name: 'circle' }};
                        break;
                    case 'concentric':
                        layout = {{ name: 'concentric', concentric: function(node) {{ return node.degree(); }} }};
                        break;
                    default:
                        layout = {{ 
                            name: 'cose-bilkent',
                            nodeRepulsion: 8000,
                            idealEdgeLength: 100,
                            animate: true
                        }};
                }}
                
                cy.layout(layout).run();
            }});
            
            document.getElementById('category-filter').addEventListener('change', function(e) {{
                const category = e.target.value;
                
                if (category === 'all') {{
                    cy.elements().show();
                }} else {{
                    cy.elements().hide();
                    cy.nodes(`[category="${{category}}"]`).show();
                    cy.nodes(`[category="${{category}}"]`).neighborhood().show();
                }}
            }});
            
            document.getElementById('source-filter').addEventListener('change', function(e) {{
                const source = e.target.value;
                
                if (source === 'all') {{
                    cy.elements().show();
                }} else {{
                    cy.elements().hide();
                    cy.nodes(`[source="${{source}}"]`).show();
                    cy.nodes(`[source="${{source}}"]`).neighborhood().show();
                }}
            }});
            
            document.getElementById('reset-view').addEventListener('click', function() {{
                cy.elements().show().removeClass('dimmed highlighted');
                cy.fit();
                document.getElementById('node-info').style.display = 'none';
            }});
            
            document.getElementById('center-doublets').addEventListener('click', function() {{
                const doubletNodes = cy.nodes('[type="doublet"]');
                cy.fit(doubletNodes, 50);
            }});
            
            document.getElementById('export-png').addEventListener('click', function() {{
                const png64 = cy.png({{ scale: 2, full: true }});
                const link = document.createElement('a');
                link.download = 'biblical_doublets_network.png';
                link.href = png64;
                link.click();
            }});
            
            document.getElementById('export-json').addEventListener('click', function() {{
                const data = JSON.stringify(networkData, null, 2);
                const blob = new Blob([data], {{ type: 'application/json' }});
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.download = 'biblical_doublets_network.json';
                link.href = url;
                link.click();
                URL.revokeObjectURL(url);
            }});
            
            document.getElementById('fullscreen').addEventListener('click', function() {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    document.documentElement.requestFullscreen();
                }}
            }});
        }});
    </script>
</body>
</html>"""
        
        # Save HTML file
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Enhanced Cytoscape HTML saved to: {output_path}")
        return str(output_path)
    
    def save_doublet_network_data(self, output_file: str = "cytoscape_doublets_network.json"):
        """Save doublet network data to JSON file"""
        network_data = self.create_doublet_network()
        
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Doublet network data saved to: {output_path}")
        return str(output_path)

def main():
    """Main function to create enhanced Cytoscape doublets visualization"""
    print("Cytoscape Doublets Integration")
    print("==============================")
    
    try:
        # Initialize the integration
        integration = CytoscapeDoubletsIntegration()
        
        # Create enhanced HTML visualization
        print("Creating enhanced Cytoscape visualization...")
        html_file = integration.create_enhanced_cytoscape_html()
        
        # Save network data
        print("Saving doublet network data...")
        json_file = integration.save_doublet_network_data()
        
        print(f"\n✅ Cytoscape doublets integration completed!")
        print(f"🌐 Enhanced visualization: {html_file}")
        print(f"💾 Network data: {json_file}")
        print(f"\nFeatures:")
        print(f"  📊 Interactive network with {len(integration.nodes)} nodes")
        print(f"  🎯 Doublet-focused visualization")
        print(f"  🎨 Multiple layout algorithms")
        print(f"  🔍 Filtering by category and source")
        print(f"  📱 Responsive design with sidebar controls")
        print(f"  💾 Export capabilities (PNG, JSON)")
        
    except Exception as e:
        print(f"❌ Error creating integration: {e}")
        raise

if __name__ == "__main__":
    main()
