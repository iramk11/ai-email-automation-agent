# 🔧 Chrome Extension Troubleshooting

## Button Not Appearing in Gmail

### Quick Checks:

1. **Open Browser Console** (in Gmail tab):
   - Press `F12` (or `Cmd+Option+I` on Mac)
   - Click the **"Console"** tab
   - Look for messages like "Graph RAG Email Assistant: Content script loaded"

2. **Check for Errors**:
   - Any red error messages in console?
   - Look for messages about "content.js"

3. **Verify Extension is Active**:
   - Go to `chrome://extensions/`
   - Make sure "Graph RAG Email Assistant" toggle is **ON**
   - Click "Details" → Check "Allow access to file URLs" is checked (if needed)

### Common Issues:

#### Issue 1: Gmail Not Recognized
**Symptom**: Console shows no messages
**Fix**: 
- Refresh Gmail page (Cmd/Ctrl + R)
- Make sure you're on `https://mail.google.com` (not `http://`)

#### Issue 2: Content Script Not Loading
**Symptom**: No console messages at all
**Fix**:
1. Go to `chrome://extensions/`
2. Find "Graph RAG Email Assistant"
3. Click "Reload" (🔄) icon
4. Refresh Gmail page

#### Issue 3: Reply Box Not Detected
**Symptom**: Console shows "Content script loaded" but no button
**Fix**:
- Make sure you clicked Gmail's "Reply" button first
- The compose box needs to be open

### Step-by-Step Debug:

1. **Open Gmail** (https://mail.google.com)
2. **Open Developer Console** (F12)
3. **Refresh page** (Cmd/Ctrl + R)
4. **Check Console** - Should see:
   ```
   Graph RAG Email Assistant: Content script loaded
   Graph RAG Email Assistant initialized
   ```
5. **Open an email** → Click "Reply"
6. **Wait 2 seconds** - Should see:
   ```
   Found container for button insertion
   Generate Reply button inserted
   ```

### If Still Not Working:

Check these in Console:
```javascript
// Check if content script is running
console.log(document.getElementById('rag-generate-reply-btn'));

// Manual button insertion test
// (paste this in console while reply box is open)
const toolbar = document.querySelector('div[role="toolbar"]');
console.log('Toolbar found:', toolbar);
```

### Manual Test:

If button still doesn't appear, try this in Console:
```javascript
const button = document.createElement('button');
button.textContent = '🤖 TEST BUTTON';
button.style.cssText = 'margin: 10px; padding: 8px 16px; background: blue; color: white; border: none; border-radius: 4px;';
const toolbar = document.querySelector('div[role="toolbar"]') || document.querySelector('.btC');
if (toolbar) toolbar.appendChild(button);
```

If this works, the issue is with the content script timing.

