import json, re, subprocess
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from llama_index.core import Document

from llama_index.core import ServiceContext, StorageContext, KnowledgeGraphIndex
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import warnings
warnings.filterwarnings("ignore", category=UserWarning)



import subprocess


# 1. Setup
client = QdrantClient(host="localhost", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
ollama_llm = Ollama(model="llama3", request_timeout=600)

# 2. Loading the dataset
with open("emails_dataset_with_replies.jsonl") as f:
    data = [json.loads(line) for line in f]

# 3. Build Graph Store
graph_store = Neo4jGraphStore(
    url="bolt://localhost:7687",
    username="neo4j",
    password="test1234"
)

from llama_index.core import Settings
Settings.llm = ollama_llm
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = embed_model
documents = [
    Document(
        text=f"{d['subject']} {d['body_text']} {d['reply_text']}",
        metadata={
            "subject": d["subject"],
            "intent": d["intent_label"],
            "sender": d["sender_email"]
        }
    )
    for d in data
]

index = KnowledgeGraphIndex.from_documents(
    documents=documents,
    max_triplets_per_chunk=10,
    storage_context=StorageContext.from_defaults(graph_store=graph_store)
)

# -----------------------------
# 4. Build Vector Index in Qdrant
# -----------------------------
vectors, payloads = [], []
for d in data:
    vec = embedder.encode(d["body_text"]).tolist()
    vectors.append(vec)
    payloads.append({
        "subject": d["subject"],
        "body_text": d["body_text"],
        "reply_text": d["reply_text"],
        "intent": d["intent_label"],
        "sender": d["sender_email"]
    })

client.recreate_collection(
    collection_name="emails_rag",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
)
client.upsert(
    collection_name="emails_rag",
    points=models.Batch(ids=list(range(len(vectors))), vectors=vectors, payloads=payloads)
)

# 5. Helper: extract entities and intent
def extract_entities(email_text):
    sender = re.search(r"from ([A-Za-z\s]+)", email_text, re.IGNORECASE)
    company = re.search(r"at ([A-Za-z\s]+)", email_text, re.IGNORECASE)
    intent = "interview_schedule" if "schedule" in email_text.lower() or "connect" in email_text.lower() else \
             "rejection" if "unfortunately" in email_text.lower() else "application_update"
    return {
        "sender": sender.group(1).strip() if sender else "Unknown",
        "company": company.group(1).strip() if company else "Unknown",
        "intent": intent
    }

# 6. Graph + Vector Hybrid Retrieval

def retrieve_hybrid_context(incoming_email):
    info = extract_entities(incoming_email)
    print(f" Extracted Info: {info}")

    # Semantic retrieval
    query_vec = embedder.encode(incoming_email).tolist()
    results = client.search(collection_name="emails_rag", query_vector=query_vec, limit=5)

    # Graph retrieval (triplet-based expansion)
    graph_results = index.query(f"Find emails or entities related to {info['intent']} or {info['company']}")
    
    # Build hybrid context
    semantic_context = "\n\n".join([r.payload["body_text"] for r in results])
    graph_context = str(graph_results)
    
    return f"Semantic Context:\n{semantic_context}\n\nGraph Context:\n{graph_context}"


# 7. Generate reply

def generate_reply(incoming_email):
    context = retrieve_hybrid_context(incoming_email)
    prompt = f"""
You are Ali's AI email assistant.

Incoming email:
{incoming_email}

Relevant context from previous emails and relationships:
{context}

Write a short, polite, personalized reply consistent with Ali's usual tone.
"""
    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("\n--- Generated Reply ---\n")
    print(result.stdout.decode("utf-8"))


# 8. Run
if __name__ == "__main__":
    incoming_email = """
Hey Ali, we really liked your application!
Would you require sponsorship?
Let me know a good time to connect.
"""
    generate_reply(incoming_email)
