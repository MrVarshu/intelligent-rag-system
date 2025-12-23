import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict

HEADERS = {"User-Agent": "rag-groq-bot/0.1 (+https://example.com)"}

def fetch_url_text(url: str, timeout: int = 10) -> Dict[str, str]:
    """
    Fetches a URL and returns a dict with:
      - url: original URL
      - title: page title (fallback to domain)
      - text: concatenated paragraph text ('' if none)
      - error: present if fetch/parsing failed
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        return {"url": url, "title": "", "text": "", "error": str(e)}

    content_type = resp.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        return {
            "url": url,
            "title": urlparse(url).netloc,
            "text": "",
            "error": f"Unsupported Content-Type: {content_type}"
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    # Best-effort extraction
    article_tag = soup.find("article")
    if article_tag:
        paragraphs = [p.get_text(strip=True) for p in article_tag.find_all("p")]
    else:
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

    paragraphs = [p for p in paragraphs if p]
    text = "\n\n".join(paragraphs)

    title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(url).netloc

    return {"url": url, "title": title, "text": text, "error": ""}


