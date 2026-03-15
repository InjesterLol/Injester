"""API routes for injester.lol."""

import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.agent import run_agent
from app.benchmark import score_content
from app.config import BENCHMARK_QUESTIONS, DEMO_URLS
from app.extractor import extract_url
from app.html_generator import generate_optimized_html
from app.karpathy_loop import run_loop
from app.optimizer import optimize_content
from app.ws import agent_event_callback

router = APIRouter()


class IngestRequest(BaseModel):
    url: str
    questions: list[str] | None = None
    site_type: str | None = None
    use_tavily: bool | None = None


class LoopRequest(BaseModel):
    url: str
    questions: list[str] | None = None
    site_type: str | None = None
    max_iterations: int = 3
    use_tavily: bool | None = None


class GenerateRequest(BaseModel):
    url: str
    site_type: str | None = None
    use_tavily: bool | None = None


class AgentRequest(BaseModel):
    url: str
    site_type: str = "united"


class DemoRequest(BaseModel):
    site_type: str = "united"
    max_iterations: int = 3


def _get_questions(req_questions: list[str] | None, site_type: str | None) -> list[str]:
    if req_questions:
        return req_questions
    if site_type and site_type in BENCHMARK_QUESTIONS:
        return BENCHMARK_QUESTIONS[site_type]
    return BENCHMARK_QUESTIONS["airbnb"]


def _should_use_tavily(url: str, override: bool | None) -> bool:
    if override is not None:
        return override
    if "localhost" in url or "127.0.0.1" in url or url.startswith("http://192.168"):
        return False
    return True


def _do_extract(url: str, use_tavily: bool | None):
    tavily = _should_use_tavily(url, use_tavily)
    result = extract_url(url, use_tavily=tavily)
    if not result["raw_content"]:
        raise HTTPException(
            status_code=422,
            detail=result.get("error", "Could not extract content from URL"),
        )
    return result


# --- Existing endpoints ---


@router.post("/extract")
def api_extract(req: IngestRequest):
    """Step 1: Extract clean content from URL."""
    return _do_extract(req.url, req.use_tavily)


@router.post("/optimize")
def api_optimize(req: IngestRequest):
    """Step 2: Extract + optimize via Nebius."""
    extracted = _do_extract(req.url, req.use_tavily)
    optimized = optimize_content(extracted["raw_content"])
    return {
        "extracted": extracted,
        "optimized": optimized,
    }


@router.post("/benchmark")
def api_benchmark(req: IngestRequest):
    """Step 3: Extract + optimize + benchmark raw vs. optimized."""
    questions = _get_questions(req.questions, req.site_type)
    extracted = _do_extract(req.url, req.use_tavily)
    optimized = optimize_content(extracted["raw_content"])

    raw_score = score_content(extracted["raw_content"], questions)
    opt_text = json.dumps(optimized["optimized"])
    opt_score = score_content(opt_text, questions)

    return {
        "url": req.url,
        "raw_benchmark": raw_score,
        "optimized_benchmark": opt_score,
        "improvement": {
            "raw_score": f"{raw_score['score']}/{raw_score['total']}",
            "optimized_score": f"{opt_score['score']}/{opt_score['total']}",
            "token_reduction": f"{raw_score['tokens_used']} → {opt_score['tokens_used']}",
        },
    }


@router.post("/loop")
def api_loop(req: LoopRequest):
    """Step 4: Full Karpathy AutoResearch loop."""
    questions = _get_questions(req.questions, req.site_type)
    extracted = _do_extract(req.url, req.use_tavily)

    raw_score = score_content(extracted["raw_content"], questions)

    loop_result = run_loop(
        extracted["raw_content"],
        questions,
        max_iterations=req.max_iterations,
    )

    return {
        "url": req.url,
        "raw_benchmark": raw_score,
        "loop": loop_result,
        "summary": {
            "raw_score": f"{raw_score['score']}/{raw_score['total']}",
            "optimized_score": f"{loop_result['best_score']}/{loop_result['best_total']}",
            "iterations": loop_result["iterations"],
        },
    }


