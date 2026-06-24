from dotenv import load_dotenv
load_dotenv(override=True)
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(question, context):
    prompt = f"""
Answer ONLY using the context below.
Do NOT guess.

Context:
{context}

Question:
{question}
"""

    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content