# 🚀 Graph RAG Email Assistant - Complete Setup Instructions

## ✅ What You Have

A complete Chrome extension with FastAPI backend that generates AI-powered email replies using:
- 🤖 **Local LLM** (Ollama Llama3)
- 🔍 **Vector Search** (Qdrant)  
- 🕸️ **Graph RAG** (NetworkX)
- ✉️ **Gmail Integration** (Chrome Extension)

---

## 📋 Prerequisites

### 1. Install Ollama & Pull Model
```bash
# Install Ollama from https://ollama.ai
# Then pull the model:
ollama pull llama3
```

### 2. Verify Python Environment
```bash
# Check Python version (need 3.10+)
python --version

# You should already have conda
conda --version
```

### 3. Verify Knowledge Base Exists
```bash
# Make sure your notebook has generated these:
ls /Users/iramkamdar/RAG/qdrant_data/
# Should show: collection/, meta.json

ls /Users/iramkamdar/RAG/faq.csv
# Should exist
```

---

## 🎯 Setup (Choose One Method)

### Method A: Quick Setup (Recommended) ⚡

```bash
# 1. Navigate to project
cd /Users/iramkamdar/RAG

# 2. Create environment & install dependencies
conda create -n graph_rag python=3.10 -y
conda activate graph_rag
pip install -r backend/requirements.txt

# 3. Start Ollama (in separate terminal)
ollama serve

# 4. Start backend
./start_backend.sh
# OR manually: python -m backend.main
```

### Method B: Step-by-Step Setup 📝

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Setup & Start Backend:**
```bash
# Navigate to project
cd /Users/iramkamdar/RAG

# Create conda environment
conda create -n graph_rag python=3.10 -y

# Activate environment
conda activate graph_rag

# Install dependencies
pip install -r backend/requirements.txt

# Start backend
python -m backend.main
```

**Expected Output:**
```
INFO: Starting Graph RAG Email Assistant API...
INFO: Loaded embedding model: all-MiniLM-L6-v2
INFO: Connected to Qdrant at /Users/iramkamdar/RAG/qdrant_data
INFO: Loaded graph with X nodes, Y edges
INFO: Initialized Ollama service with model: llama3
INFO: All services initialized successfully!
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Test Backend

**Terminal 3 - Run Tests:**
```bash
cd /Users/iramkamdar/RAG
conda activate graph_rag

# Method 1: Automated test suite
python test_backend.py

# Method 2: Manual health check
curl http://localhost:8000/api/health

# Method 3: Manual reply generation
curl -X POST http://localhost:8000/api/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Meeting Request",
    "sender": "test@university.edu",
    "body": "Can we schedule a meeting to discuss the project?"
  }'
```

**✅ Success Indicators:**
- Health check returns `{"status": "healthy", ...}`
- Reply generation completes in 5-30 seconds
- Draft reply is contextually relevant

---

## 🔌 Install Chrome Extension

### Step 1: Load Extension

1. **Open Chrome** → Navigate to `chrome://extensions/`

2. **Enable Developer Mode** (toggle in top-right corner)

3. **Click "Load unpacked"**

4. **Select folder:**
   ```
   /Users/iramkamdar/RAG/chrome-extension
   ```

5. **Extension loads** with "Graph RAG Email Assistant" name

6. **Pin extension** to toolbar (click puzzle icon → pin)

### Step 2: Configure Extension

1. **Click extension icon** (🤖) in Chrome toolbar

2. **Verify settings:**
   - API URL: `http://localhost:8000/api` ✓
   - Confidence Threshold: `0.85` ✓
   - Auto-insert drafts: ☑ Checked

3. **Click "Test Connection"**

4. **Should see:** "✅ Backend online and healthy"

---

## 📧 Use in Gmail

### Step 1: Open Gmail
```
https://mail.google.com
```

### Step 2: Test Extension

1. **Open any email** in your inbox

2. **Click the "Reply" button** (standard Gmail button)

