import json
import numpy as np
from openai import OpenAI

client = OpenAI()

def build_embeddings(chunks_path="data/knowledge/chunks.jsonl",
                     out_path="data/knowledge/embeddings.npz",
                     model="text-embedding-3-small"):
    texts, meta = [], []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texts.append(obj["text"])
            meta.append({k: v for k, v in obj.items() if k != "text"})

    emb = client.embeddings.create(model=model, input=texts)
    vectors = np.array([e.embedding for e in emb.data], dtype=np.float32)
    np.savez_compressed(out_path, vectors=vectors, meta=json.dumps(meta), texts=json.dumps(texts))
    return out_path
