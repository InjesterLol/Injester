"""Nebius AI optimization layer — the architect that rebuilds the room."""

import json
from typing import Optional

import openai

from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL

nebius_client = openai.OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)

DEFAULT_RESTRUCTURE_PROMPT = """Convert this webpage content into an AI agent-optimized format.

Content:
{content}

Return valid JSON with these fields:
- page_intent: what this page is for (e.g., "product purchase", "flight booking")
- primary_entities: array of typed entities with values (prices, dates, names)
- agent_actions: array of actions an agent can take on this page (typed as book/search/filter/contact)
- key_facts: 3-5 bullet facts an agent needs
- agent_summary: 2-sentence grounding context for an agent
- noise_removed_pct: estimated percentage of original content that was irrelevant

Return ONLY valid JSON, no markdown fencing."""


def optimize_content(clean_text: str, prompt_template: Optional[str] = None) -> dict:
    """Restructure clean text into agent-optimized JSON using Nebius."""
    template = prompt_template or DEFAULT_RESTRUCTURE_PROMPT
    prompt = template.format(content=clean_text[:8000])  # token budget guard

    response = nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else 0

    try:
        optimized = json.loads(raw)
    except json.JSONDecodeError:
        optimized = {"raw_response": raw, "parse_error": True}

    return {"optimized": optimized, "tokens_used": tokens_used}
