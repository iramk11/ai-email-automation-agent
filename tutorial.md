# Complete Tutorial: Getting Started with AI Email Automation Agent

Welcome! This tutorial will guide you through setting up and using the AI Email Automation Agent from scratch. By the end, you'll have a fully functional system that generates intelligent email replies using your own data and writing style.

---

## 📋 Table of Contents

1. [What You'll Build](#what-youll-build)
2. [Prerequisites](#prerequisites)
3. [Step 1: Install System Dependencies](#step-1-install-system-dependencies)
4. [Step 2: Set Up Knowledge Base](#step-2-set-up-knowledge-base)
5. [Step 3: Set Up Backend](#step-3-set-up-backend)
6. [Step 4: Install Chrome Extension](#step-4-install-chrome-extension)
7. [Step 5: Generate Your First Reply](#step-5-generate-your-first-reply)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## What You'll Build

You'll create an AI-powered email assistant that:

- **Understands context** from your email history using Graph RAG
- **Generates personalized replies** matching your writing style
- **Works with Gmail and Outlook** via a Chrome extension
- **Runs completely locally** - your data never leaves your machine
- **Learns from your FAQs** and email patterns

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10 or higher** installed
- **Chrome browser** (latest version)
- **Git** (to clone the repository)
- **8GB+ RAM** (for running Ollama and Qdrant)
- **Basic command-line knowledge**

---

## Step 1: Install System Dependencies

### 1.1 Install Ollama

Ollama is the local LLM runtime that powers the AI reply generation.

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from [ollama.ai](https://ollama.ai) and run it.

**Verify installation:**
```bash
ollama --version
```

### 1.2 Download Llama 3 Model

The system uses Llama 3 for generating replies. Download it:

```bash
ollama pull llama3
```

This may take several minutes depending on your internet connection (~4.7GB download).

**Verify the model:**
```bash
ollama list
```

You should see `llama3` in the list.

### 1.3 Install Qdrant (Vector Database)

Qdrant stores embeddings for semantic search. Install it:

**macOS (using Homebrew):**
```bash
brew install qdrant
```

**Linux:**
```bash
curl -fsSL https://get.qdrant.io/install.sh | sh
```

**Windows:**
Download from [qdrant.io](https://qdrant.io/documentation/guides/installation/) or use Docker:
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 qdrant/qdrant
```

**Start Qdrant:**
```bash
qdrant
```

Keep this running in a terminal. Qdrant will be available at `http://localhost:6333`.

---

## Step 2: Set Up Knowledge Base

The knowledge base is built from your email data and FAQs. This step creates the graph structure and vector embeddings.

### 2.1 Prepare Your Data

Ensure you have the required data files:

- `data/faq_updated.csv` - Your FAQ data
- `data/generated_email_pairs.json` - Labeled email pairs

If you don't have these files, the notebook will create sample data structures.

### 2.2 Build the Knowledge Base

1. **Open Jupyter Notebook:**

```bash
# Install Jupyter if you haven't already
pip install jupyter

# Start Jupyter
jupyter notebook
```

2. **Navigate to the notebook:**

Open `graphrag_local/graph_rag_updated2.ipynb` in your browser.

3. **Run all cells:**

Click **Cell → Run All** or press `Shift + Enter` through each cell.

**What happens:**

- ✅ Loads FAQ data from CSV
- ✅ Loads email pairs from JSON
- ✅ Creates NetworkX knowledge graph with:
  - Topics (email subjects/themes)
  - Intents (what the email is asking for)
  - Artifacts (specific information mentioned)
- ✅ Creates Qdrant collections:
  - `knowledge_space`: FAQs and graph node embeddings
  - `writing_style`: Your reply examples for style matching
- ✅ Generates embeddings and indexes everything

**Expected output:**

You should see progress messages like:
```
Loading FAQs...
Building graph...
Creating Qdrant collections...
Indexing data...
✅ Knowledge base ready!
```

4. **Important:** Close the notebook before proceeding (Qdrant locks the database when notebooks are open).

---

## Step 3: Set Up Backend

The backend is a FastAPI server that handles email processing and reply generation.

### 3.1 Clone and Navigate to Project

```bash
git clone <your-repo-url>
cd ai-automation-agent
```

### 3.2 Create Virtual Environment

**Option A: Using Python venv (Recommended)**

```bash
python3 -m venv email-agent
source email-agent/bin/activate  # macOS/Linux
# OR
email-agent\Scripts\activate    # Windows
```

**Option B: Using Conda**

```bash
conda create -n graph_rag python=3.10 -y
conda activate graph_rag
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn (web server)
- Qdrant client (vector database)
- NetworkX (graph operations)
- Sentence-transformers (embeddings)
- Ollama Python client
- And other dependencies

**Verify installation:**
```bash
pip list | grep fastapi
```

### 3.4 Configure Backend

Edit `backend/config.py` if needed:

```python
# Default settings (usually work out of the box)
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
OLLAMA_BASE_URL = "http://localhost:11434"
```

### 3.5 Start Backend Server

**Option A: Using the startup script (Recommended)**

```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Option B: Manual start**

```bash
source email-agent/bin/activate  # Activate venv first
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

**Success indicators:**

You should see:
```
INFO:     Starting Graph RAG Email Assistant API...
INFO:     All services initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

### 3.6 Test Backend

Open a new terminal and test:

```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{"status":"healthy","services":{"ollama":true,"qdrant":true}}
```

If you see errors, check the [Troubleshooting](#troubleshooting) section.

---

## Step 4: Install Chrome Extension

The Chrome extension adds the "Generate Reply" button to Gmail and Outlook.

### 4.1 Load Extension

1. **Open Chrome Extensions:**

Navigate to `chrome://extensions/` in your browser.

2. **Enable Developer Mode:**

Toggle the switch in the top-right corner.

3. **Load Extension:**

- Click **"Load unpacked"**
- Navigate to your project directory
- Select the `chrome-extension-v2` folder
- Click **"Select"**

4. **Verify Installation:**

You should see the extension appear with a 📧 icon.

### 4.2 Configure Extension

1. **Click the extension icon** in Chrome's toolbar.

2. **Set API URL:**

Ensure it's set to: `http://localhost:8001/api`

3. **Test Connection:**

Click **"Test Connection"** button.

**Success:** You should see "✅ Backend online and healthy"

**If connection fails:**
- Verify backend is running (Step 3.5)
- Check the API URL matches your backend port
- Check browser console (F12) for errors

### 4.3 Grant Permissions

The extension needs permission to:
- Access Gmail and Outlook pages
- Send requests to your local backend

These permissions are automatically requested when you load the extension.

---

## Step 5: Generate Your First Reply

Now for the fun part - generating your first AI-powered email reply!

### 5.1 Using Gmail

1. **Open Gmail:**

Go to [mail.google.com](https://mail.google.com)

2. **Open an Email:**

Click on any email in your inbox.

3. **Click Reply:**

Click the **"Reply"** button in Gmail.

4. **Find the Generate Button:**

Look for the **"🤖 Generate Reply"** button near the reply box. It appears automatically after a few seconds.

5. **Generate Reply:**

Click **"🤖 Generate Reply"**

**What happens:**
- Extension extracts email content
- Sends to backend for processing
- Backend:
  - Classifies intent and artifacts
  - Searches FAQs for relevant content
  - Retrieves graph context
  - Finds style examples matching your writing
  - Generates reply using Llama 3
- Reply appears in the text box

6. **Review and Edit:**

The generated reply includes:
- Contextual information from FAQs
- Your writing style
- Relevant graph relationships

Edit as needed, then send!

### 5.2 Using Outlook

1. **Open Outlook:**

Go to [outlook.live.com](https://outlook.live.com) or [outlook.office.com](https://outlook.office.com)

2. **Follow the same steps** as Gmail (open email → Reply → Generate)

The extension works identically for both email providers.

### 5.3 Understanding the Generated Reply

The system uses:

- **FAQ Matches:** Relevant information from your knowledge base
- **Graph Context:** Related topics and relationships
- **Style Examples:** Your previous replies for tone matching
- **Intent Classification:** Understanding what the email is asking for

You'll see a confidence score indicating how well the system understood the context.

---

## Troubleshooting

### Backend Won't Start

**Problem:** Backend fails to start or shows errors.

**Solutions:**

1. **Check Ollama is running:**
```bash
ollama list
# If empty, start Ollama:
ollama serve
```

2. **Check Qdrant is running:**
```bash
curl http://localhost:6333/health
# If fails, start Qdrant:
qdrant
```

3. **Check Python version:**
```bash
python3 --version  # Should be 3.10+
```

4. **Reinstall dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

5. **Check port availability:**
```bash
# macOS/Linux
lsof -i :8001
# Windows
netstat -ano | findstr :8001
```

### Extension Button Not Appearing

**Problem:** "Generate Reply" button doesn't show up.

**Solutions:**

1. **Refresh the page:**
   - Press `Cmd/Ctrl + R` to reload Gmail/Outlook

2. **Check extension is enabled:**
   - Go to `chrome://extensions/`
   - Ensure extension is enabled (toggle ON)

3. **Check browser console:**
   - Press `F12` to open DevTools
   - Look for errors in Console tab
   - Common issues: CORS errors, connection failures

4. **Verify backend connection:**
   - Click extension icon
   - Test connection
   - Ensure backend is running

5. **Wait a few seconds:**
   - Button appears after page loads
   - May take 2-3 seconds

### Low Quality Replies

**Problem:** Generated replies don't make sense or are generic.

**Solutions:**

1. **Check knowledge base:**
   - Ensure Step 2 completed successfully
   - Verify Qdrant has data:
   ```bash
   curl http://localhost:6333/collections
   ```

2. **Check FAQ data:**
   - Ensure `data/faq_updated.csv` has relevant FAQs
   - More FAQs = better context

3. **Check email pairs:**
   - Ensure `data/generated_email_pairs.json` has examples
   - More examples = better style matching

4. **Adjust confidence threshold:**
   - Edit `backend/config.py`
   - Lower thresholds for more aggressive retrieval

### Qdrant Database Lock

**Problem:** "Database is locked" error.

**Solutions:**

1. **Close Jupyter notebooks:**
   - Notebooks lock Qdrant when open
   - Close all notebooks before starting backend

2. **Restart Qdrant:**
```bash
# Stop Qdrant (Ctrl+C)
# Start again:
qdrant
```

### Ollama Connection Errors

**Problem:** "Cannot connect to Ollama" errors.

**Solutions:**

1. **Verify Ollama is running:**
```bash
ollama list
```

2. **Check Ollama URL:**
   - Default: `http://localhost:11434`
   - Verify in `backend/config.py`

3. **Restart Ollama:**
```bash
# Stop Ollama (Ctrl+C)
ollama serve
```

---

## Next Steps

Congratulations! You've successfully set up the AI Email Automation Agent. Here's what to explore next:

### Customization

1. **Add More FAQs:**
   - Edit `data/faq_updated.csv`
   - Rebuild knowledge base (Step 2)

2. **Add Email Examples:**
   - Add more pairs to `data/generated_email_pairs.json`
   - Improves style matching

3. **Adjust Configuration:**
   - Edit `backend/config.py` for:
     - Retrieval parameters
     - Confidence thresholds
     - Model settings

### Advanced Usage

1. **Run Evaluations:**
   - See `eval/README.md` for evaluation pipeline
   - Test system performance on your data

2. **Modify Prompts:**
   - Edit prompts in `backend/services/ollama_service.py`
   - Customize reply generation style

3. **Add New Intents:**
   - Update `KNOWN_INTENTS` in `backend/config.py`
   - Retrain knowledge base

### Development

1. **Run Tests:**
```bash
pytest
# Or with coverage:
pytest --cov=backend --cov-report=html
```

2. **API Documentation:**
   - Visit `http://localhost:8001/docs` when backend is running
   - Interactive API documentation

3. **Check Logs:**
   - Backend logs show detailed processing
   - Useful for debugging

---

## Getting Help

If you encounter issues not covered here:

1. **Check the main README:** `README.md` has detailed documentation
2. **Review extension docs:** `chrome-extension-v2/README.md`
3. **Check evaluation docs:** `eval/README.md`
4. **Browser console:** Press F12 for detailed error messages
5. **Backend logs:** Check terminal where backend is running

---

**Happy emailing! 🚀**
