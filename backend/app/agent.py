"""Playwright agent — navigates and books flights using LLM-driven element matching.

The agent reads the page's accessibility tree / HTML snapshot, uses Nebius LLM
to decide what to click/fill, executes the action, and captures a screenshot.
Works on both raw proxy sites (poorly) and optimized HTML (well).
"""

import asyncio
import base64
import json
from typing import Any

import openai
from playwright.async_api import Page, async_playwright

from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL
from app.agent_tasks import TASK_SETS

nebius_client = openai.AsyncOpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)

# Callback type for streaming agent events to WebSocket
EventCallback = Any  # async callable(event: dict) -> None


async def _get_page_snapshot(page: Page) -> str:
    """Get a simplified HTML snapshot of the current page for LLM consumption."""
    snapshot = await page.evaluate("""() => {
        function getSimplifiedHTML(el, depth = 0) {
            if (depth > 5) return '';
            if (!el || !el.tagName) return '';

            const tag = el.tagName.toLowerCase();
            const skip = ['script', 'style', 'svg', 'path', 'meta', 'link'];
            if (skip.includes(tag)) return '';

            let attrs = '';
            const importantAttrs = ['id', 'name', 'type', 'value', 'placeholder',
                'data-action', 'data-entity-type', 'href', 'for', 'aria-label', 'role'];
            for (const attr of importantAttrs) {
                const val = el.getAttribute(attr);
                if (val) attrs += ` ${attr}="${val}"`;
            }

            const text = el.childNodes.length === 1 && el.childNodes[0].nodeType === 3
                ? el.childNodes[0].textContent.trim().slice(0, 100)
                : '';

            let children = '';
            for (const child of el.children) {
                children += getSimplifiedHTML(child, depth + 1);
            }

            const textContent = text ? text : '';
            if (!attrs && !children && !textContent && !['button', 'input', 'select', 'a', 'h1', 'h2', 'h3', 'label', 'form'].includes(tag)) {
                return children;
            }

            return `<${tag}${attrs}>${textContent}${children}</${tag}>`;
        }
        return getSimplifiedHTML(document.body);
    }""")
    # Truncate to stay within token limits
    return snapshot[:6000] if snapshot else ""


async def _ask_llm_for_action(
    page_html: str,
    task_description: str,
    action: dict,
) -> dict:
    """Ask Nebius LLM to identify the correct element and generate a Playwright selector."""
    prompt = f"""You are an AI agent navigating a webpage using Playwright.

Current page HTML (simplified):
{page_html}

Your current task: {task_description}
Action to perform: {json.dumps(action)}

Based on the HTML, identify the EXACT element to interact with.
Return valid JSON with:
- "selector": a CSS selector or text selector that uniquely identifies the element
  (prefer: [data-action="..."], [name="..."], [id="..."], button:has-text("..."), label:has-text("...") >> input)
- "action": "click", "fill", or "select"
- "value": the value to type/select (if applicable, from the action above)
- "confidence": 0-100 how confident you are this is the right element
- "reasoning": brief explanation of why you chose this element

Return ONLY valid JSON, no markdown fencing."""

    response = await nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"selector": "", "action": action["type"], "value": action.get("value", ""), "confidence": 0, "reasoning": "Failed to parse LLM response"}


async def _take_screenshot(page: Page) -> str:
    """Take a screenshot and return as base64."""
    screenshot_bytes = await page.screenshot(full_page=False)
    return base64.b64encode(screenshot_bytes).decode("utf-8")


async def _execute_action(page: Page, llm_action: dict) -> dict:
    """Execute a single action on the page based on LLM guidance."""
    selector = llm_action.get("selector", "")
    action_type = llm_action.get("action", "click")
    value = llm_action.get("value", "")

    if not selector:
        return {"success": False, "error": "No selector provided by LLM"}

    try:
        if action_type == "fill":
            await page.locator(selector).first.fill(value, timeout=5000)
        elif action_type == "click":
            await page.locator(selector).first.click(timeout=5000)
        elif action_type == "select":
            await page.locator(selector).first.select_option(value, timeout=5000)

        # Small wait for page to update
        await asyncio.sleep(0.5)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _check_task_success(page: Page, success_condition: str) -> dict:
    """Ask LLM if the current page state satisfies the task's success condition."""
    page_html = await _get_page_snapshot(page)

    prompt = f"""You are evaluating whether an AI agent successfully completed a task on a webpage.

Current page HTML:
{page_html}

Success condition: {success_condition}

Is the success condition met based on the current page state?
Return valid JSON:
- "success": true or false
- "reasoning": brief explanation

Return ONLY valid JSON, no markdown fencing."""

    response = await nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"success": False, "reasoning": "Failed to parse LLM evaluation"}


