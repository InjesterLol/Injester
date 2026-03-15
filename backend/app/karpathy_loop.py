"""Karpathy AutoResearch loop — the system that optimizes itself.

The agent reads its own prompt, runs the restructure, scores itself,
identifies what failed, improves the prompt, and repeats.
"""

import json

import openai

from app.benchmark import score_content
from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL
from app.optimizer import DEFAULT_RESTRUCTURE_PROMPT, optimize_content

nebius_client = openai.OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)


def improve_prompt(
    current_prompt: str,
    score: int,
    total: int,
    failed_questions: list[str],
    answers: list[dict],
) -> str:
    """Ask the model to improve its own restructuring prompt."""
    meta_prompt = f"""You are optimizing a prompt that converts webpages into AI agent-readable format.

Current prompt:
{current_prompt}

Score: {score}/{total}
Failed questions (agent could not answer these from the output):
{json.dumps(failed_questions)}

Full answer details:
{json.dumps(answers)}

Write an IMPROVED version of the restructuring prompt that would help the agent
answer the failed questions. Focus on extracting the specific information that was missing.

Return ONLY the new prompt text, nothing else. Keep the {{content}} placeholder."""

    response = nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": meta_prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


def run_loop(
    clean_text: str,
    questions: list[str],
    max_iterations: int = 3,
) -> dict:
    """Run the full Karpathy AutoResearch optimization loop.

    Returns the iteration log and the best result.
    """
    current_prompt = DEFAULT_RESTRUCTURE_PROMPT
    log = []
    best_score = -1
    best_result = None

    for i in range(max_iterations):
        # Step 1: Optimize content with current prompt
        opt_result = optimize_content(clean_text, current_prompt)
        optimized_text = json.dumps(opt_result["optimized"])

        # Step 2: Benchmark
        bench = score_content(optimized_text, questions)
        score = bench["score"]
        total = bench["total"]

        # Step 3: Identify failures
        failed = [
            a["question"]
            for a in bench["answers"]
            if not a.get("answerable", False)
        ]

        entry = {
            "version": i + 1,
            "score": score,
            "total": total,
            "failed_questions": failed,
            "prompt_snippet": current_prompt[:200],
            "kept": score > best_score,
        }
        log.append(entry)

        if score > best_score:
            best_score = score
            best_result = opt_result

        # Step 4: If perfect score, stop
        if score == total:
            break

        # Step 5: Improve prompt for next iteration
        current_prompt = improve_prompt(
            current_prompt, score, total, failed, bench["answers"]
        )

    return {
        "log": log,
        "best_score": best_score,
        "best_total": len(questions),
        "best_result": best_result,
        "iterations": len(log),
    }
