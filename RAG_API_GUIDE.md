# 🚀 KJV Sources RAG API Guide

## 📖 Overview

The KJV Sources RAG API is a FastAPI-based backend that exposes your existing biblical analysis system (Qdrant + Doublet Analysis + POV Analysis) through RESTful endpoints. This API is specifically designed to integrate with the **King James Pure Bible Search (KJPBS)** Qt application, enabling AI-powered biblical research capabilities.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     KJPBS Qt Frontend (C++)         │
│  • Search Interface                 │
│  • Results Display                  │  
│  • NEW: AI Assistant Panel          │
└─────────────────┬───────────────────┘
                  │ HTTP/REST API
┌─────────────────┴───────────────────┐
│     FastAPI Backend (Python)       │
│  • Chat Endpoints                   │
│  • Doublet Analysis API             │
│  • POV Analysis API                 │
│  • Semantic Search API              │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│     Your Existing RAG System       │
│  • Qdrant Vector Database           │
│  • 5,852+ Analyzed Verses           │
│  • 30+ Identified Doublets          │
│  • Documentary Hypothesis Sources   │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Install FastAPI requirements
pip install -r api_requirements.txt

# Your existing requirements should already be installed:
# qdrant-client, sentence-transformers, pandas, rich, click
```

### 2. Start the API Server

```powershell
# Option 1: Use the startup script
.\start_rag_api.bat

# Option 2: Run directly
python rag_api_server.py
```

### 3. Test the API

```powershell
# Run comprehensive tests
python test_rag_api.py

# Or manually browse to:
# http://127.0.0.1:8000/docs (Interactive API documentation)
```

## 📡 API Endpoints

### 🏠 Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and feature list |
| `/health` | GET | Health check and system status |
| `/docs` | GET | Interactive API documentation |

### 💬 Chat & AI Assistant

#### `POST /api/chat`
Main endpoint for AI-powered biblical Q&A.

**Request:**
```json
{
  "query": "Tell me about the creation stories in Genesis",
  "context": {
    "previous_topic": "creation",
    "verse_reference": "Genesis 1:1"
  },
  "include_sources": true,
  "max_results": 10
}
```

**Response:**
```json
{
  "response": "I found 2 doublet passages related to your query about 'creation stories'...",
  "sources": [
    {
      "book": "Genesis",
      "chapter": 1,
      "verse": 1,
      "text": "In the beginning God created...",
      "sources": "P",
      "doublet_name": "Creation Stories"
    }
  ],
  "doublets_found": [...],
  "analysis_type": "semantic_search_with_doublets",
  "timestamp": "2025-01-08T..."
}
```

### 🔍 Search Endpoints

#### `POST /api/search`
Semantic search for biblical verses.

**Request:**
```json
{
  "query": "creation of man",
  "book": "Genesis",      // Optional filter
  "source": "P",          // Optional: J, E, P, D, R
  "limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "query": "creation of man",
    "count": 5,
    "filters_applied": {"book_filter": "Genesis", "source_filter": "P"}
  },
  "message": "Found 5 verses matching 'creation of man'"
}
```

### 📚 Doublet Analysis

#### `POST /api/doublets/search`
Search for biblical doublets with various filters.

**Request Options:**
```json
// Semantic search
{
  "query": "flood narrative",
  "limit": 10
}

// Category search
{
  "category": "cosmogony",
  "limit": 5
}

