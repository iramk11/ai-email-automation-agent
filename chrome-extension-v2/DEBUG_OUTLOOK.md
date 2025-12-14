# Debugging Outlook Support

If the extension isn't working on Outlook, follow these steps:

## Quick Debug Steps

1. **Open Browser Console** (F12 or Cmd+Option+I)

2. **Run Debug Command**:
   ```javascript
   debugAIEmailAssistant()
   ```
   This will show:
   - Detected provider
   - Email extraction results
   - Reply box detection results
   - Button insertion status

## Common Issues

### Issue: "Could not extract email content"

**Symptoms**: Button works but can't read the email

**Solutions**:
1. Make sure you're viewing an email (not in compose window)
2. Try refreshing the page
3. Check console for extraction errors
4. The email body might be in an iframe - check console logs

**Debug**:
```javascript
// Check what elements are found
const readingPane = document.querySelector('[data-automation-id="readingPaneContainer"]');
console.log('Reading pane:', readingPane);

const messageBody = document.querySelector('[role="article"]');
console.log('Message body:', messageBody);
```

### Issue: "Please click Reply first"

**Symptoms**: Can't find reply box

**Solutions**:
1. Click the **Reply** button first to open compose window
2. Wait 2-3 seconds for button to appear
3. Check if compose dialog opened

**Debug**:
```javascript
// Check for compose dialog
const dialog = document.querySelector('[role="dialog"]');
console.log('Compose dialog:', dialog);

// Check for contenteditable elements
const editables = document.querySelectorAll('[contenteditable="true"]');
console.log('Contenteditable elements:', editables.length);
editables.forEach((el, i) => {
    console.log(`Element ${i}:`, {
        ariaLabel: el.getAttribute('aria-label'),
        role: el.getAttribute('role'),
        inDialog: !!el.closest('[role="dialog"]')
    });
});
```

### Issue: Button not appearing

**Symptoms**: No "Generate Reply" button visible

**Solutions**:
1. Refresh the page
2. Reload the extension at `chrome://extensions/`
3. Check console for errors
4. Make sure you're on a supported Outlook domain:
   - outlook.live.com
   - outlook.office.com
   - outlook.office365.com

**Debug**:
```javascript
// Check provider detection
console.log('Current URL:', window.location.href);
console.log('Detected provider:', window.location.hostname.includes('outlook') ? 'outlook' : 'unknown');

// Check if button exists
const button = document.getElementById('ai-email-generate-btn');
console.log('Button exists:', !!button);
```

### Issue: Draft inserted but not visible

**Symptoms**: Reply generated but text doesn't appear

**Solutions**:
1. Check if reply box is focused
2. Try clicking in the reply box after generation
3. Check console for insertion errors

**Debug**:
```javascript
// Find reply box
const replyBox = document.querySelector('[contenteditable="true"]');
if (replyBox) {
    console.log('Reply box content:', replyBox.innerHTML);
    console.log('Reply box text:', replyBox.innerText);
    replyBox.focus();
}
```

## Manual Testing

1. **Test Email Extraction**:
   ```javascript
   // In console
   const emailData = extractEmailContent();
   console.log(emailData);
   ```

2. **Test Reply Box Finding**:
   ```javascript
   // After clicking Reply
   const replyBox = findReplyBox();
   console.log('Reply box:', replyBox);
   ```

3. **Test Button Insertion**:
   ```javascript
   // Check if button container exists
   const container = document.querySelector('[role="toolbar"]');
   console.log('Toolbar:', container);
   ```

## Reporting Issues

If issues persist, please provide:

1. **Console Output**: Copy all console logs
2. **Screenshot**: Of the email page and compose window
3. **URL**: The exact Outlook URL you're on
4. **Browser**: Chrome version
5. **Extension Version**: Check at `chrome://extensions/`

## Known Limitations

- Outlook.com uses dynamic DOM that changes frequently
- Some email formats may not be detected
- Compose window must be open for reply box detection
- Iframe-based emails may not be extractable

