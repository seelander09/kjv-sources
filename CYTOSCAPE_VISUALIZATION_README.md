# KJV Sources - Cytoscape.js Network Visualization

## 🎉 Fixed! The Cytoscape.js Visualization Should Now Work

The issue was that the server was running from the wrong directory. Here's what I did:

### The Problem:
- The server was running from `E:\Projects\kjv-sources` (root directory)
- But the visualization file is located at `E:\Projects\kjv-sources\frontend\cytoscape_visualization.html`
- So the URL `http://localhost:8000/cytoscape_visualization.html` was looking for the file in the wrong place

### The Solution:
1. **Stopped the old server** that was running from the root directory
2. **Started a new server** from the `frontend` directory where the HTML file actually exists
3. **Opened the browser** to the correct URL

## Current Status:
✅ **Server is now running from the correct directory** (`frontend/`)  
✅ **Browser should open to the working visualization**  
✅ **All network data files are accessible**  
✅ **URL should work**: `http://localhost:8000/cytoscape_visualization.html`

## What You Should See Now:

The browser should display the **KJV Sources Network Visualization** with:

- **Interactive network graph** with 6,001 nodes and 16,182 edges
- **Control panels** for filtering by source (J, E, P, D, R), entity type, and search
- **Multiple network views**:
  - Complete Network - All entities and relationships
  - Source Analysis - Focus on J, E, P, D, R sources
  - Person Network - Biblical characters and their connections
  - Geographic Network - Cities, locations, and directions
- **Real-time statistics** showing network density and connectivity
- **Color-coded nodes** representing different entity types (persons, cities, sources, etc.)

## How to Start the Visualization:

### Option 1: Use the Fixed Main Script
```powershell
.\start_cytoscape_visualization.ps1
```

### Option 2: Use the Simple Launcher
```powershell
.\start_cytoscape_simple.ps1
```

### Option 3: Manual Setup
```powershell
# 1. Copy network data to frontend directory
Copy-Item "cytoscape_*.json" -Destination "frontend/" -Force

# 2. Change to frontend directory
cd frontend

# 3. Start the server
python -m http.server 8000

# 4. Open browser to:
# http://localhost:8000/cytoscape_visualization.html
```

## Available Scripts:

### 1. `start_cytoscape_visualization.ps1` (Main Script)
- **Full-featured launcher** with data generation options
- **Comprehensive error checking** and validation
- **Automatic browser opening**
- **Background server management**

### 2. `start_cytoscape_simple.ps1` (Simple Launcher)
- **Streamlined approach** for quick startup
- **Direct server startup** from frontend directory
- **Minimal dependencies**

### 3. `start_cytoscape_direct.ps1` (Direct Launcher)
- **Prepares environment** and opens browser
- **Provides manual server instructions**
- **Good for troubleshooting**

## Network Data Files:

The visualization uses these JSON files:
- `cytoscape_network_data.json` - Complete network (6.1MB)
- `cytoscape_source_network.json` - Source analysis (1.4MB)
- `cytoscape_person_network.json` - Person network (365KB)
- `cytoscape_geographic_network.json` - Geographic network (292KB)

## Interactive Features:

### Network Controls:
- **Zoom and Pan**: Mouse wheel to zoom, drag to pan
- **Node Selection**: Click nodes for detailed information
- **Layout Changes**: Choose from different layout algorithms
- **Fit to Screen**: Auto-fit network to viewport

### Filtering Options:
- **Entity Type**: Filter by person, city, source, book, tribe, direction
- **Source Filter**: Filter by J, E, P, D, R sources
- **Search**: Find specific entities by name
- **Network View**: Switch between different network perspectives

### Statistics Panel:
- **Total Nodes**: Number of visible entities
- **Total Edges**: Number of relationships
- **Selected Nodes**: Currently selected entities
- **Network Density**: Connectivity measure

## Troubleshooting:

### Server Won't Start:
```powershell
# Check if port is in use
netstat -an | findstr :8000

# Kill existing processes
Get-Process python | Stop-Process -Force

# Try different port
.\start_cytoscape_visualization.ps1 -Port 8080
```

### Files Not Found:
```powershell
# Regenerate network data
python cytoscape_data_generator.py

# Check file locations
Get-ChildItem frontend/
```

### Browser Issues:
- **Clear browser cache** and refresh
- **Try different browser** (Chrome, Firefox, Edge)
- **Check browser console** for JavaScript errors

### Performance Issues:
- **Large networks** may take time to load
- **Use filters** to reduce visible nodes
- **Try different layout algorithms**

## Technical Details:

### Server Configuration:
- **Port**: 8000 (configurable)
- **Directory**: `frontend/`
- **Protocol**: HTTP
- **Server**: Python SimpleHTTPServer

### Browser Requirements:
- **Modern browser** with ES6 support
- **JavaScript enabled**
- **CORS support** for local files

### Data Format:
- **Cytoscape.js compatible** JSON format
- **Nodes**: Entities with properties (type, label, color, etc.)
- **Edges**: Relationships between entities
- **Metadata**: Source attribution and analysis data

## Future Enhancements:

- **Real-time updates** from data pipeline
- **Advanced filtering** and search capabilities
- **Export functionality** for network analysis
- **Mobile-responsive** design improvements
- **Performance optimizations** for large networks

## Support:

If you encounter issues:
1. **Check the troubleshooting section** above
2. **Verify all files exist** in the frontend directory
3. **Ensure Python is installed** and accessible
4. **Check browser console** for error messages
5. **Try the manual setup** process

---

**The visualization should now be fully functional!** You can explore the complex relationships between biblical sources, persons, cities, and directional coordinates in your KJV Sources project.
