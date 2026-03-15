"""Extraction layer — Tavily for public URLs, Playwright fallback for JS-heavy sites, direct fetch for proxy/local."""

import asyncio

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
    resp = httpx.get(
        url,
        timeout=15,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)


def _extract_with_playwright(url: str) -> str:
    """Use Playwright to render JS-heavy pages and extract text content."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        # Wait for content to render
        page.wait_for_timeout(3000)

        # Get the rendered HTML and parse it
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript", "svg"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)


def extract_url(url: str, use_tavily: bool = True) -> dict:
    """Extract clean content from a URL.

    Args:
        url: The URL to extract.
        use_tavily: If True, try Tavily first. Falls back to Playwright for JS-heavy sites.
    """
    raw_content = ""
    method = "unknown"

    try:
        if use_tavily:
            raw_content = _extract_with_tavily(url)
            method = "tavily"

        # If Tavily returned empty or was skipped, try direct fetch
        if not raw_content and not use_tavily:
            raw_content = _extract_direct(url)
            method = "direct"

        # If still empty (Tavily returned nothing), try Playwright as fallback
        if not raw_content:
            raw_content = _extract_with_playwright(url)
            method = "playwright"

    except Exception as e:
        # Last resort: try Playwright if other methods raised
        if not raw_content:
            try:
                raw_content = _extract_with_playwright(url)
                method = "playwright_fallback"
            except Exception as e2:
                return {"url": url, "raw_content": "", "error": f"{str(e)} | playwright: {str(e2)}"}

    return {
        "url": url,
        "raw_content": raw_content,
        "char_count": len(raw_content),
        "method": method,
    }