3. **Wait 2-3 seconds** for the "🤖 Generate Reply" button to appear

4. **Click "🤖 Generate Reply"**

5. **Watch the magic:**
   - Button shows "⏳ Generating..."
   - Backend processes the email
   - Draft appears in reply box
   - Notification shows confidence score

6. **Review and edit** the draft as needed

7. **Send!** 🚀

---

## 🐛 Troubleshooting

### Backend Issues

| Problem | Solution |
|---------|----------|
| `ImportError` or module not found | `pip install -r backend/requirements.txt --force-reinstall` |
| Ollama connection error | Start Ollama: `ollama serve` in separate terminal |
| `qdrant_data not found` | Run your notebook first to generate knowledge base |
| Port 8000 already in use | Kill process: `lsof -ti:8000 \| xargs kill -9` |
| Slow/timeout responses | Check Ollama is running, try smaller model: `ollama pull llama3.2:1b` |

### Extension Issues

| Problem | Solution |
|---------|----------|
| Button not appearing | Refresh Gmail (Cmd/Ctrl+R), wait 2-3 seconds |
| "Backend offline" | Verify backend running: `curl http://localhost:8000/api/health` |
| Extension won't load | Check chrome://extensions/ for errors, reload extension |
| Draft not inserting | Make sure reply box is open first (click Reply) |
| CORS errors | Check browser console (F12), verify API URL in settings |

### Generation Quality Issues

| Problem | Solution |
|---------|----------|
| Generic/irrelevant replies | Add more specific FAQs to `faq.csv` |
| Low confidence scores | Expand knowledge base, add more labeled emails |
| Wrong tone | Edit `DEFAULT_USER_TONE` in `backend/config.py` |
| Too long/short replies | Adjust `MAX_REPLY_LENGTH` in config |

---

## 🎨 Customization

### Change User Name & Tone

Edit `/Users/iramkamdar/RAG/backend/config.py`:
```python
# Line ~45-46
DEFAULT_USER_NAME = "Iram"  # Your name
DEFAULT_USER_TONE = "friendly and professional"  # Your style
```

Restart backend to apply changes.

### Adjust Confidence Threshold

1. Click extension icon
2. Adjust "Confidence Threshold" slider
3. Higher = more conservative (0.9+)
4. Lower = more permissive (0.5-0.7)

### Modify Prompts

Edit `/Users/iramkamdar/RAG/backend/services/ollama_service.py`:
- Look for `_build_prompt()` method (line ~80)
- Customize the prompt template
- Restart backend

### Add Custom Icons

```bash
cd /Users/iramkamdar/RAG/chrome-extension/icons

# Create 3 PNG files:
# icon16.png (16x16 pixels)
# icon48.png (48x48 pixels)
# icon128.png (128x128 pixels)

# Reload extension in chrome://extensions/
```

---

## 📊 Understanding the Output

### Confidence Score
- **0.85+** (High): Very confident, auto-send recommended
- **0.65-0.85** (Medium): Good match, review recommended
- **<0.65** (Low): Uncertain, edit carefully

### Intent Classification
- `schedule` - Meeting/appointment requests
- `request_info` - Information queries
- `follow_up` - Follow-up messages
- `confirm` - Confirmations
- `general_inquiry` - Other/unclear

### Context Used
Shows what knowledge was retrieved:
- **FAQ Hits**: Matching Q&A pairs
- **Graph Nodes**: Related concepts from your email graph
- **Expanded Graph**: Connected entities

---

## 📁 Quick Reference

### File Locations
```bash
Backend:          /Users/iramkamdar/RAG/backend/
Extension:        /Users/iramkamdar/RAG/chrome-extension/
Knowledge Base:   /Users/iramkamdar/RAG/qdrant_data/
Config:           /Users/iramkamdar/RAG/backend/config.py
Startup Script:   /Users/iramkamdar/RAG/start_backend.sh
Test Script:      /Users/iramkamdar/RAG/test_backend.py
```

