import os
from pathlib import Path


def read_mdx_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def get_project_root():
    current = Path(__file__).resolve()

    for parent in current.parents:
        if parent.name == "fyno_rag":
            return parent

    return current.parents[3]  # fallback (rare case)


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

                    text = read_mdx_file(path)

                    docs.append({
                        "url": str(path),
                        "markdown": text
                    })

    return docs