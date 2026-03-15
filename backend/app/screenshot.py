"""Capture a screenshot of a URL using Playwright."""

import base64

from playwright.async_api import async_playwright


async def capture_screenshot(url: str, width: int = 1280, height: int = 800) -> str:
    """Navigate to a URL and return a base64-encoded PNG screenshot."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": width, "height": height})
        try:
            await page.goto(url, wait_until="load", timeout=30000)
        except Exception:
            # If full load times out, try with just domcontentloaded
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception:
                pass
        # Give JS-heavy SPAs time to render
        await page.wait_for_timeout(3000)
        screenshot_bytes = await page.screenshot(type="png")
        await browser.close()
        return base64.b64encode(screenshot_bytes).decode("utf-8")
