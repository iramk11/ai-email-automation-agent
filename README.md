# Graph RAG Email Assistant

AI-powered email reply generator for Gmail and Outlook using Graph RAG (Retrieval-Augmented Generation) with local LLM. Generates personalized email replies based on your historical email patterns and writing style.

> 📚 **Looking for comprehensive project information?** See the [Tutorial Guide](tutorial.md) for complete component mapping, testing details, and extensive documentation.

##  Features

- **Smart Email Understanding**: Extracts context using hybrid retrieval (vector + graph)
- **AI-Powered Replies**: Generates contextual drafts using local Llama 3 model via Ollama
- **Writing Style Matching**: Gmail-style semantic search to match your writing tone
- **Privacy First**: All processing happens locally - no data sent to third parties
- **One-Click Generation**: Simple button in Gmail to generate replies
- **Confidence Scoring**: Shows how confident the AI is about the reply

##  Prerequisites

1. **Python 3.10+**
2. **Ollama** with Llama 3 model
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3
   ```
3. **Conda** (recommended) or Python venv
4. **Chrome Browser**

##  Installation & Setup

### Step 1: Prepare Knowledge Base (graph_rag_updated2.ipynb)

The system uses a Jupyter notebook to build the knowledge base from your email data:

1. **Open the notebook**: `graphrag/graph_rag_updated2.ipynb`

2. **Run all cells** to:
   - Load FAQ data from `data/faq_updated.csv`
   - Load labeled email pairs from `data/generated_email_pairs.json`
   - Build NetworkX graph with topics, intents, and artifacts
   - Create Qdrant collections:
     - `knowledge_space`: FAQs and graph node embeddings
     - `writing_style`: Reply chunks for style matching (Gmail-style approach)
   - Index all data in Qdrant

3. **Key Features of the Notebook**:
   - **Multi-intent Classification**: Detects multiple intents per email
   - **Intent-based Graph Retrieval**: Direct NetworkX lookup (no vector search for graph)
   - **Separate FAQ Search**: Always retrieves FAQs using filtered search
   - **Style-based Retrieval**: Semantic search for writing style examples
   - **Graph Expansion**: Retrieves related nodes for richer context

4. **Important**: Close the notebook before starting the backend (Qdrant database lock)

### Step 2: Set Up Backend

1. **Navigate to project directory**:
   ```bash
   cd .
   ```

2. **Create and activate virtual environment** (choose one):
   
   **Option A: Using Python venv** (recommended if conda is not available):
   ```bash
   python3 -m venv email-agent
   source email-agent/bin/activate  # On macOS/Linux
   # or: email-agent\Scripts\activate  # On Windows
   ```
   
   **Option B: Using conda**:
   ```bash
   conda create -n graph_rag python=3.10 -y
   conda activate graph_rag
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**:
   
   **Option A: Using the start script** (recommended):
   ```bash
   ./start_backend.sh
   ```
   
   **Option B: Manual start**:
   ```bash
   # From project root (not inside backend/)
   source email-agent/bin/activate  # Activate venv first
   python -m uvicorn backend.main:app --reload
   ```
   
   You should see:
   ```
   INFO: Starting Graph RAG Email Assistant API...
   INFO: All services initialized successfully!
   INFO: Uvicorn running on http://0.0.0.0:8001
   ```

   **Note**: If port 8000 is available, the backend will use it. Otherwise, it defaults to 8001.

5. **Test the backend** (in a new terminal):
   ```bash
   curl http://localhost:8001/api/health
   ```

### Step 3: Install Chrome Extension

1. **Open Chrome** and navigate to `chrome://extensions/`

2. **Enable "Developer mode"** (toggle in top-right corner)

3. **Click "Load unpacked"**

4. **Navigate to and select** the `chrome-extension` folder in your project directory

5. **The extension should now appear** in your extensions list

6. **Pin the extension** to your toolbar for easy access

