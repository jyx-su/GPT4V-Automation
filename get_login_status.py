import asyncio
from playwright.async_api import async_playwright, Playwright
import time

async def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = await firefox.launch_persistent_context('', headless=False, timeout=0)
    page = await browser.new_page()
    await page.goto("https://chat.openai.com")
    time.sleep(90)
    storage = await browser.storage_state(path="state.json")
    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
