

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import subprocess


def load_dataset(path: str):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]


client = QdrantClient(host="localhost", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def create_collection(name="emails_personalized"):
    client.recreate_collection(
        collection_name=name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )


def ingest_dataset(data, collection="emails_personalized"):
    payloads, vectors = [], []

    for d in tqdm(data, desc="Embedding emails"):
        vec = embedder.encode(d["body_text"]).tolist()
        payloads.append({
            "message_id": d["message_id"],
            "thread_id": d["thread_id"],
            "subject": d["subject"],
            "intent": d["intent_label"],
            "sender": d["sender_email"],
            "body_text": d["body_text"],
            "reply_text": d["reply_text"]
        })
        vectors.append(vec)

    client.upsert(
        collection_name=collection,
        points=models.Batch(
            ids=[i for i in range(len(payloads))],
            vectors=vectors,
            payloads=payloads,
        )
    )
    print(f"Ingested {len(payloads)} email–reply pairs into Qdrant.")



def retrieve_context(incoming_email, collection="emails_personalized", top_k=5):
    query_vec = embedder.encode(incoming_email).tolist()
    results = client.search(
        collection_name=collection,
        query_vector=query_vec,
        limit=top_k,
    )
    return [
        {
            "subject": r.payload["subject"],
            "intent": r.payload["intent"],
            "body_text": r.payload["body_text"],
            "reply_text": r.payload["reply_text"],
            "similarity": r.score
        }
        for r in results
    ]


def generate_with_ollama(model: str, prompt: str) -> str:
    """Run Ollama model locally"""
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def generate_personalized_reply(incoming_email: str, retrieved_docs, model="llama3"):
    # Build prompt using how user has replied before
    examples = "\n\n".join([
        f"[{r['intent']}]\nIncoming: {r['body_text']}\nUser's Reply: {r['reply_text']}"
        for r in retrieved_docs
    ])

    prompt = f"""
You are Ali's personal email assistant.
Use the examples below to understand Ali's usual tone and style when replying to similar emails.

--- Examples of Ali's Past Replies ---
{examples}

--- New Incoming Email ---
{incoming_email}

Now, write a new reply email that matches Ali's usual tone and structure.
Be polite, natural, and concise.
"""

    return generate_with_ollama(model, prompt)



if __name__ == "__main__":
    dataset = load_dataset("emails_dataset_with_replies.jsonl")

    create_collection("emails_personalized")
    ingest_dataset(dataset, "emails_personalized")

    
    incoming_email = """
Hey Ali,
We really liked your application. Will you require sponsorship?
Let me know a time we can connect.
"""

retrieved = retrieve_context(incoming_email, "emails_personalized", top_k=5)

print("\n--- Retrieved Context ---")
for r in retrieved:
    print(f"- {r['intent']}: {r['subject']} ({r['similarity']:.3f})")

print("\n--- Generated Personalized Reply ---")
reply = generate_personalized_reply(incoming_email, retrieved, model="llama3")
print(reply)

