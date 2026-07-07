import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse
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
# Fyno webhook verification (public)
# -------------------------
@app.get("/ask")
async def verify_fyno(request: Request):
    token = request.query_params.get("fyno_token")
    if token:
        return PlainTextResponse(token, status_code=200)
    return PlainTextResponse("no token", status_code=400)

# -------------------------
# Ask endpoint (protected)
# -------------------------
@app.post("/ask")
def ask_question(payload: Question, api_key: str = Security(verify_api_key)):
    print("🚨🚨🚨 DEBUG MARKER - THIS IS THE LATEST CODE 🚨🚨🚨")
    question = payload.question

    query_embedding = get_embedding(question)
    results = search(query_embedding, k=8)

    if not results:
        return {"answer": "No relevant information found.", "sources": "", "source_list": []}

    primary = results[:3]
    secondary = results[3:]

    context = "MOST RELEVANT:\n"
    context += "\n".join([c["content"] for c in primary])

    if secondary:
        context += "\n\nRELATED INFO:\n"
        context += "\n".join([c["content"] for c in secondary])

        print("=== CONTEXT SENT TO MODEL ===")
        print(context)
        print("=== END CONTEXT ===")

        prompt = f"""You are answering questions for someone who is brand new to Fyno — likely a new intern who has never opened the platform before and has zero prior context. Do not assume they know any Fyno-specific terms, where anything is located in the UI, or what screen they're currently on.

First, decide what kind of question this is:
- **Conceptual/definitional** — asking what something IS, what it's for, or how it compares to something else (e.g., "What is Fyno?", "What is a workflow?", "What's the difference between X and Y?"). These do NOT need step-by-step instructions.
- **Procedural/how-to** — asking how to DO something, set something up, or complete a task (e.g., "How do I integrate WhatsApp?", "How do I create a workflow?"). These DO need step-by-step instructions.

For conceptual/definitional questions:
- Answer directly and clearly in a few short paragraphs — a plain-language explanation of what it is, why it matters, and what it's used for.
- Do NOT invent steps, actions, or instructions just to fill space. If the question doesn't involve doing something in the UI, don't describe UI navigation at all.
- It's fine for this kind of answer to just be explanatory prose (with occasional *bold* for key terms) rather than a bulleted list.

For procedural/how-to questions, follow this structure:
Critical rule for step-by-step instructions: Never start a step with an abstract action like "complete the verification" or "click Add Account" without first saying WHERE that happens. Every step must be concrete enough that someone looking at Fyno for the first time could actually follow it. For example:
- Bad: "Start by completing the verification process for your WhatsApp account."
- Good: "Go to *Integrations* in the left sidebar, then click *WhatsApp*. You'll see a verification screen — this is where you'll connect your number."

If the context doesn't tell you exactly where a button, tab, or screen is located, say so explicitly (e.g., "the context doesn't specify exactly where this button is, but it should appear after step X") rather than skipping straight to the action.

Structure your answer like this:
1. One sentence on what the person is about to do and why (the end goal, in plain language).
2. Where to start — the exact screen, tab, or menu to open first.
3. Each subsequent step, always naming the screen/location before the action taken on it.
4. Define any Fyno-specific term the first time it's used (e.g., "a *workflow* — the automated sequence Fyno follows when a message comes in").

Formatting rules (this will be read on WhatsApp):
- Use *bold* (single asterisks) for key terms, button names, and screen/tab names.
- Use a leading dash "- " for each item in a list, on its own line.
- Keep paragraphs short (2-3 sentences max).
- Do not use markdown headers (#), tables, or numbered lists with periods — use dashes or bolded step labels instead.

Strict rules:
- Only use information from the context below. Do not invent UI locations, button names, or steps that aren't supported by it.
- If the context is missing a concrete detail (like exact button location), say so rather than guessing or glossing over it.

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )

    # Deduplicate source URLs while keeping order
    seen = set()
    unique_urls = []
    for c in results:
        url = c["metadata"]["url"]
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    sources_text = "\n".join(unique_urls)

    return {
        "answer": response.choices[0].message.content,
        "sources": sources_text,        # clean plain-text URLs, one per line
        "source_list": unique_urls      # keep the raw list too, in case you need it elsewhere
    }
# Mangum wraps app for Vercel — keep app as FastAPI for local uvicorn
handler = Mangum(app)
