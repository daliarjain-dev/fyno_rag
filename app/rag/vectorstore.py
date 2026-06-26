import faiss
import numpy as np
import os
import pickle

INDEX_PATH = "data/faiss.index"
DOCS_PATH = "data/documents.pkl"

index = faiss.IndexFlatL2(1536)
documents = []

# -------------------------
# SAVE
# -------------------------
def save_store():
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

# -------------------------
# LOAD
# -------------------------
def load_store():
    global index, documents
    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(DOCS_PATH, "rb") as f:
            documents = pickle.load(f)
        print(f"Loaded {index.ntotal} embeddings from disk")
    else:
        print("No existing index found")

# -------------------------
# ADD
# -------------------------
def add_embedding(vector, doc):
    vector = np.array(vector).astype("float32")
    if vector.ndim == 1:
        vector = np.expand_dims(vector, axis=0)

    index.add(vector)
    documents.append(doc)

# -------------------------
# SEARCH
# -------------------------
def search(query_embedding, k=5):
    if index.ntotal == 0:
        return []

    query_embedding = np.array(query_embedding).astype("float32")
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)

    D, I = index.search(query_embedding, k)

    results = []
    for i in I[0]:
        if 0 <= i < len(documents):
            results.append(documents[i])

    return results

def store_size():
    return index.ntotal