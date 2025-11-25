# 📧 Gmail API: Costs, Limits & Alternatives

## Gmail API Reality Check

### **Cost:**
✅ **FREE** - Gmail API is free to use (no charges)

### **Quota Limits:**
- **1 billion quota units per day** (very generous)
- Most operations cost 1-5 quota units
- **1,000 requests per 100 seconds per user** (rate limit)
- **250 quota units per user per second** (burst limit)

**Translation:** You can make **millions of requests per day** for free, but need to respect rate limits.

### **Constraints:**
1. **OAuth 2.0 Required** - Need user authentication
2. **Rate Limiting** - Can't make too many requests too fast
3. **Scopes Required** - Need specific permissions (read, send, etc.)
4. **User Consent** - Users must approve access
5. **Quota Exhaustion** - If you exceed limits, requests fail (but resets daily)

---

## 🚫 **Real Constraints:**

### **1. Authentication Complexity**
- Requires OAuth 2.0 setup
- User must grant permissions
- Token management needed
- More complex than IMAP

### **2. Rate Limits**
- 1,000 requests per 100 seconds per user
- Need to implement backoff/retry logic
- Can't fetch all emails instantly

### **3. Scope Limitations**
- Can only access what user grants permission for
- Some scopes require Google verification for public apps
- Limited to what Gmail API exposes

### **4. Development Overhead**
- More complex than IMAP
- Requires proper error handling
- Need to handle token refresh

---

## 💡 **Alternative Methods (No Gmail API)**

### **Method 1: IMAP (Like Zubair's Approach)**

**Pros:**
- ✅ Simple to implement
- ✅ No API quotas
- ✅ Direct email access
- ✅ Works with any email provider

**Cons:**
- ❌ Requires app password
- ❌ Less secure (password in .env)
- ❌ No real-time updates
- ❌ Need to poll for new emails

**Implementation:**
```python
# backend/services/imap_email_service.py

import imaplib
import email
from email.header import decode_header

class IMAPEmailService:
    def __init__(self, email_account, password):
        self.email_account = email_account
        self.password = password
    
    def connect(self):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.email_account, self.password)
        self.mail.select('"[Gmail]/Sent Mail"')  # Sent folder
    
    def get_sent_emails(self, limit=500):
        """Get sent emails via IMAP"""
        # Search for sent emails
        status, messages = self.mail.search(None, 'ALL')
        email_ids = messages[0].split()[-limit:]  # Last N emails
        
        pairs = []
        for email_id in email_ids:
            # Fetch email
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract content
            body = self.get_email_body(email_message)
            subject = email_message['Subject']
            date = email_message['Date']
            
            # Get thread to find original message
            thread_id = email_message['In-Reply-To'] or email_message['References']
            
            pairs.append({
                'user_reply': body,
                'subject': subject,
                'date': date,
                'thread_id': thread_id
            })
        
        return pairs
    
    def get_email_body(self, email_message):
        """Extract text body from email"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        return body
```

**Usage:**
```python
# One-time sync script
imap_service = IMAPEmailService(
    email_account="user@gmail.com",
    password=os.getenv("EMAIL_PASSWORD")  # App password
)

imap_service.connect()
sent_emails = imap_service.get_sent_emails(limit=500)

# Process and store in Qdrant
for email in sent_emails:
    # Extract pairs, embed, store
    ...
```

---

### **Method 2: Manual Export + Import**

**Pros:**
- ✅ No API needed
- ✅ No authentication complexity
- ✅ User has full control
- ✅ Works offline

**Cons:**
- ❌ Manual process
- ❌ Not automatic
- ❌ User must export periodically

**Implementation:**

1. **User exports emails from Gmail:**
   - Gmail → Settings → Download all mail data
   - Download as `.mbox` file

2. **Process mbox file:**
   ```python
   # backend/services/mbox_processor.py
   
   import mailbox
   import email
   
   class MboxProcessor:
       def process_mbox(self, mbox_path):
           """Process mbox file and extract email pairs"""
           mbox = mailbox.mbox(mbox_path)
           
           pairs = []
           for message in mbox:
               # Extract email data
               body = self.get_body(message)
               subject = message['Subject']
               date = message['Date']
               
               # Try to find original message in thread
               original = self.find_original_in_thread(message)
               
               if original:
                   pairs.append({
                       'original_message': original,
                       'user_reply': body,
                       'subject': subject,
                       'date': date
                   })
           
           return pairs
   ```

3. **Upload via Chrome Extension:**
   ```javascript
   // In chrome-extension/popup.html
   
   <input type="file" id="mboxFile" accept=".mbox">
   <button onclick="uploadMbox()">Import Email History</button>
   
   async function uploadMbox() {
       const file = document.getElementById('mboxFile').files[0];
       const formData = new FormData();
       formData.append('mbox', file);
       
       const response = await fetch(`${API_BASE_URL}/import-mbox`, {
           method: 'POST',
           body: formData
       });
   }
   ```

