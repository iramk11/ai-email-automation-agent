# 🚀 Integrating Personal Email Data into Chrome Extension

## Overview

This document outlines innovative methods to integrate personal email history (like Zubair's approach) into the Chrome Extension's Graph RAG system for better personalization.

---

## 🎯 **Goal**

Combine the **structured Graph RAG approach** (current Chrome Extension) with **personal email history** (Zubair's approach) to create a hybrid system that:
- Understands relationships (Graph RAG)
- Mimics personal style (Personal history)
- Learns from user behavior (Adaptive)

---

## 💡 **Innovative Integration Methods**

### **Method 1: Hybrid Knowledge Base (Recommended)**

**Concept:** Add personal email pairs as a third knowledge source alongside FAQs and Graph.

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│ Incoming Email                                          │
└─────────────────────────────────────────────────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌───────────────────┐      ┌───────────────────┐
│ Graph RAG         │      │ Personal History  │
│ (Current System)  │      │ (New Addition)    │
│                   │      │                   │
│ - FAQs (Qdrant)   │      │ - Email Pairs     │
│ - Graph (NetworkX)│      │   (Qdrant)        │
│ - Intents         │      │ - Style Patterns  │
└───────────────────┘      └───────────────────┘
        │                           │
        └─────────────┬─────────────┘
                      ↓
        ┌─────────────────────────────┐
        │ Hybrid Context Fusion       │
        │ - Graph context             │
        │ - FAQ context               │
        │ - Personal style context    │
        └─────────────────────────────┘
                      ↓
        ┌─────────────────────────────┐
        │ LLM Generation              │
        │ (with all context)          │
        └─────────────────────────────┘
```

**Implementation:**

1. **Add Personal Email Pairs Collection to Qdrant:**
   ```python
   # In backend/services/qdrant_service.py
   
   def __init__(self):
       # Existing collections
       self.collection_name = "knowledge_space"  # FAQs + Graph nodes
       
       # NEW: Personal email pairs collection
       self.personal_collection = "personal_email_pairs"
       
   def search_personal_emails(self, query_vector, limit=3):
       """Search personal email history for style examples"""
       hits = self.client.search(
           collection_name=self.personal_collection,
           query_vector=query_vector,
           limit=limit
       )
       return hits
   ```

2. **Create Personal Email Pairs from Gmail:**
   ```python
   # New file: backend/services/personal_email_service.py
   
   class PersonalEmailService:
       def extract_email_pairs_from_gmail(self, gmail_api):
           """Extract email pairs from Gmail using Gmail API"""
           # Get sent emails
           sent_emails = gmail_api.get_sent_emails(limit=1000)
           
           pairs = []
           for email in sent_emails:
               # Get thread to find original message
               thread = gmail_api.get_thread(email.thread_id)
               
               # Find original message (incoming)
               original = self.find_original_message(thread)
               
               # Extract pair
               pairs.append({
                   "original_message": original.body,
                   "user_reply": email.body,
                   "subject": email.subject,
                   "sender": original.from_email,
                   "date": email.date
               })
           
           return pairs
       
       def embed_and_store_pairs(self, pairs):
           """Embed and store in Qdrant"""
           for pair in pairs:
               # Embed original message
               original_vec = embedder.encode(pair["original_message"])
               
               # Store in Qdrant
               qdrant.upsert(
                   collection_name="personal_email_pairs",
                   points=[{
                       "id": pair["id"],
                       "vector": original_vec,
                       "payload": {
                           "type": "personal_pair",
                           "original_message": pair["original_message"],
                           "user_reply": pair["user_reply"],
                           "subject": pair["subject"],
                           "sender": pair["sender"],
                           "date": pair["date"]
                       }
                   }]
               )
   ```

3. **Integrate into RAG Pipeline:**
   ```python
   # In backend/services/rag_service.py
   
   async def generate_reply(self, request: EmailRequest):
       # ... existing code ...
       
       # NEW: Search personal email history
       personal_hits = self.qdrant_service.search_personal_emails(
           query_vector, limit=3
       )
       
       # Combine all context
       context = {
           "faq_hits": faq_hits,
           "graph_hits": graph_hits,
           "personal_examples": personal_hits  # NEW
       }
       
       # Generate with all context
       draft = self.ollama_service.generate_reply(
           email_text=email_text,
           intent=intent,
           faq_hits=faq_hits,
           graph_hits=graph_hits,
           personal_examples=personal_hits,  # NEW
           expanded_graph=expanded_graph,
           user_name=user_name,
           user_tone=user_tone
       )
   ```

**Benefits:**
- ✅ Maintains Graph RAG structure
- ✅ Adds personal style mimicry
- ✅ Uses same Qdrant infrastructure
- ✅ Easy to implement

---

### **Method 2: Style Embedding Model**

**Concept:** Create a separate embedding model trained on user's writing style.

**Architecture:**
```
Personal Emails → Style Embedding Model → Style Vector
                                              ↓
                                    Style Similarity Search
```

**Implementation:**

1. **Train Style Embedding Model:**
   ```python
   # New file: backend/services/style_embedding_service.py
   
   from sentence_transformers import SentenceTransformer
   from sentence_transformers import InputExample, losses
   from torch.utils.data import DataLoader
   
   class StyleEmbeddingService:
       def __init__(self):
           # Start with base model
           self.model = SentenceTransformer('all-MiniLM-L6-v2')
       
       def fine_tune_on_personal_emails(self, email_pairs):
           """Fine-tune embedding model on personal email style"""
           
           # Create training examples
           examples = []
           for pair in email_pairs:
               # Positive: original message → user's reply (same style)
               examples.append(InputExample(
                   texts=[pair["original_message"], pair["user_reply"]],
                   label=1.0  # High similarity (same person's style)
               ))
               
               # Negative: original message → random reply (different style)
               examples.append(InputExample(
                   texts=[pair["original_message"], random_reply],
                   label=0.0  # Low similarity
               ))
           
           # Train
           train_dataloader = DataLoader(examples, shuffle=True, batch_size=16)
           train_loss = losses.CosineSimilarityLoss(self.model)
           
           self.model.fit(
               train_objectives=[(train_dataloader, train_loss)],
               epochs=3,
               warmup_steps=100
           )
           
           # Save model
           self.model.save('models/personal_style_embedder')
       
       def encode_style(self, text):
           """Encode text using style-aware embedding"""
           return self.model.encode(text)
   ```

2. **Use Style Embeddings for Retrieval:**
   ```python
   # In RAG service
   
   # Regular semantic search (for content)
   content_vector = content_embedder.encode(email_text)
   faq_hits = qdrant.search(content_vector)
   
   # Style-aware search (for personal examples)
   style_vector = style_embedder.encode(email_text)
   personal_hits = personal_qdrant.search(style_vector)
   ```

**Benefits:**
- ✅ Captures writing style, not just content
- ✅ Better personalization
- ✅ Can be fine-tuned over time

---

### **Method 3: Personal Graph Construction**

**Concept:** Build a personal knowledge graph from email history.

**Architecture:**
```
Personal Emails → Entity Extraction → Personal Graph
                                        ↓
                              Merge with Main Graph
```

**Implementation:**

1. **Extract Entities from Personal Emails:**
   ```python
   # New file: backend/services/personal_graph_service.py
   
   class PersonalGraphService:
       def build_personal_graph(self, email_pairs):
           """Build graph from personal email history"""
           personal_graph = nx.DiGraph()
           
           for pair in email_pairs:
               # Extract entities using LLM
               entities = self.extract_entities(pair["original_message"])
               
               # Extract user's response patterns
               response_pattern = self.analyze_response(pair["user_reply"])
               
               # Build graph
               for entity in entities:
                   personal_graph.add_node(entity, type="personal_entity")
                   personal_graph.add_edge(
                       entity, 
                       response_pattern,
                       relation="USER_RESPONDS_WITH"
                   )
           
           return personal_graph
       
       def extract_entities(self, text):
           """Extract entities using LLM"""
           prompt = f"""
           Extract key entities from this email:
           {text}
           
           Return as JSON array: ["entity1", "entity2", ...]
           """
           # Call Ollama
           response = ollama.chat(...)
           return json.loads(response)
       
       def merge_with_main_graph(self, personal_graph, main_graph):
           """Merge personal graph with main graph"""
           # Add personal nodes to main graph
           main_graph.add_nodes_from(personal_graph.nodes(data=True))
           main_graph.add_edges_from(personal_graph.edges(data=True))
           
           return main_graph
   ```

**Benefits:**
- ✅ Personal relationships in graph
- ✅ Better context understanding
- ✅ Unified graph structure

---

### **Method 4: Real-Time Learning from User Edits**

**Concept:** Learn from how users edit generated replies.

**Architecture:**
```
Generated Reply → User Edits → Learn Patterns → Update Model
```

**Implementation:**

1. **Track User Edits:**
   ```javascript
   // In chrome-extension/content.js
   
   function trackUserEdits(originalDraft, finalReply) {
       // Compare original vs final
       const edits = diff(originalDraft, finalReply);
       
       // Send to backend for learning
       fetch(`${API_BASE_URL}/learn-from-edit`, {
           method: 'POST',
           body: JSON.stringify({
               original: originalDraft,
               edited: finalReply,
               edits: edits,
               email_context: currentEmailContext
           })
       });
   }
   ```

2. **Learn from Edits:**
   ```python
   # In backend/api/routes.py
   
   @router.post("/learn-from-edit")
   async def learn_from_edit(edit_data: EditData):
       """Learn from user edits to improve future generations"""
       
       # Analyze what user changed
       changes = analyze_edits(edit_data.original, edit_data.edited)
       
       # Update personal style model
       style_service.update_from_edit(
           original=edit_data.original,
           edited=edit_data.edited,
           context=edit_data.email_context
       )
       
       # Store as new example
       personal_email_service.add_pair(
           original=edit_data.email_context.body,
           reply=edit_data.edited
       )
   ```

**Benefits:**
- ✅ Continuous improvement
- ✅ Adapts to user preferences
- ✅ No manual data collection needed

---

### **Method 5: Gmail API Integration (Most Innovative)**

**Concept:** Directly access Gmail API from Chrome Extension to extract personal history.

**Architecture:**
```
Chrome Extension → Gmail API → Extract History → Process → Store Locally
```

**Implementation:**

1. **Gmail API Setup:**
   ```javascript
   // In chrome-extension/background.js
   
   // Request Gmail API access
   chrome.identity.getAuthToken({ interactive: true }, (token) => {
       // Use token to access Gmail API
       fetch('https://www.googleapis.com/gmail/v1/users/me/messages', {
           headers: {
               'Authorization': `Bearer ${token}`
           }
       });
   });
   ```

2. **Extract Email Pairs:**
   ```javascript
   // In chrome-extension/personal-data-extractor.js
   
   class PersonalDataExtractor {
       async extractEmailPairs(limit = 500) {
           // Get sent emails
           const sentEmails = await this.getSentEmails(limit);
           
           const pairs = [];
           for (const email of sentEmails) {
               // Get thread
               const thread = await this.getThread(email.threadId);
               
               // Find original message
               const original = this.findOriginalMessage(thread);
               
               pairs.push({
                   original_message: original.body,
                   user_reply: email.body,
                   subject: email.subject,
                   date: email.date
               });
           }
           
           return pairs;
       }
       
       async syncToBackend(pairs) {
           // Send to backend for processing
           await fetch(`${API_BASE_URL}/sync-personal-data`, {
               method: 'POST',
               body: JSON.stringify({ pairs })
           });
       }
   }
   ```

3. **Backend Processing:**
   ```python
   # In backend/api/routes.py
   
   @router.post("/sync-personal-data")
   async def sync_personal_data(pairs: List[EmailPair]):
       """Process and store personal email pairs"""
       
       # Embed and store
       for pair in pairs:
           vector = embedder.encode(pair.original_message)
           
           qdrant.upsert(
               collection_name="personal_email_pairs",
               points=[{
                   "id": pair.id,
                   "vector": vector,
                   "payload": {
                       "type": "personal_pair",
                       "original_message": pair.original_message,
                       "user_reply": pair.user_reply,
                       "subject": pair.subject,
                       "date": pair.date
                   }
               }]
           )
       
       return {"status": "synced", "count": len(pairs)}
   ```

**Benefits:**
- ✅ Automatic data collection
- ✅ No manual export needed
- ✅ Always up-to-date
- ✅ Works directly from browser

---

### **Method 6: Hybrid Prompt Engineering**

**Concept:** Use personal examples in the prompt itself, not just retrieval.

**Implementation:**

```python
# In backend/services/ollama_service.py

def _build_prompt(self, email_text, intent, faq_hits, graph_hits, 
                  personal_examples, expanded_graph, user_name, user_tone):
    
    # Build personal examples section
    personal_section = ""
    if personal_examples:
        personal_section = "\n📧 YOUR PAST REPLIES TO SIMILAR EMAILS:\n"
        for i, ex in enumerate(personal_examples[:3], 1):
            personal_section += f"""
{i}. Original Email:
   "{ex['original_message'][:200]}..."
   
   Your Reply:
   "{ex['user_reply']}"
   
"""
    
    prompt = f"""You are {user_name}, known for being {user_tone}.

Your job is to draft a short, natural, and professional email reply.

---

✉️ **Incoming Email**
\"\"\"{email_text}\"\"\"

🎯 **Detected Intent**: {intent}

📘 **Relevant FAQs**
{faq_section}

🧩 **Graph Context**
{graph_section}

{personal_section}  # NEW: Personal examples

🔗 **Related Concepts**
{expansion_section}

---

Write your reply in {user_name}'s tone:
- Match the style of your past replies above
- Use the same level of formality
- Include similar details (links, availability, etc.)
- Keep the reply under 120 words.
"""
```

**Benefits:**
- ✅ Direct style mimicry
- ✅ Simple to implement
- ✅ Works with existing system

---

## 🎯 **Recommended Implementation Plan**

### **Phase 1: Quick Win (Method 6 - Hybrid Prompt)**
- Add personal examples to prompt
- Use existing Qdrant infrastructure
- Minimal code changes
- **Time: 1-2 days**

### **Phase 2: Data Collection (Method 5 - Gmail API)**
- Integrate Gmail API in extension
- Extract email pairs automatically
- Store in Qdrant
- **Time: 3-5 days**

### **Phase 3: Advanced (Method 2 - Style Embedding)**
- Fine-tune embedding model
- Style-aware retrieval
- Better personalization
- **Time: 1-2 weeks**

### **Phase 4: Learning (Method 4 - Real-Time Learning)**
- Track user edits
- Learn from feedback
- Continuous improvement
- **Time: 1 week**

---

## 📊 **Comparison of Methods**

| Method | Complexity | Effectiveness | Innovation | Time |
|--------|-----------|---------------|------------|------|
| **1. Hybrid KB** | Medium | High | Medium | 3-5 days |
| **2. Style Embedding** | High | Very High | High | 1-2 weeks |
| **3. Personal Graph** | High | High | High | 1 week |
| **4. Real-Time Learning** | Medium | Very High | Very High | 1 week |
| **5. Gmail API** | Medium | High | Very High | 3-5 days |
| **6. Hybrid Prompt** | Low | Medium | Low | 1-2 days |

---

## 🚀 **Quick Start: Method 6 (Easiest)**

Want to get started quickly? Here's the simplest implementation:

1. **Add personal email pairs to Qdrant:**
   ```python
   # One-time script: sync_personal_emails.py
   import json
   from backend.services.qdrant_service import QdrantService
   from backend.services.embedding_service import EmbeddingService
   
   # Load personal email pairs (from Gmail export or manual)
   with open('personal_email_pairs.json', 'r') as f:
       pairs = json.load(f)
   
   qdrant = QdrantService()
   embedder = EmbeddingService()
   
   for pair in pairs:
       vector = embedder.encode(pair['original_message'])
       qdrant.client.upsert(
           collection_name="personal_email_pairs",
           points=[{
               "id": pair['id'],
               "vector": vector,
               "payload": pair
           }]
       )
   ```

2. **Update RAG service to include personal examples:**
   ```python
   # In rag_service.py
   personal_hits = self.qdrant_service.search(
       query_vector, 
       collection="personal_email_pairs",
       limit=3
   )
   ```

3. **Update prompt to include personal examples:**
   ```python
   # In ollama_service.py
   # Add personal_examples parameter and include in prompt
   ```

**That's it!** You now have personal style integration. 🎉

---

## 💡 **Most Innovative: Method 4 + Method 5 Combined**

Combine **Gmail API extraction** (Method 5) with **real-time learning** (Method 4):

1. **Extract personal history** automatically from Gmail
2. **Learn from user edits** in real-time
3. **Continuously improve** without manual work

This creates a **self-improving system** that gets better with use!

---

Would you like me to implement any of these methods? I recommend starting with **Method 6** (quick win) and then adding **Method 5** (Gmail API) for automatic data collection.

