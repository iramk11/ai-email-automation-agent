# Quick Installation Guide - Chrome Extension

## 🎯 Quick Start (5 minutes)

### Step 1: Start Backend (Terminal 1)

```bash
# From project root directory
cd .

# Option A: Use the startup script (recommended)
./start_backend.sh

# Option B: Manual start
source email-agent/bin/activate  # Activate virtual environment
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

**Note**: Backend runs on port 8001 by default (port 8000 may be in use). Update extension settings if needed.

**✅ Success**: You should see "All services initialized successfully!"

### Step 2: Install Extension

1. Open Chrome and go to: `chrome://extensions/`
2. Toggle **"Developer mode"** ON (top-right)
3. Click **"Load unpacked"**
4. Navigate to and select the `chrome-extension` folder in your project directory
5. Extension will appear with 🤖 icon

### Step 3: Test

1. Click the extension icon (🤖) in Chrome toolbar
2. Verify API URL is set to: `http://localhost:8001/api` (or your backend port)
3. Click **"Test Connection"**
4. Should show: **"Backend online and healthy"** ✅

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

