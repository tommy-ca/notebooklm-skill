---
status: pending
priority: p2
issue_id: 012
tags: [architecture, symlinks, complexity, windows-compatibility]
dependencies: []
---

# Symlink Strategy Adds Unnecessary Complexity

## Problem Statement

The youtube-research skill uses symlinks to share 4 files with the notebooklm skill (`auth_manager.py`, `browser_utils.py`, `setup_environment.py`, `__init__.py`). This adds 24 lines of security verification code, creates Windows compatibility issues, and introduces mental overhead with minimal benefit over direct file copying.

**Why it matters**: The complexity of symlink verification, .gitattributes configuration, and cross-platform compatibility outweighs the benefit of avoiding ~200 lines of code duplication. The security verification code is itself a form of complexity that wouldn't exist without symlinks.

**Severity**: P2 - Architectural over-engineering that hinders maintainability

## Findings

**Files**:
- `plugins/notebooklm/skills/youtube-research/scripts/` (4 symlink files)
- `plugins/notebooklm/skills/youtube-research/scripts/create_notebook.py` (lines 20-43: verification code)
- `.gitattributes` (symlink tracking configuration)

**Source**: Code simplicity reviewer + Architecture strategist + Security sentinel

**Complexity Added**:
- 24 lines of symlink verification code (`verify_symlink_safety()` function + loop)
- 2 lines of .gitattributes configuration
- sys.path manipulation required for imports
- Windows developer mode requirement
- Security verification overhead on every script execution

**Complexity vs Benefit**:
- Symlinks save: ~200 lines (4 shared files)
- Symlinks add: ~26 lines of verification + ongoing mental overhead
- Net savings: ~174 lines but MUCH higher complexity

**Windows Compatibility Issue**:
Symlinks don't work on Windows without developer mode enabled. Git may check out symlinks as text files containing the link path.

## Proposed Solutions

### Solution 1: Remove Symlinks, Copy Files Directly (Recommended)
**Pros**:
- Zero security verification code needed
- Works on all platforms (Windows, Mac, Linux)
- Clear, explicit imports
- No runtime verification overhead
- No .gitattributes needed
- Simpler mental model

**Cons**: ~200 LOC duplication (4 files)

**Effort**: Small (1 hour)
**Risk**: None

**Implementation**:
```bash
# Remove symlinks
cd plugins/notebooklm/skills/youtube-research/scripts/
rm auth_manager.py browser_utils.py setup_environment.py __init__.py

# Copy files directly
cp ../../notebooklm/scripts/auth_manager.py .
cp ../../notebooklm/scripts/browser_utils.py .
cp ../../notebooklm/scripts/setup_environment.py .
cp ../../notebooklm/scripts/__init__.py .

# Remove verification code from create_notebook.py (lines 20-43)
# Remove .gitattributes
# Remove sys.path manipulation
```

### Solution 2: Create Proper Python Package
**Pros**:
- Standard Python import mechanism
- No symlinks, no verification code
- pip manages dependencies correctly

**Cons**: More architectural change required

**Effort**: Medium (2-3 hours)
**Risk**: Low

**Implementation**:
```python
# Create plugins/notebooklm/shared_lib/ package
# Move shared files to shared_lib/
# Install as editable package: pip install -e ../../shared_lib
# Import normally: from shared_lib import auth_manager
```

### Solution 3: Keep Symlinks, Accept Complexity
**Pros**: Avoids duplication
**Cons**: All current complexity remains

**Effort**: None
**Risk**: Ongoing maintenance burden

## Recommended Action

Implement **Solution 1** (remove symlinks, copy files) for immediate simplification. The ~200 lines of duplication is a worthy trade-off for eliminating 26 lines of complex security code, Windows compatibility issues, and mental overhead.

**Philosophy**: Choose "simple" over "clever". Accept duplication to eliminate complexity.

## Technical Details

**Files to Change**:
- Remove 4 symlinks in `youtube-research/scripts/`
- Copy 4 files from `notebooklm/scripts/`
- Remove lines 20-43 in `create_notebook.py` (verification code)
- Remove lines 46-47 (sys.path manipulation)
- Remove `.gitattributes` file
- Update imports in `create_notebook.py` to be direct

**LOC Impact**:
- Remove: 24 lines (verification) + 2 lines (.gitattributes) = -26 lines
- Add: ~200 lines (copied files)
- Net: +174 lines but MUCH simpler

## Acceptance Criteria

- [ ] Remove all 4 symlinks
- [ ] Copy files directly into youtube-research/scripts/
- [ ] Remove `verify_symlink_safety()` function
- [ ] Remove symlink verification loop
- [ ] Remove sys.path manipulation
- [ ] Delete `.gitattributes` file
- [ ] Test youtube-research skill works on all platforms
- [ ] Verify Windows compatibility (no developer mode needed)

## Work Log

_No work completed yet_

## Resources

- Code Simplicity Reviewer findings: "Symlink Strategy - Over-engineered Solution"
- Architecture Strategist findings: "Recommendation #1: Replace Symlinks with Proper Python Package"
- YAGNI Principle: https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it
