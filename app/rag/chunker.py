import tiktoken
import hashlib
import uuid
import re
import nltk
from nltk.tokenize import sent_tokenize

# Run once outside production if needed
nltk.download("punkt", quiet=True)

encoder = tiktoken.get_encoding("cl100k_base")

MAX_TOKENS = 400
MIN_TOKENS = 80
OVERLAP_SENTENCES = 2


# -----------------------
# TOKEN HELPERS
# -----------------------
def tokenize(text):
    return encoder.encode(text)


def detokenize(tokens):
    return encoder.decode(tokens)


# -----------------------
# SPLIT BY HEADINGS
# -----------------------
def split_by_headers(text: str):
    sections = []
    current_header = "root"
    buffer = []

    for line in text.split("\n"):
        match = re.match(r"^#{1,6}\s*(.*)", line)

        if match:
            if buffer:
                sections.append({
                    "header": current_header,
                    "text": "\n".join(buffer).strip()
                })

            current_header = match.group(1).strip()
            buffer = []
        else:
            buffer.append(line)

    if buffer:
        sections.append({
            "header": current_header,
            "text": "\n".join(buffer).strip()
        })

    return sections


# -----------------------
# SENTENCE GROUPING
# -----------------------
def group_sentences(sentences):
    groups = []
    current = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = len(tokenize(sent))

        if current_tokens + sent_tokens > MAX_TOKENS:
            groups.append(current)
            current = current[-OVERLAP_SENTENCES:]  # overlap
            current_tokens = sum(len(tokenize(s)) for s in current)

        current.append(sent)
        current_tokens += sent_tokens

    if current:
        groups.append(current)

    return groups


# -----------------------
# MAIN CHUNKER
# -----------------------
def chunk_markdown(text: str, metadata: dict):
    sections = split_by_headers(text)

    chunks = []
    seen = set()

    for section_index, section in enumerate(sections):
        header = section["header"]
        content = section["text"]

        if not content.strip():
            continue

        sentences = sent_tokenize(content)
        groups = group_sentences(sentences)

        for chunk_index, group in enumerate(groups):
            chunk_text = " ".join(group).strip()

            if len(tokenize(chunk_text)) < MIN_TOKENS:
                continue

            enriched = f"SECTION: {header}\n\n{chunk_text}"

            normalized = re.sub(r"\s+", " ", enriched.strip())
            h = hashlib.sha256(normalized.encode()).hexdigest()

            if h in seen:
                continue
            seen.add(h)

            chunks.append({
                "id": str(uuid.uuid4()),
                "content": enriched,
                "metadata": {
                    **metadata,
                    "section": header,
                    "chunk_index": chunk_index,
                    "section_index": section_index
                },
                "hash": h
            })

    return chunks