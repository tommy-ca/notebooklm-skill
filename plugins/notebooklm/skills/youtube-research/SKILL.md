---
name: youtube-research
description: Automate NotebookLM notebook creation from YouTube videos. Given a YouTube video URL, extract information about people featured in the video, research them online, create a new NotebookLM notebook with the video and research as sources, and generate an audio overview.
---

# NotebookLM YouTube Video Research Skill

Automate NotebookLM notebook creation from YouTube videos with automatic research and Audio Overview generation.

## When to Use This Skill

Trigger when user:
- Provides a YouTube URL and wants to create a NotebookLM notebook
- Asks to "research this video"
- Wants to "create notebook from YouTube video"
- Mentions creating audio overview from YouTube content
- Uses phrases like "analyze this YouTube video", "research people in this video"

## Critical: Always Use run.py Wrapper

**NEVER call scripts directly. ALWAYS use `python scripts/run.py [script]`:**

```bash
# ✅ CORRECT - Always use run.py:
python scripts/run.py create_notebook.py --youtube-url "..."

# ❌ WRONG - Never call directly:
python scripts/create_notebook.py  # Fails without venv!
```

The `run.py` wrapper automatically:
1. Creates `.venv` if needed
2. Installs all dependencies
3. Activates environment
4. Executes script properly

## Core Workflow

### Step 1: Check Authentication Status

This skill shares authentication with the main notebooklm skill:

```bash
python scripts/run.py auth_manager.py status
```

If not authenticated, the user must authenticate via the main notebooklm skill:
```bash
cd ../notebooklm
python scripts/run.py auth_manager.py setup
```

### Step 2: Create Notebook from YouTube URL

**Basic usage:**
```bash
python scripts/run.py create_notebook.py --youtube-url "https://www.youtube.com/watch?v=VIDEO_ID"
```

**With research (optional):**
```bash
# First, research the video manually or ask Claude to research
# Then create notebook with both video and research:
python scripts/run.py create_notebook.py \
  --youtube-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --research "Research text about people mentioned..." \
  --generate-audio
```

**Options:**
- `--youtube-url URL` - YouTube video URL (required)
- `--research TEXT` - Research text to add as second source (optional)
- `--generate-audio` - Generate audio overview after adding sources (optional)
- `--show-browser` - Show browser for debugging (optional)

### Step 3: Workflow with Research

**Complete example:**

```bash
# User provides YouTube URL
# Claude researches people mentioned in video using web_search
# Claude creates research document
# Claude runs create_notebook with both sources

python scripts/run.py create_notebook.py \
  --youtube-url "https://www.youtube.com/watch?v=abc123" \
  --research "Detailed research about Person A: career, background..." \
  --generate-audio
```

## Script Reference

### Notebook Creation (`create_notebook.py`)

```bash
python scripts/run.py create_notebook.py \
  --youtube-url URL \
  [--research TEXT] \
  [--generate-audio] \
  [--show-browser]
```

**What it does:**
1. Uses shared authentication from main notebooklm skill
2. Navigates to notebooklm.google.com
3. Creates new notebook
4. Adds YouTube URL as first source
5. Optionally adds research text as second source
6. Optionally generates audio overview
7. Returns notebook URL

## Environment Management

The virtual environment is shared with the main notebooklm skill through symlinked scripts.

Manual setup (only if automatic fails):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r ../notebooklm/requirements.txt
```

## Data Storage

Authentication is shared with the main notebooklm skill:
- Auth stored at: `~/.claude/skills/notebooklm/data/`
- Browser state shared between skills
- Single Google login for all NotebookLM operations

## Decision Flow

```
User provides YouTube URL
    ↓
Check auth → python scripts/run.py auth_manager.py status
    ↓
If not authenticated → Redirect to main skill for auth
    ↓
Optionally: Research video content (use web_search, extract info)
    ↓
Create notebook → python scripts/run.py create_notebook.py --youtube-url "..."
    ↓
Return notebook URL to user
```

## Critical Implementation Notes

**Element Targeting:**
- NotebookLM has multiple textareas - must use specific selectors
- URL input: `textarea[placeholder="Paste any links"]`
- Text input: `textarea[placeholder="Paste text here"]`
- Always verify correct textarea is targeted

**Wait Times:**
- YouTube source processing: 8-10 seconds
- Text source processing: 5 seconds
- Audio generation: 5-10 minutes (long operation!)

**Error Handling:**
- Check button states before clicking
- Wait for async operations to complete
- Verify sources were added successfully

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Authentication fails | Use main notebooklm skill to re-authenticate |
| Wrong textarea targeted | Script uses specific selectors to avoid this |
| Source processing stuck | Wait longer, show browser to debug |
| Audio generation timeout | Audio takes 5-10 minutes, be patient |

## Best Practices

1. **Always authenticate via main skill first** - Shared auth simplifies workflow
2. **Research before creating** - Better notebooks with context
3. **Use --show-browser for debugging** - See what's happening
4. **Be patient with audio** - Generation takes 5-10 minutes
5. **Return notebook URL** - User can access it later

## Limitations

- Requires existing authentication (via main notebooklm skill)
- Audio generation is slow (5-10 minutes)
- YouTube videos must be publicly accessible
- Research text must be provided manually or via web_search

## Resources (Skill Structure)

**Important directories and files:**

- `scripts/` - All automation scripts
- `scripts/run.py` - Universal wrapper (shared pattern with main skill)
- `scripts/config.py` - NotebookLM UI selectors and configuration
- `scripts/create_notebook.py` - Main notebook creation script
- `references/` - Extended documentation
  - `notebooklm_ui_guide.md` - UI element reference
