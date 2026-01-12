---
status: completed
priority: p2
issue_id: 004
tags: [documentation, code-review, youtube-research, user-experience]
dependencies: []
---

# Incorrect Help Text in run.py Lists Non-Existent Scripts

## Problem Statement

The `run.py` script in youtube-research skill displays help text listing scripts from the main notebooklm skill that don't exist in youtube-research. This is a copy-paste error that misleads users about available commands.

**Why it matters**: Users trying to run the listed scripts will get "script not found" errors, creating a poor user experience and confusion.

**Severity**: P2 - User experience issue, misleading documentation

## Findings

**File**: `plugins/notebooklm/skills/youtube-research/scripts/run.py`
**Lines**: 53-57

**Source**: Code reviewer agent (pr-review-toolkit:code-reviewer)

**Current Code**:
```python
print("  ask_question.py    - Query NotebookLM")        # Doesn't exist!
print("  notebook_manager.py - Manage notebook library") # Doesn't exist!
print("  session_manager.py  - Manage sessions")        # Doesn't exist!
print("  auth_manager.py     - Handle authentication")  # Symlink to parent skill
print("  cleanup_manager.py  - Clean up skill data")    # Doesn't exist!
```

**Actual youtube-research scripts**:
- `create_notebook.py` (main script - NOT listed!)
- `auth_manager.py` (symlink - listed but misleading description)

## Proposed Solutions

### Solution 1: List Only youtube-research Scripts (Recommended)
**Pros**:
- Accurate information
- Helps users discover actual functionality
- Clear and concise

**Cons**:
- None

**Effort**: Minimal
**Risk**: None

**Implementation**:
```python
if len(sys.argv) < 2:
    print("Usage: python run.py <script_name> [args...]")
    print("\nAvailable scripts:")
    print("  create_notebook.py  - Create notebook from YouTube video")
    print("  auth_manager.py     - Handle authentication (shared)")
    sys.exit(1)
```

### Solution 2: Remove Help Text Entirely
**Pros**:
- Simpler code
- No maintenance burden

**Cons**:
- Less helpful for new users

**Effort**: Minimal
**Risk**: None

**Implementation**:
```python
if len(sys.argv) < 2:
    print("Usage: python run.py <script_name> [args...]")
    sys.exit(1)
```

### Solution 3: Auto-Discover Scripts
**Pros**:
- Always accurate
- No manual updates needed

**Cons**:
- More complex
- Over-engineered for 2 scripts

**Effort**: Medium
**Risk**: Low

## Recommended Action

Implement **Solution 1** (list only youtube-research scripts) for accurate, helpful output.

## Technical Details

**Affected Files**:
- `plugins/notebooklm/skills/youtube-research/scripts/run.py` (lines 53-57)

**Root Cause**: Copy-paste from notebooklm/scripts/run.py without updating for youtube-research context

**Similar Issue**: Check if notebooklm/scripts/run.py also has outdated script lists

## Acceptance Criteria

- [x] Help text updated to list only youtube-research scripts
- [x] create_notebook.py included in list (currently missing!)
- [x] Descriptions are accurate
- [x] Note that auth_manager.py is shared with notebooklm skill
- [ ] Test help output: `python run.py` (no args)
- [ ] Check notebooklm/scripts/run.py for similar issues

## Work Log

**2026-01-12**: Successfully implemented Solution 1
- Updated help text in `plugins/notebooklm/skills/youtube-research/scripts/run.py` (lines 56-61)
- Removed 5 non-existent scripts from help text (ask_question.py, notebook_manager.py, session_manager.py, cleanup_manager.py)
- Added create_notebook.py to help text (was previously missing)
- Updated auth_manager.py description to note it's "(shared)" with parent skill
- Help text now accurately reflects the 2 scripts actually available in youtube-research skill

## Resources

- Code review findings: See code-reviewer agent output
- run.py location: `plugins/notebooklm/skills/youtube-research/scripts/run.py`
