"""
Browser Utilities for NotebookLM Skill
Handles browser launching, stealth features, and common interactions
"""

from __future__ import annotations

import json
import time
import random
from pathlib import Path

from patchright.sync_api import Playwright, BrowserContext, Page, ElementHandle

# Import from skill's config (need to add skills to path)
# Shared utilities can be imported by any skill, so we need a way to find config
# For now, we'll make these parameters to avoid tight coupling
# The calling code should pass these values from their own config


class BrowserFactory:
    """Factory for creating configured browser contexts"""

    @staticmethod
    def launch_persistent_context(
        playwright: Playwright,
        headless: bool = True,
        user_data_dir: str | None = None,
        state_file: Path | None = None,
        browser_args: list[str] | None = None,
        user_agent: str | None = None
    ) -> BrowserContext:
        """
        Launch a persistent browser context with anti-detection features
        and cookie workaround.

        Args:
            playwright: Playwright instance
            headless: Run in headless mode
            user_data_dir: Path to browser profile directory
            state_file: Path to state.json for cookie injection
            browser_args: List of browser arguments
            user_agent: User agent string
        """
        # Default browser args if not provided
        if browser_args is None:
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--no-first-run',
                '--no-default-browser-check'
            ]

        if user_agent is None:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        # Launch persistent context
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",  # Use real Chrome
            headless=headless,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            user_agent=user_agent,
            args=browser_args
        )

        # Cookie Workaround for Playwright bug #36139
        # Session cookies (expires=-1) don't persist in user_data_dir automatically
        if state_file:
            BrowserFactory._inject_cookies(context, state_file)

        return context

    @staticmethod
    def _inject_cookies(context: BrowserContext, state_file: Path) -> None:
        """Inject cookies from state.json if available"""
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    if 'cookies' in state and len(state['cookies']) > 0:
                        context.add_cookies(state['cookies'])
                        # print(f"  🔧 Injected {len(state['cookies'])} cookies from state.json")
            except Exception as e:
                print(f"  ⚠️  Could not load state.json: {e}")


class StealthUtils:
    """Human-like interaction utilities"""

    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500) -> None:
        """Add random delay"""
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    @staticmethod
    def human_type(page: Page, selector: str, text: str, wpm_min: int = 320, wpm_max: int = 480) -> None:
        """Type with human-like speed"""
        element = page.query_selector(selector)
        if not element:
            # Try waiting if not immediately found
            try:
                element = page.wait_for_selector(selector, timeout=2000)
            except:
                pass
        
        if not element:
            print(f"⚠️ Element not found for typing: {selector}")
            return

        # Click to focus
        element.click()
        
        # Type
        for char in text:
            element.type(char, delay=random.uniform(25, 75))
            if random.random() < 0.05:
                time.sleep(random.uniform(0.15, 0.4))

    @staticmethod
    def random_mouse_movement(page: Page, num_movements: int = 3) -> None:
        """
        Simulate random mouse movements for human-like behavior

        Args:
            page: Playwright page object
            num_movements: Number of random movements to perform
        """
        # Get viewport size
        viewport = page.viewport_size
        if not viewport:
            return  # Skip if no viewport

        width, height = viewport['width'], viewport['height']

        for _ in range(num_movements):
            # Random position within viewport
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)

            # Move mouse with human-like easing
            page.mouse.move(x, y, steps=random.randint(10, 20))

            # Random delay between movements
            time.sleep(random.uniform(0.1, 0.3))

    @staticmethod
    def realistic_click(page: Page, selector: str) -> None:
        """Click with realistic movement"""
        element = page.query_selector(selector)
        if not element:
            return

        # Optional: Move mouse to element (simplified)
        box = element.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.move(x, y, steps=5)

        StealthUtils.random_delay(100, 300)
        element.click()
        StealthUtils.random_delay(100, 300)
