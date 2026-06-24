from .embeddings import get_embedding
from .vectorstore import search


def retrieve(question, top_k=5, per_source_limit=1):
    """
    Retrieves relevant chunks with:
    - FAISS similarity search
    - per-source deduplication
    - better ranking control
    """

    # 1. Embed the query
    q_embedding = get_embedding(question)

    # 2. Get raw FAISS results
    results = search(q_embedding, k=20)

    seen_sources = {}
    unique_results = []

    # 3. Enforce diversity (fix repeated sources problem)
    for r in results:
        metadata = r.get("metadata", {})
        source = metadata.get("source", "unknown")

        # initialize counter
        if source not in seen_sources:
            seen_sources[source] = 0

        # limit chunks per source
        if seen_sources[source] >= per_source_limit:
            continue

        seen_sources[source] += 1
        unique_results.append(r)

        # stop early if enough results
        if len(unique_results) >= top_k:
            break

    # 4. Split into top + related context
    return {
        "top": unique_results[:3],
        "related": unique_results[3:top_k]
    }