### Important URLs
```
Backend API:      http://localhost:8000
API Docs:         http://localhost:8000/docs
Health Check:     http://localhost:8000/api/health
Extensions:       chrome://extensions/
```

### Commands
```bash
# Start backend
conda activate graph_rag
python -m backend.main

# Test backend
python test_backend.py

# Start Ollama
ollama serve

# Check Ollama models
ollama list
```

---

## 🚀 Next Steps

1. ✅ **Test with 10+ emails** - Different types (meetings, info, feedback)
2. 📝 **Customize prompts** - Match your communication style
3. 📊 **Add more FAQs** - Improve context and relevance
4. 🎨 **Create icons** - Make it look professional
5. 📈 **Monitor performance** - Track confidence scores
6. 🔄 **Iterate** - Keep improving based on results

---

## 📚 Documentation

- **Full Guide:** `README_CHROME_EXTENSION.md`
- **Quick Start:** `QUICK_START.md`
- **Architecture:** `CHROME_EXTENSION_RESEARCH.md`
- **Project Summary:** `PROJECT_SUMMARY.md`
- **This File:** `SETUP_INSTRUCTIONS.md`

---

## 💡 Tips for Best Results

1. **Add More FAQs**: The more Q&A pairs, the better the context
2. **Label More Emails**: Build richer graph with more relationships
3. **Monitor Scores**: Track what works well (high confidence)
4. **Iterate Prompts**: Adjust tone and style over time
5. **Use Keyboard Shortcuts**: Pin extension for quick access
6. **Review Before Sending**: AI is helpful but not perfect

---

## 🎓 What's Happening Behind the Scenes

When you click "Generate Reply":

1. **Email Extraction** → Content script reads Gmail DOM
2. **API Call** → Sends to backend (POST /api/generate-reply)
3. **Intent Classification** → Ollama determines email type
4. **Embedding** → Converts email to 384-dim vector
5. **Vector Search** → Qdrant finds top-6 similar items
6. **Graph Expansion** → NetworkX gets related concepts
7. **Context Building** → Combines FAQ + graph knowledge
8. **Draft Generation** → Ollama creates personalized reply
9. **Insertion** → Content script fills reply box
10. **Done!** → You review and send

Average time: **5-15 seconds** (depends on your hardware)

---

## ✅ Success Checklist

- [ ] Ollama installed and serving
- [ ] Llama3 model pulled
- [ ] Conda environment created
- [ ] Backend dependencies installed
- [ ] Backend starts without errors
- [ ] Health check returns "healthy"
- [ ] Test script passes all tests
- [ ] Chrome extension loaded
- [ ] Extension settings configured
- [ ] Test connection shows "online"
- [ ] Button appears in Gmail
- [ ] Draft generation works
- [ ] Replies are contextually relevant

---

## 🆘 Still Having Issues?

1. **Check Logs:**
   ```bash
   # Backend terminal shows errors
   # Browser console (F12) shows extension errors
   ```

2. **Verify Services:**
   ```bash
   # Ollama running?
   curl http://localhost:11434
   
   # Backend running?
   curl http://localhost:8000/api/health
   
   # Qdrant data exists?
   ls -la qdrant_data/
   ```

3. **Clean Restart:**
   ```bash
   # Kill all processes
   pkill -f ollama
   pkill -f uvicorn
   
   # Restart Ollama
   ollama serve
   
   # Restart backend (new terminal)
   conda activate graph_rag
   python -m backend.main
   ```

4. **Reinstall Dependencies:**
   ```bash
   conda activate graph_rag
   pip install -r backend/requirements.txt --force-reinstall --no-cache
   ```

---

## 🎉 You're Done!

Enjoy your AI-powered email assistant! 

Remember: The more you use it and refine your knowledge base, the better it gets. 🚀

**Questions?** Check the troubleshooting sections in the documentation files.

**Want to improve it?** Start by adding more FAQs and testing with different email types!

