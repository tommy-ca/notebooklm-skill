"""
Configuration for YouTube Research Skill
Centralizes constants, selectors, and paths for NotebookLM notebook creation
"""

from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
# Use standardized data location (shared with main notebooklm skill)
DATA_DIR = Path.home() / ".claude" / "skills" / "notebooklm" / "data"
BROWSER_STATE_DIR = DATA_DIR / "browser_state"
BROWSER_PROFILE_DIR = BROWSER_STATE_DIR / "browser_profile"
STATE_FILE = BROWSER_STATE_DIR / "state.json"
AUTH_INFO_FILE = DATA_DIR / "auth_info.json"

# NotebookLM Home Page Selectors
NEW_NOTEBOOK_BUTTON = "button:has-text('New notebook')"
NOTEBOOK_CARD = ".notebook-card"

# Source Addition Selectors
ADD_SOURCE_BUTTON = "button:has-text('Add source')"
YOUTUBE_URL_INPUT = "textarea[placeholder='Paste any links']"
TEXT_SOURCE_INPUT = "textarea[placeholder='Paste text here']"
INSERT_BUTTON = "button:has-text('Insert')"

# Audio Overview Selectors
STUDIO_PANEL = "[data-panel='studio']"
AUDIO_OVERVIEW_BUTTON = "button:has-text('Audio Overview')"
GENERATE_BUTTON = "button:has-text('Generate')"

# Status Selectors
SOURCE_COUNT = ".source-count"
PROCESSING_INDICATOR = ".processing"
AUDIO_GENERATING = ".audio-generating"

# Browser Configuration
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--no-first-run',
    '--no-default-browser-check'
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Timeouts
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds
DIALOG_OPEN_TIMEOUT = 2000  # 2 seconds
YOUTUBE_PROCESSING_TIMEOUT = 10000  # 10 seconds
TEXT_PROCESSING_TIMEOUT = 5000  # 5 seconds
AUDIO_GENERATION_TIMEOUT = 600000  # 10 minutes

