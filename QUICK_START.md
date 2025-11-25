# 🚀 Quick Start - Graph RAG Email Assistant

Complete setup in **5 minutes**!

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Ollama installed ([get it here](https://ollama.ai))
- [ ] Llama 3 model pulled: `ollama pull llama3`
- [ ] Chrome browser installed
- [ ] Your notebook has been run (qdrant_data exists)

## Setup Steps

### 1️⃣ Backend Setup (2 minutes)

```bash
# Navigate to project
cd /Users/iramkamdar/RAG

# Create environment (if not exists)
conda create -n graph_rag python=3.10 -y
conda activate graph_rag

# Install dependencies
pip install -r backend/requirements.txt

# Start backend
./start_backend.sh
# OR manually:
# python -m backend.main
```

**✅ Check**: Open http://localhost:8000/api/health
- Should return: `{"status": "healthy", ...}`

### 2️⃣ Chrome Extension (2 minutes)

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **"Load unpacked"**
4. Select folder: `/Users/iramkamdar/RAG/chrome-extension`
5. Extension appears in toolbar 🤖

### 3️⃣ Test (1 minute)

1. **Click extension icon** → **"Test Connection"**
   - Should show: ✅ "Backend online and healthy"

2. **Go to Gmail** → Open any email → Click **Reply**

3. **Click "🤖 Generate Reply"** button

4. **Watch the magic!** 🎉
   - AI reads the email
   - Generates contextual reply
   - Inserts into reply box

## 🎯 What It Does

```
Email → AI Analysis → Context Retrieval → Draft Generation
         ↓              ↓                    ↓
    Intent       FAQ + Graph          Llama 3 Local
 Classification    Search              LLM Reply
```

## 📊 Architecture

```
Gmail (Browser)
    ↓
Chrome Extension (extract email)
    ↓ HTTP
FastAPI Backend
    ├─ Qdrant (semantic search)
    ├─ NetworkX (graph relationships)
    └─ Ollama (LLM generation)
    ↑ Insert draft
Gmail Reply Box
```

## 🎨 Customization

### Change Reply Tone

Edit `backend/config.py`:
```python
DEFAULT_USER_NAME = "Your Name"
DEFAULT_USER_TONE = "casual and friendly"  # or "formal and professional"
```

### Adjust Confidence

In extension popup:
- Set threshold: 0.85 = conservative, 0.5 = permissive

### Add More Context

1. Add FAQs to `faq.csv`
2. Add labeled emails to generate graph
3. Re-run notebook cells to update knowledge base

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Ollama is running: `ollama serve` |
| Import errors | Re-install: `pip install -r backend/requirements.txt` |
| Button not showing | Refresh Gmail, wait 2-3 seconds |
| "Backend offline" | Verify: `curl http://localhost:8000/api/health` |
| Low confidence | Add more FAQs, expand knowledge base |

## 📁 Project Files

```
RAG/
├── backend/              ← FastAPI server
│   ├── main.py          ← Entry point
│   ├── services/        ← RAG components
│   └── requirements.txt
├── chrome-extension/     ← Chrome extension
│   ├── manifest.json    ← Config
│   ├── content.js       ← Gmail integration
│   └── popup.html       ← Settings UI
├── qdrant_data/         ← Vector DB (from notebook)
└── start_backend.sh     ← Quick start script
```

## 🚀 Next Steps

1. ✅ Test with 5-10 different emails
2. 📝 Customize prompts in `backend/services/ollama_service.py`
3. 📊 Add more FAQs to improve context
4. 🎨 Create custom icons for extension
5. 🌐 (Optional) Deploy backend to server

## 📚 Full Documentation

- `README_CHROME_EXTENSION.md` - Detailed setup & troubleshooting
- `CHROME_EXTENSION_RESEARCH.md` - Architecture & design decisions
- `chrome-extension/INSTALL_EXTENSION.md` - Extension-specific guide

## 💡 Tips

- **First time**: Replies might be generic. Add more FAQs!
- **Slow?**: Try smaller model: `ollama pull llama3.2:1b`
- **Privacy**: Everything runs locally, no data leaves your machine
- **Customize**: Edit prompts to match your communication style

---

**Enjoy your AI email assistant! 🎉**

Questions? Check the troubleshooting sections in the full README.

