# graphrag.py

import json
import re
import subprocess
import warnings

from qdrant_client import QdrantClient
from qdrant_client import models as qmodels
from sentence_transformers import SentenceTransformer

from llama_index.core import Document, Settings, StorageContext, KnowledgeGraphIndex
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

warnings.filterwarnings("ignore", category=UserWarning)

# =========================
# 1) Setup
# =========================
print(">>> Initializing services/models...")
client = QdrantClient(host="localhost", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
ollama_llm = Ollama(model="llama3", request_timeout=600)

# LlamaIndex global settings
Settings.llm = ollama_llm
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Neo4j graph store (use 127.0.0.1 to avoid IPv6 resolution oddities)
graph_store = Neo4jGraphStore(
    url="neo4j://127.0.0.1:7687",
    username="neo4j",
    password="test1234",
    database="neo4j",  # explicit is better with Neo4j 5.x
)

# =========================
# 2) Load dataset
# =========================
print(">>> Loading dataset...")
with open("emails_dataset_with_replies.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

# =========================
# 3) Build Knowledge Graph
# =========================
print(">>> Building Knowledge Graph index (this can take several minutes on first run)...")
documents = [
    Document(
        text=f"{d['subject']} {d['body_text']} {d['reply_text']}",
        metadata={
            "subject": d.get("subject"),
            "intent": d.get("intent_label"),
            "sender": d.get("sender_email"),
        },
    )
    for d in data
]

index = KnowledgeGraphIndex.from_documents(
    documents=documents,
    max_triplets_per_chunk=10,  # tune down to 3–5 if you want faster graph build
    storage_context=StorageContext.from_defaults(graph_store=graph_store),
)
print(">>> Knowledge Graph built.\n")

# =========================
# 4) Build Vector Index in Qdrant
# =========================
COLLECTION = "emails_rag"
VECTOR_SIZE = 384

def ensure_qdrant_collection(name: str, size: int = VECTOR_SIZE):
    """Create a fresh collection. If it exists, drop and recreate."""
    try:
        if client.collection_exists(name):
            print(f">>> Deleting existing Qdrant collection: {name}")
            client.delete_collection(name)
        print(f">>> Creating Qdrant collection: {name}")
        client.create_collection(
            collection_name=name,
            vectors_config=qmodels.VectorParams(
                size=size,
                distance=qmodels.Distance.COSINE,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Failed to ensure Qdrant collection '{name}': {e}") from e

print(">>> Building / refreshing Qdrant vector index...")
ensure_qdrant_collection(COLLECTION, VECTOR_SIZE)

vectors, payloads = [], []
for d in data:
    vec = embedder.encode(d["body_text"]).tolist()
    vectors.append(vec)
    payloads.append({
        "subject": d.get("subject"),
        "body_text": d.get("body_text"),
        "reply_text": d.get("reply_text"),
        "intent": d.get("intent_label"),
        "sender": d.get("sender_email"),
    })

client.upsert(
    collection_name=COLLECTION,
    points=qmodels.Batch(
        ids=list(range(len(vectors))),
        vectors=vectors,
        payloads=payloads,
    ),
)
print(f">>> Upserted {len(vectors)} vectors into Qdrant collection '{COLLECTION}'.\n")

# =========================
# 5) Helpers
# =========================
def extract_entities(email_text: str):
    sender = re.search(r"from ([A-Za-z\s]+)", email_text, re.IGNORECASE)
    company = re.search(r"at ([A-Za-z\s]+)", email_text, re.IGNORECASE)
    text_lower = email_text.lower()
    if "schedule" in text_lower or "connect" in text_lower:
        intent = "interview_schedule"
    elif "unfortunately" in text_lower:
        intent = "rejection"
    else:
        intent = "application_update"
    return {
        "sender": sender.group(1).strip() if sender else "Unknown",
        "company": company.group(1).strip() if company else "Unknown",
        "intent": intent,
    }

def qdrant_topk_by_vector(vec, top_k=5):
    """Use new query_points; fall back to deprecated search if needed."""
    try:
        qp = client.query_points(
            collection_name=COLLECTION,
            query=qmodels.Query(vector=vec, limit=top_k),
        )
        return qp.points  # list[ScoredPoint]
    except Exception:
        # Backward compatibility if SDK versions differ
        return client.search(
            collection_name=COLLECTION,
            query_vector=vec,
            limit=top_k,
        )

# =========================
# 6) Hybrid Retrieval
# =========================
def retrieve_hybrid_context(incoming_email: str):
    info = extract_entities(incoming_email)
    print(f" Extracted Info: {info}")

    # Semantic (Qdrant)
    query_vec = embedder.encode(incoming_email).tolist()
    results = qdrant_topk_by_vector(query_vec, top_k=5)

    # Graph (LlamaIndex KG) — use a query engine (newer LlamaIndex APIs)
    qe = index.as_query_engine()
    kg_query = f"Find emails or entities related to {info['intent']} or {info['company']}"
    graph_results = qe.query(kg_query)

    # LlamaIndex Response object may store text on .response or .text depending on version
    graph_context = getattr(graph_results, "response", None)
    if graph_context is None:
        graph_context = getattr(graph_results, "text", str(graph_results))

    # Build hybrid context
    semantic_context = "\n\n".join([
        (r.payload["body_text"] if hasattr(r, "payload") else r.get("payload", {}).get("body_text", ""))
        for r in results
    ])

    return f"Semantic Context:\n{semantic_context}\n\nGraph Context:\n{graph_context}"

# =========================
# 7) Generate reply (Ollama CLI)
# =========================
def generate_reply(incoming_email: str):
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
        stderr=subprocess.PIPE,
    )
    print("\n--- Generated Reply ---\n")
    print(result.stdout.decode("utf-8").strip())

# =========================
# 8) Run
# =========================
if __name__ == "__main__":
    incoming_email = """
Hey Ali, we really liked your application!
Would you require sponsorship?
Let me know a good time to connect.
"""
    generate_reply(incoming_email)
