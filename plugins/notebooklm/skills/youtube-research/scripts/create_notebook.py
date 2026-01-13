#!/usr/bin/env python3
"""
NotebookLM Notebook Creator from YouTube Videos

Creates a new NotebookLM notebook with YouTube video and optional research text as sources.
Can optionally generate an audio overview.

Usage:
    python create_notebook.py --youtube-url URL [--research TEXT] [--generate-audio] [--show-browser]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import re
from pathlib import Path
from typing import NoReturn
from urllib.parse import urlparse

# Import shared utilities from shared module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
from browser_utils import BrowserFactory, StealthUtils
from auth_manager import AuthManager

# Import local config
import config


def validate_youtube_url(url: str) -> bool:
    """Validate that URL is a legitimate YouTube URL with strict video ID validation"""
    try:
        parsed = urlparse(url)

        # Must be HTTPS
        if parsed.scheme != 'https':
            return False

        # Must be YouTube domain
        allowed_domains = [
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            'm.youtube.com'
        ]
        if parsed.netloc not in allowed_domains:
            return False

        # Extract and validate video ID
        video_id = None
        if parsed.netloc == 'youtu.be':
            # Format: https://youtu.be/VIDEO_ID
            match = re.match(r'^/([A-Za-z0-9_-]{11})/?$', parsed.path)
            if match:
                video_id = match.group(1)
        else:
            # Format: https://youtube.com/watch?v=VIDEO_ID
            from urllib.parse import parse_qs
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                potential_id = query_params['v'][0]
                if re.match(r'^[A-Za-z0-9_-]{11}$', potential_id):
                    video_id = potential_id

        return video_id is not None
    except (ValueError, AttributeError, TypeError, KeyError):
        return False


async def create_notebook_from_youtube(
    youtube_url: str,
    research_text: str | None = None,
    generate_audio: bool = False,
    show_browser: bool = False
) -> str:
    """
    Create a NotebookLM notebook from a YouTube video.

    Args:
        youtube_url: YouTube video URL
        research_text: Optional research text to add as second source
        generate_audio: Whether to generate audio overview
        show_browser: Whether to show browser window

    Returns:
        str: Notebook URL
    """
    print(f"🎥 Creating NotebookLM notebook from: {youtube_url}")

    # Launch browser with existing auth
    browser_factory = BrowserFactory(
        headless=not show_browser,
        user_data_dir=str(config.BROWSER_PROFILE_DIR)
    )

    async with browser_factory.launch_persistent_context() as (browser, context):
        # Load saved auth state
        auth_manager = AuthManager(context)
        await auth_manager.load_state()

        page = await context.new_page()

        try:
            # Step 1: Navigate to NotebookLM
            print("📂 Navigating to NotebookLM...")
            await page.goto("https://notebooklm.google.com/", timeout=config.PAGE_LOAD_TIMEOUT)
            await page.wait_for_load_state("networkidle")

            # Step 2: Create new notebook
            print("➕ Creating new notebook...")
            await page.click(config.NEW_NOTEBOOK_BUTTON)
            await page.wait_for_timeout(config.DIALOG_OPEN_TIMEOUT)

            # Step 3: Add YouTube source
            print("🔗 Adding YouTube video as source...")
            await page.click(config.ADD_SOURCE_BUTTON)
            await page.wait_for_timeout(config.DIALOG_OPEN_TIMEOUT)

            # Type YouTube URL with human-like typing
            youtube_input = await page.wait_for_selector(config.YOUTUBE_URL_INPUT)
            await StealthUtils.human_like_type(youtube_input, youtube_url)

            # Click Insert button
            insert_button = await page.wait_for_selector(config.INSERT_BUTTON)
            await insert_button.click()

            # Wait for YouTube processing
            print("⏳ Processing YouTube video... (this takes ~10 seconds)")
            await page.wait_for_timeout(config.YOUTUBE_PROCESSING_TIMEOUT)

            # Step 4: Add research text if provided
            if research_text:
                print("📝 Adding research text as second source...")
                await page.click(config.ADD_SOURCE_BUTTON)
                await page.wait_for_timeout(config.DIALOG_OPEN_TIMEOUT)

                # Type research text
                text_input = await page.wait_for_selector(config.TEXT_SOURCE_INPUT)
                await StealthUtils.human_like_type(text_input, research_text)

                # Click Insert button
                insert_button = await page.wait_for_selector(config.INSERT_BUTTON)
                await insert_button.click()

                # Wait for text processing
                print("⏳ Processing research text...")
                await page.wait_for_timeout(config.TEXT_PROCESSING_TIMEOUT)

            # Step 5: Generate audio overview if requested
            if generate_audio:
                print("🎙️ Generating audio overview...")
                print("⚠️  This can take 5-10 minutes - please be patient!")

                try:
                    # Click Audio Overview button
                    await page.click(config.AUDIO_OVERVIEW_BUTTON)
                    await page.wait_for_timeout(config.DIALOG_OPEN_TIMEOUT)

                    # Click Generate button
                    generate_button = await page.wait_for_selector(config.GENERATE_BUTTON)
                    await generate_button.click()

                    print("✅ Audio overview generation started!")
                    print("   (Generation continues in background - notebook is ready to use)")
                except Exception as e:
                    print(f"⚠️  Warning: Could not start audio generation: {e}")
                    print("   You can generate it manually from the notebook")

            # Get notebook URL
            notebook_url = page.url

            print(f"\n✅ Notebook created successfully!")
            print(f"   URL: {notebook_url}")

            return notebook_url

        except Exception as e:
            print(f"\n❌ Error creating notebook: {e}")
            raise
        finally:
            await page.close()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Create NotebookLM notebook from YouTube video"
    )
    parser.add_argument(
        "--youtube-url",
        required=True,
        help="YouTube video URL"
    )
    parser.add_argument(
        "--research",
        help="Research text to add as second source"
    )
    parser.add_argument(
        "--generate-audio",
        action="store_true",
        help="Generate audio overview after adding sources"
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Show browser window for debugging"
    )

    args = parser.parse_args()

    # Check authentication
    print("🔐 Checking authentication status...")
    auth_check = AuthManager.check_auth_status()

    if not auth_check["authenticated"]:
        print("\n❌ Not authenticated with Google!")
        print("   Please authenticate first using the main notebooklm skill:")
        print("   cd ../notebooklm && python scripts/run.py auth_manager.py setup")
        sys.exit(1)

    print("✅ Authenticated as Google user")

    # Validate YouTube URL
    if not validate_youtube_url(args.youtube_url):
        print("❌ Invalid YouTube URL")
        print("   Expected: https://youtube.com/watch?v=VIDEO_ID")
        print("   Or: https://youtu.be/VIDEO_ID")
        sys.exit(1)

    # Create notebook
    notebook_url = asyncio.run(
        create_notebook_from_youtube(
            youtube_url=args.youtube_url,
            research_text=args.research,
            generate_audio=args.generate_audio,
            show_browser=args.show_browser
        )
    )

    print(f"\n🎉 Done! Notebook URL: {notebook_url}")


if __name__ == "__main__":
    main()