---

### **Method 3: Chrome Extension DOM Scraping**

**Pros:**
- ✅ No API needed
- ✅ Works directly in browser
- ✅ Real-time access
- ✅ No authentication complexity

**Cons:**
- ❌ Fragile (breaks if Gmail UI changes)
- ❌ Limited to what's visible
- ❌ Can't access full history easily

**Implementation:**
```javascript
// In chrome-extension/content.js

class GmailHistoryExtractor {
    async extractVisibleEmails() {
        // Navigate to Sent folder
        window.location.href = 'https://mail.google.com/mail/u/0/#sent';
        await this.waitForLoad();
        
        const emails = [];
        
        // Find all email rows
        const emailRows = document.querySelectorAll('tr.zA');
        
        for (const row of emailRows) {
            // Click to open email
            row.click();
            await this.waitForLoad();
            
            // Extract email content
            const email = {
                subject: document.querySelector('h2.hP')?.innerText,
                body: document.querySelector('div.a3s')?.innerText,
                date: document.querySelector('span.g3')?.innerText,
                to: document.querySelector('span.gD')?.innerText
            };
            
            emails.push(email);
            
            // Go back
            window.history.back();
            await this.waitForLoad();
        }
        
        return emails;
    }
    
    waitForLoad() {
        return new Promise(resolve => setTimeout(resolve, 1000));
    }
}
```

**Note:** This is fragile and not recommended for production.

---

### **Method 4: Email Client Export (Thunderbird, Apple Mail, etc.)**

**Pros:**
- ✅ No API needed
- ✅ Works with any email client
- ✅ Can export full history
- ✅ Standard formats (mbox, eml)

**Cons:**
- ❌ Requires email client setup
- ❌ Manual export process
- ❌ Not automatic

**Implementation:**
1. User sets up email in Thunderbird/Apple Mail
2. Export emails as `.mbox` or `.eml` files
3. Process same as Method 2

---

### **Method 5: Hybrid: Initial Import + Real-Time Learning**

**Best of Both Worlds:**

1. **Initial Setup:** User exports emails once (Method 2)
2. **Ongoing:** Learn from user edits (Method 4 from previous doc)

**Implementation:**
```python
# Initial import (one-time)
def import_initial_history(mbox_file):
    """Import historical emails"""
    processor = MboxProcessor()
    pairs = processor.process_mbox(mbox_file)
    
    # Store in Qdrant
    for pair in pairs:
        store_in_qdrant(pair)

# Real-time learning (ongoing)
def learn_from_edit(original_draft, edited_reply, email_context):
    """Learn from user edits"""
    # Store as new example
    store_in_qdrant({
        'original_message': email_context.body,
        'user_reply': edited_reply,
        'source': 'user_edit',  # Mark as learned from edit
        'date': datetime.now()
    })
```

**Benefits:**
- ✅ No API needed
- ✅ One-time manual import
- ✅ Continuous learning from usage
- ✅ Gets better over time

---

## 🎯 **Recommended Approach**

### **For Most Users: Method 5 (Hybrid)**

1. **Initial Setup (One-Time):**
   - User exports Gmail data as `.mbox`
   - Upload via Chrome Extension
   - Process and store in Qdrant

2. **Ongoing (Automatic):**
   - Learn from user edits
   - Continuously improve
   - No manual work needed

### **For Power Users: Method 1 (IMAP)**

If user is comfortable with app passwords:
- Set up IMAP sync
- Periodic background sync
- Automatic updates

### **For Privacy-Conscious: Method 2 (Manual Export)**

- Full user control
- No cloud APIs
- Export when needed

---

## 📊 **Comparison**

| Method | Setup Complexity | Automation | Privacy | Cost |
|--------|-----------------|------------|---------|------|
| **Gmail API** | High | High | Medium | Free (with limits) |
| **IMAP** | Medium | Medium | High | Free |
| **Manual Export** | Low | Low | Very High | Free |
| **DOM Scraping** | Low | Medium | High | Free |
| **Hybrid** | Low | High | High | Free |

---

## 💡 **My Recommendation**

**Use Method 5 (Hybrid):**
1. ✅ One-time manual import (user exports Gmail data)
2. ✅ Real-time learning from edits (automatic)
3. ✅ No API complexity
4. ✅ No ongoing manual work
5. ✅ Gets better with use

This gives you the benefits of personal data without the complexity of Gmail API!

---

## 🚀 **Quick Implementation**

Want me to implement the Hybrid approach? It would include:

1. **Mbox upload endpoint** in backend
2. **Mbox processor** to extract email pairs
3. **Edit tracking** in Chrome Extension
4. **Learning endpoint** to store edits as examples

This is the best balance of simplicity, privacy, and effectiveness!

