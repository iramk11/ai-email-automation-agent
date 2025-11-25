# Graph RAG Email Assistant - Chrome Extension

AI-powered email reply generator for Gmail using Graph RAG (Retrieval-Augmented Generation) with local LLM.

## 🚀 Features

- **Smart Email Understanding**: Extracts context from your emails using hybrid retrieval (vector + graph)
- **AI-Powered Replies**: Generates contextual drafts using local Llama 3 model via Ollama
- **Privacy First**: All processing happens locally - no data sent to third parties
- **One-Click Generation**: Simple button in Gmail to generate replies
- **Confidence Scoring**: Shows how confident the AI is about the reply
- **Customizable**: Adjust confidence thresholds and settings

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.10+**
2. **Ollama** with Llama 3 model
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3
   ```
3. **Conda** (recommended) or Python venv
4. **Chrome Browser**

## 🛠️ Installation

### Step 1: Set Up Backend

1. **Navigate to the RAG directory**:
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

4. **Ensure your knowledge base is ready**:
   - Make sure `qdrant_data/` directory exists (should be there from your notebook)
   - Optionally create `graph_data.gpickle` by running your notebook once
   - The backend will work with your existing FAQ and graph data

5. **Start the backend server**:
   ```bash
   cd /Users/iramkamdar/RAG
   python -m backend.main
   ```
   
   You should see:
   ```
   INFO: Starting Graph RAG Email Assistant API...
   INFO: All services initialized successfully!
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

6. **Test the backend** (in a new terminal):
   ```bash
   curl http://localhost:8000/api/health
   ```

### Step 2: Install Chrome Extension

1. **Open Chrome** and navigate to `chrome://extensions/`

2. **Enable "Developer mode"** (toggle in top-right corner)

3. **Click "Load unpacked"**

4. **Navigate to and select** the `chrome-extension` folder:
   ```
   /Users/iramkamdar/RAG/chrome-extension
   ```

5. **The extension should now appear** in your extensions list

6. **Pin the extension** to your toolbar for easy access (click the puzzle icon, then pin)

### Step 3: Configure Extension

1. **Click the extension icon** in Chrome toolbar

2. **Verify settings**:
   - API URL: `http://localhost:8000/api` (default)
   - Confidence Threshold: `0.85` (adjust as needed)
   - Auto-insert drafts: ✓ (checked)

3. **Click "Test Connection"** to verify backend is running

4. **You should see** "Backend online and healthy" ✅

## 📧 Usage

### Generating Email Replies

1. **Open Gmail** (https://mail.google.com)

2. **Open an email** you want to reply to

3. **Click the Reply button** in Gmail

4. **Look for the "🤖 Generate Reply" button** near the reply box

5. **Click "🤖 Generate Reply"**
   - The extension will extract the email content
   - Send it to your local backend
   - Generate a contextual reply
   - Insert it into the reply box

6. **Review and edit** the generated draft as needed

7. **Send** when satisfied!

### Extension Popup

Click the extension icon to:
- View backend status
- Adjust settings
- Test connection
- See version info

## 🔧 Configuration

### Backend Configuration

Edit `backend/config.py` to customize:

```python
# RAG settings
TOP_K_RESULTS = 6  # Number of context items to retrieve
AUTO_SEND_THRESHOLD = 0.85  # Confidence for auto-send suggestion
MAX_REPLY_LENGTH = 120  # Max words in reply

# User personalization
DEFAULT_USER_NAME = "Assistant"  # Change to your name
DEFAULT_USER_TONE = "polite, proactive, and professional"
```

### Extension Settings

In the extension popup:
- **API URL**: Change if backend runs on different port
- **Confidence Threshold**: Higher = more conservative (only high-confidence replies)
- **Auto-insert**: Enable/disable automatic draft insertion

## 🏗️ Architecture

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
│   ├─ Intent Classification          │
│   ├─ Qdrant (Vector Search)         │
│   ├─ NetworkX (Graph Expansion)     │
│   └─ Ollama (Draft Generation)      │
└─────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Backend Won't Start

**Issue**: Import errors or missing dependencies
```bash
# Solution: Reinstall dependencies
conda activate graph_rag
pip install -r backend/requirements.txt --force-reinstall
```

**Issue**: Qdrant data not found
```bash
# Solution: Make sure qdrant_data exists
ls qdrant_data/
# If missing, run your notebook cells to generate it
```

**Issue**: Ollama not running
```bash
# Solution: Start Ollama
ollama serve
# In another terminal
ollama pull llama3
```

### Extension Issues

**Issue**: "Generate Reply" button doesn't appear
- Refresh Gmail page (F5 or Cmd+R)
- Check browser console (F12) for errors
- Ensure extension is enabled in chrome://extensions/

**Issue**: "Backend offline" in popup
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check API URL in extension settings
- Check browser console for CORS errors

**Issue**: Button appears but nothing happens
- Open browser console (F12)
- Check for error messages
- Verify you've clicked Reply first (reply box must be open)

### Generation Issues

**Issue**: Low confidence scores
- Your query might not match FAQ/graph well
- Add more relevant FAQ entries
- Build richer graph from more labeled emails

**Issue**: Generated replies are generic
- Improve prompt in `backend/services/ollama_service.py`
- Add more contextual FAQ entries
- Increase TOP_K_RESULTS in config

**Issue**: Slow generation
- Try smaller model: `ollama pull llama3.2:1b`
- Update config to use smaller model
- Check CPU/GPU usage

## 📝 Development

### Backend Development

```bash
# Run with auto-reload
cd /Users/iramkamdar/RAG
python -m backend.main
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

## 🔒 Privacy & Security

- ✅ All data processing happens **locally**
- ✅ No third-party API calls (except your own backend)
- ✅ No email content is stored permanently
- ✅ Ollama runs locally (no data sent to cloud)
- ⚠️ Backend runs on localhost (not accessible from internet)

## 📦 Project Structure

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
├── qdrant_data/              # Vector database
├── graph_rag_updated.ipynb   # Original notebook
└── README_CHROME_EXTENSION.md
```

## 🚀 Next Steps

1. **Test with Real Emails**: Try generating replies for various email types
2. **Customize Prompts**: Edit `ollama_service.py` to match your style
3. **Expand Knowledge Base**: Add more FAQs and labeled emails
4. **Deploy Backend** (optional): Host on a server for team use
5. **Publish Extension** (optional): Submit to Chrome Web Store

## 🤝 Contributing

This is your personal project, but you can:
- Add more features (tone selection, templates, etc.)
- Improve error handling
- Add analytics/logging
- Create tests

## 📄 License

Personal project - use as you wish!

## 🙋 Support

If you encounter issues:
1. Check this README's troubleshooting section
2. Check browser console for errors (F12)
3. Check backend logs in terminal
4. Review `CHROME_EXTENSION_RESEARCH.md` for detailed architecture

---

**Enjoy your AI-powered email assistant! 🎉**

