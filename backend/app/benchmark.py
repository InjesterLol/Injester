"""Benchmark layer — proves the optimization works."""

import json

import openai

from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL

nebius_client = openai.OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)


def score_content(content: str, questions: list[str]) -> dict:
    """Run benchmark questions against content and score answers."""
    prompt = f"""You are an AI agent evaluating webpage content.

Content:
{content[:8000]}

Answer each question below. If the content provides enough information to answer,
give the answer. If not, respond with "CANNOT_ANSWER".

Questions:
{json.dumps(questions)}

Return valid JSON: a list of objects with "question", "answer", and "answerable" (boolean).
Return ONLY valid JSON, no markdown fencing."""

    response = nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else 0

    try:
        answers = json.loads(raw)
    except json.JSONDecodeError:
        answers = []

    answerable_count = sum(1 for a in answers if a.get("answerable", False))

    return {
        "answers": answers,
        "score": answerable_count,
        "total": len(questions),
        "tokens_used": tokens_used,
    }
