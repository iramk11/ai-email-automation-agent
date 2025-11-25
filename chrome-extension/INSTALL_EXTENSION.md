# Quick Installation Guide - Chrome Extension

## 🎯 Quick Start (5 minutes)

### Step 1: Start Backend (Terminal 1)

```bash
cd /Users/iramkamdar/RAG

# Option A: Use the startup script
./start_backend.sh

# Option B: Manual start
conda activate graph_rag  # or your environment
python -m backend.main
```

**✅ Success**: You should see "All services initialized successfully!"

### Step 2: Install Extension

1. Open Chrome and go to: `chrome://extensions/`
2. Toggle **"Developer mode"** ON (top-right)
3. Click **"Load unpacked"**
4. Select this folder: `/Users/iramkamdar/RAG/chrome-extension`
5. Extension will appear with 🤖 icon

### Step 3: Test

1. Click the extension icon (🤖) in Chrome toolbar
2. Click **"Test Connection"**
3. Should show: **"Backend online and healthy"** ✅

### Step 4: Use in Gmail

1. Go to Gmail: https://mail.google.com
2. Open any email
3. Click **Reply**
4. Look for **"🤖 Generate Reply"** button
5. Click it to generate AI draft!

## 🐛 Troubleshooting

**Backend not starting?**
```bash
# Check Ollama is running
ollama list
# If not, start it
ollama serve

# Check dependencies
pip install -r backend/requirements.txt
```

**Extension not working?**
- Refresh Gmail page (Cmd/Ctrl + R)
- Check browser console (F12) for errors
- Reload extension at chrome://extensions/

**Button not appearing?**
- Make sure you clicked "Reply" first
- Wait 2-3 seconds (button appears periodically)
- Check browser console for errors

## 📝 Note

Icons are currently placeholders. You can add custom icons:
- Create 16x16, 48x48, and 128x128 PNG images
- Save as `icon16.png`, `icon48.png`, `icon128.png` in `icons/` folder

For full documentation, see `README_CHROME_EXTENSION.md`

