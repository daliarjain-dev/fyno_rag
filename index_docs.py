from dotenv import load_dotenv
load_dotenv(override=True)

from app.rag.local_loader import load_fyno_docs_local
from app.rag.chunker import chunk_markdown
from app.rag.embeddings import get_embedding
from app.rag.vectorstore import add_embedding, save_store, store_size
from app.rag.vectorstore import index

# In index_docs.py, not chunker.py
def index_documents():
    if store_size() > 0:
        print("Vector store already populated. Skipping indexing.")
        return

    docs = load_fyno_docs_local()
    print(f"Loaded {len(docs)} docs")

    global_seen_hashes = set()   # ← track across ALL files

    for page in docs:
        metadata = {"url": page["url"]}
        chunks = chunk_markdown(page["markdown"], metadata)

        for chunk in chunks:
            if chunk["hash"] in global_seen_hashes:
                continue
            global_seen_hashes.add(chunk["hash"])

            embedding = get_embedding(chunk["content"])
            add_embedding(embedding, chunk)

    save_store()
    print("Docs indexed successfully. Embeddings saved.")
    print("indexing complete")
    print("Total vectors in index:",index.ntotal)