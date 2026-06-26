from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

from app.rag.embeddings import get_embedding
from app.rag.vectorstore import search, load_store

app = FastAPI()
client = OpenAI()

print("🔥 App loaded")

# -------------------------
# Load vector DB ONLY
# -------------------------
@app.on_event("startup")
def startup_event():
    print("🚀 Starting app...")
    load_store()
    print("✅ Vector store loaded")

# -------------------------
# Request schema
# -------------------------
class Question(BaseModel):
    question: str

# -------------------------
# Health check
# -------------------------
@app.get("/")
def root():
    return {"message": "fyno_rag is running"}
# -------------------------
# Ask endpoint
# -------------------------
@app.post("/ask")
def ask_question(payload: Question):
    question = payload.question

    query_embedding = get_embedding(question)
    results = search(query_embedding, k=6)

    if not results:
        return {"answer": "No relevant information found."}

    primary = results[:3]
    secondary = results[3:]

    context = "MOST RELEVANT:\n"
    context += "\n".join([c["content"] for c in primary])

    if secondary:
        context += "\n\nRELATED INFO:\n"
        context += "\n".join([c["content"] for c in secondary])

    prompt = f"""
Answer using only context:

{context}

Question: {question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [c["metadata"]["url"] for c in results]
    }

from mangum import Mangum
handler = Mangum(app)