# --- New endpoints ---


@router.post("/generate")
def api_generate(req: GenerateRequest):
    """Full pipeline: extract → optimize → Karpathy loop → generate HTML.

    Returns the URL of the generated AI-optimized HTML page.
    """
    questions = _get_questions(None, req.site_type)
    extracted = _do_extract(req.url, req.use_tavily)

    # Run Karpathy loop to get best optimization
    loop_result = run_loop(
        extracted["raw_content"],
        questions,
        max_iterations=3,
    )

    # Generate browsable HTML from the best optimization
    page_type = req.site_type or "general"
    html_result = generate_optimized_html(
        loop_result["best_result"]["optimized"],
        req.url,
        page_type=f"{page_type}_booking",
    )

    return {
        "url": req.url,
        "generated_url": html_result["served_url"],
        "html_length": html_result["html_length"],
        "karpathy_iterations": loop_result["iterations"],
        "best_score": f"{loop_result['best_score']}/{loop_result['best_total']}",
        "loop_log": loop_result["log"],
    }


@router.post("/run-agent")
async def api_run_agent(req: AgentRequest):
    """Run the Playwright booking agent on a URL.

    Streams events via WebSocket at /ws/agent.
    Returns the final score when complete.
    """
    result = await run_agent(
        url=req.url,
        site_type=req.site_type,
        headless=True,
        on_event=agent_event_callback,
    )
    return result


@router.post("/demo")
async def api_demo(req: DemoRequest):
    """One-click demo: extract, optimize, generate HTML, run agent on both, compare.

    This is the full demo flow for the hackathon pitch.
    Streams agent events via WebSocket at /ws/agent.
    """
    proxy_url = DEMO_URLS.get(req.site_type, DEMO_URLS["united"])
    questions = _get_questions(None, req.site_type)

    # Step 1: Extract from proxy
    extracted = _do_extract(proxy_url, use_tavily=False)

    # Step 2: Karpathy loop optimization
    loop_result = run_loop(
        extracted["raw_content"],
        questions,
        max_iterations=req.max_iterations,
    )

    # Step 3: Generate optimized HTML
    html_result = generate_optimized_html(
        loop_result["best_result"]["optimized"],
        proxy_url,
        page_type=f"{req.site_type}_booking",
    )

    # Step 4: Run agent on RAW proxy site (baseline — expect low score)
    await agent_event_callback({"type": "demo_phase", "phase": "raw_agent", "url": proxy_url})
    raw_agent = await run_agent(
        url=proxy_url,
        site_type=req.site_type,
        headless=True,
        on_event=agent_event_callback,
    )

    # Step 5: Run agent on OPTIMIZED site (proof — expect high score)
    # Construct full URL for generated page
    optimized_url = f"http://localhost:8000{html_result['served_url']}"
    await agent_event_callback({"type": "demo_phase", "phase": "optimized_agent", "url": optimized_url})
    optimized_agent = await run_agent(
        url=optimized_url,
        site_type=req.site_type,
        headless=True,
        on_event=agent_event_callback,
    )

    return {
        "site_type": req.site_type,
        "proxy_url": proxy_url,
        "generated_url": html_result["served_url"],
        "karpathy": {
            "iterations": loop_result["iterations"],
            "best_score": f"{loop_result['best_score']}/{loop_result['best_total']}",
            "log": loop_result["log"],
        },
        "raw_agent": {
            "score": raw_agent["score"],
            "tasks_completed": raw_agent["tasks_completed"],
            "total_tasks": raw_agent["total_tasks"],
        },
        "optimized_agent": {
            "score": optimized_agent["score"],
            "tasks_completed": optimized_agent["tasks_completed"],
            "total_tasks": optimized_agent["total_tasks"],
        },
        "comparison": {
            "raw": raw_agent["score"],
            "optimized": optimized_agent["score"],
            "improvement": f"{raw_agent['tasks_completed']} → {optimized_agent['tasks_completed']} tasks completed",
        },
    }