### Step 4: Configure Extension

1. **Click the extension icon** in Chrome toolbar

2. **Verify settings**:
   - API URL: `http://localhost:8001/api` (default - update if backend uses different port)
   - Confidence Threshold: `0.85` (adjust as needed)
   - Auto-insert drafts: ✓ (checked)

3. **Click "Test Connection"** to verify backend is running

4. **You should see** "Backend online and healthy" 

##  Usage

### Generating Email Replies

1. **Open Gmail** (https://mail.google.com) or **Outlook** (https://outlook.live.com)

2. **Open an email** you want to reply to

3. **Click the Reply button** in Gmail/Outlook

4. **Look for the "🤖 Generate Reply" button** near the reply box

   ![Extension Button](images/1.png)

5. **Click "🤖 Generate Reply"**
   - The extension will extract the email content
   - Send it to your local backend
   - Generate a contextual reply using:
     - FAQ matches for content
     - Graph nodes for relationships
     - Style examples for tone matching
   - Insert it into the reply box

   ![Reply Generation](images/2.png)

6. **Review the generated draft** - You can see the context used for generation

   ![Context Panel](images/3.png)

7. **Review and edit** the generated draft as needed

   ![Generated Reply](images/4.png)

8. **Send** when satisfied!

### Extension Popup & Settings

![Extension Popup](images/5.png)

![Settings Configuration](images/6.png)

##  Configuration

### Backend Configuration

Edit `backend/config.py` to customize:

```python
# RAG settings
TOP_K_RESULTS = 6  # Number of context items to retrieve
AUTO_SEND_THRESHOLD = 0.85  # Confidence for auto-send suggestion
MAX_REPLY_LENGTH = 120  # Max words in reply

# User personalization
DEFAULT_USER_NAME = "Zubair"  # Your name
DEFAULT_USER_TONE = "polite, proactive, and clear in communication"
```

### Extension Settings

In the extension popup:
- **API URL**: Change if backend runs on different port
- **Confidence Threshold**: Higher = more conservative (only high-confidence replies)
- **Auto-insert**: Enable/disable automatic draft insertion

##  Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'backend'`
- **Solution**: Run from project root, not inside `backend/`:
  ```bash
  cd .
  python -m uvicorn backend.main:app --reload
  ```

**Issue**: `Storage folder is already accessed by another instance`
- **Solution**: Close the Jupyter notebook first (it locks the Qdrant database)
- **Or**: Remove lock file: `rm -f graphrag/qdrant_data/.lock`

**Issue**: Qdrant data not found
- **Solution**: Run `graphrag/graph_rag_updated2.ipynb` to generate the knowledge base

**Issue**: Ollama not running
- **Solution**: 
  ```bash
  ollama serve
  # In another terminal
  ollama pull llama3
  ```

**Issue**: Import errors or missing dependencies
- **Solution**: 
  ```bash
  conda activate graph_rag
  pip install -r requirements.txt --force-reinstall
  ```

### Extension Issues

**Issue**: "Generate Reply" button doesn't appear
- Refresh Gmail page (F5 or Cmd+R)
- Check browser console (F12) for errors
- Ensure extension is enabled in `chrome://extensions/`
- Make sure you clicked "Reply" first (reply box must be open)
- Wait 2-3 seconds (button appears periodically)

**Issue**: "Backend offline" in popup
- Verify backend is running: `curl http://localhost:8001/api/health` (or your backend port)
- Check API URL in extension settings matches your backend port
- Check browser console for CORS errors

**Issue**: Button appears but nothing happens
- Open browser console (F12)
- Check for error messages
- Verify reply box is open

**Issue**: Content script not loading
1. Go to `chrome://extensions/`
2. Find "Graph RAG Email Assistant"
3. Click "Reload" (🔄) icon
4. Refresh Gmail page

### Generation Issues

**Issue**: Low confidence scores
- Your query might not match FAQ/graph well
- Add more relevant FAQ entries in `data/faq_updated.csv`
- Build richer graph from more labeled emails

**Issue**: Generated replies are generic
- Improve prompt in `backend/services/ollama_service.py`
- Add more contextual FAQ entries
- Increase `TOP_K_RESULTS` in config

**Issue**: Slow generation
- Try smaller model: `ollama pull llama3.2:1b`
- Update config to use smaller model
- Check CPU/GPU usage

## 📊 How It Works

### Retrieval Flow

1. **Intent Classification**: LLM classifies multiple intents from email (JSON array format)
2. **FAQ Search**: Separate filtered search in `knowledge_space` collection (always retrieves FAQs)
3. **Graph Retrieval**: Intent-based lookup in NetworkX graph (direct node matching)
4. **Style Retrieval**: Semantic search in `writing_style` collection for tone matching
5. **Reply Generation**: LLM generates reply using all context + style examples

### Key Improvements

-  **Better FAQ Retrieval**: Separate search ensures FAQs are always retrieved
-  **Intent-based Graph**: Direct graph lookup is more reliable than vector search
-  **Style Matching**: Gmail-style approach matches writing tone from historical replies
-  **Multi-intent Support**: Can handle emails with multiple intents

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────┐
│   Gmail/Outlook (Chrome Extension)  │
│   ├─ Email Extraction               │
│   ├─ UI Integration                 │
│   └─ Reply Display                  │
└─────────────────────────────────────┘
                 ↕ HTTP API
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
│   ├─ Intent/Artifact Classification │
│   ├─ Qdrant (Vector Search)         │
│   │   ├─ knowledge_space (FAQs)     │
│   │   └─ writing_style (Style)      │
│   ├─ NetworkX (Graph Retrieval)     │
│   └─ Gemini/Ollama (Generation)     │
└─────────────────────────────────────┘
```

### Components

1. **Chrome Extension**: Gmail and Outlook integration for email extraction and reply display
2. **FastAPI Backend**: Main orchestration service
3. **Qdrant**: Vector database for semantic search
4. **NetworkX**: Knowledge graph for structured retrieval
5. **Gemini/Ollama**: LLM for classification and generation

### Key Features

#### 1. Interchangeable Artifacts and Intents

The system recognizes that certain artifacts and intents are functionally equivalent:
- **Artifacts**: `zoom_link` ↔ `calendly`, `report` ↔ `draft`
- **Intents**: `reschedule` ↔ `schedule`

This improves evaluation accuracy and reflects real-world usage patterns.

#### 2. Graph RAG Retrieval

- **Intent-based Graph Lookup**: Direct NetworkX graph traversal for structured retrieval
- **FAQ Search**: Separate filtered search ensures FAQs are always retrieved
- **Style Matching**: Semantic search in writing style collection for tone matching

#### 3. Multi-Intent Support

The system can handle emails with multiple intents simultaneously, improving context understanding.

#### 4. Rate Limiting

Built-in rate limiting (15 req/min) for Gemini API ensures compliance with API quotas and prevents errors.

---

## 📈 Evaluation Results

The system has been evaluated on a benchmark dataset of 20 carefully curated emails covering multiple scenarios including academic/professor communications, recruiter/job search interactions, group/event coordination, feedback/reviews, and scheduling requests.

### Aggregate Performance Summary

![Aggregate Metrics](eval/results/plots/aggregate_metrics.png)

#### Key Highlights

- **Artifact Hit Rate F1**: **0.883** (88.3%)
  - Precision: 1.000 (100%)
  - Recall: 0.875 (87.5%)
  - Exact Match: 0.850 (85%)

- **Intent Hit Rate F1**: **0.908** (90.8%)
  - Precision: 0.900 (90%)
  - Recall: 0.925 (92.5%)
  - Exact Match: 0.850 (85%)

- **ROUGE-L Score**: **0.414** (41.4%)
  - ROUGE-1: 0.517 (51.7%)
  - ROUGE-2: 0.303 (30.3%)
  
  **Note**: For email generation (not summarization), ROUGE scores are typically lower because there are many valid ways to phrase the same response. The system generates paraphrased responses rather than copying reference text, which is appropriate for personalized email generation.

- **ExPerT Overall**: **0.562** (56.2%)
  - Semantic: 0.710 (71.0%)
  - Style: 0.339 (33.9%)

- **LLM-as-a-Judge Average**: **4.09/5.0** (81.8%)

### Performance Analysis

**Strengths:**
1. **Excellent Artifact Detection** (F1: 0.883) - Perfect precision with high recall
2. **Strong Intent Classification** (F1: 0.908) - High precision and recall
3. **Good Style Matching** (LLM Judge: 4.09/5.0) - Consistent high scores
4. **Semantic Similarity** (ExPerT Semantic: 0.710) - Good understanding of email context

**Areas for Improvement:**
1. **Style Matching** (ExPerT Style: 0.339) - Could benefit from more style examples
2. **Exact Word Matching** (ROUGE-L: 0.414) - Expected for generation tasks with multiple valid phrasings

For detailed evaluation methodology, metrics explanation, and complete results, see the [Evaluation Documentation](eval/EVAL_DOCUMENTATION.md) and [Evaluation Results](eval/EVALUATION_RESULTS_FINAL.md).

---

## 🔧 Technical Implementation

### Technology Stack

- **Backend**: FastAPI (Python)
- **Vector Database**: Qdrant
- **Graph Database**: NetworkX
- **LLM**: Google Gemini 2.0 Flash / Ollama (Llama 3)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Frontend**: Chrome Extension (JavaScript)

### Key Services

1. **RAGService**: Main orchestration service
   - Intent/artifact classification
   - Multi-source retrieval (FAQ, Graph, Style)
   - Reply generation

2. **GeminiService/OllamaService**: LLM interface
   - Intent and artifact classification
   - Reply generation
   - Rate limiting

3. **GraphService**: Knowledge graph management
   - Graph construction from email pairs
   - Intent-based node retrieval
   - Graph expansion for context

4. **QdrantService**: Vector search
   - FAQ retrieval
   - Style matching
   - Semantic search

5. **CacheService**: Performance optimization
   - TTL-based caching for embeddings
   - FAQ search caching

For comprehensive technical details, component mapping, and testing information, see the [Tutorial Guide](tutorial.md).

##  Architecture

```
┌─────────────────────────────────────┐
│   Gmail (Chrome Browser)            │
│   ├─ content.js (extract email)     │
│   ├─ background.js (communication)  │
│   └─ popup.html/js (settings)       │
└─────────────────────────────────────┘
                 ↕ HTTP
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
│   ├─ Intent Classification (Ollama) │
│   ├─ Qdrant (Vector Search)         │
│   │   ├─ knowledge_space (FAQs)     │
│   │   └─ writing_style (Style)      │
│   ├─ NetworkX (Graph Retrieval)     │
│   └─ Ollama (Draft Generation)      │
└─────────────────────────────────────┘
```

##  Project Structure

```
RAG/
├── backend/                    # FastAPI backend
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── embedding_service.py
│   │   ├── qdrant_service.py
│   │   ├── graph_service.py
│   │   ├── ollama_service.py
│   │   └── rag_service.py     # Main orchestration
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── config.py              # Configuration
│   ├── main.py                # FastAPI app
│   └── requirements.txt
├── chrome-extension/          # Chrome extension
│   ├── manifest.json
│   ├── content.js            # Gmail integration
│   ├── background.js         # Service worker
│   ├── popup.html/js         # Settings UI
│   └── styles/
├── graphrag/
│   ├── graph_rag_updated2.ipynb  # Main notebook
│   └── qdrant_data/          # Qdrant database
├── data/
│   ├── faq_updated.csv       # FAQ data
│   └── generated_email_pairs.json  # Labeled emails
└── README.md                 # This file
```

##  Privacy & Security

-  All data processing happens **locally**
-  No third-party API calls (except your own backend)
-  No email content is stored permanently
-  Ollama runs locally (no data sent to cloud)
-  Backend runs on localhost (not accessible from internet)

##  Development

### Backend Development

```bash
# Run with auto-reload
cd .
python -m uvicorn backend.main:app --reload
```

### Extension Development

After making changes:
1. Go to `chrome://extensions/`
2. Click the refresh icon on your extension
3. Reload Gmail page

### Testing

The project includes comprehensive unit and integration tests:

```bash
# Run all tests
pytest

# Or use the test runner script
./run_tests.sh

# Run specific test suites
./run_tests.sh unit          # Unit tests only
./run_tests.sh integration    # Integration tests only
./run_tests.sh coverage       # With coverage report
```

**Test Structure**:
- `backend/tests/unit/` - Unit tests for individual services
- `backend/tests/integration/` - Integration tests for full pipeline
- `pytest.ini` - Test configuration with coverage settings

For complete component mapping, test details, and extensive project information, see the **[Tutorial Guide](tutorial.md)**.

### API Testing

```bash
# Test health endpoint
curl http://localhost:8001/api/health

# Test reply generation
curl -X POST http://localhost:8001/api/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Subject",
    "sender": "test@example.com",
    "body": "Can we schedule a meeting?"
  }'
```

##  Documentation

- **[README.md](README.md)** - This file - Installation, usage, architecture, and evaluation results
- **[tutorial.md](tutorial.md)** - Complete tutorial guide with component mapping, testing, and extensive project information
- **[chrome-extension-v2/README.md](chrome-extension-v2/README.md)** - Chrome extension documentation
- **[chrome-extension-v2/INSTALL.md](chrome-extension-v2/INSTALL.md)** - Quick installation guide
- **[eval/EVAL_DOCUMENTATION.md](eval/EVAL_DOCUMENTATION.md)** - Comprehensive evaluation pipeline guide
- **[eval/EVALUATION_RESULTS_FINAL.md](eval/EVALUATION_RESULTS_FINAL.md)** - Detailed evaluation results

### 📚 Need More Information?

- **For complete component mapping and where everything is located**: See [tutorial.md](tutorial.md)
- **For testing details and examples**: See [tutorial.md](tutorial.md#unit-tests-and-error-handling)
- **For evaluation methodology**: See [eval/EVAL_DOCUMENTATION.md](eval/EVAL_DOCUMENTATION.md)
- **For extension setup**: See [chrome-extension-v2/INSTALL.md](chrome-extension-v2/INSTALL.md)

## 🚀 Future Improvements

### Short-term
1. **Style Matching Enhancement** - Increase style examples in training data
2. **Content Generation** - Better phrase matching and context-aware generation
3. **Error Handling** - Better fallback mechanisms and graceful degradation

### Long-term
1. **Multi-user Support** - Per-user style profiles and personalized training
2. **Advanced Features** - Multi-language support, email thread context, sentiment analysis
3. **Performance Optimization** - Enhanced caching, batch processing, async improvements

##  Next Steps

1. **Test with Real Emails**: Try generating replies for various email types
2. **Customize Prompts**: Edit `backend/services/ollama_service.py` to match your style
3. **Expand Knowledge Base**: Add more FAQs and labeled emails
4. **Update Notebook**: Run `graphrag_local/graph_rag_updated2.ipynb` when you have new data
5. **Run Tests**: Execute `./run_tests.sh` to verify everything works
6. **Explore Tutorial**: Check [tutorial.md](tutorial.md) for comprehensive project information

---

**Last Updated**: December 2025  
**Version**: 1.0  
**Evaluation Dataset**: 20 emails from golden benchmark

