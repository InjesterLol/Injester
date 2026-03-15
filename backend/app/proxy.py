"""Reverse proxy that fetches a URL and serves it without iframe-blocking headers.

Uses httpx to fetch the page content and strips X-Frame-Options / CSP frame-ancestors
so the page can be embedded in an iframe on the frontend.
"""

import httpx
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse

router = APIRouter()

# Reusable async client
_client = httpx.AsyncClient(
    follow_redirects=True,
    timeout=15.0,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
)


@router.get("/proxy")
async def proxy_page(url: str):
    """Fetch a URL and return its HTML with iframe-blocking headers removed.

    Usage: /api/proxy?url=https://www.united.com/en/us
    The frontend can use this as an iframe src.
    """
    resp = await _client.get(url)

    content_type = resp.headers.get("content-type", "text/html")

    # Inject a <base> tag so relative URLs resolve correctly
    html = resp.text
    if "<head" in html.lower():
        # Insert base tag right after <head>
        import re
        html = re.sub(
            r'(<head[^>]*>)',
            rf'\1<base href="{url}">',
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    elif "<html" in html.lower():
        html = re.sub(
            r'(<html[^>]*>)',
            rf'\1<head><base href="{url}"></head>',
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    return HTMLResponse(
        content=html,
        status_code=resp.status_code,
        # Explicitly omit X-Frame-Options and restrictive CSP
        headers={
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "*",
        },
    )
