# 🚀 Graph RAG Email Assistant - START HERE

Welcome! This is your complete AI-powered email assistant for Gmail.

---

## 🎯 What Is This?

A Chrome extension that **automatically generates email replies** using:
- 🧠 **Local AI** (Llama 3 via Ollama)
- 🔍 **Smart Search** (Vector + Graph RAG)
- 📚 **Your Knowledge Base** (FAQs + Email patterns)
- ✉️ **Gmail Integration** (One-click generation)

**Result:** Click a button → AI reads email → Generates contextual reply → Inserts into Gmail

---

## ⚡ Quick Setup (5 Minutes)

### 1️⃣ Install Ollama & Model
```bash
# Install from https://ollama.ai
ollama pull llama3
```

### 2️⃣ Start Backend
```bash
cd /Users/iramkamdar/RAG
conda create -n graph_rag python=3.10 -y
conda activate graph_rag
pip install -r backend/requirements.txt

# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
./start_backend.sh
```

### 3️⃣ Install Extension
1. Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. "Load unpacked" → Select `/Users/iramkamdar/RAG/chrome-extension`
4. Done! 🎉

### 4️⃣ Test in Gmail
1. Go to Gmail
2. Open email → Click Reply
3. Click "🤖 Generate Reply"
4. Watch AI write your reply!

---

## 📚 Full Documentation

Pick the guide that fits your needs:

| Document | Purpose | Time |
|----------|---------|------|
| **SETUP_INSTRUCTIONS.md** | Step-by-step setup with troubleshooting | 10 min |
| **QUICK_START.md** | Fastest path to running system | 5 min |
| **README_CHROME_EXTENSION.md** | Complete reference guide | 30 min |
| **CHROME_EXTENSION_RESEARCH.md** | Architecture & design decisions | 45 min |
| **PROJECT_SUMMARY.md** | What was built & how it works | 15 min |

---

## 🏗️ Project Structure

```
RAG/
├── backend/                    # FastAPI API (Python)
│   ├── services/              # RAG components
│   │   ├── embedding_service.py
│   │   ├── qdrant_service.py
│   │   ├── graph_service.py
│   │   ├── ollama_service.py
│   │   └── rag_service.py
│   ├── api/routes.py          # Endpoints
│   ├── config.py              # Settings
│   └── main.py                # Entry point
│
├── chrome-extension/          # Chrome Extension
│   ├── manifest.json          # Config
│   ├── content.js             # Gmail integration
│   ├── background.js          # Service worker
│   └── popup.html/js          # Settings UI
│
├── qdrant_data/               # Vector database
├── faq.csv                    # Your FAQs
└── student_email_pairs.labels.jsonl  # Email patterns
```

---

## 🎬 How It Works

```
┌─────────────────────────────────────────────────────────┐
│ 1. User opens email in Gmail & clicks Reply            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Extension extracts: subject, sender, body           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Sent to FastAPI: POST /api/generate-reply           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Backend Processing:                                  │
│    • Classify intent (Ollama)                           │
│    • Embed query (sentence-transformers)                │
│    • Search FAQs (Qdrant vector DB)                     │
│    • Find graph context (NetworkX)                      │
│    • Build prompt (combine context)                     │
│    • Generate draft (Ollama Llama3)                     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Return: draft_reply + confidence_score + intent     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Extension inserts draft into Gmail reply box        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 7. User reviews, edits (if needed), and sends! ✅      │
└─────────────────────────────────────────────────────────┘
```

**Time:** 5-15 seconds from click to draft

---

## 🔧 Customization

### Quick Tweaks
```python
# backend/config.py

DEFAULT_USER_NAME = "Iram"  # Your name
DEFAULT_USER_TONE = "friendly and professional"  # Your style
AUTO_SEND_THRESHOLD = 0.85  # Confidence threshold
TOP_K_RESULTS = 6  # How many context items to retrieve
```

### Add More Knowledge
1. **FAQs**: Add to `faq.csv`
2. **Email Patterns**: Add to labels file
3. **Re-run notebook** to update vector DB
4. **Restart backend**

---

## 🐛 Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| Backend won't start | `ollama serve` in separate terminal |
| Extension not working | Refresh Gmail, check chrome://extensions/ |
| Button not appearing | Click Reply first, wait 2-3 seconds |
| Low quality replies | Add more FAQs to `faq.csv` |

**Full troubleshooting:** See `SETUP_INSTRUCTIONS.md`

---

## 🎯 Quick Commands

```bash
# Start backend
cd /Users/iramkamdar/RAG
conda activate graph_rag
./start_backend.sh

# Test backend
python test_backend.py

# Check health
curl http://localhost:8000/api/health

# View API docs
open http://localhost:8000/docs
```

---

## 📊 What You Get

✅ **Complete FastAPI Backend** with RAG pipeline  
✅ **Chrome Extension** with Gmail integration  
✅ **Vector Search** (Qdrant) for semantic matching  
✅ **Graph RAG** (NetworkX) for relationship context  
✅ **Local LLM** (Ollama) - no cloud APIs needed  
✅ **Full Documentation** with examples  
✅ **Test Suite** for validation  
✅ **Privacy-First** - all data stays local  

---

## 🚀 Next Steps

1. ✅ **Complete Setup** → Follow SETUP_INSTRUCTIONS.md
2. 📧 **Test with Real Emails** → Try 10+ different types
3. 🎨 **Customize** → Adjust tone, add FAQs, tweak prompts
4. 📊 **Monitor** → Track confidence scores
5. 🔄 **Iterate** → Keep improving your knowledge base

---

## 💡 Pro Tips

- **Start with high-confidence emails** (meetings, confirmations)
- **Add FAQs for common questions** you receive
- **Monitor which emails get low scores** → add more context
- **Customize the tone** to match your style
- **Review before sending** → AI helps, but you decide

---

## 🎉 You're Ready!

Pick your path:

1. **Want to dive in?** → `SETUP_INSTRUCTIONS.md`
2. **Need quick start?** → `QUICK_START.md`
3. **Want full details?** → `README_CHROME_EXTENSION.md`
4. **Understanding the system?** → `PROJECT_SUMMARY.md`

**Remember:** This is a complete, production-quality system. Take your time to set it up properly, and it will serve you well! 🚀

---

## 📞 File Guide

| Need | Read This |
|------|-----------|
| Setup instructions | `SETUP_INSTRUCTIONS.md` |
| Quick 5-min guide | `QUICK_START.md` |
| Full documentation | `README_CHROME_EXTENSION.md` |
| How it was built | `CHROME_EXTENSION_RESEARCH.md` |
| What you have | `PROJECT_SUMMARY.md` |
| Extension install | `chrome-extension/INSTALL_EXTENSION.md` |

---

**Let's get started! Open `SETUP_INSTRUCTIONS.md` and follow along.** 🎯

