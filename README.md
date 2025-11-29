# Graph RAG Email Assistant

AI-powered email reply generator for Gmail using Graph RAG (Retrieval-Augmented Generation) with local LLM. Generates personalized email replies based on your historical email patterns and writing style.

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
   cd /Users/iramkamdar/RAG
   ```

2. **Create and activate conda environment**:
   ```bash
   conda create -n graph_rag python=3.10 -y
   conda activate graph_rag
   ```

3. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Start the backend server**:
   ```bash
   # From project root (not inside backend/)
   python -m uvicorn backend.main:app --reload
   ```
   
   You should see:
   ```
   INFO: Starting Graph RAG Email Assistant API...
   INFO: All services initialized successfully!
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

5. **Test the backend** (in a new terminal):
   ```bash
   curl http://localhost:8000/api/health
   ```

### Step 3: Install Chrome Extension

1. **Open Chrome** and navigate to `chrome://extensions/`

2. **Enable "Developer mode"** (toggle in top-right corner)

3. **Click "Load unpacked"**

4. **Navigate to and select** the `chrome-extension` folder:
   ```
   /Users/iramkamdar/RAG/chrome-extension
   ```

5. **The extension should now appear** in your extensions list

6. **Pin the extension** to your toolbar for easy access

### Step 4: Configure Extension

1. **Click the extension icon** in Chrome toolbar

2. **Verify settings**:
   - API URL: `http://localhost:8000/api` (default)
   - Confidence Threshold: `0.85` (adjust as needed)
   - Auto-insert drafts: ✓ (checked)

3. **Click "Test Connection"** to verify backend is running

4. **You should see** "Backend online and healthy" 

##  Usage

### Generating Email Replies

1. **Open Gmail** (https://mail.google.com)

2. **Open an email** you want to reply to

3. **Click the Reply button** in Gmail

4. **Look for the " Generate Reply" button** near the reply box

5. **Click " Generate Reply"**
   - The extension will extract the email content
   - Send it to your local backend
   - Generate a contextual reply using:
     - FAQ matches for content
     - Graph nodes for relationships
     - Style examples for tone matching
   - Insert it into the reply box

6. **Review and edit** the generated draft as needed

7. **Send** when satisfied!

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
  cd /Users/iramkamdar/RAG
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
  pip install -r backend/requirements.txt --force-reinstall
  ```

### Extension Issues

**Issue**: "Generate Reply" button doesn't appear
- Refresh Gmail page (F5 or Cmd+R)
- Check browser console (F12) for errors
- Ensure extension is enabled in `chrome://extensions/`
- Make sure you clicked "Reply" first (reply box must be open)
- Wait 2-3 seconds (button appears periodically)

**Issue**: "Backend offline" in popup
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check API URL in extension settings
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
cd /Users/iramkamdar/RAG
python -m uvicorn backend.main:app --reload
```

### Extension Development

After making changes:
1. Go to `chrome://extensions/`
2. Click the refresh icon on your extension
3. Reload Gmail page

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test reply generation
curl -X POST http://localhost:8000/api/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Subject",
    "sender": "test@example.com",
    "body": "Can we schedule a meeting?"
  }'
```

##  Next Steps

1. **Test with Real Emails**: Try generating replies for various email types
2. **Customize Prompts**: Edit `backend/services/ollama_service.py` to match your style
3. **Expand Knowledge Base**: Add more FAQs and labeled emails
4. **Update Notebook**: Run `graphrag/graph_rag_updated2.ipynb` when you have new data

---

