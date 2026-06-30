import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from openai import OpenAI
from mangum import Mangum

from rag.embeddings import get_embedding
from rag.vectorstore import search, load_store

# -------------------------
# API Key Auth
# -------------------------
API_KEY = os.getenv("MY_API_KEY")
print("API KEY LOADED:", API_KEY)
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured on server")
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key
# -------------------------
# App setup
# -------------------------
app = FastAPI(
    title="Fyno RAG",
    swagger_ui_parameters={"persistAuthorization": True}
)
client = OpenAI()

print("🔥 App loaded")

# -------------------------
# Swagger auth button
# -------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Fyno RAG",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# -------------------------
# Load vector DB
# -------------------------
@app.on_event("startup")
def startup_event():
    load_store()

# -------------------------
# Request schema
# -------------------------
class Question(BaseModel):
    question: str

# -------------------------
# Health check (public)
# -------------------------
@app.get("/")
def root():
    return {"message": "fyno_rag is running"}

# -------------------------
# Ask endpoint (protected)
# -------------------------
@app.post("/ask")
def ask_question(payload: Question, api_key: str = Security(verify_api_key)):
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

# Mangum wraps app for Vercel — keep app as FastAPI for local uvicorn
handler = Mangum(app)