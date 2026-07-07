import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_live_image_map(doc_url: str) -> dict:
    """
    Fetches the live Fyno doc page and returns a mapping of
    image filename -> full resolved (real, working) image URL.
    """
    image_map = {}
    try:
        resp = requests.get(doc_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            print(f"[WARN] Could not fetch {doc_url} (status {resp.status_code})")
            return image_map

        soup = BeautifulSoup(resp.text, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue

            full_url = urljoin(doc_url, src)
            filename = full_url.split("/")[-1].split("?")[0]
            image_map[filename] = full_url

    except Exception as e:
        print(f"[WARN] Failed to fetch images for {doc_url}: {e}")

    return image_map