// Name search
{
  "doublet_name": "Creation Stories",
  "limit": 8
}
```

#### `GET /api/doublets/parallels/{book}/{chapter}/{verse}`
Get parallel passages for a specific verse.

**Example:** `GET /api/doublets/parallels/Genesis/1/1`

#### `GET /api/doublets/statistics`
Comprehensive doublet statistics including:
- Total doublet verses
- Category distribution
- Source analysis
- Most common doublets

#### `GET /api/doublets/categories`
List of available doublet categories:
- cosmogony, genealogy, catastrophe, deception
- covenant, family_conflict, prophetic_calling
- law, wilderness_miracle, wilderness_provision

### 🎭 POV (Point of View) Analysis

#### `POST /api/pov/search`
Search verses by authorial perspective characteristics.

**Request:**
```json
{
  "style": "narrative_anthropomorphic",    // Optional
  "perspective": "divine_transcendent",    // Optional
  "purpose": "theological_instruction",    // Optional
  "theme": "creation",                     // Optional
  "complexity": "high",                    // Optional
  "limit": 15
}
```

#### `GET /api/pov/statistics`
POV analysis statistics including style distribution, themes, and complexity metrics.

### 🔧 Utility Endpoints

#### `GET /api/books`
List of available books in the database.

#### `GET /api/sources`
Information about Documentary Hypothesis sources (J, E, P, D, R).

## 🎯 Integration with KJPBS

### Chat Interface Integration
```cpp
// C++ Qt integration example
class AIAssistantWidget : public QWidget {
public:
    void analyzeSearchResults(const QString& query, const QList<SearchResult>& results) {
        QJsonObject request;
        request["query"] = query;
        request["context"] = buildContext(results);
        
        sendApiRequest("/api/chat", request);
    }

private:
    void sendApiRequest(const QString& endpoint, const QJsonObject& data) {
        QNetworkRequest request(QUrl("http://127.0.0.1:8000" + endpoint));
        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
        
        m_networkManager->post(request, QJsonDocument(data).toJson());
    }
};
```

### Enhanced Search Results
```cpp
// Automatically detect and explain doublets
void SearchResultsWidget::displayResults(const QList<SearchResult>& results) {
    // Display traditional search results
    showTraditionalResults(results);
    
    // Add AI analysis for doublets
    if (containsDoubletVerses(results)) {
        requestDoubletAnalysis(results);
    }
}
```

## 🧪 Testing

The API includes comprehensive test coverage:

```powershell
python test_rag_api.py
```

**Test Categories:**
- ✅ Basic endpoints (health, docs, info)
- ✅ Search functionality with filters
- ✅ Chat AI assistant responses
- ✅ Doublet analysis (all search types)
- ✅ POV analysis capabilities
- ✅ Error handling and edge cases

## 🔒 Security Considerations

**Current Status:** Development mode with open access
**Production Requirements:**
- JWT authentication for API access
- HTTPS/TLS encryption
- Rate limiting
- Input validation and sanitization
- CORS policy refinement

## 📊 Performance

**Expected Response Times:**
- Health check: < 50ms
- Simple search: < 200ms
- Complex doublet analysis: < 500ms
- Chat with AI generation: < 2s

**Scalability:**
- Qdrant vector database handles millions of vectors
- FastAPI supports async operations
- Horizontal scaling possible with load balancers

## 🛠️ Development

### Adding New Endpoints
```python
@app.post("/api/new-feature", response_model=ApiResponse)
async def new_feature(
    request: NewFeatureRequest,
    client: QdrantClient = Depends(get_qdrant_client)
):
    try:
        results = client.your_new_method(request.param)
        return ApiResponse(
            success=True,
            data=results,
            message="Feature executed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Error Handling
All endpoints use consistent error handling:
- 400: Bad Request (invalid parameters)
- 500: Internal Server Error (system issues)
- 503: Service Unavailable (Qdrant connection issues)

## 🎉 Features Highlights

### For Biblical Scholars
- **Automatic Doublet Detection**: AI identifies parallel passages
- **Source Criticism**: Documentary Hypothesis analysis
- **Contextual Search**: Semantic understanding, not just keywords
- **Scholarly Citations**: Proper verse references and source attribution

### For KJPBS Users  
- **Enhanced Search**: AI explains search results
- **Interactive Chat**: Natural language biblical questions
- **Visual Doublets**: Highlighted parallel passages
- **Research Workflows**: Guided documentary analysis

### For Developers
- **RESTful Design**: Standard HTTP methods and status codes
- **Comprehensive Docs**: Auto-generated OpenAPI documentation
- **Type Safety**: Pydantic models for all requests/responses
- **Testing Suite**: 25+ automated tests

## 🔮 Future Enhancements

**Phase 1 Complete:** ✅ Basic API with all core features
**Phase 2:** Qt C++ integration and UI development
**Phase 3:** Advanced AI features (GPT-4, Claude integration)
**Phase 4:** Multi-user support and collaboration features
**Phase 5:** Mobile app and web interface

---

## 📞 Support

For questions or issues:
1. Check the `/docs` endpoint for API documentation
2. Run `python test_rag_api.py` to verify functionality
3. Review server logs for detailed error information
4. Ensure Qdrant connection and data availability

**API Server Status:** http://127.0.0.1:8000/health
**Interactive Docs:** http://127.0.0.1:8000/docs
