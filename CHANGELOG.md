# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-12

### Added
- **New Skill: YouTube Video Research** (`youtube-research`)
  - Automate NotebookLM notebook creation from YouTube videos
  - Add YouTube URL as source with optional research text
  - Generate Audio Overview from video content
  - Shares authentication with main notebooklm skill
  - Uses same Python/Patchright infrastructure
  - Adapted from [BayramAnnakov/notebooklm-youtube-skill](https://github.com/BayramAnnakov/notebooklm-youtube-skill)

### Technical
- Created `plugins/notebooklm/skills/youtube-research/` skill
- Shared infrastructure via symlinks: `browser_utils.py`, `auth_manager.py`, `setup_environment.py`
- New script: `create_notebook.py` for notebook automation
- UI reference guide: `references/notebooklm_ui_guide.md`

## [2.0.0] - 2026-01-12

### Changed
- **BREAKING: Converted to Standard Claude Plugin Structure**
  - Restructured repository to follow standard Claude Code plugin conventions
  - Added `plugins/notebooklm/.claude-plugin/plugin.json` manifest
  - Moved skill to `plugins/notebooklm/skills/notebooklm/`
  - Installation path changed from `~/.claude/skills` to `~/.claude/plugins`
  - Data directory remains at `~/.claude/skills/notebooklm/data/` for backward compatibility
  - Updated README.md with new installation instructions and directory structure
  - Updated all path references in documentation

### Added
- Plugin manifest (`plugin.json`) with metadata, version, author, and keywords
- Future-ready structure that allows adding additional skills to the plugin

### Migration Guide
**For existing users**: Your data and authentication are safe! The data directory location hasn't changed (`~/.claude/skills/notebooklm/data/`). To update:
```bash
# 1. Remove old installation
rm -rf ~/.claude/skills/notebooklm

# 2. Install new version
mkdir -p ~/.claude/plugins
cd ~/.claude/plugins
git clone https://github.com/PleasePrompto/notebooklm-skill notebooklm
```

Your notebook library and authentication will automatically work with the new structure.

## [1.3.0] - 2025-11-21

### Added
- **Modular Architecture** - Refactored codebase for better maintainability
  - New `config.py` - Centralized configuration (paths, selectors, timeouts)
  - New `browser_utils.py` - BrowserFactory and StealthUtils classes
  - Cleaner separation of concerns across all scripts

### Changed
- **Timeout increased to 120 seconds** - Long queries no longer timeout prematurely
  - `ask_question.py`: 30s → 120s
  - `browser_session.py`: 30s → 120s
  - Resolves Issue #4

### Fixed
- **Thinking Message Detection** - Fixed incomplete answers showing placeholder text
  - Now waits for `div.thinking-message` element to disappear before reading answer
  - Answers like "Reviewing the content..." or "Looking for answers..." no longer returned prematurely
  - Works reliably across all languages and NotebookLM UI changes

- **Correct CSS Selectors** - Updated to match current NotebookLM UI
  - Changed from `.response-content, .message-content` to `.to-user-container .message-text-content`
  - Consistent selectors across all scripts

- **Stability Detection** - Improved answer completeness check
  - Now requires 3 consecutive stable polls instead of 1 second wait
  - Prevents truncated responses during streaming

## [1.2.0] - 2025-10-28

### Added
- Initial public release
- NotebookLM integration via browser automation
- Session-based conversations with Gemini 2.5
- Notebook library management
- Knowledge base preparation tools
- Google authentication with persistent sessions
