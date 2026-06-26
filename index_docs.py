from dotenv import load_dotenv
load_dotenv(override=True)

from app.rag.local_loader import load_fyno_docs_local
from app.rag.chunker import chunk_markdown
from app.rag.embeddings import get_embedding
from app.rag.vectorstore import add_embedding, save_store, store_size


def index_documents():
    """
    Load docs, chunk them, embed them, and store in vector DB.
    This is called ONCE at app startup.
    """

    # 🔒 Prevent double indexing
    if store_size() > 0:
        print("Vector store already populated. Skipping indexing.")
        return

    docs = load_fyno_docs_local()
    print(f"Loaded {len(docs)} docs")

    for page in docs:
        print("Processing:", page["url"])

        metadata = {"url": page["url"]}
        chunks = chunk_markdown(page["markdown"], metadata)

        for chunk in chunks:
            embedding = get_embedding(chunk["content"])
            add_embedding(embedding, chunk)

    save_store()
    print("Docs indexed successfully. Embeddings saved.")