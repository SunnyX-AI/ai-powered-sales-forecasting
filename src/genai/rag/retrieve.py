import json
import numpy as np
from openai import OpenAI

client = OpenAI()

def _cosine_topk(q, M, k):
    q = q / (np.linalg.norm(q) + 1e-9)
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    sims = M @ q
    idx = np.argsort(-sims)[:k]
    return idx, sims[idx]

def retrieve(query: str, k: int = 6, store_path="data/knowledge/embeddings.npz", model="text-embedding-3-small"):
    store = np.load(store_path, allow_pickle=True)
    vectors = store["vectors"]
    meta = json.loads(store["meta"].item())
    texts = json.loads(store["texts"].item())

    q_emb = client.embeddings.create(model=model, input=query).data[0].embedding
    q_vec = np.array(q_emb, dtype=np.float32)

    idx, sims = _cosine_topk(q_vec, vectors, k)
    results = []
    for rank, i in enumerate(idx):
        results.append({
            "rank": rank + 1,
            "score": float(sims[rank]),
            "doc_title": meta[i].get("doc_title"),
            "chunk_id": meta[i].get("chunk_id"),
            "text": texts[i]
        })
    return results