async def run_agent(
    url: str,
    site_type: str = "united",
    headless: bool = False,
    on_event: EventCallback | None = None,
) -> dict:
    """Run the full booking agent on a URL.

    Args:
        url: The page to navigate to.
        site_type: "united" or "airbnb" — determines task set.
        headless: If False, browser is visible (for demo streaming).
        on_event: Async callback for streaming events to WebSocket.

    Returns:
        Dict with task results, total score, and screenshots.
    """
    tasks = TASK_SETS.get(site_type, TASK_SETS["united"])

    async def emit(event: dict):
        if on_event:
            await on_event(event)

    results = []
    screenshots = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        await emit({"type": "agent_start", "url": url, "site_type": site_type, "total_tasks": len(tasks)})

        try:
            await page.goto(url, timeout=15000)
            await asyncio.sleep(1)

            # Initial screenshot
            screenshot = await _take_screenshot(page)
            screenshots.append(screenshot)
            await emit({"type": "screenshot", "data": screenshot, "step": "initial"})

            for i, task in enumerate(tasks):
                task_result = {
                    "task_id": task["id"],
                    "task_name": task["name"],
                    "actions_attempted": 0,
                    "actions_succeeded": 0,
                    "completed": False,
                }

                await emit({
                    "type": "task_start",
                    "task_index": i,
                    "task_name": task["name"],
                    "task_id": task["id"],
                })

                for action in task["actions"]:
                    if action["type"] == "read":
                        task_result["actions_attempted"] += 1
                        task_result["actions_succeeded"] += 1
                        continue

                    # Get page state
                    page_html = await _get_page_snapshot(page)

                    # Ask LLM what to do
                    llm_action = await _ask_llm_for_action(
                        page_html, task["description"], action
                    )

                    await emit({
                        "type": "action",
                        "task_id": task["id"],
                        "action": action,
                        "llm_decision": {
                            "selector": llm_action.get("selector", ""),
                            "confidence": llm_action.get("confidence", 0),
                            "reasoning": llm_action.get("reasoning", ""),
                        },
                    })

                    # Execute
                    task_result["actions_attempted"] += 1
                    exec_result = await _execute_action(page, llm_action)

                    if exec_result["success"]:
                        task_result["actions_succeeded"] += 1

                    # Screenshot after action
                    screenshot = await _take_screenshot(page)
                    screenshots.append(screenshot)
                    await emit({
                        "type": "screenshot",
                        "data": screenshot,
                        "step": f"{task['id']}_{action['type']}",
                    })

                    await emit({
                        "type": "action_result",
                        "task_id": task["id"],
                        "success": exec_result["success"],
                        "error": exec_result.get("error"),
                    })

                # Check if task succeeded
                success_check = await _check_task_success(page, task["success_condition"])
                task_result["completed"] = success_check.get("success", False)

                await emit({
                    "type": "task_complete",
                    "task_index": i,
                    "task_id": task["id"],
                    "completed": task_result["completed"],
                    "reasoning": success_check.get("reasoning", ""),
                })

                results.append(task_result)

        except Exception as e:
            await emit({"type": "error", "message": str(e)})
            results.append({"error": str(e)})

        finally:
            # Final screenshot
            try:
                screenshot = await _take_screenshot(page)
                screenshots.append(screenshot)
                await emit({"type": "screenshot", "data": screenshot, "step": "final"})
            except Exception:
                pass

            await browser.close()

    # Score
    tasks_completed = sum(1 for r in results if r.get("completed", False))
    total_tasks = len(tasks)

    summary = {
        "url": url,
        "site_type": site_type,
        "tasks_completed": tasks_completed,
        "total_tasks": total_tasks,
        "score": f"{tasks_completed}/{total_tasks}",
        "task_results": results,
        "screenshot_count": len(screenshots),
    }

    await emit({"type": "agent_complete", "summary": summary})

    return summary
