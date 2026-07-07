import os
import re
from app.rag.image_resolver import get_live_image_map
from pathlib import Path
import frontmatter
IMAGE_PATTERN = re.compile(r"!\[.*?\]\((/images/[^\)]+)\)")

def get_project_root():
    current = Path(__file__).resolve()

    for parent in current.parents:
        if parent.name == "fyno_rag":
            return parent

    return current.parents[3]  # fallback (rare case)


def build_url(slug, path):
    if slug:
        return f"https://fyno.io/docs/{slug}"
    # Fallback: derive a slug from the filename if no frontmatter slug exists
    fallback_slug = path.stem  # filename without extension
    return f"https://fyno.io/docs/{fallback_slug}"


def load_fyno_docs_local():
    BASE_DIR = get_project_root()

    print("BASE DIR:", BASE_DIR)

    FOLDERS = [
        BASE_DIR / "data" / "docs",
        BASE_DIR / "pages"
    ]

    docs = []

    for folder in FOLDERS:
        if not folder.exists():
            print(f"[SKIP] Folder not found: {folder}")
            continue

        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith((".mdx", ".md")):
                    path = Path(root) / file

                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        post = frontmatter.load(f)

                    slug = post.get("slug")
                    url = build_url(slug, path)
                    content = post.content

                    image_map = {}
                    if IMAGE_PATTERN.search(content):
                        print(f"Fetching live images for: {url}")
                        image_map = get_live_image_map(url)

                    docs.append({
                        "url": url,
                        "markdown": content,
                        "image_map": image_map
                    })

    return docs