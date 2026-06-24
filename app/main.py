from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from pydantic import BaseModel

from app.rag.embeddings import get_embedding
from app.rag.vectorstore import search
from app.rag.vectorstore import load_store
from openai import OpenAI

client = OpenAI()
load_store()
app = FastAPI()

# -------------------------
# Request schema
# -------------------------
class Question(BaseModel):
    question: str

# -------------------------
# Ask endpoint
# -------------------------
@app.post("/ask")
def ask_question(payload: Question):
    question = payload.question

    # Embed question
    query_embedding = get_embedding(question)

    # Retrieve relevant chunks
    results = search(query_embedding, k=6)

    if not results:
        return {"answer": "No relevant information found in docs."}

    # Build context (relevant + less relevant)
    primary = results[:3]
    secondary = results[3:]

    context = "MOST RELEVANT:\n"
    context += "\n".join([c["content"] for c in primary])

    if secondary:
        context += "\n\nRELATED INFO:\n"
        context += "\n".join([c["content"] for c in secondary])

    # Ask LLM using retrieved context
    prompt = f"""
You are answering questions using Fyno documentation only.

Context:
{context}

Question:
{question}

Rules:
- Use ONLY the provided context
- If not found, say "Not found in documentation"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [c["metadata"]["url"] for c in results]
    }