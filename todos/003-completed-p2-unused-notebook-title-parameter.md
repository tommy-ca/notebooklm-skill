---
status: pending
priority: p2
issue_id: 003
tags: [code-quality, code-review, youtube-research, api-design]
dependencies: []
---

# Unused notebook_title Parameter - Misleading API

## Problem Statement

The `create_notebook.py` script accepts a `--notebook-title` parameter but never actually uses it to set the notebook title in NotebookLM. It only prints the title to console, creating a misleading API that promises functionality it doesn't deliver.

**Why it matters**: Users expect this parameter to work. The misleading API creates confusion and tech debt. Either implement the feature properly or remove it entirely.

**Severity**: P2 - Functional bug and API design issue

## Findings

**File**: `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py`
**Lines**: 29, 133-134, 159-160, 192

**Source**: Code reviewer agent (pr-review-toolkit:code-reviewer)

**Evidence**:
```python
# Line 29: Parameter accepted
async def create_notebook_from_youtube(
    youtube_url: str,
    research_text: str = None,
    notebook_title: str = None,  # Accepted but never used!
    ...
):

# Lines 133-134: Only printed, not actually set
if notebook_title:
    print(f"   Title: {notebook_title}")

# Lines 159-160: Documented in argparse
parser.add_argument(
    "--notebook-title",
    help="Custom notebook title (optional)"
)

# Line 192: Passed but ignored
notebook_url = asyncio.run(
    create_notebook_from_youtube(
        notebook_title=args.notebook_title,  # Never used!
        ...
    )
)
```

**Current behavior**: Title is printed but notebook retains default auto-generated name from YouTube video.

## Proposed Solutions

### Solution 1: Remove the Parameter (Recommended - YAGNI)
**Pros**:
- Simplest solution
- No misleading API
- NotebookLM auto-generates good titles from video content anyway

**Cons**:
- Loses potential future feature

**Effort**: Small
**Risk**: Low

**Implementation**:
```python
# Remove from function signature (line 29)
# Remove from print statement (lines 133-134)
# Remove from argparse (lines 159-160)
# Remove from function call (line 192)
# Update SKILL.md to remove --notebook-title from examples
```

### Solution 2: Implement Title Setting
**Pros**:
- Delivers promised functionality
- Gives users control

**Cons**:
- NotebookLM may not have API to set custom title
- Requires additional browser automation
- May need to rename after creation
- More complex implementation

**Effort**: Medium
**Risk**: Medium (may not be technically feasible)

**Implementation**:
```python
# After notebook creation:
if notebook_title:
    # Find title element (inspect NotebookLM UI)
    title_element = await page.query_selector("...")
    await title_element.click()
    await title_element.fill(notebook_title)
    # May require additional waiting/confirmation
```

## Recommended Action

Implement **Solution 1** (remove parameter) following YAGNI principle. NotebookLM auto-generates titles from video content, which is usually sufficient.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py` (lines 29, 133-134, 159-160, 192)
- `plugins/notebooklm/skills/youtube-research/SKILL.md` (documentation examples showing --notebook-title)

**Lines of Code to Remove**: ~6

**Breaking Change**: Yes (removes documented parameter)

**Migration Guide**: Remove `--notebook-title` from any scripts using this parameter. NotebookLM will auto-generate titles.

## Acceptance Criteria

- [ ] notebook_title parameter removed from function signature
- [ ] Parameter removed from argparse
- [ ] Print statement referencing title removed
- [ ] SKILL.md updated to remove --notebook-title examples
- [ ] README.md checked for any references
- [ ] CHANGELOG.md updated noting parameter removal

## Work Log

_No work completed yet_

## Resources

- Code review findings: See code-reviewer agent output
- YAGNI principle: https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it
- NotebookLM UI inspection needed to determine if title-setting is feasible
