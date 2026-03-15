"""Extraction layer — Tavily for public URLs, direct fetch for proxy/local."""

import httpx
from bs4 import BeautifulSoup
from tavily import TavilyClient

from app.config import TAVILY_API_KEY


def _extract_with_tavily(url: str) -> str:
    """Use Tavily for public URLs."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    result = client.extract([url])
    if not result.get("results"):
        return ""
    return result["results"][0].get("raw_content", "")


def _extract_direct(url: str) -> str:
    """Fetch + strip HTML for local/proxy URLs that Tavily can't reach."""
    resp = httpx.get(url, timeout=15, follow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)


def extract_url(url: str, use_tavily: bool = True) -> dict:
    """Extract clean content from a URL.

    Args:
        url: The URL to extract.
        use_tavily: If True, use Tavily. If False, fetch directly (for proxy sites).
    """
    try:
        if use_tavily:
            raw_content = _extract_with_tavily(url)
        else:
            raw_content = _extract_direct(url)
    except Exception as e:
        return {"url": url, "raw_content": "", "error": str(e)}

    return {
        "url": url,
        "raw_content": raw_content,
        "char_count": len(raw_content),
    }
