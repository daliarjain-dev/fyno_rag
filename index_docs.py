from dotenv import load_dotenv
load_dotenv(override=True)

from app.rag.local_loader import load_fyno_docs_local
from app.rag.chunker import chunk_markdown
from app.rag.embeddings import get_embedding
from app.rag.vectorstore import add_embedding
from app.rag.vectorstore import save_store
docs = load_fyno_docs_local()

print(f"Loaded {len(docs)} docs")

for page in docs:
    print("Processing:", page["url"])

    metadata = {"url": page["url"]}
    chunks = chunk_markdown(page["markdown"], metadata)

    for chunk in chunks:
        embedding = get_embedding(chunk["content"])
        add_embedding(embedding, chunk)

print("Docs indexed successfully")
save_store()
print("Embeddings saved to disk")
