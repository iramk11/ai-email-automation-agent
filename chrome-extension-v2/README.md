# AI Email Assistant - Chrome Extension v2

A modern, minimalistic Chrome extension for AI-powered email reply generation using Graph RAG. Supports both **Gmail** and **Outlook**.

## ✨ Features

- 🤖 **AI-Powered Replies**: Generate intelligent email replies using Graph RAG
- 📧 **Multi-Provider Support**: Works with Gmail and Outlook (Live, Office 365)
- 🎨 **Modern UI**: Clean, minimalistic design with smooth animations
- ⚡ **Real-time Status**: Live backend connection status monitoring
- 🔍 **Context Panel**: View detailed retrieval context (FAQ matches, similar replies)
- ⚙️ **Customizable**: Adjustable confidence threshold and auto-insert settings

## 🚀 Installation

### Prerequisites

1. **Backend Server**: Make sure your backend is running on `http://localhost:8001` (or configure custom URL)
2. **Chrome Browser**: Version 88 or higher

### Steps

1. **Load Extension**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable **"Developer mode"** (toggle in top-right)
   - Click **"Load unpacked"**
   - Select the `chrome-extension-v2` folder

2. **Configure Settings**:
   - Click the extension icon in the toolbar
   - Set your API URL (default: `http://localhost:8001/api`)
   - Adjust confidence threshold if needed
   - Click **"Test Connection"** to verify backend is running

3. **Start Using**:
   - Open Gmail or Outlook
   - Open any email
   - Click **"Reply"**
   - Look for the **"🤖 Generate Reply"** button
   - Click to generate AI-powered draft!

## 📸 Screenshots

![Extension Screenshot 1](images/1.png)

![Extension Screenshot 2](images/2.png)

![Extension Screenshot 3](images/3.png)

![Extension Screenshot 4](images/4.png)

![Extension Screenshot 5](images/5.png)

![Extension Screenshot 6](images/6.png)

## 📋 Supported Email Providers

### Gmail
- ✅ mail.google.com
- Full support for email extraction and reply insertion

### Outlook
- ✅ outlook.live.com (Outlook.com)
- ✅ outlook.office.com (Office 365)
- ✅ outlook.office365.com (Office 365)
- Full support for email extraction and reply insertion

## 🎨 UI Features

### Popup Interface
- **Status Card**: Real-time backend connection status with visual indicators
- **Settings Panel**: Clean form inputs with icons
- **Confidence Slider**: Visual slider for threshold adjustment
- **Toast Notifications**: Non-intrusive success/error messages

### Content Script UI
- **Generate Button**: Modern gradient button with hover effects
- **Loading States**: Animated spinner during generation
- **Context Panel**: Detailed breakdown of retrieval context
- **Notifications**: Toast-style notifications for user feedback

## ⚙️ Configuration

### Settings

- **API URL**: Backend API endpoint (default: `http://localhost:8001/api`)
- **Confidence Threshold**: Minimum confidence score (0-1, default: 0.85)
- **Auto-insert**: Automatically insert generated drafts into reply box

### Backend Requirements

The extension expects a backend API with the following endpoints:

- `GET /api/health` - Health check endpoint
- `POST /api/generate-reply` - Generate email reply

See the main project README for backend setup instructions.

## 🐛 Troubleshooting

### Extension not working?

1. **Check Backend**:
   - Verify backend is running: `http://localhost:8001/api/health`
   - Check browser console for errors (F12)

2. **Reload Extension**:
   - Go to `chrome://extensions/`
   - Click reload icon on the extension card

3. **Check Permissions**:
   - Ensure extension has access to Gmail/Outlook domains
   - Check if popup is blocked

### Button not appearing?

- **Gmail**: Make sure you've clicked "Reply" first
- **Outlook**: Open the reply compose window
- Wait 2-3 seconds (button appears periodically)
- Check browser console (F12) for errors

### Email content not extracted?

- Refresh the email page
- Make sure you're viewing a single email (not inbox)
- Check browser console for extraction errors

## 📁 File Structure

```
chrome-extension-v2/
├── manifest.json          # Extension manifest
├── popup.html             # Popup UI
├── popup.js               # Popup logic
├── background.js          # Service worker
├── content.js             # Content script (Gmail & Outlook)
├── styles/
│   ├── popup.css         # Popup styles
│   └── content.css       # Content script styles
├── icons/
│   ├── icon16.png        # 16x16 icon
│   ├── icon48.png        # 48x48 icon
│   ├── icon128.png       # 128x128 icon
│   └── icon.svg          # Source SVG
└── README.md             # This file
```

## 🔄 Updates from v1

- ✨ **Outlook Support**: Full support for Outlook.com and Office 365
- 🎨 **Modern UI**: Complete redesign with minimalistic aesthetic
- 📱 **Better UX**: Improved status indicators, toast notifications, context panels
- 🎯 **Provider Detection**: Automatic detection of email provider
- 🔧 **Improved Error Handling**: Better error messages and recovery

## 📝 License

See main project LICENSE file.

## 🤝 Contributing

See main project CONTRIBUTING guidelines.

