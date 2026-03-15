"""HTML Generator — converts Karpathy-optimized JSON into browsable AI-optimized HTML.

The generated HTML mirrors the same booking flow as the proxy site but with:
- Semantic form fields with clear labels and data attributes
- Visible action buttons with descriptive text
- Structured data in clean cards
- Minimal CSS for agent readability
"""

import hashlib
import json
import os
from pathlib import Path

import openai

from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL

GENERATED_DIR = Path(__file__).parent.parent / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

nebius_client = openai.OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)

HTML_GENERATION_PROMPT = """You are an expert web developer creating an AI-agent-optimized HTML page.

Given this structured data about a webpage, generate a complete, browsable HTML page that:
1. Contains ALL the same data and booking functionality as the original
2. Uses semantic HTML5 elements (form, label, input, select, button)
3. Every form field has a clear <label> with a `for` attribute
4. Every interactive element has a descriptive `data-action` attribute
5. Every entity has a `data-entity-type` attribute (price, date, flight, guest-count, etc.)
6. Uses a clean, minimal CSS stylesheet (inline in <style>)
7. Has a multi-step booking flow: search results → selection → passenger/guest info → payment → confirmation
8. Includes realistic mock data that matches the original page content
9. Is fully functional with standard HTML forms (no JavaScript required)
10. Each booking step is a separate <section> with a clear heading

The page MUST be navigable by a Playwright browser agent using only:
- Clicking buttons and links
- Filling text inputs
- Selecting dropdown options
- Reading text content

Structured data from the original page:
{optimized_json}

Original page URL: {url}
Page type: {page_type}

Generate the COMPLETE HTML page. Return ONLY the HTML, no markdown fencing."""

UNITED_FLIGHT_DATA = """
<section id="search-results" data-step="1">
  <h2>Flight Search Results: SFO to NYC</h2>
  <div class="flight-card" data-entity-type="flight" data-flight-id="UA101">
    <h3>United UA101 — Nonstop</h3>
    <p data-entity-type="price">$189</p>
    <p data-entity-type="duration">5h 25m</p>
    <p data-entity-type="departure">Departs: 8:00 AM SFO</p>
    <p data-entity-type="arrival">Arrives: 4:25 PM JFK</p>
    <p data-entity-type="baggage-fee">Baggage: $35 per checked bag</p>
    <button data-action="select-flight" data-flight-id="UA101">Select This Flight</button>
  </div>
  <div class="flight-card" data-entity-type="flight" data-flight-id="UA205">
    <h3>United UA205 — Nonstop</h3>
    <p data-entity-type="price">$219</p>
    <p data-entity-type="duration">5h 30m</p>
    <p data-entity-type="departure">Departs: 12:30 PM SFO</p>
    <p data-entity-type="arrival">Arrives: 9:00 PM JFK</p>
    <p data-entity-type="baggage-fee">Baggage: $35 per checked bag</p>
    <button data-action="select-flight" data-flight-id="UA205">Select This Flight</button>
  </div>
  <div class="flight-card" data-entity-type="flight" data-flight-id="UA318">
    <h3>United UA318 — 1 Stop (ORD)</h3>
    <p data-entity-type="price">$149</p>
    <p data-entity-type="duration">8h 10m</p>
    <p data-entity-type="departure">Departs: 6:15 AM SFO</p>
    <p data-entity-type="arrival">Arrives: 5:25 PM EWR</p>
    <p data-entity-type="baggage-fee">Baggage: $35 per checked bag</p>
    <button data-action="select-flight" data-flight-id="UA318">Select This Flight</button>
  </div>
</section>
"""


def generate_optimized_html(
    optimized_json: dict,
    url: str,
    page_type: str = "flight_booking",
) -> dict:
    """Generate a browsable AI-optimized HTML page from structured JSON.

    Returns dict with file_path, served_url, and the HTML content.
    """
    prompt = HTML_GENERATION_PROMPT.format(
        optimized_json=json.dumps(optimized_json, indent=2)[:6000],
        url=url,
        page_type=page_type,
    )

    response = nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )

    html_content = response.choices[0].message.content

    # Strip markdown fencing if present
    if html_content.startswith("```"):
        lines = html_content.split("\n")
        html_content = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    # Generate deterministic filename from URL
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    filename = f"{page_type}_{url_hash}.html"
    filepath = GENERATED_DIR / filename

    filepath.write_text(html_content)

    return {
        "filename": filename,
        "filepath": str(filepath),
        "served_url": f"/generated/{filename}",
        "html_length": len(html_content),
    }


def generate_united_optimized(optimized_json: dict, url: str) -> dict:
    """Generate an optimized United Airlines booking page."""
    return generate_optimized_html(optimized_json, url, page_type="united_booking")


def generate_airbnb_optimized(optimized_json: dict, url: str) -> dict:
    """Generate an optimized Airbnb listing page."""
    return generate_optimized_html(optimized_json, url, page_type="airbnb_listing")
